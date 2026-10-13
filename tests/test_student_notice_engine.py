import pytest
from app.student_notice_engine import generate_student_official_notice
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
