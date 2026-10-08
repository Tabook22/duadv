import io
import json
import pytest
from app import create_app
from app.meeting_engine import meeting_manager

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_meetings_hub_page(client):
    resp = client.get('/meetings')
    assert resp.status_code == 200
    assert b"Virtual Advising Rooms" in resp.data

def test_create_meeting_api(client):
    payload = {
        'student_id': '202210455',
        'student_name': 'Test Student',
        'title': 'Degree Recovery Consultation',
        'advisor_name': 'Dr. Nasser Tabook'
    }
    resp = client.post('/api/meetings/create', json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'success'
    assert 'room_id' in data
    assert 'meeting_url' in data
    assert data['student_id'] == '202210455'

    room_id = data['room_id']
    room = meeting_manager.get_room(room_id)
    assert room is not None
    assert room.title == 'Degree Recovery Consultation'

def test_meeting_room_view(client):
    room = meeting_manager.create_room(
        title="Spring Advising",
        student_id="202210455",
        student_name="Said Salim"
    )
    resp = client.get(f'/meeting/{room.room_id}?role=advisor')
    assert resp.status_code == 200
    assert b"Virtual Advising Room" in resp.data
    assert room.room_id.encode() in resp.data

def test_meeting_join_and_leave(client):
    room = meeting_manager.create_room(title="Join Test Room")
    join_payload = {
        'session_id': 'sess_123',
        'name': 'Student Ahmed',
        'role': 'student'
    }
    resp = client.post(f'/api/meeting/{room.room_id}/join', json=join_payload)
    assert resp.status_code == 200
    assert room.participants['sess_123']['name'] == 'Student Ahmed'

    # Leave
    leave_payload = {'session_id': 'sess_123', 'name': 'Student Ahmed'}
    resp_leave = client.post(f'/api/meeting/{room.room_id}/leave', json=leave_payload)
    assert resp_leave.status_code == 200
    assert 'sess_123' not in room.participants

def test_meeting_signaling_flow(client):
    room = meeting_manager.create_room(title="Signaling Test")
    # Register 2 participants
    room.register_participant('advisor_1', 'Dr. Nasser', 'advisor')
    room.register_participant('student_1', 'Student Khalid', 'student')

    # Send offer from advisor to student
    offer_payload = {
        'sender_id': 'advisor_1',
        'sender_name': 'Dr. Nasser',
        'recipient_id': 'student_1',
        'type': 'offer',
        'payload': {'sdp': 'dummy_sdp_offer'}
    }
    sig_resp = client.post(f'/api/meeting/{room.room_id}/signal', json=offer_payload)
    assert sig_resp.status_code == 200

    # Student polls for signals
    poll_resp = client.get(f'/api/meeting/{room.room_id}/poll?session_id=student_1')
    assert poll_resp.status_code == 200
    pdata = poll_resp.get_json()
    assert len(pdata['signals']) == 1
    assert pdata['signals'][0]['type'] == 'offer'
    assert pdata['signals'][0]['sender_id'] == 'advisor_1'

def test_in_meeting_chat(client):
    room = meeting_manager.create_room(title="Chat Room")
    chat_payload = {
        'sender': 'Dr. Nasser Tabook',
        'role': 'advisor',
        'text': 'Welcome to the advising session. Please check your degree audit.'
    }
    c_resp = client.post(f'/api/meeting/{room.room_id}/chat', json=chat_payload)
    assert c_resp.status_code == 200
    cdata = c_resp.get_json()
    assert cdata['status'] == 'success'
    assert cdata['message']['text'] == chat_payload['text']

    # Poll chat
    p_resp = client.get(f'/api/meeting/{room.room_id}/poll')
    messages = p_resp.get_json()['chat_messages']
    assert len(messages) == 1
    assert messages[0]['sender'] == 'Dr. Nasser Tabook'

def test_shared_notes_collaboration(client):
    room = meeting_manager.create_room(title="Notes Room")
    notes_payload = {
        'sender': 'Dr. Nasser Tabook',
        'notes': 'Agreed registration for Fall: CMPS 110 (Sec 1), MATH 199 (Sec 2)'
    }
    n_resp = client.post(f'/api/meeting/{room.room_id}/notes', json=notes_payload)
    assert n_resp.status_code == 200
    assert room.notes == notes_payload['notes']
    assert room.notes_version > 1

    # Poll notes with version 0
    poll_resp = client.get(f'/api/meeting/{room.room_id}/poll?notes_version=0')
    pdata = poll_resp.get_json()
    assert 'notes' in pdata
    assert 'CMPS 110' in pdata['notes']

def test_in_meeting_file_sharing(client):
    room = meeting_manager.create_room(title="File Room")
    file_content = b"%PDF-1.4 dummy transcript document"
    data = {
        'uploaded_by': 'Dr. Nasser Tabook',
        'file': (io.BytesIO(file_content), 'plan_schedule.pdf')
    }
    up_resp = client.post(f'/api/meeting/{room.room_id}/upload', data=data, content_type='multipart/form-data')
    assert up_resp.status_code == 200
    finfo = up_resp.get_json()['file']
    assert 'filename' in finfo
    assert finfo['original_name'] == 'plan_schedule.pdf'

    # Download file
    dl_resp = client.get(f'/api/meeting/{room.room_id}/file/{finfo["filename"]}')
    assert dl_resp.status_code == 200
    assert dl_resp.data == file_content

def test_create_group_meeting_api(client):
    payload = {
        'student_ids': ['202120056', '202210391'],
        'title': 'Strict Probation Group Advising Session',
        'advisor_name': 'Dr. Nasser Tabook'
    }
    resp = client.post('/api/meetings/create', json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'success'
    assert 'room_id' in data
    assert 'meeting_url' in data
    assert 'lan_url' in data
    assert data['target_count'] == 2

    # Verify room view renders with multiple students
    room_resp = client.get(f'/meeting/{data["room_id"]}?role=advisor')
    assert room_resp.status_code == 200
    assert b"Advisees" in room_resp.data
    assert b"Reem Ali Rabia Baanaqoud" in room_resp.data



def test_passcode_and_admission_controls(client):
    payload = {
        'title': 'Confidential Probation Panel',
        'require_passcode': True,
        'passcode': 'DU-9988',
        'require_admission': True,
        'duration_minutes': 45
    }
    resp = client.post('/api/meetings/create', json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'success'
    assert data['require_passcode'] is True
    assert data['passcode'] == 'DU-9988'
    assert data['require_admission'] is True
    assert data['duration_minutes'] == 45
    assert 'invitation_text' in data
    assert 'DU-9988' in data['invitation_text']

    room_id = data['room_id']
    room = meeting_manager.get_room(room_id)
    assert room.passcode == 'DU-9988'
    assert room.require_admission is True

    # 1. Knock with incorrect passcode -> should be rejected
    bad_knock = {
        'session_id': 'guest_sess_1',
        'name': 'Ahmed Al-Shanfari',
        'role': 'student',
        'passcode': 'WRONG-PIN'
    }
    k_resp = client.post(f'/api/meeting/{room_id}/knock', json=bad_knock)
    assert k_resp.status_code == 200
    k_data = k_resp.get_json()
    assert k_data['status'] == 'error'
    assert 'Incorrect meeting passcode' in k_data['message']

    # 2. Knock with correct passcode -> placed in waiting room
    good_knock = {
        'session_id': 'guest_sess_1',
        'name': 'Ahmed Al-Shanfari',
        'role': 'student',
        'passcode': 'DU-9988',
        'affiliation': 'Student Advisee'
    }
    k_resp2 = client.post(f'/api/meeting/{room_id}/knock', json=good_knock)
    assert k_resp2.status_code == 200
    k_data2 = k_resp2.get_json()
    assert k_data2['status'] == 'waiting'

    # Check status
    stat_resp = client.get(f'/api/meeting/{room_id}/knock-status?session_id=guest_sess_1')
    assert stat_resp.status_code == 200
    assert stat_resp.get_json()['status'] == 'waiting'

    # Host checks waiting list
    wait_resp = client.get(f'/api/meeting/{room_id}/waiting-list')
    assert wait_resp.status_code == 200
    waiting = wait_resp.get_json()['waiting']
    assert len(waiting) == 1
    assert waiting[0]['name'] == 'Ahmed Al-Shanfari'

    # Host admits participant
    admit_resp = client.post(f'/api/meeting/{room_id}/admit', json={'session_id': 'guest_sess_1'})
    assert admit_resp.status_code == 200
    assert admit_resp.get_json()['status'] == 'success'

    # Participant rechecks status -> now admitted!
    stat_resp2 = client.get(f'/api/meeting/{room_id}/knock-status?session_id=guest_sess_1')
    assert stat_resp2.get_json()['status'] == 'admitted'


def test_meeting_duration_extension_and_ending(client):
    room = meeting_manager.create_room(title="Timed Session", duration_minutes=30)
    assert room.duration_minutes == 30
    assert room.get_remaining_seconds() is not None
    assert room.get_remaining_seconds() > 0

    # Extend duration by 15 mins
    ext_resp = client.post(f'/api/meeting/{room.room_id}/extend', json={'minutes': 15})
    assert ext_resp.status_code == 200
    assert ext_resp.get_json()['duration_minutes'] == 45

    # Host ends meeting
    end_resp = client.post(f'/api/meeting/{room.room_id}/end')
    assert end_resp.status_code == 200
    assert room.is_ended is True

    # Polling now shows is_ended = True
    poll_resp = client.get(f'/api/meeting/{room.room_id}/poll')
    assert poll_resp.get_json()['is_ended'] is True


def test_session_recording_upload_and_download(client):
    room = meeting_manager.create_room(title="Recording Test Room")
    video_content = b"\x1a\x45\xdf\xa3dummy webm video content"
    data = {
        'recorded_by': 'Dr. Nasser Tabook',
        'file': (io.BytesIO(video_content), 'advising_session_1.webm')
    }
    rec_resp = client.post(f'/api/meeting/{room.room_id}/upload-recording', data=data, content_type='multipart/form-data')
    assert rec_resp.status_code == 200
    rdata = rec_resp.get_json()
    assert rdata['status'] == 'success'
    rec_info = rdata['recording']
    assert rec_info['original_name'] == 'advising_session_1.webm'

    # Download recording
    dl_resp = client.get(f'/api/meeting/{room.room_id}/recording/{rec_info["filename"]}')
    assert dl_resp.status_code == 200
    assert dl_resp.data == video_content


def test_external_guest_meeting_creation(client):
    payload = {
        'title': 'Faculty Co-Advising Meeting',
        'external_invitees': [
            {'name': 'Prof. Said Al-Kathiri', 'role': 'Co-Advisor'},
            {'name': 'Salim Ba-Omar', 'role': 'Industry Mentor'}
        ],
        'advisor_name': 'Dr. Nasser Tabook',
        'require_admission': True
    }
    resp = client.post('/api/meetings/create', json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'success'
    assert len(data['external_invitees']) == 2
    assert 'Prof. Said Al-Kathiri' in data['external_invitees'][0]['name']

    room_resp = client.get(f'/meeting/{data["room_id"]}')
    assert room_resp.status_code == 200
    assert b"Virtual Advising Room" in room_resp.data


def test_delete_and_clear_meeting_rooms(client):
    # Create two rooms
    r1 = meeting_manager.create_room(title="Room To Delete 1")
    r2 = meeting_manager.create_room(title="Room To Delete 2")
    assert meeting_manager.get_room(r1.room_id) is not None
    assert meeting_manager.get_room(r2.room_id) is not None

    # Delete r1
    del_resp = client.post(f'/api/meeting/{r1.room_id}/delete')
    assert del_resp.status_code == 200
    assert del_resp.get_json()['status'] == 'success'
    assert meeting_manager.get_room(r1.room_id) is None
    assert meeting_manager.get_room(r2.room_id) is not None

    # Clear all rooms
    clear_resp = client.post('/api/meetings/clear-all')
    assert clear_resp.status_code == 200
    assert clear_resp.get_json()['status'] == 'success'
    assert meeting_manager.get_room(r2.room_id) is None
    assert len(meeting_manager.list_rooms()) == 0
