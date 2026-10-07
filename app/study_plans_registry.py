"""
Study Plans Registry for Dhofar University
Contains complete curriculum roadmaps, prerequisite dependency graphs, and credit distributions for:
1. Diploma in Computer Science (65 Credit Hours)
2. Bachelor of Science in Cybersecurity (124 Credit Hours)
3. Bachelor of Science in Data Science (124 Credit Hours)
4. Bachelor of Science in Computer Science (120 Credit Hours)
"""

import os
import json
from typing import Dict, List, Any, Optional

DEFAULT_STUDY_PLANS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'study_plans')

# -------------------------------------------------------------------------
# Standard Dhofar University Degree Curricula
# -------------------------------------------------------------------------

DIPLOMA_CS_CURRICULUM = [
    # Level 1 - Semester 1
    {"code": "ENGL 101", "name": "Basic Academic English", "credits": 3, "category": "University Requirement", "term_recommended": "Year 1 Fall", "prerequisites": []},
    {"code": "ARAB 101", "name": "Academic Writing in Arabic", "credits": 3, "category": "University Requirement", "term_recommended": "Year 1 Fall", "prerequisites": []},
    {"code": "MATH 199", "name": "Calculus I", "credits": 3, "category": "College Requirement", "term_recommended": "Year 1 Fall", "prerequisites": []},
    {"code": "CMPS 100B", "name": "Introduction to Technical Computing for the Sciences", "credits": 3, "category": "Major Core", "term_recommended": "Year 1 Fall", "prerequisites": []},
    {"code": "CMPS 110N", "name": "Introduction to Problem Solving and Programming", "credits": 3, "category": "Major Core", "term_recommended": "Year 1 Fall", "prerequisites": []},
    
    # Level 1 - Semester 2
    {"code": "ENGL 102C", "name": "English for Computer Sciences I", "credits": 3, "category": "University Requirement", "term_recommended": "Year 1 Spring", "prerequisites": ["ENGL 101"]},
    {"code": "SOCS 102", "name": "Omani Society", "credits": 3, "category": "University Requirement", "term_recommended": "Year 1 Spring", "prerequisites": []},
    {"code": "CMPS 180", "name": "Digital System Design", "credits": 3, "category": "Major Core", "term_recommended": "Year 1 Spring", "prerequisites": ["CMPS 110N"]},
    {"code": "CMPS 150", "name": "Computer Programming", "credits": 3, "category": "Major Core", "term_recommended": "Year 1 Spring", "prerequisites": ["CMPS 110N"]},
    {"code": "MATH 370", "name": "Discrete Mathematics", "credits": 3, "category": "College Requirement", "term_recommended": "Year 1 Spring", "prerequisites": ["MATH 199"]},
    
    # Level 2 - Semester 3
    {"code": "ENGL 203C", "name": "English for Computer Sciences II", "credits": 3, "category": "University Requirement", "term_recommended": "Year 2 Fall", "prerequisites": ["ENGL 102C"]},
    {"code": "CMPS 215", "name": "Computer Organization with Assembly Language", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Fall", "prerequisites": ["CMPS 180"]},
    {"code": "CMPS 220", "name": "Data Structures", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Fall", "prerequisites": ["CMPS 150"]},
    {"code": "CMPS 250", "name": "Computer Networks", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Fall", "prerequisites": ["CMPS 100B"]},
    {"code": "EDUC 120", "name": "Learning and Child Development", "credits": 3, "category": "University Elective", "term_recommended": "Year 2 Fall", "prerequisites": []},
    
    # Level 2 - Semester 4
    {"code": "CMPS 260", "name": "Operating Systems", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Spring", "prerequisites": ["CMPS 215"]},
    {"code": "CMPS 270", "name": "Database Systems", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Spring", "prerequisites": ["CMPS 220"]},
    {"code": "CMPS 255", "name": "Graphical User Interface", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Spring", "prerequisites": ["CMPS 150"]},
    {"code": "CMPS 200", "name": "Analysis and Design of Information Systems", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Spring", "prerequisites": ["CMPS 220"]},
    {"code": "CMPS 299", "name": "Diploma Project in Computer Science", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Spring", "prerequisites": ["CMPS 220", "CMPS 270"]},
    {"code": "ENTR 200", "name": "Entrepreneurship: Innovation and Creativity", "credits": 2, "category": "University Requirement", "term_recommended": "Year 2 Spring", "prerequisites": []},
]

CYBERSECURITY_BS_CURRICULUM = [
    # Year 1
    {"code": "ENGL 101", "name": "Basic Academic English", "credits": 3, "category": "University Requirement", "term_recommended": "Year 1 Fall", "prerequisites": []},
    {"code": "ARAB 101", "name": "Academic Writing in Arabic", "credits": 3, "category": "University Requirement", "term_recommended": "Year 1 Fall", "prerequisites": []},
    {"code": "MATH 199", "name": "Calculus I", "credits": 3, "category": "College Requirement", "term_recommended": "Year 1 Fall", "prerequisites": []},
    {"code": "CMPS 100B", "name": "Introduction to Technical Computing for the Sciences", "credits": 3, "category": "Major Core", "term_recommended": "Year 1 Fall", "prerequisites": []},
    {"code": "CMPS 110N", "name": "Introduction to Problem Solving and Programming", "credits": 3, "category": "Major Core", "term_recommended": "Year 1 Fall", "prerequisites": []},
    {"code": "ENGL 102C", "name": "English for Computer Sciences I", "credits": 3, "category": "University Requirement", "term_recommended": "Year 1 Spring", "prerequisites": ["ENGL 101"]},
    {"code": "MATH 200", "name": "Calculus II", "credits": 3, "category": "College Requirement", "term_recommended": "Year 1 Spring", "prerequisites": ["MATH 199"]},
    {"code": "MATH 370", "name": "Discrete Mathematics", "credits": 3, "category": "College Requirement", "term_recommended": "Year 1 Spring", "prerequisites": ["MATH 199"]},
    {"code": "CMPS 150", "name": "Computer Programming", "credits": 3, "category": "Major Core", "term_recommended": "Year 1 Spring", "prerequisites": ["CMPS 110N"]},
    {"code": "CMPS 180", "name": "Digital System Design", "credits": 3, "category": "Major Core", "term_recommended": "Year 1 Spring", "prerequisites": ["CMPS 110N"]},
    
    # Year 2
    {"code": "ENGL 203C", "name": "English for Computer Sciences II", "credits": 3, "category": "University Requirement", "term_recommended": "Year 2 Fall", "prerequisites": ["ENGL 102C"]},
    {"code": "MATH 320", "name": "Linear Algebra I", "credits": 3, "category": "College Requirement", "term_recommended": "Year 2 Fall", "prerequisites": ["MATH 199"]},
    {"code": "CMPS 215", "name": "Computer Organization with Assembly Language", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Fall", "prerequisites": ["CMPS 180"]},
    {"code": "CMPS 220", "name": "Data Structures", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Fall", "prerequisites": ["CMPS 150"]},
    {"code": "CMPS 250", "name": "Computer Networks", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Fall", "prerequisites": ["CMPS 100B"]},
    {"code": "CMPS 240", "name": "Analysis of Algorithms", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Spring", "prerequisites": ["CMPS 220", "MATH 370"]},
    {"code": "CMPS 260", "name": "Operating Systems", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Spring", "prerequisites": ["CMPS 215"]},
    {"code": "CMPS 270", "name": "Database Systems", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Spring", "prerequisites": ["CMPS 220"]},
    {"code": "CSEC 210", "name": "Fundamentals of Cybersecurity & Information Assurance", "credits": 3, "category": "Cybersecurity Core", "term_recommended": "Year 2 Spring", "prerequisites": ["CMPS 250"]},
    {"code": "SOCS 102", "name": "Omani Society", "credits": 3, "category": "University Requirement", "term_recommended": "Year 2 Spring", "prerequisites": []},
    
    # Year 3
    {"code": "CSEC 310", "name": "Network & Perimeter Security", "credits": 3, "category": "Cybersecurity Core", "term_recommended": "Year 3 Fall", "prerequisites": ["CSEC 210", "CMPS 250"]},
    {"code": "CSEC 320", "name": "Cryptography and Data Protection", "credits": 3, "category": "Cybersecurity Core", "term_recommended": "Year 3 Fall", "prerequisites": ["MATH 370", "CSEC 210"]},
    {"code": "CSEC 330", "name": "Secure Software Engineering", "credits": 3, "category": "Cybersecurity Core", "term_recommended": "Year 3 Fall", "prerequisites": ["CMPS 220", "CSEC 210"]},
    {"code": "STAT 230", "name": "Probability and Statistics for Engineers & Scientists", "credits": 3, "category": "College Requirement", "term_recommended": "Year 3 Fall", "prerequisites": ["MATH 199"]},
    {"code": "CSEC 340", "name": "Ethical Hacking and Penetration Testing", "credits": 3, "category": "Cybersecurity Core", "term_recommended": "Year 3 Spring", "prerequisites": ["CSEC 310"]},
    {"code": "CSEC 350", "name": "Digital Forensics & Incident Response", "credits": 3, "category": "Cybersecurity Core", "term_recommended": "Year 3 Spring", "prerequisites": ["CMPS 260", "CSEC 210"]},
    {"code": "CSEC 360", "name": "Security Operations Center (SOC) & SIEM", "credits": 3, "category": "Cybersecurity Core", "term_recommended": "Year 3 Spring", "prerequisites": ["CSEC 310"]},
    {"code": "ENTR 200", "name": "Entrepreneurship: Innovation and Creativity", "credits": 3, "category": "University Requirement", "term_recommended": "Year 3 Spring", "prerequisites": []},
    
    # Year 4
    {"code": "CSEC 410", "name": "Cloud Security and Virtualization", "credits": 3, "category": "Cybersecurity Core", "term_recommended": "Year 4 Fall", "prerequisites": ["CSEC 310", "CMPS 260"]},
    {"code": "CSEC 420", "name": "Cyber Law, Policy and Ethics", "credits": 3, "category": "Cybersecurity Core", "term_recommended": "Year 4 Fall", "prerequisites": ["CSEC 210"]},
    {"code": "CSEC 490A", "name": "Cybersecurity Capstone Senior Project I", "credits": 3, "category": "Major Core", "term_recommended": "Year 4 Fall", "prerequisites": ["CSEC 340", "CSEC 350"]},
    {"code": "CSEC 480", "name": "Cybersecurity Industrial Internship", "credits": 3, "category": "Major Core", "term_recommended": "Year 4 Fall", "prerequisites": ["CSEC 310"]},
    {"code": "CSEC 490B", "name": "Cybersecurity Capstone Senior Project II", "credits": 3, "category": "Major Core", "term_recommended": "Year 4 Spring", "prerequisites": ["CSEC 490A"]},
    {"code": "CSEC 450", "name": "Industrial Control Systems (ICS/SCADA) Security", "credits": 3, "category": "Cybersecurity Elective", "term_recommended": "Year 4 Spring", "prerequisites": ["CSEC 310"]},
]

DATA_SCIENCE_BS_CURRICULUM = [
    # Year 1
    {"code": "ENGL 101", "name": "Basic Academic English", "credits": 3, "category": "University Requirement", "term_recommended": "Year 1 Fall", "prerequisites": []},
    {"code": "ARAB 101", "name": "Academic Writing in Arabic", "credits": 3, "category": "University Requirement", "term_recommended": "Year 1 Fall", "prerequisites": []},
    {"code": "MATH 199", "name": "Calculus I", "credits": 3, "category": "College Requirement", "term_recommended": "Year 1 Fall", "prerequisites": []},
    {"code": "CMPS 100B", "name": "Introduction to Technical Computing for the Sciences", "credits": 3, "category": "Major Core", "term_recommended": "Year 1 Fall", "prerequisites": []},
    {"code": "CMPS 110N", "name": "Introduction to Problem Solving and Programming", "credits": 3, "category": "Major Core", "term_recommended": "Year 1 Fall", "prerequisites": []},
    {"code": "ENGL 102C", "name": "English for Computer Sciences I", "credits": 3, "category": "University Requirement", "term_recommended": "Year 1 Spring", "prerequisites": ["ENGL 101"]},
    {"code": "MATH 200", "name": "Calculus II", "credits": 3, "category": "College Requirement", "term_recommended": "Year 1 Spring", "prerequisites": ["MATH 199"]},
    {"code": "MATH 370", "name": "Discrete Mathematics", "credits": 3, "category": "College Requirement", "term_recommended": "Year 1 Spring", "prerequisites": ["MATH 199"]},
    {"code": "CMPS 150", "name": "Computer Programming", "credits": 3, "category": "Major Core", "term_recommended": "Year 1 Spring", "prerequisites": ["CMPS 110N"]},
    {"code": "DSCI 110", "name": "Introduction to Data Science with Python", "credits": 3, "category": "Data Science Core", "term_recommended": "Year 1 Spring", "prerequisites": ["CMPS 110N"]},
    
    # Year 2
    {"code": "ENGL 203C", "name": "English for Computer Sciences II", "credits": 3, "category": "University Requirement", "term_recommended": "Year 2 Fall", "prerequisites": ["ENGL 102C"]},
    {"code": "MATH 320", "name": "Linear Algebra I", "credits": 3, "category": "College Requirement", "term_recommended": "Year 2 Fall", "prerequisites": ["MATH 199"]},
    {"code": "CMPS 220", "name": "Data Structures", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Fall", "prerequisites": ["CMPS 150"]},
    {"code": "STAT 230", "name": "Probability and Statistics for Engineers & Scientists", "credits": 3, "category": "College Requirement", "term_recommended": "Year 2 Fall", "prerequisites": ["MATH 199"]},
    {"code": "CMPS 270", "name": "Database Systems", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Fall", "prerequisites": ["CMPS 220"]},
    {"code": "DSCI 210", "name": "Data Wrangling and Exploratory Data Analysis", "credits": 3, "category": "Data Science Core", "term_recommended": "Year 2 Spring", "prerequisites": ["DSCI 110", "CMPS 270"]},
    {"code": "CMPS 240", "name": "Analysis of Algorithms", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Spring", "prerequisites": ["CMPS 220", "MATH 370"]},
    {"code": "STAT 330", "name": "Statistical Inference and Modeling", "credits": 3, "category": "Data Science Core", "term_recommended": "Year 2 Spring", "prerequisites": ["STAT 230", "MATH 320"]},
    {"code": "SOCS 102", "name": "Omani Society", "credits": 3, "category": "University Requirement", "term_recommended": "Year 2 Spring", "prerequisites": []},
    
    # Year 3
    {"code": "DSCI 310", "name": "Machine Learning Algorithms", "credits": 3, "category": "Data Science Core", "term_recommended": "Year 3 Fall", "prerequisites": ["DSCI 210", "MATH 320", "STAT 330"]},
    {"code": "DSCI 320", "name": "Big Data Engineering & Distributed Systems", "credits": 3, "category": "Data Science Core", "term_recommended": "Year 3 Fall", "prerequisites": ["CMPS 270", "CMPS 220"]},
    {"code": "CMPS 365", "name": "Artificial Intelligence", "credits": 3, "category": "Major Core", "term_recommended": "Year 3 Fall", "prerequisites": ["CMPS 220"]},
    {"code": "DSCI 330", "name": "Deep Learning and Neural Networks", "credits": 3, "category": "Data Science Core", "term_recommended": "Year 3 Spring", "prerequisites": ["DSCI 310"]},
    {"code": "DSCI 340", "name": "Natural Language Processing", "credits": 3, "category": "Data Science Core", "term_recommended": "Year 3 Spring", "prerequisites": ["DSCI 310"]},
    {"code": "DSCI 350", "name": "Data Visualization & Dashboard Analytics", "credits": 3, "category": "Data Science Core", "term_recommended": "Year 3 Spring", "prerequisites": ["DSCI 210"]},
    {"code": "ENTR 200", "name": "Entrepreneurship: Innovation and Creativity", "credits": 3, "category": "University Requirement", "term_recommended": "Year 3 Spring", "prerequisites": []},
    
    # Year 4
    {"code": "DSCI 410", "name": "Time Series Analysis & Forecasting", "credits": 3, "category": "Data Science Core", "term_recommended": "Year 4 Fall", "prerequisites": ["STAT 330", "DSCI 310"]},
    {"code": "DSCI 490A", "name": "Data Science Senior Capstone Project I", "credits": 3, "category": "Major Core", "term_recommended": "Year 4 Fall", "prerequisites": ["DSCI 310", "DSCI 320"]},
    {"code": "DSCI 480", "name": "Data Science Industrial Internship", "credits": 3, "category": "Major Core", "term_recommended": "Year 4 Fall", "prerequisites": ["DSCI 310"]},
    {"code": "DSCI 490B", "name": "Data Science Senior Capstone Project II", "credits": 3, "category": "Major Core", "term_recommended": "Year 4 Spring", "prerequisites": ["DSCI 490A"]},
]

COMPUTER_SCIENCE_BS_CURRICULUM = [
    # Year 1
    {"code": "ENGL 101", "name": "Basic Academic English", "credits": 3, "category": "University Requirement", "term_recommended": "Year 1 Fall", "prerequisites": []},
    {"code": "ARAB 101", "name": "Academic Writing in Arabic", "credits": 3, "category": "University Requirement", "term_recommended": "Year 1 Fall", "prerequisites": []},
    {"code": "MATH 199", "name": "Calculus I", "credits": 3, "category": "College Requirement", "term_recommended": "Year 1 Fall", "prerequisites": []},
    {"code": "CMPS 100B", "name": "Introduction to Technical Computing for the Sciences", "credits": 3, "category": "Major Core", "term_recommended": "Year 1 Fall", "prerequisites": []},
    {"code": "CMPS 110N", "name": "Introduction to Problem Solving and Programming", "credits": 3, "category": "Major Core", "term_recommended": "Year 1 Fall", "prerequisites": []},
    {"code": "ENGL 102C", "name": "English for Computer Sciences I", "credits": 3, "category": "University Requirement", "term_recommended": "Year 1 Spring", "prerequisites": ["ENGL 101"]},
    {"code": "MATH 200", "name": "Calculus II", "credits": 3, "category": "College Requirement", "term_recommended": "Year 1 Spring", "prerequisites": ["MATH 199"]},
    {"code": "MATH 370", "name": "Discrete Mathematics", "credits": 3, "category": "College Requirement", "term_recommended": "Year 1 Spring", "prerequisites": ["MATH 199"]},
    {"code": "CMPS 150", "name": "Computer Programming", "credits": 3, "category": "Major Core", "term_recommended": "Year 1 Spring", "prerequisites": ["CMPS 110N"]},
    {"code": "CMPS 180", "name": "Digital System Design", "credits": 3, "category": "Major Core", "term_recommended": "Year 1 Spring", "prerequisites": ["CMPS 110N"]},
    
    # Year 2
    {"code": "ENGL 203C", "name": "English for Computer Sciences II", "credits": 3, "category": "University Requirement", "term_recommended": "Year 2 Fall", "prerequisites": ["ENGL 102C"]},
    {"code": "MATH 320", "name": "Linear Algebra I", "credits": 3, "category": "College Requirement", "term_recommended": "Year 2 Fall", "prerequisites": ["MATH 199"]},
    {"code": "CMPS 215", "name": "Computer Organization with Assembly Language", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Fall", "prerequisites": ["CMPS 180"]},
    {"code": "CMPS 220", "name": "Data Structures", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Fall", "prerequisites": ["CMPS 150"]},
    {"code": "CMPS 250", "name": "Computer Networks", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Fall", "prerequisites": ["CMPS 100B"]},
    {"code": "CMPS 240", "name": "Analysis of Algorithms", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Spring", "prerequisites": ["CMPS 220", "MATH 370"]},
    {"code": "CMPS 260", "name": "Operating Systems", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Spring", "prerequisites": ["CMPS 215"]},
    {"code": "CMPS 270", "name": "Database Systems", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Spring", "prerequisites": ["CMPS 220"]},
    {"code": "CMPS 255", "name": "Graphical User Interface", "credits": 3, "category": "Major Core", "term_recommended": "Year 2 Spring", "prerequisites": ["CMPS 150"]},
    {"code": "SOCS 102", "name": "Omani Society", "credits": 3, "category": "University Requirement", "term_recommended": "Year 2 Spring", "prerequisites": []},
    
    # Year 3
    {"code": "CMPS 310N", "name": "Programming Languages & Paradigms", "credits": 3, "category": "Major Core", "term_recommended": "Year 3 Fall", "prerequisites": ["CMPS 220"]},
    {"code": "CMPS 340", "name": "Advanced Programming in Java", "credits": 3, "category": "Major Core", "term_recommended": "Year 3 Fall", "prerequisites": ["CMPS 220"]},
    {"code": "STAT 230", "name": "Probability and Statistics", "credits": 3, "category": "College Requirement", "term_recommended": "Year 3 Fall", "prerequisites": ["MATH 199"]},
    {"code": "CMPS 365", "name": "Artificial Intelligence", "credits": 3, "category": "Major Core", "term_recommended": "Year 3 Spring", "prerequisites": ["CMPS 220"]},
    {"code": "CMPS 410N", "name": "Software Engineering", "credits": 3, "category": "Major Core", "term_recommended": "Year 3 Spring", "prerequisites": ["CMPS 270", "CMPS 220"]},
    {"code": "CMPS 300", "name": "Human Computer Interaction", "credits": 3, "category": "Major Core", "term_recommended": "Year 3 Spring", "prerequisites": ["CMPS 255"]},
    {"code": "ENTR 200", "name": "Entrepreneurship: Innovation and Creativity", "credits": 3, "category": "University Requirement", "term_recommended": "Year 3 Spring", "prerequisites": []},
    
    # Year 4
    {"code": "CMPS 490A", "name": "Senior Project / Capstone I", "credits": 3, "category": "Major Core", "term_recommended": "Year 4 Fall", "prerequisites": ["CMPS 410N"]},
    {"code": "CMPS 480", "name": "Computer Science Industrial Internship", "credits": 3, "category": "Major Core", "term_recommended": "Year 4 Fall", "prerequisites": ["CMPS 340", "CMPS 270"]},
    {"code": "CMPS 490B", "name": "Senior Project / Capstone II", "credits": 3, "category": "Major Core", "term_recommended": "Year 4 Spring", "prerequisites": ["CMPS 490A"]},
    {"code": "CMPS 420", "name": "Internet Programming and Web Design", "credits": 3, "category": "Major Elective", "term_recommended": "Year 4 Spring", "prerequisites": ["CMPS 220", "CMPS 270"]},
]

STUDY_PLANS_BY_PROGRAM = {
    "diploma in computer science": {
        "program_title": "Diploma in Computer Science",
        "degree_type": "Diploma",
        "total_credits": 65,
        "standard_semesters": 4,
        "curriculum": DIPLOMA_CS_CURRICULUM,
        "bridge_to_bachelor": {
            "eligible": True,
            "min_gpa": 75.0,
            "description": "Graduates with CGPA >= 75.0% qualify for direct articulation into B.Sc. in Computer Science, Cybersecurity, or Data Science."
        }
    },
    "bachelor of science in cybersecurity": {
        "program_title": "Bachelor of Science in Cybersecurity",
        "degree_type": "Bachelor of Science",
        "total_credits": 124,
        "standard_semesters": 8,
        "curriculum": CYBERSECURITY_BS_CURRICULUM,
        "bridge_to_bachelor": None
    },
    "bachelor of science in computer science - data": {
        "program_title": "Bachelor of Science in Data Science",
        "degree_type": "Bachelor of Science",
        "total_credits": 124,
        "standard_semesters": 8,
        "curriculum": DATA_SCIENCE_BS_CURRICULUM,
        "bridge_to_bachelor": None
    },
    "bachelor of science in data science": {
        "program_title": "Bachelor of Science in Data Science",
        "degree_type": "Bachelor of Science",
        "total_credits": 124,
        "standard_semesters": 8,
        "curriculum": DATA_SCIENCE_BS_CURRICULUM,
        "bridge_to_bachelor": None
    },
    "bachelor of science in computer science": {
        "program_title": "Bachelor of Science in Computer Science",
        "degree_type": "Bachelor of Science",
        "total_credits": 120,
        "standard_semesters": 8,
        "curriculum": COMPUTER_SCIENCE_BS_CURRICULUM,
        "bridge_to_bachelor": None
    }
}

def resolve_study_plan(program_name: Optional[str]) -> Dict[str, Any]:
    """Resolve the matching Dhofar University degree plan given a program name string"""
    if not program_name:
        return STUDY_PLANS_BY_PROGRAM["diploma in computer science"]
        
    p_lower = program_name.lower().strip()
    
    if "cyber" in p_lower:
        return STUDY_PLANS_BY_PROGRAM["bachelor of science in cybersecurity"]
    elif "data" in p_lower:
        return STUDY_PLANS_BY_PROGRAM["bachelor of science in data science"]
    elif "diploma" in p_lower:
        return STUDY_PLANS_BY_PROGRAM["diploma in computer science"]
    elif "bachelor" in p_lower or "computer science" in p_lower:
        return STUDY_PLANS_BY_PROGRAM["bachelor of science in computer science"]
    else:
        return STUDY_PLANS_BY_PROGRAM["diploma in computer science"]

def get_all_registered_study_plans() -> List[Dict[str, Any]]:
    """Return all degree study plans catalog entries"""
    plans = []
    seen = set()
    for key, plan in STUDY_PLANS_BY_PROGRAM.items():
        title = plan["program_title"]
        if title not in seen:
            seen.add(title)
            plans.append(plan)
    return plans