"""
Tests for Dhofar University Advising Intelligence Engine,
Study Plans Registry, and LLM Advising Wiki
"""

import pytest
from app.study_plans_registry import resolve_study_plan, get_all_registered_study_plans
from app.advising_engine import (
    normalize_course_code,
    is_grade_passing,
    extract_numerical_grade,
    audit_student_degree,
    generate_student_advising_dossier
)
from app.wiki_engine import get_wiki_knowledge_base, ask_advising_wiki

def test_resolve_study_plan():
    # Test diploma
    p_dip = resolve_study_plan("Diploma in Computer Science")
    assert p_dip["degree_type"] == "Diploma"
    assert p_dip["total_credits"] == 65
    assert p_dip["bridge_to_bachelor"]["min_gpa"] == 75.0

    # Test cybersecurity
    p_cyb = resolve_study_plan("Bachelor of Science in Cybersecurity")
    assert p_cyb["total_credits"] == 124
    assert any("CSEC" in c["code"] for c in p_cyb["curriculum"])

    # Test data science
    p_dsci = resolve_study_plan("Bachelor of Science in Data Science")
    assert p_dsci["total_credits"] == 124
    assert any("DSCI" in c["code"] for c in p_dsci["curriculum"])

    # Test computer science
    p_cs = resolve_study_plan("Bachelor of Science in Computer Science")
    assert p_cs["total_credits"] == 120

def test_grade_evaluation_helpers():
    assert is_grade_passing("75") is True
    assert is_grade_passing("60") is True
    assert is_grade_passing("60 (R:2)") is True
    assert is_grade_passing("51") is False
    assert is_grade_passing("45") is False
    assert is_grade_passing("F") is False
    assert is_grade_passing("WA") is False
    assert is_grade_passing("P") is True
    
    assert extract_numerical_grade("60 (R:2)") == 60.0
    assert extract_numerical_grade("75.5") == 75.5
    assert extract_numerical_grade("WA") is None

def test_audit_student_degree():
    # Test on actual advisee: 202210391 (Sharifa Masan - Second Strict Probation)
    audit = audit_student_degree("202210391")
    assert audit["student"].id == "202210391"
    assert audit["total_plan_credits"] == 65
    assert audit["completed_credits"] == 30
    assert audit["is_under_probation"] is True
    assert audit["credit_cap"] == 12
    assert audit["gpa_deficit"] > 0
    assert len(audit["completed_courses"]) > 0
    assert len(audit["missing_courses"]) > 0
    
    # Check that failed courses are in critical_repeats
    crit_codes = [c["code"] for c in audit["critical_repeats"]]
    assert "CMPS 215" in crit_codes or "ENGL 203C" in crit_codes or "MATH 199" in crit_codes

def test_generate_student_advising_dossier():
    dossier = generate_student_advising_dossier("202210391")
    assert dossier["urgency_level"] in ["CRITICAL", "HIGH", "MODERATE"]
    assert dossier["total_recommended_credits"] <= 12  # Strict probation cap!
    assert len(dossier["recommended_schedule"]) > 0
    assert len(dossier["policy_citations"]) >= 3
    assert len(dossier["action_items"]) > 0
    
    # Ensure mandatory repeat is scheduled first
    priorities = [c["priority"] for c in dossier["recommended_schedule"]]
    assert any("Mandatory Repeat" in p for p in priorities)

def test_wiki_knowledge_base():
    kb = get_wiki_knowledge_base()
    assert len(kb["study_plans"]) >= 4
    assert len(kb["policy_modules"]) >= 5
    
    # Test Q&A
    ans_prob = ask_advising_wiki("What is the rule for student on academic probation?")
    assert ans_prob["status"] == "success"
    assert "Article 14" in ans_prob["answer"]
    
    ans_rep = ask_advising_wiki("Can a student repeat a D grade course?")
    assert ans_rep["status"] == "success"
    assert "Article 18" in ans_rep["answer"]
    
    ans_bridge = ask_advising_wiki("What is the bridge GPA from Diploma to Bachelor?")
    assert ans_bridge["status"] == "success"
    assert "75" in ans_bridge["answer"]

def test_semester_progression_analysis():
    from app.advising_engine import analyze_semester_progression
    prog = analyze_semester_progression("202310832")
    assert "chart_data" in prog
    assert "terms" in prog
    assert len(prog["terms"]) > 0
    assert "labels" in prog["chart_data"]
    assert "term_gpas" in prog["chart_data"]
    assert "cum_gpas" in prog["chart_data"]
    assert prog["chart_data"]["benchmark"] == 65.0
    assert prog["overall_trend"] in [
        "Upward / Improving Trajectory",
        "Downward / At-Risk Trajectory",
        "Fluctuating / Variable",
        "Initial Academic Baseline"
    ]
    for t in prog["terms"]:
        assert len(t["root_cause_explanation"]) > 10

def test_gpa_recovery_path_and_consultation():
    from app.advising_engine import (
        audit_student_degree,
        calculate_gpa_recovery_path,
        generate_advisor_consultation_guide,
        analyze_semester_progression
    )
    audit = audit_student_degree("202310832")
    student = audit["student"]
    prog = analyze_semester_progression(student.id)
    recovery = calculate_gpa_recovery_path(audit, student)
    
    assert "current_gpa" in recovery
    assert "repeat_items" in recovery
    assert "action_steps" in recovery
    assert len(recovery["action_steps"]) >= 4
    
    guide = generate_advisor_consultation_guide(student, audit, prog, recovery)
    assert guide["consultation_required"] is True
    assert "MANDATORY" in guide["urgency"]
    assert len(guide["advisor_script"]) >= 5
    assert len(guide["student_talking_points"]) >= 4
    assert any("Dr. Nasser" in s["dialogue"] or "Nasser" in s["speaker"] for s in guide["advisor_script"])