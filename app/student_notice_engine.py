"""
Student Official Notice & Advisory Email Generator Engine for Dhofar University.
Synthesizes individual, official academic advisory notices and ready-to-send emails
tailored for any student case (Probation, At-Risk, or Good Standing).
Provides transparent status briefing, mandatory course registration directives,
Dhofar University regulatory citations (Articles 14, 18, 22, 24), and 1-click mailto links.
"""

import urllib.parse
from datetime import datetime
from typing import Dict, Any, List
from app.models import Student
from app.utils import load_students_from_file
from app.advising_engine import audit_student_degree
from app.persona_engine import generate_student_persona

def generate_student_official_notice(student_id: str) -> Dict[str, Any]:
    """
    Generate an official, policy-referenced individual academic notice and email
    addressed directly from Dr. Nasser Tabook to a specific advisee.
    """
    students = load_students_from_file()
    student = next((s for s in students if s.id == student_id), None)
    if not student:
        raise ValueError(f"Student with ID '{student_id}' not found.")
        
    audit = audit_student_degree(student.id)
    persona = generate_student_persona(student.id)
    
    st = student.status or 'Normal / Good Standing'
    cgpa = audit['current_gpa'] or 0.0
    deficit = audit['gpa_deficit']
    cap = audit['credit_cap']
    completed_cr = audit['completed_credits']
    remaining_cr = audit['remaining_credits']
    total_cr = audit['total_plan_credits']
    student_email = student.email or f"{student.id}@du.edu.om"
    advisor_name = "Dr. Nasser Tabook"
    advisor_title = "Assistant Professor of Computer Science & Academic Advisor"
    dept_name = "Department of Computer Science"
    college_name = "College of Arts and Applied Sciences"
    university_name = "Dhofar University"
    
    is_strict = ('Strict' in st or 'Third' in st)
    is_second = ('Second Probation' in st)
    is_first = ('First Probation' in st or ('Probation' in st and 'Removal' not in st and not is_strict and not is_second))
    is_probation = (is_strict or is_second or is_first or cgpa < 65.0)
    
    now = datetime.now()
    ref_num = f"DU/CS/ADV/NOT-{now.year}-{student.id}"
    date_str = now.strftime("%B %d, %Y")
    
    # -------------------------------------------------------------
    # 1. Subject Line Formulation
    # -------------------------------------------------------------
    if is_strict:
        urgency_label = "CRITICAL / DISMISSAL WARNING"
        subject_line = f"[URGENT - CRITICAL ACTION REQUIRED] Official Academic Advising Notice: Strict Probation & Registration Cap - {student.name} ({student.id})"
    elif is_second:
        urgency_label = "HIGH MANDATORY"
        subject_line = f"[MANDATORY ACTION REQUIRED] Official Academic Advising Notice: Second Probation Review - {student.name} ({student.id})"
    elif is_first:
        urgency_label = "ACADEMIC WARNING"
        subject_line = f"[IMPORTANT] Official Academic Advising Notice: Academic Probation & Recovery Plan - {student.name} ({student.id})"
    elif 'Removal' in st:
        urgency_label = "PROBATION CLEARED"
        subject_line = f"Official Academic Advising Notice: Probation Cleared & Next Registration Plan - {student.name} ({student.id})"
    else:
        urgency_label = "STANDARD ADVISING"
        subject_line = f"Official Academic Advising Notice: Semester Progress & Registration Plan - {student.name} ({student.id})"

    # -------------------------------------------------------------
    # 2. Mandatory Course Registration Directives
    # -------------------------------------------------------------
    prescribed_courses = []
    critical_codes = [c['code'] for c in audit.get('critical_repeats', [])]
    
    # Priority 1: Mandatory repeats
    for cr in audit.get('critical_repeats', [])[:2]:
        prescribed_courses.append({
            'code': cr['code'],
            'name': cr['name'],
            'credits': cr['credits'] or 3,
            'type': 'MANDATORY REPEAT (DU Article 18)',
            'instruction': f"You MUST re-register for {cr['code']} this term. Under university bylaws, your new grade directly replaces your previous failing mark in your CGPA."
        })
        
    # Priority 2: Ready curriculum core courses
    needed_slots = max(1, (cap // 3) - len(prescribed_courses))
    for rc in audit.get('ready_courses', [])[:needed_slots]:
        prescribed_courses.append({
            'code': rc['code'],
            'name': rc['name'],
            'credits': rc['credits'] or 3,
            'type': 'CORE STUDY PLAN REQUIREMENT',
            'instruction': f"Required {rc['category']}. Prerequisites are satisfied. Register to maintain degree sequence."
        })
        
    # -------------------------------------------------------------
    # 3. Directives & Rules (What The Student MUST Do)
    # -------------------------------------------------------------
    student_action_items = []
    if is_probation:
        student_action_items.append(
            f"Adhere strictly to the {cap} credit hour maximum limit (DU Article 14 & Article 22). You are not permitted to register for more than 12 credits while on academic warning."
        )
        if critical_codes:
            student_action_items.append(
                f"Prioritize re-taking your failed prerequisite course(s): {', '.join(critical_codes)}. Under DU Article 18, scoring 70-75% in a repeated course replaces the old score and injects rapid recovery points directly into your CGPA."
            )
        student_action_items.append(
            "Dedicate a minimum of 4 to 6 hours every week to the Department Mathematics and Programming Tutorial Labs."
        )
        student_action_items.append(
            "Schedule your mandatory mid-semester check-in with me after Week 6. If any course grade remains below 60% by Week 9, we must evaluate the official Course Withdrawal (W) option before the Week 10 deadline (DU Article 24) to protect you from failing marks."
        )
        student_action_items.append(
            "Book an advising appointment with me in my office or on the Virtual Office Hub immediately to review and approve your schedule before the Add/Drop deadline."
        )
    else:
        student_action_items.append(
            f"Register for up to {cap} credit hours following your recommended study plan sequence."
        )
        student_action_items.append(
            "Ensure all prerequisite courses for next year's major electives are registered and completed on time."
        )
        student_action_items.append(
            "Confirm elective distributions and verify your remaining credit checklist towards degree graduation clearance."
        )
        student_action_items.append(
            "Contact me during office hours if you have any questions regarding your course selection or graduation roadmap."
        )

    # -------------------------------------------------------------
    # 4. Arabic Summary Section
    # -------------------------------------------------------------
    arabic_standing = "تحت الملاحظة الأكاديمية الحرجة (إنذار نهائي)" if is_strict else ("تحت الملاحظة الأكاديمية الثانية" if is_second else ("تحت الملاحظة الأكاديمية الأولى" if is_first else "وضع أكاديمي سليم (مستوفٍ للشروط)"))
    arabic_actions = []
    if is_probation:
        arabic_actions.append(f"الالتزام الصارم بالحد الأقصى للعبء الدراسي ({cap} ساعة معتمدة كحد أقصى) بموجب المادتين 14 و 22.")
        if critical_codes:
            arabic_actions.append(f"إعادة تسجيل المقررات المعلقة: ({', '.join(critical_codes)}) للاستفادة من استبدال الدرجة وفق المادة 18.")
        arabic_actions.append("حضور حصص التقوية الأسبوعية في مختبرات الرياضيات والبرمجة بالقسم.")
        arabic_actions.append("مراجعة المرشد الأكاديمي (د. ناصر تبوك) فوراً لاعتماد جدولك قبل إغلاق فترة الحذف والإضافة.")
    else:
        arabic_actions.append(f"تسجيل المقررات الأساسية ضمن الحد الطبيعي ({cap} ساعة معتمدة) وفق الخطة الدراسية.")
        arabic_actions.append("مراجعة المرشد الأكاديمي (د. ناصر تبوك) للتأكد من استيفاء متطلبات التخرج.")

    # -------------------------------------------------------------
    # 5. Formulate Plain Text Email Body
    # -------------------------------------------------------------
    email_lines = []
    email_lines.append(f"OFFICIAL ACADEMIC ADVISING NOTICE | DHOFAR UNIVERSITY")
    email_lines.append(f"DEPARTMENT OF COMPUTER SCIENCE — ACADEMIC ADVISING UNIT")
    email_lines.append("=" * 70)
    email_lines.append(f"REF: {ref_num}")
    email_lines.append(f"DATE: {date_str}")
    email_lines.append(f"TO: {student.name} (Student ID: {student.id})")
    email_lines.append(f"FROM: {advisor_name}, {advisor_title}")
    email_lines.append(f"SUBJECT: {subject_line}")
    email_lines.append("-" * 70)
    email_lines.append("")
    email_lines.append(f"Dear {student.name},")
    email_lines.append("")
    email_lines.append("I hope this message finds you well. As your designated Academic Advisor in the Department of Computer Science, I am writing to provide you with an official review of your academic transcript, your current standing at Dhofar University, and the mandatory course registration plan for the upcoming semester.")
    email_lines.append("")
    email_lines.append("1. YOUR CURRENT ACADEMIC STATUS & TRANSCRIPT AUDIT")
    email_lines.append("-" * 55)
    email_lines.append(f"• Degree Program:        {audit['program_title']} ({audit['degree_type']})")
    email_lines.append(f"• Current Standing:      {st}")
    email_lines.append(f"• Cumulative GPA (CGPA): {cgpa:.2f}% (Good Standing Requirement: >= 65.0%)")
    if deficit > 0:
        email_lines.append(f"• Academic GPA Deficit:  {deficit:.2f} points below the mandatory threshold")
    email_lines.append(f"• Credits Completed:     {completed_cr} of {total_cr} credit hours ({remaining_cr} hrs remaining)")
    email_lines.append(f"• Semester Credit Limit: CAPPED AT {cap} CREDIT HOURS MAX (DU Article 22)")
    email_lines.append("")

    if is_probation:
        email_lines.append("⚠️ IMPORTANT REGULATORY NOTICE:")
        email_lines.append("Under Dhofar University Academic Regulations Article 14, placing on academic probation is a formal institutional warning. If your Cumulative GPA remains below 65.0% for consecutive terms, it will lead to escalation of probation levels or academic dismissal. Therefore, this semester is critical to your degree continuation.")
        email_lines.append("")

    email_lines.append("2. PRESCRIBED COURSE REGISTRATION SCHEDULE")
    email_lines.append("-" * 55)
    email_lines.append(f"You must structure your schedule strictly within {cap} credit hours with the following prioritized courses:")
    for idx, c in enumerate(prescribed_courses, 1):
        email_lines.append(f"{idx}. {c['code']} - {c['name']} ({c['credits']} Cr) [{c['type']}]")
        email_lines.append(f"   Note: {c['instruction']}")
    email_lines.append("")

    email_lines.append("3. MANDATORY DIRECTIVES (WHAT YOU MUST DO NOW)")
    email_lines.append("-" * 55)
    for act in student_action_items:
        email_lines.append(f"• {act}")
    email_lines.append("")

    email_lines.append("4. ملخص إرشادي باللغة العربية (ARABIC SUMMARY)")
    email_lines.append("-" * 55)
    email_lines.append(f"• الوضع الأكاديمي الحالي: {arabic_standing} (المعدل التراكمي: {cgpa:.2f}%)")
    for a_act in arabic_actions:
        email_lines.append(f"• {a_act}")
    email_lines.append("")

    email_lines.append("5. MANDATORY ADVISOR CONSULTATION")
    email_lines.append("-" * 55)
    email_lines.append(f"Please meet with me during office hours or in the Department of Computer Science to finalize your registration. Do not submit course registrations that deviate from this approved plan.")
    email_lines.append("")
    email_lines.append("Office: Department of Computer Science, College of Arts and Applied Sciences")
    email_lines.append(f"Email:  ntabook@du.edu.om | Portal: https://nasserdiary.com/duadv/student/{student.id}")
    email_lines.append("")
    email_lines.append("Best regards,")
    email_lines.append(f"{advisor_name}")
    email_lines.append(f"{advisor_title}")
    email_lines.append(f"{dept_name} | {college_name}")
    email_lines.append(f"{university_name}")
    email_lines.append("=" * 70)

    plain_text_email = "\n".join(email_lines)

    # -------------------------------------------------------------
    # 6. Pre-encode mailto: Link
    # -------------------------------------------------------------
    encoded_subject = urllib.parse.quote(subject_line)
    encoded_body = urllib.parse.quote(plain_text_email)
    mailto_url = f"mailto:{student_email}?subject={encoded_subject}&body={encoded_body}"

    return {
        'student': student,
        'student_id': student.id,
        'student_name': student.name,
        'student_email': student_email,
        'ref_num': ref_num,
        'date_str': date_str,
        'subject_line': subject_line,
        'urgency_label': urgency_label,
        'is_probation': is_probation,
        'standing': st,
        'cgpa': cgpa,
        'gpa_deficit': deficit,
        'semester_gpa': student.semester_gpa,
        'credit_cap': cap,
        'completed_credits': completed_cr,
        'remaining_credits': remaining_cr,
        'total_credits': total_cr,
        'degree_title': audit['program_title'],
        'degree_type': audit['degree_type'],
        'prescribed_courses': prescribed_courses,
        'student_action_items': student_action_items,
        'arabic_standing': arabic_standing,
        'arabic_actions': arabic_actions,
        'advisor_name': advisor_name,
        'advisor_title': advisor_title,
        'advisor_email': 'ntabook@du.edu.om',
        'dept_name': dept_name,
        'college_name': college_name,
        'university_name': university_name,
        'plain_text_email': plain_text_email,
        'mailto_url': mailto_url,
        'persona': persona
    }
