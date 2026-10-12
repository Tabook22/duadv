"""Unit tests for bilingual engine and Arabic/English language switching"""

from app.i18n import translate, TRANSLATIONS, get_current_language, is_rtl

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
