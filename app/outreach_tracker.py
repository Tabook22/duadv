"""
Student Advising Outreach & Communication Tracker for Dhofar University.
Tracks advising notices dispatched, email communications, student responses,
and consultation touchpoints for each advisee, especially students at risk.
Stores persistent status and audit logs in data/outreach_tracking.json.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACKING_FILE = os.path.join(PROJECT_ROOT, 'data', 'outreach_tracking.json')

VALID_STATUSES = [
    "Pending Outreach",
    "Notice Sent via Email",
    "Student Responded",
    "Meeting Completed",
    "Plan Signed & Approved"
]

STATUS_COLORS = {
    "Pending Outreach": "secondary",
    "Notice Sent via Email": "primary",
    "Student Responded": "warning text-dark",
    "Meeting Completed": "success",
    "Plan Signed & Approved": "info text-dark"
}

STATUS_ICONS = {
    "Pending Outreach": "fa-clock",
    "Notice Sent via Email": "fa-paper-plane",
    "Student Responded": "fa-reply",
    "Meeting Completed": "fa-handshake",
    "Plan Signed & Approved": "fa-file-signature"
}

def load_outreach_tracking() -> Dict[str, Any]:
    """Load the persistent outreach tracking database."""
    if not os.path.exists(TRACKING_FILE):
        return {}
    try:
        with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_outreach_tracking(data: Dict[str, Any]) -> None:
    """Save the outreach tracking database atomically."""
    os.makedirs(os.path.dirname(TRACKING_FILE), exist_ok=True)
    tmp_path = f"{TRACKING_FILE}.tmp"
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    if os.path.exists(TRACKING_FILE):
        os.replace(tmp_path, TRACKING_FILE)
    else:
        os.rename(tmp_path, TRACKING_FILE)

def get_student_outreach_status(student_id: str) -> Dict[str, Any]:
    """
    Get the current advising outreach status and interaction history for a student.
    Returns default structure if student has not been contacted yet.
    """
    data = load_outreach_tracking()
    student_record = data.get(student_id)
    
    if not student_record:
        return {
            'student_id': student_id,
            'status': "Pending Outreach",
            'status_color': STATUS_COLORS["Pending Outreach"],
            'status_icon': STATUS_ICONS["Pending Outreach"],
            'last_contacted_at': None,
            'contact_method': None,
            'notes': '',
            'history': []
        }
        
    status = student_record.get('status', "Pending Outreach")
    return {
        'student_id': student_id,
        'status': status,
        'status_color': STATUS_COLORS.get(status, 'secondary'),
        'status_icon': STATUS_ICONS.get(status, 'fa-clock'),
        'last_contacted_at': student_record.get('last_contacted_at'),
        'contact_method': student_record.get('contact_method'),
        'notes': student_record.get('notes', ''),
        'history': student_record.get('history', [])
    }

def update_student_outreach_status(
    student_id: str,
    status: str,
    method: str = "Email",
    notes: str = "",
    advisor_name: str = "Dr. Nasser Tabook"
) -> Dict[str, Any]:
    """
    Update a student's contact status and append an entry to their interaction history.
    """
    if status not in VALID_STATUSES:
        status = "Notice Sent via Email"
        
    data = load_outreach_tracking()
    student_record = data.get(student_id, {
        'student_id': student_id,
        'history': []
    })
    
    timestamp = datetime.now().isoformat()
    formatted_time = datetime.now().strftime("%b %d, %Y at %I:%M %p")
    
    new_entry = {
        'timestamp': timestamp,
        'formatted_time': formatted_time,
        'status': status,
        'method': method,
        'notes': notes.strip(),
        'advisor': advisor_name
    }
    
    student_record['status'] = status
    student_record['last_contacted_at'] = formatted_time
    student_record['contact_method'] = method
    student_record['notes'] = notes.strip()
    
    history = student_record.get('history', [])
    history.insert(0, new_entry)
    student_record['history'] = history[:30] # Keep last 30 touchpoints
    
    data[student_id] = student_record
    save_outreach_tracking(data)
    
    return get_student_outreach_status(student_id)

def batch_update_outreach_status(
    student_ids: List[str],
    status: str,
    method: str = "Email",
    notes: str = ""
) -> int:
    """Batch update multiple students' contact status."""
    count = 0
    for sid in student_ids:
        if sid:
            update_student_outreach_status(sid, status, method, notes)
            count += 1
    return count
