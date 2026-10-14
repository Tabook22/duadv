"""Comprehensive Unit & Integration Tests for Bilingual Engine, Arabic RTL Support,
and Academic Translations across Dhofar University Advising Engines and Views.
"""

import pytest
from app.i18n import translate, TRANSLATIONS, get_current_language, is_rtl
from app.utils import load_students_from_file
from app.chair_report_engine import generate_chair_advising_report
from app.student_notice_engine import generate_student_official_notice, generate_batch_student_notices
from app.persona_engine import generate_student_persona
from app.advising_engine import generate_student_advising_dossier

def test_translation_dictionary_coverage():
    """Verify both English and Arabic dictionaries have core academic terms"""
    assert 'en' in TRANSLATIONS
    assert 'ar' in TRANSLATIONS
    
    # Key terms must exist in both languages
    core_keys = [
        'app_title', 'dashboard', 'advisees', 'students_at_risk', 
        'supervisor_dashboard', 'total_advisees', 'good_standing_cleared',
        'academic_probation', 'strict_probation', 'cohort_health_distribution',
        'cgpa', 'sgpa', 'student_id', 'name', 'program_major', 'standing_status'
    ]
    for key in core_keys:
        assert key in TRANSLATIONS['en'], f"Missing '{key}' in English dictionary"
        assert key in TRANSLATIONS['ar'], f"Missing '{key}' in Arabic dictionary"

def test_translation_arabic_values():
    """Verify high-quality Arabic academic terms"""
    assert TRANSLATIONS['ar']['app_title'] == 'جامعة ظفار'
    assert TRANSLATIONS['ar']['dashboard'] == 'لوحة التحكم'
    assert TRANSLATIONS['ar']['students_at_risk'] == 'الطلبة تحت الملاحظة'
    assert TRANSLATIONS['ar']['cgpa'] == 'المعدل التراكمي'
    assert TRANSLATIONS['ar']['strict_probation'] == 'الملاحظة الصارمة'

def test_language_toggle_route(client):
    """Test switching between languages via /set-language/<lang>"""
    # 1. Switch to Arabic
    resp = client.get('/set-language/ar', follow_redirects=True)
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        assert sess.get('lang') == 'ar'
    
    # In Arabic mode, the page should include Arabic labels and dir="rtl"
    assert 'dir="rtl"'.encode('utf-8') in resp.data
    assert 'لوحة التحكم'.encode('utf-8') in resp.data
    assert 'الطلبة المُرشَدون'.encode('utf-8') in resp.data
    assert 'المعدل التراكمي'.encode('utf-8') in resp.data
    
    # 2. Switch back to English
    resp_en = client.get('/set-language/en', follow_redirects=True)
    assert resp_en.status_code == 200
    with client.session_transaction() as sess:
        assert sess.get('lang') == 'en'
    assert 'dir="ltr"'.encode('utf-8') in resp_en.data
    assert 'Dashboard'.encode('utf-8') in resp_en.data

def test_chair_report_arabic():
    """Verify Chair Report Engine generates full Arabic letter and intervention notes"""
    report = generate_chair_advising_report(force_refresh=True, lang='ar')
    assert 'مرشد أكاديمي' in report['advisor_title']
    assert 'رئيس قسم علوم الحاسوب' in report['addressee_title']
    assert 'جامعة ظفار' in report['letter_text']
    assert 'المادة 14' in report['letter_text']
    assert 'المادة 22' in report['letter_text']
    assert 'د. ناصر' in report['letter_text']

    if report['strict_probation']:
        sample = report['strict_probation'][0]
        assert 'rescue_actions' in sample
        assert len(sample['rescue_actions']) > 0
        assert any('المادة' in act or 'سقف' in act or 'إعادة' in act for act in sample['rescue_actions'])

def test_student_official_notice_arabic():
    """Verify Student Notice Engine generates Arabic notice letter and mail draft"""
    students = load_students_from_file()
    assert len(students) > 0
    sid = students[0].id
    
    notice = generate_student_official_notice(sid, force_refresh=True, lang='ar')
    assert notice['lang'] == 'ar'
    assert 'إخطار' in notice['email_subject']
    assert 'د. ناصر' in notice['email_body']
    assert 'جامعة ظفار' in notice['email_body']
    assert 'المادة' in notice['email_body']
    assert len(notice['mandatory_directives']) > 0
    assert notice['is_rtl'] is True

def test_persona_engine_arabic():
    """Verify Persona Engine generates Arabic archetypes, directives, and playbook"""
    students = load_students_from_file()
    assert len(students) > 0
    sid = students[0].id
    
    persona = generate_student_persona(sid, lang='ar')
    assert 'archetype' in persona
    assert 'title' in persona['archetype']
    assert len(persona['what_the_student_does']) > 0
    assert len(persona['what_the_student_must_do']) > 0
    assert len(persona['strengths']) > 0
    assert len(persona['weaknesses']) > 0
    assert 'advisor_brief' in persona
    assert 'opening_statement' in persona['advisor_brief']
    assert len(persona['advisor_brief']['opening_statement']) > 10

def test_advising_engine_arabic():
    """Verify Advising Engine generates Arabic dossier and Article 18 blueprint"""
    students = load_students_from_file()
    assert len(students) > 0
    sid = students[0].id
    
    dossier = generate_student_advising_dossier(sid, force_refresh=True, lang='ar')
    assert 'executive_analysis' in dossier
    assert 'situation_summary' in dossier['executive_analysis']
    assert 'recovery_path' in dossier
    assert 'action_steps' in dossier['recovery_path']
    assert len(dossier['recovery_path']['action_steps']) > 0
    assert any('المادة' in s or 'ساعة' in s or 'المعدل' in s for s in dossier['recovery_path']['action_steps'])

def test_arabic_views_integration(client):
    """Test all main pages render with full Arabic when lang=ar is active"""
    client.get('/set-language/ar')
    students = load_students_from_file()
    sid = students[0].id if students else '202110123'
    
    # 1. Students at risk list view
    resp_risk = client.get('/students-at-risk')
    assert resp_risk.status_code == 200
    assert 'الطلبة تحت الملاحظة'.encode('utf-8') in resp_risk.data
    assert 'dir="rtl"'.encode('utf-8') in resp_risk.data
    
    # 2. Chair letter view
    resp_chair = client.get('/students-at-risk/chair-letter')
    assert resp_chair.status_code == 200
    assert 'رئيس قسم علوم الحاسوب'.encode('utf-8') in resp_chair.data
    assert 'المادة 18'.encode('utf-8') in resp_chair.data
    
    # 3. Batch notices view
    resp_batch = client.get('/students-at-risk/batch-notices')
    assert resp_batch.status_code == 200
    assert 'مركز التواصل والإخطارات'.encode('utf-8') in resp_batch.data
    
    # 4. Printable At-Risk report
    resp_rep = client.get('/students-at-risk/report')
    assert resp_rep.status_code == 200
    assert 'جامعة ظفار'.encode('utf-8') in resp_rep.data
    assert 'dir="rtl"'.encode('utf-8') in resp_rep.data
    
    # 5. Student detail view
    resp_detail = client.get(f'/student/{sid}')
    assert resp_detail.status_code == 200
    assert 'dir="rtl"'.encode('utf-8') in resp_detail.data
    assert 'الملف الأكاديمي'.encode('utf-8') in resp_detail.data or 'المعدل التراكمي'.encode('utf-8') in resp_detail.data
    
    # 6. Official notice view
    resp_notice = client.get(f'/student/{sid}/official-notice')
    assert resp_notice.status_code == 200
    assert 'جامعة ظفار'.encode('utf-8') in resp_notice.data
    assert 'dir="rtl"'.encode('utf-8') in resp_notice.data
    
    # 7. Advising memo view
    resp_memo = client.get(f'/student/{sid}/advising-memo')
    assert resp_memo.status_code == 200
    assert 'جامعة ظفار'.encode('utf-8') in resp_memo.data
    assert 'المادة 18'.encode('utf-8') in resp_memo.data
    assert 'dir="rtl"'.encode('utf-8') in resp_memo.data
