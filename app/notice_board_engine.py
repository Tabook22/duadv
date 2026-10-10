"""
Advisor Notice Board Engine
Provides persistent note/action-item management for academic advising:
- Color-coded sticky notes (urgent, warning, reminder, meeting, info, success)
- Card size controls (small, medium, large) & font sizes (small, normal, large)
- Direct advisee linking (student ID, name, standing, program)
- Priority, due dates, categories (at_risk, meeting, registration, general, follow_up)
- Drag-and-drop manual ordering
- Pinned & completed states
- Smart auto-generation of action notices based on at-risk advisee cohort
"""

import os
import json
import uuid
import time
from datetime import datetime
from threading import Lock
from typing import List, Dict, Any, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
NOTICES_FILE = os.path.join(DATA_DIR, 'notices.json')

_lock = Lock()

DEFAULT_COLORS = {
    'yellow': {'bg': '#fef3c7', 'border': '#f59e0b', 'text': '#92400e', 'badge': 'bg-warning text-dark'},
    'red':    {'bg': '#fee2e2', 'border': '#ef4444', 'text': '#991b1b', 'badge': 'bg-danger text-white'},
    'blue':   {'bg': '#e0f2fe', 'border': '#0284c7', 'text': '#075985', 'badge': 'bg-info text-dark'},
    'green':  {'bg': '#dcfce7', 'border': '#22c55e', 'text': '#166534', 'badge': 'bg-success text-white'},
    'purple': {'bg': '#f3e8ff', 'border': '#a855f7', 'text': '#6b21a8', 'badge': 'bg-secondary text-white'},
    'amber':  {'bg': '#ffedd5', 'border': '#f97316', 'text': '#9a3412', 'badge': 'bg-warning text-dark'},
}

def _ensure_storage() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(NOTICES_FILE):
        initial_data = {
            "version": 1,
            "notices": _create_default_seed_notices()
        }
        with open(NOTICES_FILE, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=2, ensure_ascii=False)

def _create_default_seed_notices() -> List[Dict[str, Any]]:
    now = datetime.now().isoformat()
    return [
        {
            "id": f"note-{uuid.uuid4().hex[:8]}",
            "title": "Strict Probation Urgent Check-in",
            "content": "Follow up with advisees on Strict & 2nd Probation before Drop/Add deadline. Ensure Article 14 credit limits (max 12 credits) are enforced.",
            "color": "red",
            "category": "at_risk",
            "priority": "high",
            "size": "medium",
            "font_size": "medium",
            "student_id": "",
            "student_name": "",
            "program": "All Programs",
            "due_date": "",
            "is_pinned": True,
            "is_completed": False,
            "order": 1,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": f"note-{uuid.uuid4().hex[:8]}",
            "title": "Spring 2026/2027 Advising Memo Prep",
            "content": "Review students completing 60+ credit hours for major milestone requirements and elective prerequisites.",
            "color": "blue",
            "category": "registration",
            "priority": "medium",
            "size": "medium",
            "font_size": "medium",
            "student_id": "",
            "student_name": "",
            "program": "BSc Computer Science",
            "due_date": "",
            "is_pinned": False,
            "is_completed": False,
            "order": 2,
            "created_at": now,
            "updated_at": now
        },
        {
            "id": f"note-{uuid.uuid4().hex[:8]}",
            "title": "Book Office Hours Hub Sessions",
            "content": "Schedule 15-minute 1-on-1 virtual check-ins with at-risk cohort in the Virtual Office Hours Hub.",
            "color": "yellow",
            "category": "meeting",
            "priority": "high",
            "size": "medium",
            "font_size": "medium",
            "student_id": "",
            "student_name": "",
            "program": "All Programs",
            "due_date": "",
            "is_pinned": False,
            "is_completed": False,
            "order": 3,
            "created_at": now,
            "updated_at": now
        }
    ]

def get_all_notices() -> List[Dict[str, Any]]:
    """Retrieve all notices sorted by pinned status, custom order, and updated_at."""
    _ensure_storage()
    with _lock:
        try:
            with open(NOTICES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                notices = data.get("notices", [])
        except Exception:
            return []

    # Sort: Pinned first, then by order, then by updated_at descending
    notices.sort(key=lambda n: (
        not n.get("is_pinned", False),
        n.get("is_completed", False),
        n.get("order", 9999),
        n.get("created_at", "")
    ))
    return notices

def get_notice_by_id(notice_id: str) -> Optional[Dict[str, Any]]:
    notices = get_all_notices()
    for n in notices:
        if n.get("id") == notice_id:
            return n
    return None

def create_notice(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create and persist a new notice note."""
    _ensure_storage()
    now = datetime.now().isoformat()
    notice_id = f"note-{uuid.uuid4().hex[:8]}"

    new_notice = {
        "id": notice_id,
        "title": (data.get("title") or "Untitled Notice").strip(),
        "content": (data.get("content") or "").strip(),
        "color": data.get("color", "yellow") if data.get("color") in DEFAULT_COLORS else "yellow",
        "category": data.get("category", "general"),
        "priority": data.get("priority", "medium"), # low, medium, high
        "size": data.get("size", "medium"),         # small, medium, large
        "font_size": data.get("font_size", "medium"), # small, medium, large
        "student_id": (data.get("student_id") or "").strip(),
        "student_name": (data.get("student_name") or "").strip(),
        "program": (data.get("program") or "").strip(),
        "due_date": (data.get("due_date") or "").strip(),
        "is_pinned": bool(data.get("is_pinned", False)),
        "is_completed": bool(data.get("is_completed", False)),
        "order": int(data.get("order", 0)),
        "position_x": data.get("position_x", None), # for canvas drag coordinates
        "position_y": data.get("position_y", None),
        "width": data.get("width", None),           # custom width in px
        "height": data.get("height", None),         # custom height in px
        "rotation": data.get("rotation", None),     # degrees rotation for organic sticky look
        "linked_to": data.get("linked_to", []),     # list of linked notice IDs
        "line_style": data.get("line_style", "solid"), # solid, dashed, dotted
        "line_color": data.get("line_color", "blue"),  # blue, red, green, amber, purple, slate
        "created_at": now,
        "updated_at": now
    }

    with _lock:
        try:
            with open(NOTICES_FILE, 'r', encoding='utf-8') as f:
                storage = json.load(f)
        except Exception:
            storage = {"version": 1, "notices": []}

        # Prepend to the top of the order
        storage["notices"].insert(0, new_notice)
        # Re-index orders
        for idx, item in enumerate(storage["notices"]):
            item["order"] = idx + 1

        with open(NOTICES_FILE, 'w', encoding='utf-8') as f:
            json.dump(storage, f, indent=2, ensure_ascii=False)

    return new_notice

def update_notice(notice_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update fields of an existing notice."""
    _ensure_storage()
    now = datetime.now().isoformat()
    updated_obj = None

    with _lock:
        try:
            with open(NOTICES_FILE, 'r', encoding='utf-8') as f:
                storage = json.load(f)
        except Exception:
            return None

        for n in storage.get("notices", []):
            if n.get("id") == notice_id:
                for key in ['title', 'content', 'color', 'category', 'priority', 
                            'size', 'font_size', 'student_id', 'student_name', 
                            'program', 'due_date', 'is_pinned', 'is_completed', 'order',
                            'position_x', 'position_y', 'width', 'height', 'rotation', 'linked_to',
                            'line_style', 'line_color']:
                    if key in updates:
                        n[key] = updates[key]
                n['updated_at'] = now
                updated_obj = n
                break

        if updated_obj:
            with open(NOTICES_FILE, 'w', encoding='utf-8') as f:
                json.dump(storage, f, indent=2, ensure_ascii=False)

    return updated_obj

def delete_notice(notice_id: str) -> bool:
    """Delete a notice by its ID."""
    _ensure_storage()
    deleted = False

    with _lock:
        try:
            with open(NOTICES_FILE, 'r', encoding='utf-8') as f:
                storage = json.load(f)
        except Exception:
            return False

        orig_len = len(storage.get("notices", []))
        storage["notices"] = [n for n in storage.get("notices", []) if n.get("id") != notice_id]
        if len(storage["notices"]) < orig_len:
            deleted = True
            with open(NOTICES_FILE, 'w', encoding='utf-8') as f:
                json.dump(storage, f, indent=2, ensure_ascii=False)

    return deleted

def reorder_notices(ordered_ids: List[str]) -> bool:
    """Update the order ranking based on drag-and-drop result list."""
    _ensure_storage()
    with _lock:
        try:
            with open(NOTICES_FILE, 'r', encoding='utf-8') as f:
                storage = json.load(f)
        except Exception:
            return False

        id_to_order = {nid: idx + 1 for idx, nid in enumerate(ordered_ids)}
        for item in storage.get("notices", []):
            if item.get("id") in id_to_order:
                item["order"] = id_to_order[item["id"]]

        with open(NOTICES_FILE, 'w', encoding='utf-8') as f:
            json.dump(storage, f, indent=2, ensure_ascii=False)

    return True

def auto_generate_risk_notices(students: List[Any]) -> int:
    """
    Intelligently generate notices for advisees who are on Strict Probation, 
    2nd Probation, or low CGPA, if not already present.
    Returns the count of created notices.
    """
    existing_notices = get_all_notices()
    existing_student_ids = {n.get("student_id") for n in existing_notices if n.get("student_id")}

    created_count = 0
    for s in students:
        s_id = str(getattr(s, 'id', '') or '')
        s_name = str(getattr(s, 'name', '') or '')
        s_status = str(getattr(s, 'status', '') or '')
        s_cgpa = getattr(s, 'cgpa', None) or getattr(s, 'gpa', None)
        s_program = str(getattr(s, 'program', '') or 'Computer Science')

        if not s_id or s_id in existing_student_ids:
            continue

        # Check conditions
        is_strict = 'Strict' in s_status or 'Third' in s_status
        is_second = 'Second Probation' in s_status
        is_first = 'First Probation' in s_status

        if is_strict or is_second or is_first:
            color = 'red' if is_strict else ('amber' if is_second else 'yellow')
            priority = 'high' if (is_strict or is_second) else 'medium'
            title = f"{'Strict' if is_strict else 'Academic'} Probation Alert: {s_name.split()[0]}"
            
            cgpa_str = f"{s_cgpa:.2f}%" if isinstance(s_cgpa, (int, float)) else "N/A"
            content = f"Standing: {s_status} (CGPA: {cgpa_str}). Call for advising meeting. Max credit load: 12 cr. Review transcript for retakes."
            
            create_notice({
                "title": title,
                "content": content,
                "color": color,
                "category": "at_risk",
                "priority": priority,
                "student_id": s_id,
                "student_name": s_name,
                "program": s_program,
                "is_pinned": is_strict
            })
            existing_student_ids.add(s_id)
            created_count += 1

    return created_count
