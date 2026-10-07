"""
Unit tests for Dhofar University Section Schedule Intelligence Engine
"""

import os
import pytest
from app import create_app
from app.schedule_engine import (
    load_section_schedule,
    get_sections_for_course,
    match_recommended_schedule_to_sections,
    parse_sections_from_html,
    generate_section_schedule_pdf,
    normalize_course_code,
    is_course_code_match
)


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_load_section_schedule():
    """Verify loading section schedule returns valid dataset"""
    data = load_section_schedule()
    assert isinstance(data, dict)
    assert 'sections' in data
    assert len(data['sections']) >= 30
    assert data['semester'] == 'Fall 2026-2027'


def test_normalize_course_code():
    """Verify course code normalization handles spaces and dashes"""
    assert normalize_course_code("CMPS 110") == "CMPS110"
    assert normalize_course_code("cmps-110") == "CMPS110"
    assert normalize_course_code("MATH  201 ") == "MATH201"


def test_get_sections_for_course():
    """Verify querying sections by course code"""
    sections = get_sections_for_course("CMPS 110")
    assert len(sections) >= 2
    for s in sections:
        assert is_course_code_match("CMPS 110", s['course_code'])
        assert s['capacity'] > 0
        assert 'instructor' in s
        assert 'room' in s


def test_match_recommended_schedule_to_sections():
    """Verify advisee recommended course matching to live sections"""
    recommended = [
        {'code': 'CMPS 110', 'name': 'Introduction to Computer Science', 'credits': 3, 'priority': 'Mandatory'},
        {'code': 'MATH 199', 'name': 'Calculus I', 'credits': 3, 'priority': 'Core'},
        {'code': 'UNKNOWN 999', 'name': 'Hypothetical Course', 'credits': 3, 'priority': 'Elective'}
    ]
    matched = match_recommended_schedule_to_sections(recommended)
    assert len(matched) == 3

    # CMPS 110 is offered
    assert matched[0]['is_offered'] is True
    assert matched[0]['primary_section'] is not None
    assert 'Sec' in matched[0]['primary_slot']
    assert matched[0]['seat_status'] in ['Open', 'Full']

    # MATH 199 is offered
    assert matched[1]['is_offered'] is True
    assert matched[1]['primary_section'] is not None

    # UNKNOWN 999 is not offered
    assert matched[2]['is_offered'] is False
    assert matched[2]['seat_status'] == 'Not Offered'


def test_parse_sections_from_html():
    """Verify HTML table parsing with mock DU SIS section table"""
    sample_html = """
    <table>
        <tr>
            <th>Crs.#</th><th>Title</th><th>Cr</th><th>Section</th><th>Session Type</th>
            <th>Lang.</th><th>Cap.</th><th>Enr.</th><th>Instructor</th><th>Room</th>
            <th>Day</th><th>Time</th><th>Remark</th>
        </tr>
        <tr>
            <td>CMPS 999</td><td>Advanced Quantum Computing</td><td>3</td><td>1</td><td>Morning</td>
            <td>English</td><td>30</td><td>15</td><td>Dr. Nasser Tabook</td><td>CC-102</td>
            <td>SunTueThu</td><td>09:00 - 09:50</td><td>Department Elective</td>
        </tr>
    </table>
    """
    sections = parse_sections_from_html(sample_html, semester="Fall 2026-2027")
    assert len(sections) == 1
    sec = sections[0]
    assert sec['course_code'] == 'CMPS 999'
    assert sec['title'] == 'Advanced Quantum Computing'
    assert sec['credits'] == 3
    assert sec['section'] == '1'
    assert sec['capacity'] == 30
    assert sec['enrolled'] == 15
    assert sec['instructor'] == 'Dr. Nasser Tabook'


def test_section_schedule_routes(client):
    """Verify web view and API endpoints for section schedule"""
    # 1. Main View
    res = client.get('/section-schedule')
    assert res.status_code == 200
    assert b'Course Offerings &amp; Section Schedule' in res.data or b'Course Offerings' in res.data
    assert b'CMPS 110' in res.data

    # 2. JSON Data API
    res_api = client.get('/api/section-schedule/data')
    assert res_api.status_code == 200
    json_data = res_api.get_json()
    assert 'sections' in json_data
    assert len(json_data['sections']) >= 30

    # 3. Course Sections API
    res_crs = client.get('/api/course-sections/CMPS 110')
    assert res_crs.status_code == 200
    crs_json = res_crs.get_json()
    assert crs_json['count'] >= 2
