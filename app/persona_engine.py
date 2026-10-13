"""
Student Academic Persona & 360 Degree Intelligence Engine for Dhofar University.
Synthesizes comprehensive student academic profiles into commercial-grade personas:
- Archetype Classification (e.g. Dean's List Pacesetter, Gatekeeper Bottleneck, Recovery Fighter)
- Discipline Strengths & Competency Breakdown
- Critical Academic Blind Spots & Course Bottlenecks
- Behavioral Profile ("What The Student Does")
- Actionable Directives ("What The Student MUST Do")
- Strategic Graduation Planning Roadmap & Target Horizons
- Advisor Communication Blueprint for Dr. Nasser Tabook
"""

import os
import re
import math
from typing import Dict, List, Any, Optional

from app.models import Student
from app.utils import load_students_from_file, get_student_semesters
from app.advising_engine import (
    audit_student_degree,
    analyze_semester_progression,
    normalize_course_code,
    is_grade_passing,
    extract_numerical_grade
)

# Academic Disciplines Mapping for Dhofar University Curricula
DISCIPLINE_MAP = {
    'MATH': {
        'title': 'Mathematics & Quantitative Analysis',
        'prefixes': ['MATH', 'STAT', 'CALC', 'ALGEBRA', 'QUANT'],
        'icon': 'fas fa-square-root-alt',
        'color': '#0284c7'
    },
    'CS': {
        'title': 'Computer Science & Software Development',
        'prefixes': ['CMPS', 'COMP', 'CS', 'IT', 'DATA', 'AI', 'SE', 'NETW', 'PROG', 'WEB'],
        'icon': 'fas fa-laptop-code',
        'color': '#2563eb'
    },
    'ENGR': {
        'title': 'Engineering Sciences & Applied Labs',
        'prefixes': ['ENGR', 'ELEC', 'MECH', 'CIVL', 'PHYS', 'CHEM'],
        'icon': 'fas fa-cogs',
        'color': '#d97706'
    },
    'GENED': {
        'title': 'General Education & Communication',
        'prefixes': ['ENGL', 'ARAB', 'SOCS', 'PHIL', 'HUMA', 'HIST', 'COMM', 'UNIV'],
        'icon': 'fas fa-book-open',
        'color': '#059669'
    },
    'BUSINESS': {
        'title': 'Management & Quantitative Business',
        'prefixes': ['MNGT', 'ACCT', 'ECON', 'MKTG', 'FINA', 'BUSN'],
        'icon': 'fas fa-briefcase',
        'color': '#7c3aed'
    }
}


def _classify_course_discipline(course_code: str) -> str:
    """Identify which academic discipline category a course code belongs to"""
    norm = normalize_course_code(course_code)
    for disc_key, meta in DISCIPLINE_MAP.items():
        if any(norm.startswith(p) for p in meta['prefixes']):
            return disc_key
    return 'OTHER'


def _analyze_discipline_performance(semesters: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate aggregate success rate, attempt count, and average score across disciplines"""
    stats = {}
    for k in DISCIPLINE_MAP.keys():
        stats[k] = {
            'key': k,
            'title': DISCIPLINE_MAP[k]['title'],
            'icon': DISCIPLINE_MAP[k]['icon'],
            'color': DISCIPLINE_MAP[k]['color'],
            'attempts': 0,
            'passed': 0,
            'failed': 0,
            'total_score': 0.0,
            'scored_courses': 0,
            'courses': []
        }
    stats['OTHER'] = {
        'key': 'OTHER',
        'title': 'Other Department Electives',
        'icon': 'fas fa-graduation-cap',
        'color': '#64748b',
        'attempts': 0,
        'passed': 0,
        'failed': 0,
        'total_score': 0.0,
        'scored_courses': 0,
        'courses': []
    }

    for sem in semesters:
        for c in sem.get('courses', []):
            code = c.get('code', '').strip()
            # Skip foundation courses from disciplinary statistics
            if code.startswith(('FP', 'FPE', 'FPM', 'FPT')):
                continue

            disc = _classify_course_discipline(code)
            g_raw = c.get('grade')
            score = extract_numerical_grade(g_raw)
            passed = is_grade_passing(g_raw)

            bucket = stats[disc]
            bucket['attempts'] += 1
            if passed:
                bucket['passed'] += 1
            else:
                bucket['failed'] += 1

            if score is not None:
                bucket['total_score'] += score
                bucket['scored_courses'] += 1

            bucket['courses'].append({
                'code': code,
                'name': c.get('name', ''),
                'grade': g_raw,
                'score': score,
                'passed': passed,
                'term': sem.get('term', '')
            })

    # Compute averages and pass rates
    for k, b in stats.items():
        b['avg_score'] = round(b['total_score'] / b['scored_courses'], 1) if b['scored_courses'] > 0 else None
        b['pass_rate'] = round((b['passed'] / b['attempts']) * 100, 1) if b['attempts'] > 0 else 0.0

    return stats


def generate_student_persona(student_id: str, transcripts_dir: str = None) -> Dict[str, Any]:
    """
    Generate an intelligent, commercial-grade 360-degree Student Academic Persona.
    
    Synthesizes:
    1. Persona Archetype (Title, Tagline, Theme, Icon, Urgency/Risk Level)
    2. Academic Performance DNA (Discipline breakdown, strengths vs weaknesses)
    3. Behavioral Profile: "What The Student Does"
    4. Action Mandates: "What The Student MUST Do"
    5. Strategic Horizon & Degree Timeline
    6. Advisor Consultation Protocol for Dr. Nasser Tabook
    """
    students = load_students_from_file()
    student = next((s for s in students if s.id == student_id), None)
    if not student:
        raise ValueError(f"Student with ID '{student_id}' not found.")

    audit = audit_student_degree(student_id, transcripts_dir)
    progression = analyze_semester_progression(student_id)
    raw_semesters = get_student_semesters(student_id, transcripts_dir)
    discipline_stats = _analyze_discipline_performance(raw_semesters)

    current_gpa = audit['current_gpa'] or 0.0
    status = student.status or 'Normal / Good Standing'
    completion_pct = audit['completion_percentage']
    completed_credits = audit['completed_credits']
    remaining_credits = audit['remaining_credits']
    credit_cap = audit['credit_cap']
    critical_repeats = audit['critical_repeats']
    low_repeats = audit['low_grade_repeats']
    is_under_probation = audit['is_under_probation']
    term_history = progression.get('terms', [])
    num_graded_terms = len(term_history)

    # -------------------------------------------------------------
    # 1. ARCHETYPE CLASSIFICATION
    # -------------------------------------------------------------
    # Archetype determination based on standing, completion rate, repeats, and momentum
    recent_trend = progression.get('overall_trend', 'Stable')
    has_critical_repeats = len(critical_repeats) > 0
    severe_probation = ('Strict' in status or 'Third' in status or 'Second Strict' in status)
    
    # Check for recent positive momentum
    recent_sem_delta = 0.0
    if len(term_history) >= 2 and term_history[-1].get('delta_sem') is not None:
        recent_sem_delta = term_history[-1]['delta_sem'] or 0.0

    if severe_probation or (current_gpa < 60.0 and has_critical_repeats):
        archetype_key = 'high_risk_probation'
        archetype_title = "The High-Risk Stagnator"
        archetype_tagline = "Critical academic alert: Repeated course failures and credit caps threaten degree continuation under DU Article 14."
        archetype_badge = "danger"
        archetype_icon = "fas fa-shield-virus"
        risk_level = "CRITICAL"
        risk_score = 92
    elif is_under_probation or ('Probation' in status and 'Removal' not in status):
        if recent_sem_delta > 0 or recent_trend == 'Improving':
            archetype_key = 'probation_fighter'
            archetype_title = "The Recovery Fighter"
            archetype_tagline = "Actively rebounding from academic probation with positive upward momentum; within striking distance of Good Standing."
            archetype_badge = "warning text-dark"
            archetype_icon = "fas fa-fire"
            risk_level = "MODERATE TO HIGH"
            risk_score = 68
        else:
            archetype_key = 'probation_struggler'
            archetype_title = "The Academic Warning Stagnator"
            archetype_tagline = "Persistent GPA deficit below 65.0%; requires immediate intervention to halt probation escalation."
            archetype_badge = "warning text-dark"
            archetype_icon = "fas fa-exclamation-triangle"
            risk_level = "HIGH"
            risk_score = 78
    elif has_critical_repeats:
        archetype_key = 'prereq_bottleneck'
        archetype_title = "The Gatekeeper Bottleneck"
        archetype_tagline = "Capable student encountering severe prerequisite roadblocks in quantitative or programming core courses."
        archetype_badge = "orange text-white"
        archetype_icon = "fas fa-lock"
        risk_level = "MODERATE"
        risk_score = 55
    elif completion_pct >= 75.0 and current_gpa >= 65.0:
        archetype_key = 'capstone_sprinter'
        archetype_title = "The Capstone Sprinter"
        archetype_tagline = "Final-phase senior with solid academic momentum, actively finalizing major electives and degree clearance."
        archetype_badge = "success"
        archetype_icon = "fas fa-flag-checkered"
        risk_level = "LOW"
        risk_score = 15
    elif current_gpa >= 80.0:
        archetype_key = 'high_achiever'
        archetype_title = "The Dean's List Pacesetter"
        archetype_tagline = "Exemplary high-achiever with consistent honors marks, strong conceptual mastery, and uninterrupted course flow."
        archetype_badge = "primary"
        archetype_icon = "fas fa-award"
        risk_level = "MINIMAL"
        risk_score = 8
    elif completed_credits < 30 or num_graded_terms <= 2:
        archetype_key = 'foundation_transitioner'
        archetype_title = "The Early-Career Transitioner"
        archetype_tagline = "Freshman/Sophomore establishing university study habits and adapting to departmental course pacing."
        archetype_badge = "info text-dark"
        archetype_icon = "fas fa-seedling"
        risk_level = "LOW TO MODERATE"
        risk_score = 35
    else:
        archetype_key = 'steady_builder'
        archetype_title = "The Methodical Builder"
        archetype_tagline = "Dependable, steady student progressing systematically through the curriculum without major academic friction."
        archetype_badge = "secondary"
        archetype_icon = "fas fa-layer-group"
        risk_level = "LOW"
        risk_score = 25

    # -------------------------------------------------------------
    # 2. STRENGTHS & WEAKNESSES DIAGNOSTICS
    # -------------------------------------------------------------
    strengths = []
    weaknesses = []

    # Sort disciplines by performance
    active_disciplines = [
        d for d in discipline_stats.values() 
        if d['attempts'] > 0 and d['key'] != 'OTHER'
    ]
    active_disciplines.sort(key=lambda x: (x.get('avg_score') or 0), reverse=True)

    if active_disciplines:
        best_disc = active_disciplines[0]
        if (best_disc.get('avg_score') or 0) >= 70.0 or best_disc['pass_rate'] >= 85:
            strengths.append({
                'category': best_disc['title'],
                'icon': best_disc['icon'],
                'text': f"High Aptitude in {best_disc['title']}: Achieved {best_disc['pass_rate']}% pass rate with an average mark of {best_disc['avg_score'] or 'Pass'}% across {best_disc['attempts']} attempted courses."
            })

    # Check for general education strength
    gened = discipline_stats.get('GENED')
    if gened and gened['attempts'] >= 2 and gened['pass_rate'] >= 90:
        strengths.append({
            'category': 'General Education & Communication',
            'icon': 'fas fa-comments',
            'text': f"Strong Foundation in Humanities & Language: Flawless pass rate ({gened['pass_rate']}%) across DU university requirements."
        })

    # Check credit accumulation pace
    if num_graded_terms > 0:
        avg_credits_per_term = round(completed_credits / max(1, num_graded_terms), 1)
        if avg_credits_per_term >= 15.0 and current_gpa >= 65.0:
            strengths.append({
                'category': 'Pacing & Endurance',
                'icon': 'fas fa-tachometer-alt',
                'text': f"High Credit Velocity: Maintains a brisk pace of {avg_credits_per_term} credits/term without falling behind schedule."
            })

    # Check for zero course withdrawals
    withdrawn_courses_count = sum(
        1 for sem in raw_semesters 
        for c in sem.get('courses', []) 
        if any(str(c.get('grade', '')).upper().startswith(x) for x in ['W', 'WA', 'WF'])
    )
    if withdrawn_courses_count == 0 and completed_credits >= 30:
        strengths.append({
            'category': 'Course Persistence',
            'icon': 'fas fa-check-circle',
            'text': "Exceptional Retention: Zero course withdrawals (W/WA/WF) recorded across all enrolled semesters."
        })
    elif withdrawn_courses_count > 0:
        weaknesses.append({
            'category': 'Course Withdrawals / Attendance',
            'icon': 'fas fa-sign-out-alt',
            'text': f"Recorded {withdrawn_courses_count} course withdrawal(s) (W/WA/WF), signaling mid-term attendance drops or exam drop-outs."
        })

    # Check for discipline struggles
    struggling_disciplines = [
        d for d in active_disciplines 
        if d['failed'] > 0 or (d.get('avg_score') is not None and d['avg_score'] < 65.0)
    ]
    for sd in struggling_disciplines[:2]:
        weaknesses.append({
            'category': sd['title'],
            'icon': sd['icon'],
            'text': f"Academic Resistance in {sd['title']}: Encountered {sd['failed']} failed attempt(s) with an average mark of {sd['avg_score'] or 'N/A'}%."
        })

    # Check for critical repeat bottlenecks
    if critical_repeats:
        crit_codes = ", ".join(c['code'] for c in critical_repeats[:3])
        weaknesses.append({
            'category': 'Prerequisite Blockers',
            'icon': 'fas fa-exclamation-triangle',
            'text': f"Unresolved Mandatory Repeats: Currently blocked by {len(critical_repeats)} failed course(s) ({crit_codes}) weighing down cumulative standing."
        })

    # Check for GPA deficit
    if audit['gpa_deficit'] > 0:
        weaknesses.append({
            'category': 'Cumulative Standing Deficit',
            'icon': 'fas fa-balance-scale',
            'text': f"Cumulative GPA is {audit['gpa_deficit']} points below the mandatory 65.0% Good Standing mark (Article 14)."
        })

    # Ensure fallback if empty
    if not strengths:
        strengths.append({
            'category': 'Active Enrollment',
            'icon': 'fas fa-user-check',
            'text': f"Active student with {completed_credits} completed credit hours towards the {audit['program_title']} degree."
        })
    if not weaknesses:
        weaknesses.append({
            'category': 'Advanced Challenge',
            'icon': 'fas fa-info-circle',
            'text': "No structural academic deficiencies detected. Maintain diligence in upper-level technical electives."
        })

    # -------------------------------------------------------------
    # 3. BEHAVIORAL PROFILE: "WHAT THE STUDENT DOES"
    # -------------------------------------------------------------
    what_the_student_does = []

    # Behavioral Point 1: Registration Load Habit
    if credit_cap == 12:
        what_the_student_does.append(
            "Enrolls under probation restrictions capped at 12 credit hours, creating a lower course volume but requiring maximum focus."
        )
    elif completed_credits > 0 and num_graded_terms > 0:
        pace = round(completed_credits / num_graded_terms, 1)
        if pace >= 15:
            what_the_student_does.append(
                f"Consistently registers for full-time heavy course loads ({pace} credits/semester), prioritizing fast degree completion."
            )
        else:
            what_the_student_does.append(
                f"Prefers moderate course loads averaging {pace} credits/semester, pacing out credit completion steadily."
            )

    # Behavioral Point 2: Course Selection Pattern
    if len(audit['critical_repeats']) > 0:
        what_the_student_does.append(
            "Tends to bypass repeated courses in favor of taking new general requirements, which inadvertently locks prerequisite progression."
        )
    elif len(audit['ready_courses']) > len(audit['blocked_courses']):
        what_the_student_does.append(
            "Adheres closely to prerequisite sequencing, successfully opening up the majority of downstream curriculum electives."
        )

    # Behavioral Point 3: Trajectory & Recovery Response
    if recent_trend == 'Improving':
        what_the_student_does.append(
            f"Demonstrated positive academic responsiveness in the latest semester ({progression.get('latest_term_gpa', '')}%), showing strong rebound potential."
        )
    elif recent_trend == 'Declining':
        what_the_student_does.append(
            "Experienced grade erosion over the past two terms, often due to taking multiple challenging quantitative courses concurrently."
        )
    else:
        what_the_student_does.append(
            "Maintains consistent and stable semester performance with minimal variance across academic terms."
        )

    # -------------------------------------------------------------
    # 4. ACTION MANDATES: "WHAT THE STUDENT MUST DO"
    # -------------------------------------------------------------
    what_the_student_must_do = []

    # Mandate 1: Course Repeats & Prerequisite Unlocking
    if critical_repeats:
        primary_repeat = critical_repeats[0]['code']
        what_the_student_must_do.append({
            'priority': 'URGENT',
            'action': f"Register for {primary_repeat} in the immediate upcoming term without exception.",
            'rationale': f"Under DU Article 18, repeating {primary_repeat} replaces the failing score, directly boosting CGPA and unlocking blocked courses.",
            'badge': 'danger'
        })
    elif low_repeats and is_under_probation:
        low_c = low_repeats[0]['code']
        what_the_student_must_do.append({
            'priority': 'RECOMMENDED',
            'action': f"Repeat {low_c} (Grade: {low_repeats[0]['grade']}) to elevate CGPA.",
            'rationale': "Article 18 permits repeating D/D+ grades to replace them with higher marks, accelerating probation removal.",
            'badge': 'warning text-dark'
        })
    else:
        top_ready = audit['ready_courses'][0]['code'] if audit['ready_courses'] else 'next major requirement'
        what_the_student_must_do.append({
            'priority': 'CORE REQUIREMENT',
            'action': f"Enroll in {top_ready} as the cornerstone course for the upcoming semester.",
            'rationale': "Prerequisites are fully satisfied; maintaining core sequence ensures on-time graduation.",
            'badge': 'primary'
        })

    # Mandate 2: Credit Cap & Schedule Balancing
    if credit_cap == 12:
        what_the_student_must_do.append({
            'priority': 'MANDATORY RULE',
            'action': "Strictly enforce the 12 credit hour ceiling (DU Article 22).",
            'rationale': "Taking more than 12 credits while on academic warning is prohibited by university bylaws and dilutes study focus.",
            'badge': 'danger'
        })
    else:
        what_the_student_must_do.append({
            'priority': 'SCHEDULE DESIGN',
            'action': "Balance schedule with maximum 2 heavy quantitative courses + 2-3 applied or general requirements.",
            'rationale': "Prevents cognitive overload during midterm and final examination periods.",
            'badge': 'info text-dark'
        })

    # Mandate 3: Department Tutorial Lab Commitment
    if has_critical_repeats or is_under_probation:
        what_the_student_must_do.append({
            'priority': 'ACADEMIC SUPPORT',
            'action': "Commit to 4 to 6 hours weekly at Department Mathematics & Programming Tutorial Labs.",
            'rationale': "Structured peer tutoring and faculty lab hours prevent falling behind before Week 6 assessments.",
            'badge': 'warning text-dark'
        })
    else:
        what_the_student_must_do.append({
            'priority': 'ENRICHMENT',
            'action': "Engage in Department workshop sessions, hackathons, and undergraduate research opportunities.",
            'rationale': "Enhances practical portfolio readiness for internship and capstone clearance.",
            'badge': 'success'
        })

    # Mandate 4: Midterm Review & Article 24 Safety Net
    what_the_student_must_do.append({
        'priority': 'POLICY SAFEGUARD',
        'action': "Conduct mandatory Week 7 Midterm Progress Review with Dr. Nasser Tabook.",
        'rationale': "If any course grade falls below 60% by Week 9, evaluate the official Withdrawal (W) option before the Week 10 deadline to prevent failing grades.",
        'badge': 'secondary'
    })

    # -------------------------------------------------------------
    # 5. STRATEGIC DEGREE HORIZON & PLANNING
    # -------------------------------------------------------------
    est_semesters = audit['semesters_remaining']
    cur_year = student.year or 'Undergraduate'
    
    # Estimate projected graduation term
    if est_semesters <= 1:
        projected_grad = "Upcoming Semester (Degree Clearance Phase)"
        degree_phase = "Final Graduation Clearance"
    elif est_semesters <= 2:
        projected_grad = "Next Academic Year (Senior Phase)"
        degree_phase = "Upper-Division Capstone & Senior Electives"
    elif est_semesters <= 4:
        projected_grad = f"Within ~{est_semesters} Semesters (Junior Phase)"
        degree_phase = "Core Major Specialization"
    else:
        projected_grad = f"Within ~{est_semesters} Semesters"
        degree_phase = "Foundation & Intermediate Core"

    roadmap = {
        'current_phase': degree_phase,
        'completed_credits': completed_credits,
        'remaining_credits': remaining_credits,
        'total_credits': audit['total_plan_credits'],
        'completion_pct': completion_pct,
        'semesters_remaining': est_semesters,
        'projected_graduation': projected_grad,
        'recommended_credit_load': credit_cap,
        'target_semester_gpa': 75.0 if is_under_probation else (80.0 if current_gpa >= 75 else 70.0)
    }

    # -------------------------------------------------------------
    # 6. ADVISOR CONSULTATION PROTOCOL FOR DR. NASSER TABOOK
    # -------------------------------------------------------------
    if archetype_key in ['high_risk_probation', 'probation_struggler']:
        advisor_tone = "Firm, direct, and structured with non-negotiable prerequisite guardrails."
        meeting_cadence = "Mandatory Bi-Weekly check-in (Weeks 2, 4, 7, 10)"
        opening_statement = f"Hello {student.name}, our priority is strictly safeguarding your enrollment status. Let us review your 12-credit recovery schedule and lab attendance agreement."
        suggested_questions = [
            f"What specific hurdles caused you difficulty in {critical_repeats[0]['code'] if critical_repeats else 'previous terms'}?",
            "How many hours each day do you allocate to study outside of scheduled class hours?",
            "Can you commit to attending the tutorial labs every Tuesday and Thursday afternoon?"
        ]
    elif archetype_key == 'probation_fighter':
        advisor_tone = "Encouraging, momentum-building, and accountability-oriented."
        meeting_cadence = "Tri-weekly check-in (Weeks 3, 7, 10)"
        opening_statement = f"Welcome {student.name}! Your progress last term proved you have the capability to clear probation. We are here to lock in that success this term."
        suggested_questions = [
            "What study routines worked best for you during your improvement last semester?",
            "Are there any courses this term where you feel quiz scores might dip below 70%?",
            "Have you reviewed the grade replacement points calculation under DU Article 18?"
        ]
    elif archetype_key == 'prereq_bottleneck':
        advisor_tone = "Diagnostic, problem-solving, and curriculum-focused."
        meeting_cadence = "Pre-registration review + Week 7 midterm check-in"
        opening_statement = f"Hello {student.name}, you are doing well in your broader courses, but we need to solve the bottleneck in {critical_repeats[0]['code'] if critical_repeats else 'core math'} so your upper-level courses unlock."
        suggested_questions = [
            f"Where exactly does the gap emerge when studying {critical_repeats[0]['code'] if critical_repeats else 'this course'} (lectures, assignments, or exam timing)?",
            "Would pairing this course with lighter electives give you the study bandwidth you need?",
            "Are you working with a study partner or attending the Department instructor office hours?"
        ]
    elif archetype_key == 'high_achiever':
        advisor_tone = "Mentoring, acceleration-oriented, and aspirational."
        meeting_cadence = "Semester kickoff & Capstone/Internship guidance"
        opening_statement = f"Great to see you {student.name}. Your academic trajectory is outstanding. Let us talk about research, internships, and maximizing your honors portfolio."
        suggested_questions = [
            "Are you interested in undergraduate research or participating in regional student competitions?",
            "Have you started exploring industry internship opportunities for the upcoming summer?",
            "How can the Department support your postgraduate or career placement goals?"
        ]
    else:
        advisor_tone = "Supportive, methodical, and degree-progress oriented."
        meeting_cadence = "Regular pre-registration window + Week 7 Midterm check-in"
        opening_statement = f"Welcome {student.name}. Let us review your study plan progress to ensure your next term registration keeps you on the smoothest track to graduation."
        suggested_questions = [
            "How do you feel about your course balance this semester?",
            "Are there specific major electives you are most enthusiastic about taking next year?",
            "Do your current class schedules align well with your transportation and personal routine?"
        ]

    advisor_brief = {
        'tone': advisor_tone,
        'cadence': meeting_cadence,
        'opening_statement': opening_statement,
        'suggested_questions': suggested_questions
    }

    return {
        'student': student,
        'archetype': {
            'key': archetype_key,
            'title': archetype_title,
            'tagline': archetype_tagline,
            'badge': archetype_badge,
            'icon': archetype_icon,
            'risk_level': risk_level,
            'risk_score': risk_score
        },
        'strengths': strengths,
        'weaknesses': weaknesses,
        'discipline_stats': discipline_stats,
        'what_the_student_does': what_the_student_does,
        'what_the_student_must_do': what_the_student_must_do,
        'roadmap': roadmap,
        'advisor_brief': advisor_brief,
        'audit': audit,
        'progression': progression
    }
