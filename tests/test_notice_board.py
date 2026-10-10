"""
Tests for Advisor Notice Board Engine and API Routes
"""

import os
import json
import pytest
from app import create_app
from app.notice_board_engine import (
    get_all_notices,
    create_notice,
    update_notice,
    delete_notice,
    reorder_notices,
    auto_generate_risk_notices
)
from app.models import Student

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        yield client

def test_notice_engine_crud():
    # Test create
    note = create_notice({
        "title": "Test Reminder",
        "content": "Check graduation petition",
        "color": "green",
        "category": "registration",
        "priority": "high",
        "size": "large",
        "font_size": "medium",
        "student_id": "202310720",
        "student_name": "Ahmed Younis"
    })
    assert note["id"].startswith("note-")
    assert note["title"] == "Test Reminder"
    assert note["color"] == "green"
    assert note["size"] == "large"

    # Test retrieve
    notices = get_all_notices()
    found = any(n["id"] == note["id"] for n in notices)
    assert found is True

    # Test update
    updated = update_notice(note["id"], {"title": "Updated Title", "is_completed": True})
    assert updated is not None
    assert updated["title"] == "Updated Title"
    assert updated["is_completed"] is True

    # Test delete
    deleted = delete_notice(note["id"])
    assert deleted is True
    assert not any(n["id"] == note["id"] for n in get_all_notices())

def test_notice_reorder():
    n1 = create_notice({"title": "Note 1"})
    n2 = create_notice({"title": "Note 2"})
    success = reorder_notices([n2["id"], n1["id"]])
    assert success is True

    # Clean up
    delete_notice(n1["id"])
    delete_notice(n2["id"])

def test_auto_generate_risk_notices():
    mock_students = [
        Student(id="99901", name="Ali Test", status="Strict Academic Probation", cgpa=58.5, program="CS"),
        Student(id="99902", name="Sara Good", status="Normal / Good Standing", cgpa=82.0, program="CS")
    ]
    created = auto_generate_risk_notices(mock_students)
    assert created >= 1

    notices = get_all_notices()
    risk_note = next((n for n in notices if n.get("student_id") == "99901"), None)
    assert risk_note is not None
    assert risk_note["color"] == "red"
    assert risk_note["priority"] == "high"

    # Clean up
    if risk_note:
        delete_notice(risk_note["id"])

def test_api_notices_endpoints(client):
    # GET
    res = client.get('/api/notices')
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True

    # POST
    res = client.post('/api/notices', json={
        "title": "API Test Note",
        "content": "API content",
        "color": "blue"
    })
    assert res.status_code == 200
    new_note = res.get_json()["notice"]
    nid = new_note["id"]

    # PATCH
    res = client.patch(f'/api/notices/{nid}', json={"is_pinned": True})
    assert res.status_code == 200
    assert res.get_json()["notice"]["is_pinned"] is True

    # DELETE
    res = client.delete(f'/api/notices/{nid}')
    assert res.status_code == 200
    assert res.get_json()["success"] is True
