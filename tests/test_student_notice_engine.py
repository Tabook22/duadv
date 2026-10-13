import pytest
from app.student_notice_engine import (
    generate_student_official_notice,
    generate_batch_student_notices
)
from app.outreach_tracker import (
    get_student_outreach_status,
    update_student_outreach_status,
    batch_update_outreach_status
)
from app.utils import load_students_from_file

def test_generate_student_official_notice():
    students = load_students_from_file()
    assert len(students) > 0
    sample = students[0]
    
    notice = generate_student_official_notice(sample.id)
    assert 'student_id' in notice
    assert 'student_name' in notice
    assert 'student_email' in notice
    assert 'subject_line' in notice
    assert 'plain_text_email' in notice
    assert 'mailto_url' in notice
    assert 'prescribed_courses' in notice
    assert 'student_action_items' in notice
    assert 'arabic_standing' in notice
    assert 'arabic_actions' in notice
    assert 'outreach' in notice
    
    # Verify content formatting
    assert "DHOFAR UNIVERSITY" in notice['plain_text_email']
    assert sample.name in notice['plain_text_email']
    assert sample.id in notice['plain_text_email']
    assert "Article 22" in notice['plain_text_email']
    assert notice['mailto_url'].startswith("mailto:")
    assert "@du.edu.om" in notice['mailto_url']

def test_generate_student_official_notice_invalid_id():
    with pytest.raises(ValueError, match="Student with ID 'INVALID_999999' not found"):
        generate_student_official_notice('INVALID_999999')

def test_generate_batch_student_notices():
    batch = generate_batch_student_notices(force_refresh=True)
    assert batch['total_at_risk'] > 0
    assert len(batch['students']) == batch['total_at_risk']
    assert len(batch['all_emails']) == batch['total_at_risk']
    assert batch['emails_comma'] != ""
    assert batch['emails_semicolon'] != ""
    assert batch['group_mailto_url'].startswith("mailto:")
    assert "bcc=" in batch['group_mailto_url']
    
    first_item = batch['students'][0]
    assert 'student_id' in first_item
    assert 'student_name' in first_item
    assert 'tier' in first_item
    assert 'mailto_url' in first_item
    assert 'outreach' in first_item

def test_outreach_tracker():
    test_id = '202310720'
    res = update_student_outreach_status(
        student_id=test_id,
        status="Notice Sent via Email",
        method="Email",
        notes="Automated test note",
        advisor_name="Dr. Nasser Tabook"
    )
    assert res['student_id'] == test_id
    assert res['status'] == "Notice Sent via Email"
    assert res['contact_method'] == "Email"
    assert len(res['history']) >= 1
    assert res['history'][0]['notes'] == "Automated test note"
    
    fetched = get_student_outreach_status(test_id)
    assert fetched['status'] == "Notice Sent via Email"

def test_batch_notices_and_outreach_routes(client):
    # 1. Batch Hub HTML view
    resp = client.get('/students-at-risk/batch-notices')
    assert resp.status_code == 200
    assert b"Batch Academic Advising Outreach" in resp.data

    # 2. Batch Hub JSON API
    api_resp = client.get('/api/students-at-risk/batch-notices')
    assert api_resp.status_code == 200
    json_data = api_resp.get_json()
    assert json_data['total_at_risk'] > 0

    # 3. Export batch text dossier
    export_resp = client.get('/students-at-risk/export-notices-txt')
    assert export_resp.status_code == 200
    assert b"DHOFAR UNIVERSITY" in export_resp.data
    assert export_resp.headers['Content-Disposition'].startswith('attachment')

    # 4. Individual outreach status POST API
    post_resp = client.post('/api/student/202310720/outreach-status', json={
        'status': 'Student Responded',
        'method': 'Office Visit (Office 214)',
        'notes': 'Route test note'
    })
    assert post_resp.status_code == 200
    post_data = post_resp.get_json()
    assert post_data['status'] == 'success'
    assert post_data['outreach']['status'] == 'Student Responded'

    # 5. Batch outreach status POST API
    batch_post_resp = client.post('/api/students-at-risk/batch-outreach-status', json={
        'student_ids': ['202310720', '202211549'],
        'status': 'Notice Sent via Email',
        'method': 'Email',
        'notes': 'Batch route test'
    })
    assert batch_post_resp.status_code == 200
    batch_json = batch_post_resp.get_json()
    assert batch_json['updated_count'] == 2
