"""Unit tests for models"""

from datetime import datetime
from app.models import Student, Course, Transcript, StudyPlan

def test_student_model():
    student = Student(
        id="20211001",
        name="Ahmed Al-Kathiri",
        email="20211001@du.edu.om",
        phone="+968 9123 4567",
        program="Computer Science",
        year="Senior",
        gpa=3.65,
        advisor="Dr. Mohammed"
    )
    assert student.id == "20211001"
    assert student.name == "Ahmed Al-Kathiri"
    assert student.gpa == 3.65

def test_course_model():
    course = Course(
        code="CS310",
        name="Database Systems",
        credits=3,
        grade="A",
        semester="Fall",
        year="2025"
    )
    assert course.code == "CS310"
    assert course.credits == 3
    assert course.grade == "A"

def test_policy_reference_model():
    from app.models import PolicyReference
    policy = PolicyReference(
        id="pol_101",
        title="DU Student Guide",
        category="Student Handbook & Guide",
        filename="guide.pdf",
        original_filename="guide.pdf",
        file_size="1.2 MB",
        file_type="pdf",
        description="Guide for students",
        tags=["handbook", "guidance"],
        page_count=24
    )
    assert policy.id == "pol_101"
    assert policy.title == "DU Student Guide"
    assert policy.page_count == 24
    assert "handbook" in policy.tags

