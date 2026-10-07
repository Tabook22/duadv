"""
Meeting Engine for Dhofar University Advising System
Manages virtual rooms, WebRTC peer signaling exchange, live text chat,
collaborative advising notes, and in-meeting document sharing.
"""

import os
import time
import uuid
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from werkzeug.utils import secure_filename

MEETINGS_STORAGE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'data', 'meetings'
)
os.makedirs(MEETINGS_STORAGE_DIR, exist_ok=True)

class MeetingRoom:
    """Represents a virtual advising meeting room (supports 1-on-1 and multi-student group sessions)"""
    def __init__(self, room_id: str, title: str = 'Advising Session', 
                 student_id: Optional[str] = None, student_name: Optional[str] = None,
                 target_students: Optional[List[Dict[str, Any]]] = None,
                 advisor_name: str = 'Dr. Nasser Tabook'):
        self.room_id = room_id
        self.title = title
        self.advisor_name = advisor_name
        self.created_at = datetime.now()
        self.last_activity = time.time()
        
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
        else:
            self.student_id = student_id
            self.student_name = student_name or (f'Student {student_id}' if student_id else 'Student Group')
            
        # Participants tracking: {session_id: {'name': str, 'role': str, 'last_seen': float}}
        self.participants: Dict[str, Dict[str, Any]] = {}
        
        # Signaling inbox: {recipient_session_id: [signals]}
        self.signals: Dict[str, List[Dict[str, Any]]] = {}
        
        # Chat messages: list of {'id': str, 'sender': str, 'role': str, 'text': str, 'time': str}
        self.chat_messages: List[Dict[str, Any]] = []
        
        # Shared advising notes
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        students_bullet = "\n".join([f"- **{s.get('name', 'Student')}** (ID: {s.get('id', '')})" for s in self.target_students]) if self.target_students else f"- {self.student_name}"
        self.notes: str = (
            f"### Academic Advising Notes - {self.title}\n"
            f"**Date:** {now_str}\n"
            f"**Advisor:** {self.advisor_name}\n\n"
            f"#### Participating Advisees:\n{students_bullet}\n\n"
            "#### 1. Academic Status & Probation Review\n- \n\n"
            "#### 2. Course Registration & Schedule Agreements\n- \n\n"
            "#### 3. Action Items & Follow-up\n- \n"
        )
        self.notes_version: int = 1
        
        # Shared files: list of {'id': str, 'filename': str, 'original_name': str, 'uploaded_by': str, 'size': int, 'time': str}
        self.shared_files: List[Dict[str, Any]] = []

    def touch(self):
        """Update activity timestamp"""
        self.last_activity = time.time()

    def register_participant(self, session_id: str, name: str, role: str = 'guest') -> Dict[str, Any]:
        """Join or update a participant in the room"""
        self.touch()
        self.participants[session_id] = {
            'session_id': session_id,
            'name': name,
            'role': role,
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

    def add_signal(self, sender_id: str, sender_name: str, recipient_id: Optional[str], signal_type: str, payload: Any):
        """Queue a WebRTC signaling message (SDP or ICE candidate)"""
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
            for pid in list(self.participants.keys()):
                if pid != sender_id:
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

    def add_chat_message(self, sender: str, role: str, text: str) -> Dict[str, Any]:
        """Add in-room chat message"""
        self.touch()
        msg = {
            'id': str(uuid.uuid4()),
            'sender': sender,
            'role': role,
            'text': text.strip(),
            'time': datetime.now().strftime('%H:%M:%S')
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

    def get_file_path(self, filename: str) -> Optional[str]:
        """Get absolute path to a shared meeting file"""
        safe_name = os.path.basename(filename)
        path = os.path.join(MEETINGS_STORAGE_DIR, self.room_id, safe_name)
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
            'advisor_name': self.advisor_name,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
            'participants_count': len(self.participants),
            'participants': list(self.participants.values()),
            'notes_version': self.notes_version,
            'chat_count': len(self.chat_messages),
            'files_count': len(self.shared_files)
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
                    custom_room_id: Optional[str] = None) -> MeetingRoom:
        """Create a new advising room for single student or group of students"""
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
                advisor_name=advisor_name
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
