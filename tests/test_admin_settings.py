"""Tests for Admin Authentication, Settings Governance, and About Application"""

import pytest
from app.settings_manager import (
    get_settings,
    verify_admin_credentials,
    update_branding,
    update_footer,
    update_about,
    update_permissions,
    update_admin_security
)

def test_settings_manager_defaults():
    settings = get_settings()
    assert 'admin' in settings
    assert 'branding' in settings
    assert 'footer' in settings
    assert 'about' in settings
    assert 'permissions' in settings
    
    assert settings['admin']['username'] == 'admin'
    assert verify_admin_credentials('admin', 'admin123') is True
    assert verify_admin_credentials('admin', 'wrong_pass') is False

def test_settings_branding_update():
    update_branding(app_title="Dhofar Advising Hub", app_badge="PORTAL")
    settings = get_settings()
    assert settings['branding']['app_title'] == "Dhofar Advising Hub"
    assert settings['branding']['app_badge'] == "PORTAL"

def test_settings_footer_update():
    update_footer(
        organization_line="Dhofar University • College of Arts & Applied Sciences",
        disclaimer="Custom test educational disclaimer."
    )
    settings = get_settings()
    assert "Dhofar University" in settings['footer']['organization_line']
    assert settings['footer']['disclaimer'] == "Custom test educational disclaimer."

def test_about_page_route(client):
    response = client.get('/about')
    assert response.status_code == 200
    assert b"Independent Academic Advisory Tool" in response.data or b"Educational Disclaimer" in response.data
    assert b"Release" in response.data or b"v2.5" in response.data

def test_admin_settings_unauthenticated_redirect(client):
    response = client.get('/admin/settings', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']

def test_admin_login_and_access(client):
    # Test valid login
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=False)
    assert response.status_code == 302
    
    # After login, access settings
    with client.session_transaction() as sess:
        sess['is_admin'] = True
        sess['admin_username'] = 'admin'

    settings_resp = client.get('/admin/settings')
    assert settings_resp.status_code == 200
    assert b"System Settings & Governance" in settings_resp.data
    assert b"Branding & Logo" in settings_resp.data

def test_admin_save_branding_post(client):
    with client.session_transaction() as sess:
        sess['is_admin'] = True
        sess['admin_username'] = 'admin'

    response = client.post('/admin/settings/branding', data={
        'app_title': 'Dhofar University',
        'app_badge': 'ADVISING',
        'logo_icon': 'fa-graduation-cap',
        'logo_image_url': '',
        'browser_tab_title': 'Dhofar University - Student Management System'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Branding and logo settings updated successfully" in response.data

def test_admin_save_footer_post(client):
    with client.session_transaction() as sess:
        sess['is_admin'] = True
        sess['admin_username'] = 'admin'

    response = client.post('/admin/settings/footer', data={
        'organization_line': 'Dhofar University • College of Arts & Applied Sciences',
        'tagline': 'Student Management System • Advisee Analytics & WebRTC Hub',
        'disclaimer': 'This independent advising management platform is developed solely for educational mentoring.',
        'copyright': '© 2026 Academic Advising Hub. All rights reserved.'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Footer content and educational disclaimers updated successfully" in response.data

def test_admin_save_permissions_post(client):
    with client.session_transaction() as sess:
        sess['is_admin'] = True
        sess['admin_username'] = 'admin'

    response = client.post('/admin/settings/permissions', data={
        'require_advisor_admission': 'true',
        'allow_guest_chat': 'true',
        'allow_guest_notes_edit': 'false',
        'allow_guest_video': 'true',
        'allow_guest_audio': 'true',
        'meeting_passcode': '1234'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Access control and participant permissions saved successfully" in response.data

def test_advisor_profile_view_route(client):
    response = client.get('/advisor')
    assert response.status_code == 200
    assert b"Dr. Nasser Tabook" in response.data
    assert b"Biography &amp; Introduction" in response.data or b"Biography & Introduction" in response.data
    assert b"Staff ID" in response.data

    # Test alias route
    profile_resp = client.get('/profile')
    assert profile_resp.status_code == 200

def test_admin_save_profile_post(client):
    with client.session_transaction() as sess:
        sess['is_admin'] = True
        sess['admin_username'] = 'admin'

    response = client.post('/admin/settings/profile', data={
        'full_name': 'Dr. Nasser Tabook',
        'title': 'Assistant Professor of Computer Science',
        'staff_id': 'DU-FAC-2026',
        'bio': 'I am an academic advisor dedicated to student success and academic excellence.',
        'advising_mission': 'Guiding advisees to achieve degree completion with high academic standing.',
        'email_primary': 'ntabook@du.edu.om',
        'email_secondary': 'nasser@nasserdiary.com',
        'phone_office': '+968 2323 7000',
        'phone_mobile': '+968 9911 2233',
        'whatsapp': '+968 9911 2233',
        'office_location': 'College of Arts & Applied Sciences, Office 214',
        'office_hours': 'Sun / Tue / Thu 10:00 AM - 12:00 PM',
        'college': 'College of Arts & Applied Sciences',
        'department': 'Computer Science Department',
        'research_interests': 'AI, Educational Data Mining, Software Systems',
        'personal_website': 'https://nasserdiary.com',
        'linkedin_url': 'https://linkedin.com/in/nasser-tabook',
        'google_scholar_url': '',
        'avatar_url': '',
        'avatar_initials': 'NT'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Advisor biography, contact channels, and profile updated successfully" in response.data

    # Verify that the updated information is visible on the public advisor profile page
    pub_resp = client.get('/advisor')
    assert pub_resp.status_code == 200
    assert b"DU-FAC-2026" in pub_resp.data
    assert b"I am an academic advisor dedicated to student success" in pub_resp.data
    assert b"nasser@nasserdiary.com" in pub_resp.data
    assert b"Office 214" in pub_resp.data

