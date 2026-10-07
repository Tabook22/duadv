"""Data models for the application"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Student:
    """Student data model"""
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    program: Optional[str] = None
    status: Optional[str] = None
    year: Optional[str] = None
    gpa: Optional[float] = None          # Cumulative GPA (CGPA) - graduation benchmark
    cgpa: Optional[float] = None         # Explicit alias for Cumulative GPA
    semester_gpa: Optional[float] = None # Latest Semester GPA (SGPA) - probation benchmark
    credits: Optional[int] = None
    advisor: Optional[str] = None
    last_updated: Optional[datetime] = None

    def __post_init__(self):
        if self.cgpa is None and self.gpa is not None:
            self.cgpa = self.gpa
        elif self.gpa is None and self.cgpa is not None:
            self.gpa = self.cgpa

@dataclass
class Course:
    """Course data model"""
    code: str
    name: str
    credits: int
    grade: Optional[str] = None
    semester: Optional[str] = None
    year: Optional[str] = None

@dataclass
class Transcript:
    """Student transcript model"""
    student_id: str
    courses: List[Course]
    total_credits: int
    gpa: float
    last_updated: datetime

@dataclass
class StudyPlan:
    """Study plan model"""
    student_id: str
    program: str
    required_courses: List[Course]
    completed_courses: List[Course]
    remaining_courses: List[Course]
    expected_graduation: Optional[str] = None

@dataclass
class PolicyReference:
    """Academic policy & advising guidance reference document model"""
    id: str
    title: str
    category: str
    filename: str
    original_filename: str
    file_size: str
    file_type: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    page_count: Optional[int] = None
    uploaded_at: Optional[datetime] = None

