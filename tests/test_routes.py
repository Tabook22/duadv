"""Integration tests for application routes"""

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Student Management System" in response.data

def test_dashboard_route(client):
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b"Supervisor Dashboard" in response.data

def test_students_route(client):
    response = client.get('/students')
    assert response.status_code == 200
    assert b"My Advisees" in response.data

def test_student_detail_route_success(client):
    from app.utils import load_students_from_file
    students = load_students_from_file()
    if students:
        sid = students[0].id
        response = client.get(f'/student/{sid}')
        assert response.status_code == 200
        assert students[0].name.encode('utf-8') in response.data or str(sid).encode('utf-8') in response.data

def test_student_detail_route_not_found(client):
    response = client.get('/student/99999999')
    assert response.status_code == 404
    assert b"404" in response.data

def test_auth_login_route(client):
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b"Supervisor Login" in response.data

def test_auth_logout_route(client):
    response = client.get('/auth/logout', follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'] == '/'

def test_student_transcript_pdf_existing(client):
    from app.utils import load_students_from_file
    students = load_students_from_file()
    if students:
        sid = students[0].id
        response = client.get(f'/student/{sid}/transcript/pdf')
        assert response.status_code == 200
        assert response.mimetype == 'application/pdf'
        assert len(response.data) > 0

def test_student_transcript_pdf_not_found(client):
    response = client.get('/student/00000000/transcript/pdf')
    assert response.status_code == 404

def test_download_transcripts_zip(client):
    response = client.get('/api/download-transcripts-zip')
    assert response.status_code == 200
    assert response.mimetype == 'application/zip'
    assert len(response.data) > 0

def test_sync_students_validation(client):
    # Empty payload
    response = client.post('/api/sync-students', json={})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'

def test_sync_students_stream_validation(client):
    # Empty payload on streaming endpoint
    response = client.post('/api/sync-students/stream', json={})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert 'Username and password required' in json_data['message']

def test_import_advisee_html_empty(client):
    response = client.post('/api/import-advisee-html', json={'html': '   '})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'

def test_upload_transcripts_zip_no_file(client):
    response = client.post('/api/upload-transcripts-zip', data={})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'

def test_upload_transcripts_zip_invalid_extension(client):
    import io
    data = {'file': (io.BytesIO(b'dummy'), 'test.txt')}
    response = client.post('/api/upload-transcripts-zip', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'must be a .zip' in json_data['message'].lower()

def test_students_at_risk_route(client):
    response = client.get('/students-at-risk')
    assert response.status_code == 200
    assert b"Students at Risk" in response.data
    assert b"Strict Probation" in response.data
    assert b"Second Probation" in response.data
    assert b"First Probation" in response.data

def test_students_at_risk_report_html(client):
    response = client.get('/students-at-risk/report')
    assert response.status_code == 200
    assert b"DHOFAR UNIVERSITY" in response.data
    assert b"Official Students at Risk Roster" in response.data
    assert b"Strict Probation" in response.data

def test_students_at_risk_report_pdf(client):
    response = client.get('/students-at-risk/report/pdf')
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'
    assert len(response.data) > 0

def test_students_at_risk_report_excel(client):
    response = client.get('/students-at-risk/report/excel')
    assert response.status_code == 200
    assert 'spreadsheetml' in response.mimetype
    assert len(response.data) > 0
    assert 'DU_Students_at_Risk_Report.xlsx' in response.headers.get('Content-Disposition', '')

def test_policies_library_route(client):
    response = client.get('/policies')
    assert response.status_code == 200
    assert b"Academic Policies" in response.data
    assert b"Upload Reference Document" in response.data

def test_policies_search_api(client):
    response = client.get('/api/policies/search?q=probation')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'results' in data

def test_policy_file_view_and_download(client):
    from app.utils import load_policies_from_file
    policies = load_policies_from_file()
    if policies:
        pid = policies[0].id
        res_view = client.get(f'/policies/{pid}/view')
        assert res_view.status_code == 200
        
        res_dl = client.get(f'/policies/{pid}/download')
        assert res_dl.status_code == 200
        assert 'attachment' in res_dl.headers.get('Content-Disposition', '')

def test_upload_policy_validation(client):
    # Missing file
    response = client.post('/api/policies/upload', data={}, headers={'X-Requested-With': 'XMLHttpRequest'})
    assert response.status_code == 400

def test_upload_multiple_policies_batch(client):
    import io
    pdf1 = (io.BytesIO(b"%PDF-1.4 Mock Cyber Plan"), "Cybersecurity_Plan_of_Study_v2.pdf")
    pdf2 = (io.BytesIO(b"%PDF-1.4 Mock Requirements"), "Requirements_for_Studying_Computer_Science_Diploma_v2.pdf")
    
    response = client.post(
        '/api/policies/upload',
        data={
            'files': [pdf1, pdf2],
            'category': 'Auto-Detect',
            'description': 'Test batch upload'
        },
        content_type='multipart/form-data',
        headers={'X-Requested-With': 'XMLHttpRequest'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['uploaded_count'] == 2
    categories = [p['category'] for p in data['policies']]
    assert 'Plan of Study' in categories
    assert 'Degree Requirements' in categories

def test_advising_wiki_route(client):
    response = client.get('/advising-wiki')
    assert response.status_code == 200
    assert b"Academic Advising Wiki" in response.data
    assert b"Ask the Advising Wiki" in response.data

def test_api_wiki_ask(client):
    response = client.get('/api/wiki/ask?question=probation')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'Article 14' in data['answer']

def test_student_degree_audit_api(client):
    response = client.get('/student/202210391/degree-audit')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['student_id'] == '202210391'
    assert data['total_plan_credits'] == 65
    assert data['credit_cap'] == 12

def test_student_advising_plan_route(client):
    # Test HTML memo
    res_html = client.get('/student/202210391/advising-plan')
    assert res_html.status_code == 200
    assert b"Official Academic Advising Action Plan" in res_html.data
    assert b"DHOFAR UNIVERSITY" in res_html.data
    
    # Test JSON format
    res_json = client.get('/student/202210391/advising-plan?format=json')
    assert res_json.status_code == 200
    data = res_json.get_json()
    assert data['status'] == 'success'
    assert data['total_recommended_credits'] <= 12
    assert len(data['recommended_schedule']) > 0





