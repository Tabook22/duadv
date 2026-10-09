"""
Meeting Engine for Dhofar University Advising System
Manages virtual rooms, WebRTC peer signaling exchange, live text chat,
collaborative advising notes, in-meeting document sharing, waiting room admission control,
passcode security, session recordings, and meeting duration timers.
"""

import os
import json
import shutil
import time
import uuid
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from werkzeug.utils import secure_filename

MEETINGS_STORAGE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'data', 'meetings'
)
os.makedirs(MEETINGS_STORAGE_DIR, exist_ok=True)

class MeetingRoom:
    """Represents a virtual advising meeting room (supports 1-on-1, multi-student and guest sessions)"""
    def __init__(self, room_id: str, title: str = 'Advising Session', 
                 student_id: Optional[str] = None, student_name: Optional[str] = None,
                 target_students: Optional[List[Dict[str, Any]]] = None,
                 advisor_name: str = 'Dr. Nasser Tabook',
                 passcode: Optional[str] = None,
                 require_admission: bool = True,
                 duration_minutes: Optional[int] = 30,
                 max_participants: Optional[int] = None,
                 external_invitees: Optional[List[Dict[str, Any]]] = None):
        self.room_id = room_id
        self.title = title
        self.advisor_name = advisor_name
        self.created_at = datetime.now()
        self.last_activity = time.time()
        self.start_timestamp = time.time()
        
        # Security & Admission Controls
        self.passcode = passcode.strip() if passcode and passcode.strip() else None
        self.require_passcode = bool(self.passcode)
        self.require_admission = require_admission
        self.duration_minutes = duration_minutes
        self.max_participants = max_participants
        self.is_ended = False
        
        # Waiting room registry: {session_id: {'session_id': str, 'name': str, 'role': str, 'affiliation': str, 'requested_at': float, 'status': 'waiting'|'admitted'|'denied'}}
        self.waiting_room: Dict[str, Dict[str, Any]] = {}
        self.admitted_sessions: Set[str] = set()

        # External Guests (Co-advisors, parents, observers)
        self.external_invitees: List[Dict[str, Any]] = external_invitees or []
        
        # Multiple target students tracking
        self.target_students: List[Dict[str, Any]] = target_students or []
        if student_id and not self.target_students:
            self.target_students.append({
                'id': student_id,
                'name': student_name or f'Student {student_id}'
            })
            
        # Backward compatibility single student attributes
        if self.target_students:
            self.student_id = self.target_students[0]['id']
            if len(self.target_students) == 1:
                self.student_name = self.target_students[0]['name']
            else:
                self.student_name = f"{len(self.target_students)} Advisees Group"
        elif self.external_invitees:
            self.student_id = None
            self.student_name = self.external_invitees[0].get('name', 'External Guest')
        else:
            self.student_id = student_id
            self.student_name = student_name or (f'Student {student_id}' if student_id else 'Student Group')
            
        # Participants tracking: {session_id: {'name': str, 'role': str, 'affiliation': str, 'last_seen': float}}
        self.participants: Dict[str, Dict[str, Any]] = {}
        
        # Signaling inbox: {recipient_session_id: [signals]}
        self.signals: Dict[str, List[Dict[str, Any]]] = {}
        
        # Chat messages: list of {'id': str, 'sender': str, 'role': str, 'text': str, 'time': str, 'is_system': bool}
        self.chat_messages: List[Dict[str, Any]] = []
        
        # Shared advising notes
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        students_bullet = "\n".join([f"- **{s.get('name', 'Student')}** (ID: {s.get('id', '')})" for s in self.target_students]) if self.target_students else f"- {self.student_name}"
        self.notes: str = (
            f"### Academic Advising Notes - {self.title}\n"
            f"**Date:** {now_str}\n"
            f"**Advisor / Host:** {self.advisor_name}\n\n"
            f"#### Participating Advisees & Guests:\n{students_bullet}\n\n"
            "#### 1. Academic Status & Goals\n- \n\n"
            "#### 2. Course Registration & Schedule Agreements\n- \n\n"
            "#### 3. Agreed Action Items & Follow-up\n- \n"
        )
        self.notes_version: int = 1
        
        # Shared files: list of {'id': str, 'filename': str, 'original_name': str, 'uploaded_by': str, 'size': int, 'time': str}
        self.shared_files: List[Dict[str, Any]] = []

        # Session Recordings: list of {'id': str, 'filename': str, 'original_name': str, 'recorded_by': str, 'size': int, 'duration': str, 'time': str}
        self.recordings: List[Dict[str, Any]] = []

        # Advisor Multi-Page Interactive Notebook & Whiteboard
        self.notebook: Dict[str, Any] = self._load_notebook()

    def _load_notebook(self) -> Dict[str, Any]:
        """Loads persistent notebook from disk or initializes default multi-page notebook"""
        room_dir = os.path.join(MEETINGS_STORAGE_DIR, self.room_id)
        os.makedirs(room_dir, exist_ok=True)
        nb_path = os.path.join(room_dir, 'notebook.json')
        if os.path.exists(nb_path):
            try:
                with open(nb_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'pages' in data and len(data['pages']) > 0:
                        return data
            except Exception:
                pass
        
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        header_text = (
            f"Advising Session: {self.title}\n"
            f"Date: {now_str}\n"
            f"Advisee: {self.student_name}\n"
            f"Advisor: {self.advisor_name}\n\n"
            f"Notes & Recommendations:\n- "
        )
        return {
            'pages': [
                {
                    'id': 'page_1',
                    'title': 'Page 1 - Advising Session Plan',
                    'pattern': 'lined',
                    'color': '#ffffff',
                    'drawing': '',
                    'notes': header_text,
                    'created_at': now_str
                }
            ],
            'current_page': 0,
            'updated_at': time.time(),
            'version': 1
        }

    def update_notebook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates and persists the multi-page notebook to memory and disk"""
        self.touch()
        if not isinstance(data, dict):
            return self.notebook
            
        pages = data.get('pages', [])
        if not pages:
            pages = self.notebook.get('pages', [])
            
        current_page = int(data.get('current_page', 0))
        if current_page < 0 or current_page >= len(pages):
            current_page = 0
            
        version = int(self.notebook.get('version', 0)) + 1
        
        self.notebook = {
            'pages': pages,
            'current_page': current_page,
            'updated_at': time.time(),
            'version': version
        }
        
        self.save_notebook_to_disk()
        return self.notebook

    def save_notebook_to_disk(self) -> bool:
        """Persist notebook JSON file in meeting data folder"""
        try:
            room_dir = os.path.join(MEETINGS_STORAGE_DIR, self.room_id)
            os.makedirs(room_dir, exist_ok=True)
            nb_path = os.path.join(room_dir, 'notebook.json')
            with open(nb_path, 'w', encoding='utf-8') as f:
                json.dump(self.notebook, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def touch(self):
        """Update activity timestamp"""
        self.last_activity = time.time()

    def get_remaining_seconds(self) -> Optional[int]:
        """Calculates remaining duration in seconds, or None if unlimited"""
        if not self.duration_minutes or self.duration_minutes <= 0:
            return None
        elapsed = time.time() - self.start_timestamp
        total_seconds = self.duration_minutes * 60
        return max(0, int(total_seconds - elapsed))

    def extend_duration(self, minutes: int = 15) -> int:
        """Host extends meeting time limit"""
        self.touch()
        if not self.duration_minutes:
            self.duration_minutes = minutes
        else:
            self.duration_minutes += minutes
        return self.duration_minutes

    def end_meeting(self) -> bool:
        """Host terminates the meeting for all participants"""
        self.touch()
        self.is_ended = True
        return True

    def request_admission(self, session_id: str, name: str, role: str = 'guest', 
                          passcode: Optional[str] = None, affiliation: str = '') -> Dict[str, Any]:
        """Validates credentials and requests entry or grants entry"""
        self.touch()
        if self.is_ended:
            return {'status': 'ended', 'message': 'This meeting has ended.'}

        # Check Passcode if enabled
        if self.require_passcode and role != 'advisor':
            entered_pin = (passcode or '').strip()
            if not entered_pin or entered_pin.lower() != (self.passcode or '').lower():
                return {'status': 'error', 'message': 'Incorrect meeting passcode. Please verify and try again.'}

        # Capacity check
        if self.max_participants and len(self.participants) >= self.max_participants and session_id not in self.participants:
            return {'status': 'error', 'message': f'Meeting room has reached its maximum capacity of {self.max_participants} attendees.'}

        # Advisor/Host is always auto-admitted
        if role == 'advisor':
            self.admitted_sessions.add(session_id)
            return {'status': 'admitted', 'message': 'Host admitted automatically.'}

        # If already admitted previously
        if session_id in self.admitted_sessions:
            return {'status': 'admitted', 'message': 'Admitted.'}

        # If waiting room admission is not required
        if not self.require_admission:
            self.admitted_sessions.add(session_id)
            return {'status': 'admitted', 'message': 'Admitted directly.'}

        # Place in waiting room
        self.waiting_room[session_id] = {
            'session_id': session_id,
            'name': name.strip() or 'Guest',
            'role': role,
            'affiliation': affiliation.strip() or ('Student' if role == 'student' else 'Guest'),
            'requested_at': time.time(),
            'status': 'waiting'
        }
        return {'status': 'waiting', 'message': 'Entry request submitted. Waiting for host approval.'}

    def check_admission_status(self, session_id: str) -> Dict[str, Any]:
        """Checks if participant in waiting room has been admitted, denied or expired"""
        self.touch()
        if self.is_ended:
            return {'status': 'ended', 'message': 'This meeting has ended.'}

        if session_id in self.admitted_sessions:
            return {'status': 'admitted'}

        entry = self.waiting_room.get(session_id)
        if not entry:
            if not self.require_admission:
                self.admitted_sessions.add(session_id)
                return {'status': 'admitted'}
            return {'status': 'not_found'}

        return {'status': entry.get('status', 'waiting')}

    def admit_participant(self, session_id: str) -> bool:
        """Host approves admission for a waiting attendee"""
        self.touch()
        if session_id in self.waiting_room:
            self.waiting_room[session_id]['status'] = 'admitted'
        self.admitted_sessions.add(session_id)
        return True

    def deny_participant(self, session_id: str) -> bool:
        """Host rejects entry for a waiting attendee"""
        self.touch()
        if session_id in self.waiting_room:
            self.waiting_room[session_id]['status'] = 'denied'
        if session_id in self.admitted_sessions:
            self.admitted_sessions.remove(session_id)
        return True

    def get_waiting_list(self) -> List[Dict[str, Any]]:
        """Active pending admission requests for host review"""
        now = time.time()
        return [
            item for item in self.waiting_room.values()
            if item.get('status') == 'waiting' and (now - item.get('requested_at', now) < 600)
        ]

    def register_participant(self, session_id: str, name: str, role: str = 'guest', affiliation: str = '') -> Dict[str, Any]:
        """Join or update a participant in the room"""
        self.touch()
        self.participants[session_id] = {
            'session_id': session_id,
            'name': name,
            'role': role,
            'affiliation': affiliation,
            'last_seen': time.time()
        }
        if session_id not in self.signals:
            self.signals[session_id] = []
            
        return self.participants[session_id]

    def remove_participant(self, session_id: str):
        """Remove participant when leaving"""
        self.touch()
        if session_id in self.participants:
            del self.participants[session_id]
        if session_id in self.signals:
            del self.signals[session_id]
        if session_id in self.waiting_room and self.waiting_room[session_id].get('status') == 'waiting':
            del self.waiting_room[session_id]

    def add_signal(self, sender_id: str, sender_name: str, recipient_id: Optional[str], signal_type: str, payload: Any):
        """Queue a WebRTC signaling message (SDP offer/answer, ICE candidate, host actions)"""
        self.touch()
        sig_data = {
            'id': str(uuid.uuid4()),
            'sender_id': sender_id,
            'sender_name': sender_name,
            'type': signal_type,
            'payload': payload,
            'timestamp': time.time()
        }
        
        if recipient_id:
            if recipient_id not in self.signals:
                self.signals[recipient_id] = []
            self.signals[recipient_id].append(sig_data)
        else:
            recipients = (set(self.participants.keys()) | set(self.admitted_sessions)) - {sender_id}
            for pid in recipients:
                if pid not in self.signals:
                    self.signals[pid] = []
                self.signals[pid].append(sig_data)

    def fetch_signals(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieve and clear pending signaling messages for a participant"""
        self.touch()
        if session_id in self.participants:
            self.participants[session_id]['last_seen'] = time.time()
            
        pending = self.signals.get(session_id, [])
        self.signals[session_id] = []
        return pending

    def add_chat_message(self, sender: str, role: str, text: str, is_system: bool = False) -> Dict[str, Any]:
        """Add in-room chat message"""
        self.touch()
        msg = {
            'id': str(uuid.uuid4()),
            'sender': sender,
            'role': role,
            'text': text.strip(),
            'time': datetime.now().strftime('%H:%M:%S'),
            'is_system': is_system
        }
        self.chat_messages.append(msg)
        return msg

    def update_notes(self, new_notes: str, sender: str) -> int:
        """Update shared notes buffer"""
        self.touch()
        self.notes = new_notes
        self.notes_version += 1
        return self.notes_version

    def add_shared_file(self, file_storage, uploaded_by: str) -> Optional[Dict[str, Any]]:
        """Save and track a shared file attachment inside the room"""
        self.touch()
        if not file_storage or not file_storage.filename:
            return None
            
        orig_name = secure_filename(file_storage.filename)
        file_id = str(uuid.uuid4())[:8]
        stored_name = f"{file_id}_{orig_name}"
        
        room_dir = os.path.join(MEETINGS_STORAGE_DIR, self.room_id)
        os.makedirs(room_dir, exist_ok=True)
        file_path = os.path.join(room_dir, stored_name)
        file_storage.save(file_path)
        
        size = os.path.getsize(file_path)
        file_info = {
            'id': file_id,
            'filename': stored_name,
            'original_name': orig_name,
            'uploaded_by': uploaded_by,
            'size': size,
            'time': datetime.now().strftime('%H:%M:%S')
        }
        self.shared_files.append(file_info)
        return file_info

    def add_recording(self, file_storage, recorded_by: str) -> Optional[Dict[str, Any]]:
        """Save and track a recorded session video file"""
        self.touch()
        if not file_storage or not file_storage.filename:
            return None

        orig_name = secure_filename(file_storage.filename)
        rec_id = str(uuid.uuid4())[:8]
        stored_name = f"rec_{rec_id}_{orig_name}"

        rec_dir = os.path.join(MEETINGS_STORAGE_DIR, self.room_id, 'recordings')
        os.makedirs(rec_dir, exist_ok=True)
        rec_path = os.path.join(rec_dir, stored_name)
        file_storage.save(rec_path)

        size = os.path.getsize(rec_path)
        rec_info = {
            'id': rec_id,
            'filename': stored_name,
            'original_name': orig_name,
            'recorded_by': recorded_by,
            'size': size,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.recordings.append(rec_info)
        return rec_info

    def get_file_path(self, filename: str) -> Optional[str]:
        """Get absolute path to a shared meeting file"""
        safe_name = os.path.basename(filename)
        path = os.path.join(MEETINGS_STORAGE_DIR, self.room_id, safe_name)
        if os.path.exists(path):
            return path
        return None

    def get_recording_path(self, filename: str) -> Optional[str]:
        """Get absolute path to a saved session recording"""
        safe_name = os.path.basename(filename)
        path = os.path.join(MEETINGS_STORAGE_DIR, self.room_id, 'recordings', safe_name)
        if os.path.exists(path):
            return path
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Summary representation of the room"""
        return {
            'room_id': self.room_id,
            'title': self.title,
            'student_id': self.student_id,
            'student_name': self.student_name,
            'target_students': self.target_students,
            'target_count': len(self.target_students),
            'external_invitees': self.external_invitees,
            'advisor_name': self.advisor_name,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
            'participants_count': len(self.participants),
            'participants': list(self.participants.values()),
            'notes_version': self.notes_version,
            'notebook_version': self.notebook.get('version', 1),
            'notebook_pages_count': len(self.notebook.get('pages', [])),
            'chat_count': len(self.chat_messages),
            'files_count': len(self.shared_files),
            'recordings_count': len(self.recordings),
            'passcode': self.passcode,
            'require_passcode': self.require_passcode,
            'require_admission': self.require_admission,
            'duration_minutes': self.duration_minutes,
            'remaining_seconds': self.get_remaining_seconds(),
            'max_participants': self.max_participants,
            'is_ended': self.is_ended,
            'waiting_count': len(self.get_waiting_list())
        }


class MeetingManager:
    """Thread-safe registry of active rooms"""
    def __init__(self):
        self._rooms: Dict[str, MeetingRoom] = {}
        self._lock = threading.Lock()

    def create_room(self, title: str = 'Advising Session', 
                    student_id: Optional[str] = None, 
                    student_name: Optional[str] = None,
                    target_students: Optional[List[Dict[str, Any]]] = None,
                    advisor_name: str = 'Dr. Nasser Tabook',
                    custom_room_id: Optional[str] = None,
                    passcode: Optional[str] = None,
                    require_admission: bool = True,
                    duration_minutes: Optional[int] = 30,
                    max_participants: Optional[int] = None,
                    external_invitees: Optional[List[Dict[str, Any]]] = None) -> MeetingRoom:
        """Create a new advising room for single student, group of students, or external guests"""
        with self._lock:
            if custom_room_id and custom_room_id in self._rooms:
                return self._rooms[custom_room_id]
                
            room_id = custom_room_id or str(uuid.uuid4())[:8]
            room = MeetingRoom(
                room_id=room_id,
                title=title,
                student_id=student_id,
                student_name=student_name,
                target_students=target_students,
                advisor_name=advisor_name,
                passcode=passcode,
                require_admission=require_admission,
                duration_minutes=duration_minutes,
                max_participants=max_participants,
                external_invitees=external_invitees
            )
            self._rooms[room_id] = room
            return room

    def get_room(self, room_id: str) -> Optional[MeetingRoom]:
        """Fetch room by ID"""
        with self._lock:
            room = self._rooms.get(room_id)
            if room:
                room.touch()
            return room

    def list_rooms(self) -> List[Dict[str, Any]]:
        """Return list of active rooms sorted by creation date"""
        with self._lock:
            now = time.time()
            for r in self._rooms.values():
                stale_pids = [
                    pid for pid, p in r.participants.items()
                    if now - p.get('last_seen', now) > 60
                ]
                for pid in stale_pids:
                    r.remove_participant(pid)
                    
            return sorted(
                [r.to_dict() for r in self._rooms.values()],
                key=lambda x: x['created_at'],
                reverse=True
            )

    def delete_room(self, room_id: str) -> bool:
        """Permanently delete a meeting room and all associated storage files"""
        with self._lock:
            if room_id in self._rooms:
                del self._rooms[room_id]
            room_dir = os.path.join(MEETINGS_STORAGE_DIR, room_id)
            if os.path.exists(room_dir):
                shutil.rmtree(room_dir, ignore_errors=True)
            return True

    def clear_all_rooms(self) -> int:
        """Permanently clear all meeting rooms and delete all meeting storage folders"""
        with self._lock:
            count = len(self._rooms)
            self._rooms.clear()
            if os.path.exists(MEETINGS_STORAGE_DIR):
                for item in os.listdir(MEETINGS_STORAGE_DIR):
                    p = os.path.join(MEETINGS_STORAGE_DIR, item)
                    if os.path.isdir(p):
                        shutil.rmtree(p, ignore_errors=True)
            return count

    def cleanup_old_rooms(self, max_idle_seconds: int = 86400):
        """Remove rooms idle for more than 24 hours"""
        with self._lock:
            now = time.time()
            expired = [
                rid for rid, r in self._rooms.items()
                if (now - r.last_activity) > max_idle_seconds
            ]
            for rid in expired:
                del self._rooms[rid]

# Global singleton meeting manager
meeting_manager = MeetingManager()
