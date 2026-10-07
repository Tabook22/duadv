"""
Academic Advising & Degree Audit Intelligence Engine for Dhofar University
Performs deep transcript audit, prerequisite checking, study plan gap analysis,
and generates policy-referenced advising action plans.
"""

import os
import re
import math
from typing import Dict, List, Any, Optional
from app.models import Student
from app.utils import load_students_from_file, get_student_semesters
from app.study_plans_registry import resolve_study_plan

def normalize_course_code(code: str) -> str:
    """Normalize course codes (e.g., 'CMPS 110N' -> 'CMPS110N')"""
    if not code:
        return ""
    return re.sub(r'\s+', '', code).upper()

def is_grade_passing(grade_str: Any) -> bool:
    """Determine if a transcript grade is considered passing (>= 60 or P)"""
    if grade_str is None:
        return False
    g_s = str(grade_str).strip().upper()
    
    # Check for withdraw / incomplete / fail symbols
    if any(g_s.startswith(x) for x in ['WA', 'WF', 'W', 'F', 'I', 'IP', 'NP', 'AUD']):
        # If it's pure 'F' or 'WA' or 'WF'
        if g_s in ['F', 'WA', 'WF', 'I', 'IP', 'NP', 'AUD', 'FIRST FAIL', 'FAIL']:
            return False
        
    # Check for repeat notation e.g. '60 (R:2)' or '75'
    m = re.search(r'(\d+(?:\.\d+)?)', g_s)
    if m:
        try:
            val = float(m.group(1))
            return val >= 60.0
        except ValueError:
            pass
            
    if g_s in ['P', 'CR', 'PASS']:
        return True
            
    # Letter grades
    if any(letter in g_s for letter in ['A', 'B', 'C', 'D']):
        return True
        
    return False

def extract_numerical_grade(grade_str: Any) -> Optional[float]:
    """Extract numeric score from grade string"""
    if grade_str is None:
        return None
    m = re.search(r'(\d+(?:\.\d+)?)', str(grade_str))
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return None

def audit_student_degree(student_id: str, transcripts_dir: str = None) -> Dict[str, Any]:
    """
    Perform deep degree audit for a student:
    - Match historical courses against the official study plan.
    - Identify completed, missing, failed, and low-grade repeat courses.
    - Check prerequisite readiness for missing courses.
    - Calculate credit limits and GPA recovery targets according to DU regulations.
    """
    students = load_students_from_file()
    student = next((s for s in students if s.id == student_id), None)
    if not student:
        raise ValueError(f"Student with ID '{student_id}' not found.")
        
    plan = resolve_study_plan(student.program)
    curriculum = plan["curriculum"]
    semesters = get_student_semesters(student.id, transcripts_dir)
    
    # 1. Parse historical course attempts
    courses_history: Dict[str, List[Dict[str, Any]]] = {}
    for sem in semesters:
        for c in sem.get('courses', []):
            code_raw = c['code'].strip()
            code_norm = normalize_course_code(code_raw)
            grade_raw = c.get('grade')
            credits_val = int(c.get('credits', 3))
            is_pass = is_grade_passing(grade_raw)
            score = extract_numerical_grade(grade_raw)
            
            entry = {
                'raw_code': code_raw,
                'name': c.get('name', ''),
                'term': sem.get('term', ''),
                'season': sem.get('season', ''),
                'credits': credits_val,
                'grade': grade_raw,
                'score': score,
                'is_passed': is_pass
            }
            if code_norm not in courses_history:
                courses_history[code_norm] = []
            courses_history[code_norm].append(entry)
            
    # Determine best passed status for each course
    passed_course_codes = set()
    best_attempts = {}
    
    for code_norm, attempts in courses_history.items():
        passed_attempts = [a for a in attempts if a['is_passed']]
        if passed_attempts:
            passed_course_codes.add(code_norm)
            # Pick highest score
            best_attempts[code_norm] = max(passed_attempts, key=lambda x: (x['score'] if x['score'] is not None else 60))
        else:
            best_attempts[code_norm] = attempts[-1]
            
    # 2. Match with Curriculum
    completed_courses = []
    missing_courses = []
    category_summary: Dict[str, Dict[str, int]] = {}
    
    for req in curriculum:
        c_norm = normalize_course_code(req['code'])
        cat = req.get('category', 'Major Core')
        if cat not in category_summary:
            category_summary[cat] = {'required_credits': 0, 'completed_credits': 0, 'required_count': 0, 'completed_count': 0}
        category_summary[cat]['required_credits'] += req['credits']
        category_summary[cat]['required_count'] += 1
        
        # Flexible code matching for equivalents
        matched_norm = None
        if c_norm in passed_course_codes:
            matched_norm = c_norm
        elif c_norm.endswith('N') and c_norm[:-1] in passed_course_codes:
            matched_norm = c_norm[:-1]
        elif (c_norm + 'N') in passed_course_codes:
            matched_norm = c_norm + 'N'
            
        if matched_norm:
            att = best_attempts.get(matched_norm, {})
            completed_courses.append({
                'code': req['code'],
                'name': req['name'],
                'credits': req['credits'],
                'category': cat,
                'term_recommended': req.get('term_recommended', ''),
                'grade': att.get('grade'),
                'score': att.get('score'),
                'term_taken': att.get('term')
            })
            category_summary[cat]['completed_credits'] += req['credits']
            category_summary[cat]['completed_count'] += 1
        else:
            # Prerequisite readiness check
            prereqs = req.get('prerequisites', [])
            unmet_prereqs = []
            for pr in prereqs:
                pr_norm = normalize_course_code(pr)
                pr_met = (
                    pr_norm in passed_course_codes or 
                    (pr_norm.endswith('N') and pr_norm[:-1] in passed_course_codes) or 
                    ((pr_norm + 'N') in passed_course_codes)
                )
                if not pr_met:
                    unmet_prereqs.append(pr)
                    
            ready = (len(unmet_prereqs) == 0)
            missing_courses.append({
                'code': req['code'],
                'name': req['name'],
                'credits': req['credits'],
                'category': cat,
                'term_recommended': req.get('term_recommended', ''),
                'prerequisites': prereqs,
                'unmet_prerequisites': unmet_prereqs,
                'is_ready_to_register': ready
            })
            
    # 3. Identify Deficiencies & Repeat Candidates (DU Article 18)
    critical_repeats = []   # Failed courses (< 60, F, WA) that are required
    low_grade_repeats = []  # Passed with D/D+ (60-64%) where CGPA < 65%
    
    current_gpa = student.gpa or 0.0
    is_under_probation = ('Probation' in (student.status or '') and 'Removal' not in (student.status or '')) or (current_gpa < 65.0)
    
    for code_norm, attempts in courses_history.items():
        latest = attempts[-1]
        raw_c = latest['raw_code']
        
        # Skip Foundation Program courses (FPE, FPM, FPT) or 0 credit items
        if raw_c.startswith(('FP', 'FPE', 'FPM', 'FPT')) or latest.get('credits', 0) == 0:
            continue
            
        # Check if course has ever been passed
        is_ever_passed = (
            code_norm in passed_course_codes or 
            (code_norm.endswith('N') and code_norm[:-1] in passed_course_codes) or 
            ((code_norm + 'N') in passed_course_codes)
        )
        
        if not is_ever_passed:
            in_curriculum = any(
                normalize_course_code(r['code']) == code_norm or 
                normalize_course_code(r['code']) == code_norm + 'N' or 
                normalize_course_code(r['code']) == code_norm[:-1] 
                for r in curriculum
            )
            critical_repeats.append({
                'code': latest['raw_code'],
                'name': latest['name'],
                'credits': latest['credits'] or 3,
                'last_grade': latest['grade'],
                'last_score': latest['score'],
                'last_term': latest['term'],
                'in_curriculum': in_curriculum,
                'attempts_count': len(attempts),
                'reason': 'Mandatory Repeat: Course attempted and not passed. Blocks prerequisites and hurts CGPA.'
            })
        else:
            # Course was passed, but check for low score (60-64%) under probation
            if is_under_probation and latest.get('score') is not None and 60 <= latest['score'] < 65:
                low_grade_repeats.append({
                    'code': latest['raw_code'],
                    'name': latest['name'],
                    'credits': latest['credits'],
                    'grade': latest['grade'],
                    'score': latest['score'],
                    'term': latest['term'],
                    'reason': 'Recommended Repeat: Grade is D/D+ (60-64%). Article 18 allows replacing with higher grade to lift GPA >= 65%'
                })
                
    # Sort ready missing courses by recommended term order
    def _term_sort_key(item):
        t = item.get('term_recommended', '')
        val = 9.9
        if 'Year 1' in t: val = 1.0 + (0.1 if 'Spring' in t else 0.0)
        elif 'Year 2' in t: val = 2.0 + (0.1 if 'Spring' in t else 0.0)
        elif 'Year 3' in t: val = 3.0 + (0.1 if 'Spring' in t else 0.0)
        elif 'Year 4' in t: val = 4.0 + (0.1 if 'Spring' in t else 0.0)
        return val

    ready_courses = [c for c in missing_courses if c['is_ready_to_register']]
    ready_courses.sort(key=_term_sort_key)
    
    blocked_courses = [c for c in missing_courses if not c['is_ready_to_register']]
    blocked_courses.sort(key=_term_sort_key)
    
    # 4. Credit & Standing Metrics
    total_plan_credits = plan["total_credits"]
    completed_credits = student.credits if student.credits is not None else sum(c['credits'] for c in completed_courses)
    remaining_credits = max(0, total_plan_credits - completed_credits)
    completion_pct = min(100.0, round((completed_credits / total_plan_credits) * 100, 1)) if total_plan_credits > 0 else 0
    
    # Registration Credit Cap (Article 22)
    st = student.status or ''
    if 'Strict' in st or 'Third' in st or 'Second Probation' in st or 'First Probation' in st or ('Probation' in st and 'Removal' not in st):
        credit_cap = 12
        cap_reason = 'Academic Probation Cap: Maximum 12 Credit Hours (Dhofar University Academic Regulations Article 14 & 22)'
    elif current_gpa > 0 and current_gpa < 65.0 and 'Removal' not in st and 'Good' not in st:
        credit_cap = 12
        cap_reason = 'Pre-Probation Warning Cap: Advised max 12 Credit Hours to recover CGPA >= 65.0%'
    else:
        credit_cap = 18
        cap_reason = 'Normal Full-Time Course Load: 15 to 18 Credit Hours (Dhofar University Academic Regulations Article 22)'
        
    gpa_deficit = max(0.0, round(65.0 - current_gpa, 2)) if current_gpa > 0 else 0.0
    semesters_remaining = math.ceil(remaining_credits / (12 if credit_cap == 12 else 15)) if remaining_credits > 0 else 0
    
    return {
        'student': student,
        'program_title': plan['program_title'],
        'degree_type': plan['degree_type'],
        'bridge_info': plan.get('bridge_to_bachelor'),
        'total_plan_credits': total_plan_credits,
        'completed_credits': completed_credits,
        'remaining_credits': remaining_credits,
        'completion_percentage': completion_pct,
        'current_gpa': current_gpa,
        'cgpa': student.cgpa if student.cgpa is not None else current_gpa,
        'semester_gpa': student.semester_gpa,
        'gpa_deficit': gpa_deficit,
        'is_under_probation': is_under_probation,
        'credit_cap': credit_cap,
        'credit_cap_reason': cap_reason,
        'semesters_remaining': semesters_remaining,
        'completed_courses': completed_courses,
        'missing_courses': missing_courses,
        'ready_courses': ready_courses,
        'blocked_courses': blocked_courses,
        'critical_repeats': critical_repeats,
        'low_grade_repeats': low_grade_repeats,
        'category_summary': category_summary
    }


def analyze_semester_progression(student_id: str) -> Dict[str, Any]:
    """
    Analyze student semester-by-semester trajectory, compute term & cumulative deltas,
    diagnose root causes for improvements or declines, and structure Chart.js dataset.
    """
    raw_semesters = get_student_semesters(student_id)
    
    # Filter to credit-bearing or graded terms
    graded_semesters = []
    for s in raw_semesters:
        has_graded_course = any(
            not c['code'].startswith(('FP', 'FPE', 'FPM', 'FPT')) and 
            c.get('credits', 0) > 0 
            for c in s.get('courses', [])
        )
        cum_gpa = s.get('cumulative_gpa')
        sem_gpa = s.get('semester_gpa')
        
        if has_graded_course or (cum_gpa and cum_gpa > 0):
            graded_semesters.append(s)
            
    if not graded_semesters:
        graded_semesters = raw_semesters
        
    term_records = []
    prev_term_gpa = None
    prev_cum_gpa = None
    
    for idx, s in enumerate(graded_semesters):
        t_name = s['term']
        chart_label = re.sub(r'\(Year \d\)', '', t_name).strip()
        
        sem_gpa = s.get('semester_gpa')
        cum_gpa = s.get('cumulative_gpa')
        standing = s.get('standing', 'Normal / Good Standing')
        courses = s.get('courses', [])
        
        passed_courses = []
        failed_courses = []
        withdrawn_courses = []
        repeated_courses = []
        
        for c in courses:
            c_code = c['code']
            c_grade = str(c.get('grade', '')).strip()
            c_score = c.get('score')
            c_credits = c.get('credits', 0)
            
            if any(c_grade.upper().startswith(x) for x in ['WA', 'WF', 'W']):
                withdrawn_courses.append({
                    'code': c_code,
                    'name': c['name'],
                    'grade': c_grade,
                    'credits': c_credits
                })
            elif is_grade_passing(c_grade):
                passed_courses.append({
                    'code': c_code,
                    'name': c['name'],
                    'grade': c_grade,
                    'score': c_score,
                    'credits': c_credits
                })
            else:
                failed_courses.append({
                    'code': c_code,
                    'name': c['name'],
                    'grade': c_grade,
                    'score': c_score,
                    'credits': c_credits
                })
                
            if '(R:' in c_grade or 'R:' in c_grade:
                repeated_courses.append({
                    'code': c_code,
                    'name': c['name'],
                    'grade': c_grade
                })
                
        delta_sem = None
        delta_cum = None
        if prev_term_gpa is not None and sem_gpa is not None:
            delta_sem = round(sem_gpa - prev_term_gpa, 2)
        if prev_cum_gpa is not None and cum_gpa is not None:
            delta_cum = round(cum_gpa - prev_cum_gpa, 2)
            
        if idx == 0:
            status = "INITIAL"
        elif delta_cum is not None and delta_cum > 1.0:
            status = "IMPROVED"
        elif delta_cum is not None and delta_cum < -1.0:
            status = "DECLINED"
        else:
            status = "STABLE"
            
        reasons = []
        if status == "INITIAL":
            if cum_gpa and cum_gpa >= 65.0:
                reasons.append(f"Initial academic baseline established at {cum_gpa:.2f}% (Good Standing). Successfully completed {len(passed_courses)} course(s).")
            elif cum_gpa:
                failed_str = ", ".join(c['code'] for c in failed_courses) or "unresolved courses"
                reasons.append(f"Initial credit-bearing term resulted in academic jeopardy ({cum_gpa:.2f}%). Deficits incurred in {failed_str}.")
            else:
                reasons.append("Foundation assessment period.")
        elif status == "IMPROVED":
            gain_str = f"+{delta_cum:.2f}%" if delta_cum else ""
            pass_str = ", ".join(f"{c['code']} ({c['grade']})" for c in passed_courses[:3])
            reasons.append(f"Cumulative average rebounded by {gain_str} points.")
            if pass_str:
                reasons.append(f"Key drivers: Strong performance in {pass_str}.")
            if repeated_courses:
                rep_str = ", ".join(c['code'] for c in repeated_courses)
                reasons.append(f"Grade replacement benefit realized from repeating {rep_str} under DU Article 18.")
            if failed_courses:
                fail_str = ", ".join(c['code'] for c in failed_courses)
                reasons.append(f"Note: Lingering deficiencies remain in {fail_str}.")
        elif status == "DECLINED":
            loss_str = f"{delta_cum:.2f}%" if delta_cum else ""
            reasons.append(f"Performance experienced a downward decline of {loss_str} points.")
            if failed_courses:
                fail_str = ", ".join(f"{c['code']} ({c['grade']})" for c in failed_courses)
                reasons.append(f"Primary impediment: Course failure(s) in {fail_str}.")
            if withdrawn_courses:
                w_str = ", ".join(f"{c['code']} ({c['grade']})" for c in withdrawn_courses)
                reasons.append(f"Course disruption due to withdrawal(s) in {w_str}.")
            if len(courses) > 4:
                reasons.append(f"High credit burden ({s['total_credits']} credits attempted) exacerbated academic strain.")
        else:
            reasons.append("Academic performance remained essentially unchanged.")
            if cum_gpa and cum_gpa < 65.0:
                reasons.append(f"Marginal course passes prevented lifting CGPA out of the probation zone.")
            else:
                reasons.append(f"Consistent performance maintained in Good Standing.")
                
        diagnosis_text = " ".join(reasons)
        
        term_records.append({
            'term': t_name,
            'chart_label': chart_label,
            'semester_gpa': sem_gpa,
            'cumulative_gpa': cum_gpa,
            'delta_semester_gpa': delta_sem,
            'delta_cumulative_gpa': delta_cum,
            'standing': standing,
            'status': status,
            'total_credits': s.get('total_credits', 0),
            'courses_count': len(courses),
            'passed_count': len(passed_courses),
            'failed_count': len(failed_courses),
            'withdrawn_count': len(withdrawn_courses),
            'passed_courses': passed_courses,
            'failed_courses': failed_courses,
            'withdrawn_courses': withdrawn_courses,
            'repeated_courses': repeated_courses,
            'root_cause_explanation': diagnosis_text
        })
        
        if sem_gpa is not None:
            prev_term_gpa = sem_gpa
        if cum_gpa is not None:
            prev_cum_gpa = cum_gpa
            
    all_cum_gpas = [r['cumulative_gpa'] for r in term_records if r['cumulative_gpa'] is not None and r['cumulative_gpa'] > 0]
    highest_gpa = max(all_cum_gpas) if all_cum_gpas else 0.0
    lowest_gpa = min(all_cum_gpas) if all_cum_gpas else 0.0
    latest_record = term_records[-1] if term_records else None
    
    if len(all_cum_gpas) >= 2:
        if all_cum_gpas[-1] > all_cum_gpas[0] and (all_cum_gpas[-1] - all_cum_gpas[-2] >= 0):
            overall_trend = "Upward / Improving Trajectory"
            trend_badge = "success"
        elif all_cum_gpas[-1] < all_cum_gpas[-2]:
            overall_trend = "Downward / At-Risk Trajectory"
            trend_badge = "danger"
        else:
            overall_trend = "Fluctuating / Variable"
            trend_badge = "warning"
    else:
        overall_trend = "Initial Academic Baseline"
        trend_badge = "info"
        
    chart_data = {
        'labels': [r['chart_label'] for r in term_records],
        'term_gpas': [r['semester_gpa'] if r['semester_gpa'] is not None and r['semester_gpa'] > 0 else None for r in term_records],
        'cum_gpas': [r['cumulative_gpa'] if r['cumulative_gpa'] is not None and r['cumulative_gpa'] > 0 else None for r in term_records],
        'benchmark': 65.0,
        'standings': [r['standing'] for r in term_records]
    }
    
    return {
        'student_id': student_id,
        'terms': term_records,
        'chart_data': chart_data,
        'overall_trend': overall_trend,
        'trend_badge': trend_badge,
        'highest_gpa': round(highest_gpa, 2),
        'lowest_gpa': round(lowest_gpa, 2),
        'latest_record': latest_record
    }

def calculate_gpa_recovery_path(audit: Dict[str, Any], student: Student) -> Dict[str, Any]:
    """
    Simulate the mathematical impact of repeating courses under DU Article 18 (Grade Replacement).
    Calculates points needed and projected CGPA at 70%, 75%, and 80% repeat target marks.
    """
    current_gpa = audit['current_gpa'] or 0.0
    completed_credits = max(audit['completed_credits'], 3)
    deficit = audit['gpa_deficit']
    
    repeat_items = []
    total_potential_gain = 0.0
    
    for cr in audit['critical_repeats']:
        c_code = cr['code']
        old_score = extract_numerical_grade(cr['last_grade']) or 40.0
        credits = cr.get('credits') or 3
        
        gain_at_75 = (75.0 - old_score) * credits / completed_credits
        gain_at_80 = (80.0 - old_score) * credits / completed_credits
        
        repeat_items.append({
            'code': c_code,
            'name': cr['name'],
            'credits': credits,
            'old_grade': cr['last_grade'],
            'old_score': old_score,
            'projected_gain_75': round(gain_at_75, 2),
            'projected_gain_80': round(gain_at_80, 2),
            'priority': 'Critical Mandatory Repeat'
        })
        total_potential_gain += gain_at_75
        
    for lr in audit['low_grade_repeats']:
        c_code = lr['code']
        old_score = extract_numerical_grade(lr['grade']) or 60.0
        credits = lr.get('credits') or 3
        gain_at_75 = (75.0 - old_score) * credits / completed_credits
        gain_at_80 = (80.0 - old_score) * credits / completed_credits
        
        repeat_items.append({
            'code': c_code,
            'name': lr['name'],
            'credits': credits,
            'old_grade': lr['grade'],
            'old_score': old_score,
            'projected_gain_75': round(gain_at_75, 2),
            'projected_gain_80': round(gain_at_80, 2),
            'priority': 'Recommended D-Grade Repeat'
        })
        total_potential_gain += gain_at_75
        
    projected_cgpa_75 = round(min(100.0, current_gpa + total_potential_gain), 2)
    recovers_good_standing = projected_cgpa_75 >= 65.0
    
    action_steps = [
        f"Strictly prioritize repeating failed prerequisite courses ({', '.join(c['code'] for c in audit['critical_repeats'][:3]) or 'core courses'}).",
        "Target minimum 70-75% in repeated courses to trigger the DU Article 18 grade replacement multiplier.",
        "Observe the 12 credit hour probation limit (DU Article 22) to avoid overburdening your schedule.",
        "Dedicate minimum 6 hours/week to Department tutorial labs for programming and calculus.",
        "Track quiz and continuous assessment marks weekly to ensure grades stay above 65% before the Week 10 withdrawal (W) deadline."
    ]
    
    return {
        'current_gpa': current_gpa,
        'deficit_points': deficit,
        'repeat_items': repeat_items,
        'total_potential_gain': round(total_potential_gain, 2),
        'projected_cgpa_at_75': projected_cgpa_75,
        'recovers_good_standing': recovers_good_standing,
        'action_steps': action_steps
    }

def generate_advisor_consultation_guide(
    student: Student,
    audit: Dict[str, Any],
    progression: Dict[str, Any],
    recovery: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate formal Advisor Consultation Protocol:
    Determines meeting urgency, consultation windows, exact talking points script for Dr. Nasser Tabook,
    and preparation guidelines for the student.
    """
    st = student.status or 'Normal / Good Standing'
    gpa = audit['current_gpa'] or 0.0
    deficit = audit['gpa_deficit']
    cap = audit['credit_cap']
    
    if 'Strict' in st or 'Third' in st:
        urgency = "CRITICAL & MANDATORY (Week 1 Priority)"
        urgency_badge = "danger"
        schedule_window = "Immediate - First 5 days of semester (Before Add/Drop closes)"
        frequency = "Weekly mandatory check-in with Academic Advisor"
    elif 'Second Probation' in st:
        urgency = "HIGH MANDATORY (Add/Drop Period)"
        urgency_badge = "warning text-dark"
        schedule_window = "Week 1 to Week 2 of classes"
        frequency = "Bi-weekly mandatory check-in with Academic Advisor"
    elif 'First Probation' in st:
        urgency = "MANDATORY (Academic Warning Review)"
        urgency_badge = "warning text-dark"
        schedule_window = "First 2 weeks of classes"
        frequency = "Bi-weekly progress check-ins with Academic Advisor"
    else:
        urgency = "RECOMMENDED (Regular Semester Check-in)"
        urgency_badge = "info text-dark"
        schedule_window = "Regular pre-registration advising window"
        frequency = "Midterm check-in (Week 7)"

    critical_codes = [c['code'] for c in audit['critical_repeats']]
    crit_text = ", ".join(critical_codes[:3]) if critical_codes else "your core curriculum courses"
    
    advisor_script = [
        {
            'phase': '1. Empathetic Welcome & Objective',
            'speaker': 'Academic Advisor (Dr. Nasser Tabook)',
            'dialogue': (
                f"Hello {student.name}, thank you for meeting with me today. I called you in because your academic success "
                f"and your degree progression are our top priority in the Department. My purpose today is not to reprimand you, "
                f"but to work together on an evidence-based Academic Recovery Plan that will lift your GPA and protect your standing at Dhofar University."
            )
        },
        {
            'phase': '2. Academic Reality Check & Bylaws',
            'speaker': 'Academic Advisor (Dr. Nasser Tabook)',
            'dialogue': (
                f"Let us examine your transcript with complete transparency. Your current cumulative GPA is **{gpa:.2f}%**, which is "
                f"**{deficit:.2f} points below our required 65.0% Good Standing threshold**, placing your status at **{st}**. "
                f"Under Dhofar University Article 14 and Article 22, this is a formal warning. Your course load is strictly capped at "
                f"**{cap} credit hours** this term. We cannot register for more than 12 credits, because another term below 65% will trigger severe probation escalation or dismissal."
            )
        },
        {
            'phase': '3. The Strategic Solution (DU Article 18 Grade Replacement)',
            'speaker': 'Academic Advisor (Dr. Nasser Tabook)',
            'dialogue': (
                f"Here is why your situation is completely recoverable: Under DU Article 18, when you repeat courses you previously failed "
                f"—specifically **{crit_text}**—your new grade directly replaces the old failing mark in your cumulative GPA! "
                f"Mathematically, scoring a 75% in these repeated courses will inject an estimated **+{recovery['total_potential_gain']:.2f}% directly into your CGPA**, "
                f"lifting you right back into Good Standing. Repeating these courses gives you twice the leverage of taking new courses."
            )
        },
        {
            'phase': '4. Operational Routine & Department Tutoring',
            'speaker': 'Academic Advisor (Dr. Nasser Tabook)',
            'dialogue': (
                f"To make this happen, we are locking your registration to these exact {audit['credit_cap']} credit hours. "
                f"You must commit to attending the Department tutorial labs for mathematics and programming every single week. "
                f"If you ever struggle with a concept or assignment, do not isolate yourself and do not wait for the final exam—come see me during office hours immediately."
            )
        },
        {
            'phase': '5. Milestones & The Action Plan Agreement',
            'speaker': 'Academic Advisor (Dr. Nasser Tabook)',
            'dialogue': (
                f"We will hold our mandatory midterm review right after Week 6. If any course grade is under 60% by Week 9, we will evaluate "
                f"the official Course Withdrawal (W) option before the Week 10 deadline, ensuring no failing grade ever blemishes your transcript again. "
                f"Let us sign this official Academic Recovery Agreement together today."
            )
        }
    ]
    
    student_talking_points = [
        "Ask Dr. Nasser to verify which specific repeated course provides the highest point leverage toward lifting GPA above 65.0%.",
        "Disclose any personal, health, or transportation hurdles openly so Dr. Nasser can tailor your class schedule times.",
        "Inquire about the exact hours and room locations of the Department Mathematics and Programming tutorial labs.",
        "Ask for clarification on the Week 10 official Course Withdrawal (W) deadline rules and how to protect against WF penalties.",
        "Commit to scheduling the Week 7 Midterm Follow-up advising appointment before leaving the office."
    ]
    
    return {
        'consultation_required': True,
        'urgency': urgency,
        'urgency_badge': urgency_badge,
        'schedule_window': schedule_window,
        'frequency': frequency,
        'advisor_script': advisor_script,
        'student_talking_points': student_talking_points
    }


def generate_student_advising_dossier(student_id: str) -> Dict[str, Any]:
    """
    Synthesize complete academic advising dossier with tailored course selection,
    probation compliance, and exact Dhofar University regulation citations.
    """
    audit = audit_student_degree(student_id)
    student = audit['student']
    cap = audit['credit_cap']
    st = student.status or 'Normal / Good Standing'
    gpa = audit['current_gpa']
    
    # -----------------------------------------------------------------
    # 1. Next-Semester Course Selection Algorithm
    # -----------------------------------------------------------------
    recommended_schedule = []
    accumulated_credits = 0
    scheduled_codes = set()
    
    # Priority 1: Mandatory repeats (failed prerequisite/core courses)
    for cr in audit['critical_repeats']:
        c_norm = normalize_course_code(cr['code'])
        if c_norm in scheduled_codes:
            continue
        crd = cr['credits'] or 3
        if accumulated_credits + crd <= cap:
            recommended_schedule.append({
                'code': cr['code'],
                'name': cr['name'],
                'credits': crd,
                'priority': 'High (Mandatory Repeat)',
                'reason': f"Repeat course previously not passed ({cr['last_grade']}). Critical to lift CGPA and unlock future prerequisites."
            })
            accumulated_credits += crd
            scheduled_codes.add(c_norm)
            
    # Priority 2: Ready missing core curriculum courses
    for rc in audit['ready_courses']:
        c_norm = normalize_course_code(rc['code'])
        if c_norm in scheduled_codes:
            continue
        crd = rc['credits'] or 3
        if accumulated_credits + crd <= cap:
            recommended_schedule.append({
                'code': rc['code'],
                'name': rc['name'],
                'credits': crd,
                'priority': 'Standard Core Requirement',
                'reason': f"Required {rc['category']}. All prerequisites satisfied. Recommended for {rc.get('term_recommended', 'immediate term')}."
            })
            accumulated_credits += crd
            scheduled_codes.add(c_norm)
            
    # Priority 3: Low D grade repeat if space remains under probation
    if audit['is_under_probation']:
        for lr in audit['low_grade_repeats']:
            c_norm = normalize_course_code(lr['code'])
            if c_norm in scheduled_codes:
                continue
            crd = lr['credits'] or 3
            if accumulated_credits + crd <= cap:
                recommended_schedule.append({
                    'code': lr['code'],
                    'name': lr['name'],
                    'credits': crd,
                    'priority': 'Recommended GPA Recovery',
                    'reason': f"Repeat to replace D/D+ grade ({lr['grade']}). Highest grade replaces previous attempt under DU Article 18."
                })
                accumulated_credits += crd
                scheduled_codes.add(c_norm)
                
    # -----------------------------------------------------------------
    # 2. Executive Situation Analysis
    # -----------------------------------------------------------------
    urgency_level = "CRITICAL" if ("Strict" in st or "Third" in st) else "HIGH" if "Second" in st else "MODERATE" if "First" in st else "NORMAL"
    
    analysis_paragraphs = []
    if "Strict" in st:
        analysis_paragraphs.append(
            f"**Critical Standing Alert:** {student.name} is currently placed on **{st}** with a cumulative GPA of **{gpa:.2f}%**, "
            f"which is **{audit['gpa_deficit']:.2f} points below** the Dhofar University required Good Standing threshold of 65.0%. "
            f"Continued academic deficit places the student at immediate risk of dismissal. A strictly monitored 12-credit recovery schedule is mandatory."
        )
    elif "Second Probation" in st:
        analysis_paragraphs.append(
            f"**Second Academic Probation Warning:** {student.name} has maintained a cumulative GPA of **{gpa:.2f}%**, remaining in academic jeopardy. "
            f"Under university bylaws, failing to raise the semester average above 65.0% this semester will trigger escalation to Strict Probation."
        )
    elif "First Probation" in st:
        analysis_paragraphs.append(
            f"**Academic Warning (First Probation):** {student.name}'s cumulative GPA is **{gpa:.2f}%**. "
            f"Early intervention is critical to prevent cascading probation stages. Course load is restricted to 12 credit hours."
        )
    else:
        analysis_paragraphs.append(
            f"**Satisfactory Standing:** {student.name} is in **{st}** with a cumulative GPA of **{gpa:.2f}%** and **{audit['completed_credits']} earned credit hours** "
            f"({audit['completion_percentage']}% of the {audit['program_title']} degree plan completed)."
        )
        
    if audit['critical_repeats']:
        crit_names = ', '.join(c['code'] for c in audit['critical_repeats'])
        analysis_paragraphs.append(
            f"**Deficiency Analysis:** The student has {len(audit['critical_repeats'])} unresolved course attempt(s) needing repeat ({crit_names}). "
            f"Repeating these courses replaces the failing scores under Article 18 and accelerates GPA recovery towards Good Standing."
        )
        
    if audit['blocked_courses']:
        blocked_sample = ', '.join(c['code'] for c in audit['blocked_courses'][:4])
        analysis_paragraphs.append(
            f"**Prerequisite Roadmap:** {len(audit['blocked_courses'])} upcoming curriculum courses (including {blocked_sample}) "
            f"are currently locked until prerequisite courses are successfully completed."
        )

    # -----------------------------------------------------------------
    # 3. Policy Citations & Bylaw Links
    # -----------------------------------------------------------------
    policy_citations = [
        {
            'bylaw': 'Article 14: Academic Probation & CGPA Thresholds',
            'source_document': 'DU Undergraduate Academic Regulations',
            'page': 1,
            'summary': 'Undergraduate students must maintain a cumulative GPA >= 65.0%. Any student below 65.0% is placed on probation with mandatory advising.'
        },
        {
            'bylaw': 'Article 18: Course Repetition & Grade Replacement',
            'source_document': 'DU Undergraduate Academic Regulations',
            'page': 1,
            'summary': 'Students may repeat courses with F, D, or D+. The highest grade achieved is counted in the cumulative GPA calculation.'
        },
        {
            'bylaw': 'Article 22: Course Registration Limits & Overloads',
            'source_document': 'DU Undergraduate Academic Regulations',
            'page': 1,
            'summary': f"Students on probation are strictly capped at 12 credit hours per semester. Standard full-time load is 15-18 credit hours."
        }
    ]
    
    if audit['bridge_info']:
        policy_citations.append({
            'bylaw': 'Section 3: Bridge to Bachelor Degree Requirements',
            'source_document': 'Requirements for Studying Computer Science Diploma',
            'page': 1,
            'summary': 'Diploma graduates must achieve a CGPA >= 75.0% to qualify for direct articulation into B.Sc. in Computer Science, Cybersecurity, or Data Science.'
        })

    # -----------------------------------------------------------------
    # 4. Action Plan & Follow-up Schedule
    # -----------------------------------------------------------------
    action_items = [
        f"Register exactly {accumulated_credits} credit hours (strictly capped at {cap} credit hours).",
        "Sign the official Academic Recovery Plan agreement with the Academic Advisor before add/drop closes.",
    ]
    if audit['is_under_probation']:
        action_items.append("Attend mandatory bi-weekly academic progress reviews with Academic Advisor Dr. Nasser Tabook.")
        action_items.append("Utilize Department tutoring labs for programming, mathematics, and digital logic courses.")
        action_items.append("Submit midterm progress updates prior to the official course withdrawal (W) deadline (Week 10).")
    else:
        action_items.append("Maintain semester GPA >= 70.0% to ensure on-time graduation trajectory.")

    # Calculate progression, recovery blueprint, and advisor consultation guide
    progression = analyze_semester_progression(student_id)
    recovery_plan = calculate_gpa_recovery_path(audit, student)
    consultation_guide = generate_advisor_consultation_guide(student, audit, progression, recovery_plan)

    # Cross-reference recommended courses with live Section Schedule
    try:
        from app.schedule_engine import match_recommended_schedule_to_sections
        matched_schedule = match_recommended_schedule_to_sections(recommended_schedule)
    except Exception:
        matched_schedule = recommended_schedule

    return {
        'audit': audit,
        'progression': progression,
        'recovery_plan': recovery_plan,
        'consultation_guide': consultation_guide,
        'urgency_level': urgency_level,
        'analysis_summary': analysis_paragraphs,
        'recommended_schedule': matched_schedule,
        'total_recommended_credits': accumulated_credits,
        'policy_citations': policy_citations,
        'action_items': action_items,
        'advisor_name': student.advisor or 'Dr. Nasser Tabook',
        'generated_at': 'Academic Year 2025/2026'
    }