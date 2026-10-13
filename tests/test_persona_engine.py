import pytest
from app.persona_engine import generate_student_persona, _classify_course_discipline, _analyze_discipline_performance
from app.utils import load_students_from_file

def test_classify_course_discipline():
    assert _classify_course_discipline('MATH 199') == 'MATH'
    assert _classify_course_discipline('CMPS110N') == 'CS'
    assert _classify_course_discipline('ENGL101') == 'GENED'
    assert _classify_course_discipline('ENGR200') == 'ENGR'
    assert _classify_course_discipline('MNGT101') == 'BUSINESS'
    assert _classify_course_discipline('UNKNOWN999') == 'OTHER'

def test_generate_student_persona_sample():
    students = load_students_from_file()
    assert len(students) > 0
    sample_student = students[0]

    persona = generate_student_persona(sample_student.id)
    assert 'student' in persona
    assert 'archetype' in persona
    assert 'strengths' in persona
    assert 'weaknesses' in persona
    assert 'what_the_student_does' in persona
    assert 'what_the_student_must_do' in persona
    assert 'roadmap' in persona
    assert 'advisor_brief' in persona

    # Check archetype structure
    arch = persona['archetype']
    assert 'key' in arch
    assert 'title' in arch
    assert 'tagline' in arch
    assert 'badge' in arch
    assert 'icon' in arch
    assert 'risk_level' in arch

    # Check that what_the_student_does and what_the_student_must_do have items
    assert len(persona['what_the_student_does']) > 0
    assert len(persona['what_the_student_must_do']) > 0
    assert len(persona['strengths']) > 0
    assert len(persona['weaknesses']) > 0

def test_generate_student_persona_invalid_id():
    with pytest.raises(ValueError, match="Student with ID 'INVALID_ID_999' not found"):
        generate_student_persona('INVALID_ID_999')

def test_student_persona_api_endpoint(client):
    students = load_students_from_file()
    if students:
        sid = students[0].id
        response = client.get(f'/api/student/{sid}/persona')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['student_id'] == sid
        assert 'archetype' in data
        assert 'strengths' in data
        assert 'weaknesses' in data
        assert 'what_the_student_does' in data
        assert 'what_the_student_must_do' in data
        assert 'roadmap' in data
        assert 'advisor_brief' in data

def test_student_persona_api_not_found(client):
    response = client.get('/api/student/INVALID_99999/persona')
    assert response.status_code == 404

