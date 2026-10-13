"""
Chairperson Advising Report Engine for Dhofar University.
Generates formal, executive academic briefing letters and comprehensive intervention dossiers
from the Academic Advisor (Dr. Nasser Tabook) to the Chairperson of the Department of Computer Science
regarding advisees on First, Second, Third/Strict Academic Probation and students at risk.
"""

import time
from datetime import datetime
from typing import Dict, List, Any
from app.utils import load_students_from_file
from app.advising_engine import audit_student_degree

_REPORT_CACHE: Dict[str, Any] = {'data': None, 'timestamp': 0.0}

def generate_chair_advising_report(academic_term: str = "Academic Year 2026-2027", force_refresh: bool = False) -> Dict[str, Any]:
    """
    Synthesize complete, official academic briefing and intervention dossier
    addressed from Dr. Nasser Tabook to the Chair of the Department of Computer Science.
    Cached for 120 seconds for instant page loads.
    """
    now_ts = time.time()
    if not force_refresh and _REPORT_CACHE['data'] is not None and (now_ts - _REPORT_CACHE['timestamp'] < 120):
        return _REPORT_CACHE['data']

    students = load_students_from_file()
    total_advisees = len(students)
    
    strict_probation: List[Dict[str, Any]] = []
    second_probation: List[Dict[str, Any]] = []
    first_probation: List[Dict[str, Any]] = []
    low_gpa_warning: List[Dict[str, Any]] = []
    
    # Track program distribution and gatekeeper course bottlenecks
    program_counts = {'Diploma in Computer Science': 0, 'Bachelor of Science in Computer Science': 0, 'Other': 0}
    bottleneck_courses: Dict[str, int] = {}
    
    for s in students:
        st = s.status or ''
        cgpa = s.cgpa if s.cgpa is not None else s.gpa
        
        is_strict = ('Strict' in st or 'Third' in st)
        is_second = ('Second Probation' in st)
        is_first = ('First Probation' in st or ('Probation' in st and 'Removal' not in st and not is_strict and not is_second))
        is_low_gpa = (cgpa is not None and cgpa < 65.0 and not is_strict and not is_second and not is_first and 'Removal' not in st and 'Good' not in st)
        
        if not (is_strict or is_second or is_first or is_low_gpa):
            continue
            
        # Single audit call per at-risk student for speed
        try:
            audit = audit_student_degree(s.id)
        except Exception:
            audit = {
                'current_gpa': cgpa or 0.0,
                'gpa_deficit': max(0.0, round(65.0 - (cgpa or 0.0), 2)) if cgpa else 0.0,
                'completed_credits': s.credits or 0,
                'remaining_credits': 65 if 'Diploma' in (s.program or '') else 120,
                'total_plan_credits': 65 if 'Diploma' in (s.program or '') else 120,
                'credit_cap': 12,
                'critical_repeats': [],
                'low_grade_repeats': [],
                'ready_courses': []
            }
            
        trend = 'Improving' if (s.semester_gpa and cgpa and s.semester_gpa > cgpa) else ('Declining' if (s.semester_gpa and cgpa and s.semester_gpa < cgpa) else 'Stable')
        if is_strict:
            archetype_info = {'title': 'The High-Risk Stagnator', 'badge': 'danger', 'icon': 'fas fa-shield-virus'}
        elif is_second:
            archetype_info = {'title': 'The Academic Warning Stagnator', 'badge': 'warning text-dark', 'icon': 'fas fa-exclamation-triangle'}
        else:
            archetype_info = {'title': 'The Recovery Fighter' if trend == 'Improving' else 'The Early-Warning Trainee', 'badge': 'warning text-dark', 'icon': 'fas fa-bell'}

            
        # Tally bottlenecks
        for cr in audit.get('critical_repeats', []):
            code = cr.get('code', '').strip()
            if code:
                bottleneck_courses[code] = bottleneck_courses.get(code, 0) + 1
                
        # Program classification
        prog_clean = s.program or 'Computer Science'
        if 'Diploma' in prog_clean:
            program_counts['Diploma in Computer Science'] += 1
            degree_label = 'Diploma in Computer Science'
        elif 'Bachelor' in prog_clean:
            program_counts['Bachelor of Science in Computer Science'] += 1
            degree_label = 'Bachelor of Science in Computer Science'
        else:
            program_counts['Other'] += 1
            degree_label = prog_clean

        critical_codes = [c['code'] for c in audit.get('critical_repeats', [])]
        
        # Tailor specific Rescue Action Plan and Department Intervention
        rescue_actions = []
        chair_intervention = ""
        
        if critical_codes:
            primary_crit = ", ".join(critical_codes[:2])
            rescue_actions.append(f"Immediate repeat registration for gatekeeper course(s): {primary_crit} (DU Article 18 Grade Replacement).")
        else:
            rescue_actions.append("Prioritize lower-level curriculum requirements before advancing to upper-division electives.")
            
        if audit.get('credit_cap') == 12:
            rescue_actions.append("Strictly enforce the 12 credit hour ceiling (DU Article 14 & 22) to prevent course overloads.")
            chair_intervention = "Enforce 12-credit cap; reject elective overload petitions until CGPA >= 65.0%."
        else:
            rescue_actions.append("Cap schedule at 12-14 credits with balanced theoretical and laboratory workload.")
            chair_intervention = "Monitor study plan adherence during Add/Drop."
            
        rescue_actions.append("Mandatory 4-6 hours/week Department tutorial lab attendance (Calculus/Programming).")
        rescue_actions.append("Conduct Week 7 midterm audit; evaluate Article 24 Course Withdrawal (W) prior to Week 10 deadline if marks remain below 60%.")
        
        if is_strict:
            chair_intervention += " CRITICAL: Requires formal Department warning letter and advisor check-in agreement signed."
        elif is_second:
            chair_intervention += " HIGH: Review prerequisite chains; ensure seat reserved in repeated course section."

        record = {
            'student': s,
            'id': s.id,
            'name': s.name,
            'degree_plan': degree_label,
            'status': s.status,
            'cgpa': audit['current_gpa'],
            'gpa_deficit': audit['gpa_deficit'],
            'semester_gpa': s.semester_gpa,
            'trend': trend,
            'completed_credits': audit['completed_credits'],
            'total_credits': audit['total_plan_credits'],
            'credit_cap': audit['credit_cap'],
            'critical_repeats': audit['critical_repeats'],
            'critical_codes': critical_codes,
            'archetype': archetype_info,
            'rescue_actions': rescue_actions,
            'chair_intervention': chair_intervention
        }
        
        if is_strict:
            strict_probation.append(record)
        elif is_second:
            second_probation.append(record)
        elif is_first:
            first_probation.append(record)
        elif is_low_gpa:
            low_gpa_warning.append(record)
            
    # Sort groups by GPA ascending (lowest GPA / most urgent first)
    strict_probation.sort(key=lambda x: x['cgpa'])
    second_probation.sort(key=lambda x: x['cgpa'])
    first_probation.sort(key=lambda x: x['cgpa'])
    low_gpa_warning.sort(key=lambda x: x['cgpa'])
    
    total_at_risk = len(strict_probation) + len(second_probation) + len(first_probation) + len(low_gpa_warning)
    at_risk_percentage = round((total_at_risk / total_advisees) * 100, 1) if total_advisees > 0 else 0.0
    
    # Sort top bottleneck courses
    top_bottlenecks = sorted(bottleneck_courses.items(), key=lambda x: x[1], reverse=True)[:5]
    
    now = datetime.now()
    ref_number = f"DU/CAAS/CS/ADV-{now.year}-{now.strftime('%m%d')}-01"
    report_date = now.strftime("%B %d, %Y")
    
    # Build text version of the official letter for copy/pasting
    letter_text = _build_plain_text_letter(
        ref_number=ref_number,
        report_date=report_date,
        academic_term=academic_term,
        total_advisees=total_advisees,
        total_at_risk=total_at_risk,
        at_risk_percentage=at_risk_percentage,
        program_counts=program_counts,
        top_bottlenecks=top_bottlenecks,
        strict_probation=strict_probation,
        second_probation=second_probation,
        first_probation=first_probation,
        low_gpa_warning=low_gpa_warning
    )
    
    result = {
        'ref_number': ref_number,
        'report_date': report_date,
        'academic_term': academic_term,
        'advisor_name': 'Dr. Nasser Tabook',
        'advisor_title': 'Assistant Professor of Computer Science & Academic Advisor',
        'department_name': 'Department of Computer Science',
        'college_name': 'College of Arts and Applied Sciences',
        'university_name': 'Dhofar University',
        'addressee_title': 'Chairperson, Department of Computer Science',
        'subject': 'OFFICIAL ADVISING BRIEFING & INTERVENTION DOSSIER: STUDENTS UNDER ACADEMIC PROBATION & AT-RISK COHORT (ACTION REQUIRED)',
        'total_advisees': total_advisees,
        'total_at_risk': total_at_risk,
        'at_risk_percentage': at_risk_percentage,
        'counts': {
            'strict': len(strict_probation),
            'second': len(second_probation),
            'first': len(first_probation),
            'warning': len(low_gpa_warning),
            'total': total_at_risk
        },
        'program_counts': program_counts,
        'top_bottlenecks': top_bottlenecks,
        'strict_probation': strict_probation,
        'second_probation': second_probation,
        'first_probation': first_probation,
        'low_gpa_warning': low_gpa_warning,
        'letter_text': letter_text
    }
    
    _REPORT_CACHE['data'] = result
    _REPORT_CACHE['timestamp'] = now_ts
    return result



def _build_plain_text_letter(
    ref_number: str,
    report_date: str,
    academic_term: str,
    total_advisees: int,
    total_at_risk: int,
    at_risk_percentage: float,
    program_counts: Dict[str, int],
    top_bottlenecks: List[tuple],
    strict_probation: List[Dict[str, Any]],
    second_probation: List[Dict[str, Any]],
    first_probation: List[Dict[str, Any]],
    low_gpa_warning: List[Dict[str, Any]]
) -> str:
    """Generate cleanly formatted official letter text ready for copying into email or Word"""
    lines = []
    lines.append("=" * 80)
    lines.append("DHOFAR UNIVERSITY | COLLEGE OF ARTS AND APPLIED SCIENCES")
    lines.append("DEPARTMENT OF COMPUTER SCIENCE — ACADEMIC ADVISING UNIT")
    lines.append("=" * 80)
    lines.append(f"REF: {ref_number}")
    lines.append(f"DATE: {report_date}")
    lines.append(f"ACADEMIC TERM: {academic_term}")
    lines.append("")
    lines.append("TO:     Chairperson, Department of Computer Science")
    lines.append("FROM:   Dr. Nasser Tabook, Assistant Professor & Academic Advisor")
    lines.append(f"SUBJECT: OFFICIAL BRIEFING & INTERVENTION DOSSIER: STUDENTS UNDER ACADEMIC PROBATION ({total_at_risk} ADVISEES)")
    lines.append("-" * 80)
    lines.append("")
    lines.append("Dear Chairperson,")
    lines.append("")
    lines.append("I am submitting herewith the formal academic diagnostic briefing and comprehensive intervention plan for all students under my academic advising purview who are currently placed on Academic Probation or categorized as academically at risk at Dhofar University.")
    lines.append("")
    lines.append("1. EXECUTIVE COHORT OVERVIEW & RISK SUMMARY")
    lines.append("=" * 45)
    lines.append(f"• Total Assigned Advisees:          {total_advisees} students")
    lines.append(f"• Total Students at Risk:           {total_at_risk} students ({at_risk_percentage}% of cohort)")
    lines.append(f"• Category A - Strict/Third Probation (Critical Dismissal Hazard): {len(strict_probation)} students")
    lines.append(f"• Category B - Second Probation (Escalating Warning Stage):         {len(second_probation)} students")
    lines.append(f"• Category C - First Probation (Initial Intervention Stage):        {len(first_probation)} students")
    if low_gpa_warning:
        lines.append(f"• Category D - Pre-Probation Warning (CGPA < 65.0%):               {len(low_gpa_warning)} students")
    lines.append("")
    lines.append(f"Degree Program Breakdown: Diploma in CS ({program_counts.get('Diploma in Computer Science', 0)}) | Bachelor of Science in CS ({program_counts.get('Bachelor of Science in Computer Science', 0)})")
    if top_bottlenecks:
        b_str = ", ".join(f"{code} ({cnt} students)" for code, cnt in top_bottlenecks)
        lines.append(f"Primary Gatekeeper Course Bottlenecks: {b_str}")
    lines.append("")
    lines.append("2. COMPREHENSIVE ROSTER OF AT-RISK STUDENTS & RESCUE ACTION PLANS")
    lines.append("=" * 80)

    # Section A: Strict Probation
    if strict_probation:
        lines.append("")
        lines.append(f"CATEGORY A: STRICT / THIRD PROBATION — IMMEDIATE DISMISSAL HAZARD ({len(strict_probation)} Students)")
        lines.append("Governed by DU Academic Regulations Article 14 & Article 22 (Strict 12-credit cap enforced)")
        lines.append("-" * 80)
        for idx, rec in enumerate(strict_probation, 1):
            s = rec['student']
            lines.append(f"{idx}. {s.name} (ID: {s.id})")
            lines.append(f"   • Degree Plan:       {rec['degree_plan']}")
            lines.append(f"   • Standing:          {s.status}")
            lines.append(f"   • CGPA:              {rec['cgpa']:.2f}% (Deficit: {rec['gpa_deficit']:.2f} points below 65.0% Good Standing)")
            lines.append(f"   • SGPA:              {rec['semester_gpa']:.2f}%" if rec['semester_gpa'] is not None else "   • SGPA:              N/A")
            lines.append(f"   • Credits Earned:    {rec['completed_credits']} / {rec['total_credits']} hrs")
            if rec['critical_codes']:
                lines.append(f"   • Gatekeeper Blocks: {', '.join(rec['critical_codes'])}")
            lines.append("   • Prescribed Rescue Plan:")
            for act in rec['rescue_actions']:
                lines.append(f"     - {act}")
            lines.append(f"   • Chair Action:      {rec['chair_intervention']}")
            lines.append("")

    # Section B: Second Probation
    if second_probation:
        lines.append("")
        lines.append(f"CATEGORY B: SECOND PROBATION — ESCALATING RISK ({len(second_probation)} Students)")
        lines.append("-" * 80)
        for idx, rec in enumerate(second_probation, 1):
            s = rec['student']
            lines.append(f"{idx}. {s.name} (ID: {s.id})")
            lines.append(f"   • Degree Plan:       {rec['degree_plan']}")
            lines.append(f"   • Standing:          {s.status}")
            lines.append(f"   • CGPA:              {rec['cgpa']:.2f}% (Deficit: {rec['gpa_deficit']:.2f} points)")
            if rec['critical_codes']:
                lines.append(f"   • Gatekeeper Blocks: {', '.join(rec['critical_codes'])}")
            lines.append("   • Prescribed Rescue Plan:")
            for act in rec['rescue_actions']:
                lines.append(f"     - {act}")
            lines.append(f"   • Chair Action:      {rec['chair_intervention']}")
            lines.append("")

    # Section C: First Probation
    if first_probation:
        lines.append("")
        lines.append(f"CATEGORY C: FIRST PROBATION — EARLY WARNING & INTERVENTION ({len(first_probation)} Students)")
        lines.append("-" * 80)
        for idx, rec in enumerate(first_probation, 1):
            s = rec['student']
            lines.append(f"{idx}. {s.name} (ID: {s.id})")
            lines.append(f"   • Degree Plan:       {rec['degree_plan']}")
            lines.append(f"   • Standing:          {s.status}")
            lines.append(f"   • CGPA:              {rec['cgpa']:.2f}% (Deficit: {rec['gpa_deficit']:.2f} points)")
            if rec['critical_codes']:
                lines.append(f"   • Gatekeeper Blocks: {', '.join(rec['critical_codes'])}")
            lines.append("   • Prescribed Rescue Plan:")
            for act in rec['rescue_actions']:
                lines.append(f"     - {act}")
            lines.append(f"   • Chair Action:      {rec['chair_intervention']}")
            lines.append("")

    lines.append("3. DEPARTMENTAL ACTION RECOMMENDATIONS FOR THE CHAIRPERSON")
    lines.append("=" * 65)
    lines.append("In order to reverse the academic deterioration and elevate the CGPA of these students, I respectfully recommend the following institutional actions by the Department:")
    lines.append("1. Strict Enforcement of the 12-Credit Cap (Article 22): Instruct the registration registrar and advisors to block any overload requests above 12 credits for students on probation.")
    lines.append("2. Priority Seat Allocation for Prerequisite Repeats: Ensure reserved seats in core sections (MATH 199, CMPS 110N, CMPS 180) to maximize DU Article 18 grade replacement benefit.")
    lines.append("3. Department Tutorial Lab Sections: Direct the Department lab instructors to schedule mandatory tutoring hours and submit bi-weekly attendance rosters to advisors.")
    lines.append("4. Midterm Warning & Article 24 Safety Net: Conduct a departmental progress audit after Week 6; guide students failing by Week 9 toward the official Course Withdrawal (W) before the Week 10 deadline to prevent dismissal.")
    lines.append("")
    lines.append("Respectfully submitted,")
    lines.append("")
    lines.append("Dr. Nasser Tabook")
    lines.append("Assistant Professor of Computer Science & Academic Advisor")
    lines.append("Department of Computer Science | Dhofar University")
    lines.append("=" * 80)

    return "\n".join(lines)
