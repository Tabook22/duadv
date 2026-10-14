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

DISCIPLINE_TITLES_AR = {
    'MATH': 'الرياضيات والتحليل الكمي',
    'CS': 'علوم الحاسوب وهندسة البرمجيات',
    'ENGR': 'العلوم الهندسية والمختبرات التطبيقية',
    'GENED': 'متطلبات الجامعة العامة واللغات',
    'BUSINESS': 'الإدارة والأعمال الكمية',
    'OTHER': 'المساقات الاختيارية الأخرى'
}

ARCHETYPE_TEXTS = {
    'high_risk_probation': {
        'en': {
            'title': "The High-Risk Stagnator",
            'tagline': "Critical academic alert: Repeated course failures and credit caps threaten degree continuation under DU Article 14.",
            'risk_level': "CRITICAL"
        },
        'ar': {
            'title': "المتعثر المعرض لخطر الفصل الأكاديمي",
            'tagline': "تنبيه أكاديمي حرج: تعثر متكرر وسقف ساعات إلزامي يهدد الاستمرار بالدراسة وفق المادة 14 من لوائح الجامعة.",
            'risk_level': "حرج جداً"
        }
    },
    'probation_fighter': {
        'en': {
            'title': "The Recovery Fighter",
            'tagline': "Actively rebounding from academic probation with positive upward momentum; within striking distance of Good Standing.",
            'risk_level': "MODERATE TO HIGH"
        },
        'ar': {
            'title': "المكافح للتعافي الأكاديمي",
            'tagline': "يسجل تقدماً ملموساً واستعادة للمعدل مع تحسن صاعد؛ على مقربة من استعادة الوضع الأكاديمي السليم.",
            'risk_level': "متوسط إلى مرتفع"
        }
    },
    'probation_struggler': {
        'en': {
            'title': "The Academic Warning Stagnator",
            'tagline': "Persistent GPA deficit below 65.0%; requires immediate intervention to halt probation escalation.",
            'risk_level': "HIGH"
        },
        'ar': {
            'title': "المتعثر تحت الملاحظة الأكاديمية",
            'tagline': "عجز تراكمي مستمر تحت 65.0%؛ يتطلب تدخلاً إرشادياً عاجلاً لوقف تصاعد الملاحظة.",
            'risk_level': "مرتفع"
        }
    },
    'prereq_bottleneck': {
        'en': {
            'title': "The Gatekeeper Bottleneck",
            'tagline': "Capable student encountering severe prerequisite roadblocks in quantitative or programming core courses.",
            'risk_level': "MODERATE"
        },
        'ar': {
            'title': "المتعثر عند المتطلبات السابقة (عنق الزجاجة)",
            'tagline': "طالب ذو قدرات جيدة يواجه عائقاً حرجاً في متطلب كمي أو برمجي أساسي بالخطة.",
            'risk_level': "متوسط"
        }
    },
    'capstone_sprinter': {
        'en': {
            'title': "The Capstone Sprinter",
            'tagline': "Final-phase senior with solid academic momentum, actively finalizing major electives and degree clearance.",
            'risk_level': "LOW"
        },
        'ar': {
            'title': "المنجز في مرحلة التخرج",
            'tagline': "طالب في المرحلة النهائية بزخم أكاديمي متين، يستكمل المواد الاختيارية وإجراءات التخرج.",
            'risk_level': "منخفض"
        }
    },
    'high_achiever': {
        'en': {
            'title': "The Dean's List Pacesetter",
            'tagline': "Exemplary high-achiever with consistent honors marks, strong conceptual mastery, and uninterrupted course flow.",
            'risk_level': "MINIMAL"
        },
        'ar': {
            'title': "المتفوق المتميز (قائمة العميد)",
            'tagline': "طالب متميز بمرتبة الشرف، إتقان مفاهيمي عالي، وتدرج دراسي متواصل دون تعثر.",
            'risk_level': "ضئيل جداً"
        }
    },
    'foundation_transitioner': {
        'en': {
            'title': "The Early-Career Transitioner",
            'tagline': "Freshman/Sophomore establishing university study habits and adapting to departmental course pacing.",
            'risk_level': "LOW TO MODERATE"
        },
        'ar': {
            'title': "المستجد في المرحلة الانتقالية",
            'tagline': "طالب في السنة الأولى/الثانية يعتاد وتيرة الدراسة الجامعية ومتطلبات القسم.",
            'risk_level': "منخفض إلى متوسط"
        }
    },
    'steady_builder': {
        'en': {
            'title': "The Methodical Builder",
            'tagline': "Dependable, steady student progressing systematically through the curriculum without major academic friction.",
            'risk_level': "LOW"
        },
        'ar': {
            'title': "المثابر المنظم",
            'tagline': "طالب منضبط يتقدم بخطى ثابتة ومنهجية عبر الخطة الدراسية دون احتكاك أكاديمي كبير.",
            'risk_level': "منخفض"
        }
    }
}


def _classify_course_discipline(course_code: str) -> str:
    """Identify which academic discipline category a course code belongs to"""
    norm = normalize_course_code(course_code)
    for disc_key, meta in DISCIPLINE_MAP.items():
        if any(norm.startswith(p) for p in meta['prefixes']):
            return disc_key
    return 'OTHER'


def _analyze_discipline_performance(semesters: List[Dict[str, Any]], lang: str = 'en') -> Dict[str, Any]:
    """Calculate aggregate success rate, attempt count, and average score across disciplines"""
    is_ar = (lang == 'ar')
    stats = {}
    for k in DISCIPLINE_MAP.keys():
        disc_title = DISCIPLINE_TITLES_AR[k] if is_ar else DISCIPLINE_MAP[k]['title']
        stats[k] = {
            'key': k,
            'title': disc_title,
            'icon': DISCIPLINE_MAP[k]['icon'],
            'color': DISCIPLINE_MAP[k]['color'],
            'attempts': 0,
            'passed': 0,
            'failed': 0,
            'total_score': 0.0,
            'scored_courses': 0,
            'courses': []
        }
    other_title = DISCIPLINE_TITLES_AR['OTHER'] if is_ar else 'Other Department Electives'
    stats['OTHER'] = {
        'key': 'OTHER',
        'title': other_title,
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


def generate_student_persona(student_id: str, transcripts_dir: str = None, lang: str = None) -> Dict[str, Any]:
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
    if lang is None:
        try:
            from app.i18n import get_current_language
            lang = get_current_language()
        except Exception:
            lang = 'en'
    is_ar = (lang == 'ar')

    students = load_students_from_file()
    student = next((s for s in students if s.id == student_id), None)
    if not student:
        raise ValueError(f"Student with ID '{student_id}' not found.")

    audit = audit_student_degree(student_id, transcripts_dir)
    progression = analyze_semester_progression(student_id)
    raw_semesters = get_student_semesters(student_id, transcripts_dir)
    discipline_stats = _analyze_discipline_performance(raw_semesters, lang=lang)

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
        archetype_badge = "danger"
        archetype_icon = "fas fa-shield-virus"
        risk_score = 92
    elif is_under_probation or ('Probation' in status and 'Removal' not in status):
        if recent_sem_delta > 0 or recent_trend == 'Improving':
            archetype_key = 'probation_fighter'
            archetype_badge = "warning text-dark"
            archetype_icon = "fas fa-fire"
            risk_score = 68
        else:
            archetype_key = 'probation_struggler'
            archetype_badge = "warning text-dark"
            archetype_icon = "fas fa-exclamation-triangle"
            risk_score = 78
    elif has_critical_repeats:
        archetype_key = 'prereq_bottleneck'
        archetype_badge = "orange text-white"
        archetype_icon = "fas fa-lock"
        risk_score = 55
    elif completion_pct >= 75.0 and current_gpa >= 65.0:
        archetype_key = 'capstone_sprinter'
        archetype_badge = "success"
        archetype_icon = "fas fa-flag-checkered"
        risk_score = 15
    elif current_gpa >= 80.0:
        archetype_key = 'high_achiever'
        archetype_badge = "primary"
        archetype_icon = "fas fa-award"
        risk_score = 8
    elif completed_credits < 30 or num_graded_terms <= 2:
        archetype_key = 'foundation_transitioner'
        archetype_badge = "info text-dark"
        archetype_icon = "fas fa-seedling"
        risk_score = 35
    else:
        archetype_key = 'steady_builder'
        archetype_badge = "secondary"
        archetype_icon = "fas fa-layer-group"
        risk_score = 25

    # Retrieve localized texts
    arch_lang = 'ar' if is_ar else 'en'
    t_entry = ARCHETYPE_TEXTS.get(archetype_key, {}).get(arch_lang, ARCHETYPE_TEXTS[archetype_key]['en'])
    archetype_title = t_entry['title']
    archetype_tagline = t_entry['tagline']
    risk_level = t_entry['risk_level']

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
            if is_ar:
                st_text = f"كفاءة عالية في {best_disc['title']}: حقق نسبة نجاح {best_disc['pass_rate']}% بمعدل {best_disc['avg_score'] or 'ناجح'}% عبر {best_disc['attempts']} مساقاً مسجلاً."
            else:
                st_text = f"High Aptitude in {best_disc['title']}: Achieved {best_disc['pass_rate']}% pass rate with an average mark of {best_disc['avg_score'] or 'Pass'}% across {best_disc['attempts']} attempted courses."
            strengths.append({
                'category': best_disc['title'],
                'icon': best_disc['icon'],
                'text': st_text
            })

    # Check for general education strength
    gened = discipline_stats.get('GENED')
    if gened and gened['attempts'] >= 2 and gened['pass_rate'] >= 90:
        if is_ar:
            gen_cat = "متطلبات الجامعة العامة واللغات"
            gen_text = f"أساس متين في العلوم الإنسانية واللغات: نسبة نجاح تامة ({gened['pass_rate']}%) في متطلبات جامعة ظفار العامة."
        else:
            gen_cat = "General Education & Communication"
            gen_text = f"Strong Foundation in Humanities & Language: Flawless pass rate ({gened['pass_rate']}%) across DU university requirements."
        strengths.append({
            'category': gen_cat,
            'icon': 'fas fa-comments',
            'text': gen_text
        })

    # Check credit accumulation pace
    if num_graded_terms > 0:
        avg_credits_per_term = round(completed_credits / max(1, num_graded_terms), 1)
        if avg_credits_per_term >= 15.0 and current_gpa >= 65.0:
            if is_ar:
                p_cat = "وتيرة وسرعة الإنجاز"
                p_text = f"وتيرة إنجاز عالية للساعات: يحافظ على معدل إنجاز نشط بواقع {avg_credits_per_term} ساعة معتمدة/فصل دراسي دون تأخر عن الخطة."
            else:
                p_cat = "Pacing & Endurance"
                p_text = f"High Credit Velocity: Maintains a brisk pace of {avg_credits_per_term} credits/term without falling behind schedule."
            strengths.append({
                'category': p_cat,
                'icon': 'fas fa-tachometer-alt',
                'text': p_text
            })

    # Check for zero course withdrawals
    withdrawn_courses_count = sum(
        1 for sem in raw_semesters 
        for c in sem.get('courses', []) 
        if any(str(c.get('grade', '')).upper().startswith(x) for x in ['W', 'WA', 'WF'])
    )
    if withdrawn_courses_count == 0 and completed_credits >= 30:
        strengths.append({
            'category': "الاستمرارية والانضباط في المقررات" if is_ar else "Course Persistence",
            'icon': 'fas fa-check-circle',
            'text': "استمرارية دراسية استثنائية: صفر حالات انسحاب (W/WA/WF) طوال الفصول المسجلة بالجامعة." if is_ar else "Exceptional Retention: Zero course withdrawals (W/WA/WF) recorded across all enrolled semesters."
        })
    elif withdrawn_courses_count > 0:
        weaknesses.append({
            'category': "الانسحاب من المقررات / الحضور" if is_ar else "Course Withdrawals / Attendance",
            'icon': 'fas fa-sign-out-alt',
            'text': f"سجل {withdrawn_courses_count} حالة انسحاب (W/WA/WF)، مما يشير إلى انقطاعات حضور أو صعوبات أثناء منتصف الفصل." if is_ar else f"Recorded {withdrawn_courses_count} course withdrawal(s) (W/WA/WF), signaling mid-term attendance drops or exam drop-outs."
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
            'text': f"مقاومة أكاديمية في {sd['title']}: واجه {sd['failed']} محاولة غير مجتازة بمتوسط درجات {sd['avg_score'] or 'غير متوفر'}%." if is_ar else f"Academic Resistance in {sd['title']}: Encountered {sd['failed']} failed attempt(s) with an average mark of {sd['avg_score'] or 'N/A'}%."
        })

    # Check for critical repeat bottlenecks
    if critical_repeats:
        crit_codes = ", ".join(c['code'] for c in critical_repeats[:3])
        weaknesses.append({
            'category': "المتطلبات السابقة المعلقة" if is_ar else "Prerequisite Blockers",
            'icon': 'fas fa-exclamation-triangle',
            'text': f"متطلبات إجبارية معلقة: مقيد حالياً بـ {len(critical_repeats)} مساق متعثر ({crit_codes}) مما يثقل المعدل التراكمي." if is_ar else f"Unresolved Mandatory Repeats: Currently blocked by {len(critical_repeats)} failed course(s) ({crit_codes}) weighing down cumulative standing."
        })

    # Check for GPA deficit
    if audit['gpa_deficit'] > 0:
        weaknesses.append({
            'category': "عجز المعدل التراكمي" if is_ar else "Cumulative Standing Deficit",
            'icon': 'fas fa-balance-scale',
            'text': f"المعدل التراكمي يقل بمقدار {audit['gpa_deficit']} نقطة عن حد الوضع الأكاديمي السليم الإلزامي 65.0% (المادة 14)." if is_ar else f"Cumulative GPA is {audit['gpa_deficit']} points below the mandatory 65.0% Good Standing mark (Article 14)."
        })

    # Ensure fallback if empty
    if not strengths:
        strengths.append({
            'category': "طالب نشط بالجامعة" if is_ar else "Active Enrollment",
            'icon': 'fas fa-user-check',
            'text': f"طالب نشط أنجز {completed_credits} ساعة معتمدة في الخطة الدراسية لتخصص {audit['program_title']}." if is_ar else f"Active student with {completed_credits} completed credit hours towards the {audit['program_title']} degree."
        })
    if not weaknesses:
        weaknesses.append({
            'category': "تحديات أكاديمية متقدمة" if is_ar else "Advanced Challenge",
            'icon': 'fas fa-info-circle',
            'text': "لا توجد عثرات أكاديمية هيكلية مرصودة. يوصى بمواصلة الاجتهاد في المقررات الاختيارية المتقدمة." if is_ar else "No structural academic deficiencies detected. Maintain diligence in upper-level technical electives."
        })

    # -------------------------------------------------------------
    # 3. BEHAVIORAL PROFILE: "WHAT THE STUDENT DOES"
    # -------------------------------------------------------------
    what_the_student_does = []

    # Behavioral Point 1: Registration Load Habit
    if credit_cap == 12:
        what_the_student_does.append(
            "يسجل وفق ضوابط الملاحظة الأكاديمية بسقف 12 ساعة معتمدة، مما يقلل عبء المواد ويتطلب تركيزاً مضاعفاً." if is_ar else "Enrolls under probation restrictions capped at 12 credit hours, creating a lower course volume but requiring maximum focus."
        )
    elif completed_credits > 0 and num_graded_terms > 0:
        pace = round(completed_credits / num_graded_terms, 1)
        if pace >= 15:
            what_the_student_does.append(
                f"يسجل بانتظام عبئاً دراسياً كاملاً ({pace} ساعة/فصل)، مع إعطاء الأولوية لسرعة إتمام متطلبات التخرج." if is_ar else f"Consistently registers for full-time heavy course loads ({pace} credits/semester), prioritizing fast degree completion."
            )
        else:
            what_the_student_does.append(
                f"يفضل عبئاً دراسياً متوازناً بمعدل {pace} ساعة/فصل، متقدماً في الساعات المعتمدة بنسق منتظم." if is_ar else f"Prefers moderate course loads averaging {pace} credits/semester, pacing out credit completion steadily."
            )

    # Behavioral Point 2: Course Selection Pattern
    if len(audit['critical_repeats']) > 0:
        what_the_student_does.append(
            "يميل إلى تأجيل إعادة المواد المتعثرة مقابل تسجيل متطلبات عامة جديدة، مما يعطل تتابع المتطلبات السابقة دون قصد." if is_ar else "Tends to bypass repeated courses in favor of taking new general requirements, which inadvertently locks prerequisite progression."
        )
    elif len(audit['ready_courses']) > len(audit['blocked_courses']):
        what_the_student_does.append(
            "يلتزم بدقة بتسلسل المتطلبات السابقة، مما يفتح أمامه غالبية مساقات التخصص المتقدمة بالخطة." if is_ar else "Adheres closely to prerequisite sequencing, successfully opening up the majority of downstream curriculum electives."
        )

    # Behavioral Point 3: Trajectory & Recovery Response
    if recent_trend == 'Improving':
        what_the_student_does.append(
            f"أظهر استجابة أكاديمية إيجابية وتحسناً في الفصل الأخير ({progression.get('latest_term_gpa', '')}%) مع إمكانية تعافٍ قوية." if is_ar else f"Demonstrated positive academic responsiveness in the latest semester ({progression.get('latest_term_gpa', '')}%), showing strong rebound potential."
        )
    elif recent_trend == 'Declining':
        what_the_student_does.append(
            "تعرض لتراجع في الدرجات خلال الفصلين الماضيين، غالباً نتيجة الجمع بين مقررات كمية صعبة في آن واحد." if is_ar else "Experienced grade erosion over the past two terms, often due to taking multiple challenging quantitative courses concurrently."
        )
    else:
        what_the_student_does.append(
            "يحافظ على أداء فصلي مستقر وثابت مع فروقات طفيفة بين الفصول الدراسية." if is_ar else "Maintains consistent and stable semester performance with minimal variance across academic terms."
        )

    # -------------------------------------------------------------
    # 4. ACTION MANDATES: "WHAT THE STUDENT MUST DO"
    # -------------------------------------------------------------
    what_the_student_must_do = []

    # Mandate 1: Course Repeats & Prerequisite Unlocking
    if critical_repeats:
        primary_repeat = critical_repeats[0]['code']
        what_the_student_must_do.append({
            'priority': "عاجل" if is_ar else 'URGENT',
            'action': f"التسجيل الفوري في مساق {primary_repeat} في الفصل القادم دون أي تأجيل." if is_ar else f"Register for {primary_repeat} in the immediate upcoming term without exception.",
            'rationale': f"بموجب المادة 18 من لوائح الجامعة، فإن إعادة {primary_repeat} تستبدل درجة الرسوب، مما يرفع المعدل التراكمي مباشرة ويفتح المقررات المعلقة." if is_ar else f"Under DU Article 18, repeating {primary_repeat} replaces the failing score, directly boosting CGPA and unlocking blocked courses.",
            'badge': 'danger'
        })
    elif low_repeats and is_under_probation:
        low_c = low_repeats[0]['code']
        what_the_student_must_do.append({
            'priority': "موصى به" if is_ar else 'RECOMMENDED',
            'action': f"إعادة مساق {low_c} (الدرجة: {low_repeats[0]['grade']}) لرفع المعدل التراكمي." if is_ar else f"Repeat {low_c} (Grade: {low_repeats[0]['grade']}) to elevate CGPA.",
            'rationale': "تتيح المادة 18 إعادة الدرجات المتدنية D/D+ واستبدالها بدرجات أعلى لتسريع الخروج من الملاحظة الأكاديمية." if is_ar else "Article 18 permits repeating D/D+ grades to replace them with higher marks, accelerating probation removal.",
            'badge': 'warning text-dark'
        })
    else:
        top_ready = audit['ready_courses'][0]['code'] if audit['ready_courses'] else ('المتطلب التخصصي التالي' if is_ar else 'next major requirement')
        what_the_student_must_do.append({
            'priority': "متطلب أساسي بالخطة" if is_ar else 'CORE REQUIREMENT',
            'action': f"التسجيل في مساق {top_ready} كحجر زاوية للفصل الدراسي القادم." if is_ar else f"Enroll in {top_ready} as the cornerstone course for the upcoming semester.",
            'rationale': "المتطلبات السابقة مستوفاة بالكامل؛ والالتزام بالخطة يضمن التخرج في الموعد المحدد." if is_ar else "Prerequisites are fully satisfied; maintaining core sequence ensures on-time graduation.",
            'badge': 'primary'
        })

    # Mandate 2: Credit Cap & Schedule Balancing
    if credit_cap == 12:
        what_the_student_must_do.append({
            'priority': "سقف إلزامي (لوائح)" if is_ar else 'MANDATORY RULE',
            'action': "الالتزام الصارم بسقف 12 ساعة معتمدة كحد أقصى (المادة 22 من لوائح جامعة ظفار)." if is_ar else "Strictly enforce the 12 credit hour ceiling (DU Article 22).",
            'rationale': "تسجيل أكثر من 12 ساعة أثناء الملاحظة الأكاديمية محظور باللوائح ويشتت التركيز المطلوب لرفع المعدل." if is_ar else "Taking more than 12 credits while on academic warning is prohibited by university bylaws and dilutes study focus.",
            'badge': 'danger'
        })
    else:
        what_the_student_must_do.append({
            'priority': "توازن الجدول" if is_ar else 'SCHEDULE DESIGN',
            'action': "موازنة الجدول الدراسي بحد أقصى مادتين كميتين مكثفتين + 2-3 مقررات تطبيقية أو عامة." if is_ar else "Balance schedule with maximum 2 heavy quantitative courses + 2-3 applied or general requirements.",
            'rationale': "يمنع الإجهاد الذهني وتضارب الواجبات خلال فترتي الاختبارات النصفية والنهائية." if is_ar else "Prevents cognitive overload during midterm and final examination periods.",
            'badge': 'info text-dark'
        })

    # Mandate 3: Department Tutorial Lab Commitment
    if has_critical_repeats or is_under_probation:
        what_the_student_must_do.append({
            'priority': "دعم ومختبرات تقوية" if is_ar else 'ACADEMIC SUPPORT',
            'action': "الالتزام بحضور 4 إلى 6 ساعات أسبوعياً في مختبرات التقوية للرياضيات والبرمجة بالقسم." if is_ar else "Commit to 4 to 6 hours weekly at Department Mathematics & Programming Tutorial Labs.",
            'rationale': "حلقات الدعم الإرشادي وساعات مكتب أعضاء هيئة التدريس تضمن عدم التراجع قبل تقييمات الأسبوع السادس." if is_ar else "Structured peer tutoring and faculty lab hours prevent falling behind before Week 6 assessments.",
            'badge': 'warning text-dark'
        })
    else:
        what_the_student_must_do.append({
            'priority': "إثراء أكاديمي" if is_ar else 'ENRICHMENT',
            'action': "المشاركة في ورش العمل والهاكاثونات وفرص التدريب البحثي التي ينظمها القسم." if is_ar else "Engage in Department workshop sessions, hackathons, and undergraduate research opportunities.",
            'rationale': "يعزز الجاهزية العملية والملف الإنجازي قبل فترة التدريب الميداني ومشروع التخرج." if is_ar else "Enhances practical portfolio readiness for internship and capstone clearance.",
            'badge': 'success'
        })

    # Mandate 4: Midterm Review & Article 24 Safety Net
    what_the_student_must_do.append({
        'priority': "إجراء وقائي نظامي" if is_ar else 'POLICY SAFEGUARD',
        'action': "إجراء مراجعة إلزامية لنتائج منتصف الفصل في الأسبوع السابع مع المرشد الأكاديمي د. ناصر تبوك." if is_ar else "Conduct mandatory Week 7 Midterm Progress Review with Dr. Nasser Tabook.",
        'rationale': "في حال انخفاض أي درجة عن 60% حتى الأسبوع التاسع، يتم تقييم خيار الانسحاب النظامي (W) قبل موعد الأسبوع العاشر وفق المادة 24 تجنباً لأي رسوب." if is_ar else "If any course grade falls below 60% by Week 9, evaluate the official Withdrawal (W) option before the Week 10 deadline to prevent failing grades.",
        'badge': 'secondary'
    })

    # -------------------------------------------------------------
    # 5. STRATEGIC DEGREE HORIZON & PLANNING
    # -------------------------------------------------------------
    est_semesters = audit['semesters_remaining']
    cur_year = student.year or 'Undergraduate'
    
    # Estimate projected graduation term
    if est_semesters <= 1:
        projected_grad = "الفصل الدراسي القادم (مرحلة إنهاء متطلبات التخرج)" if is_ar else "Upcoming Semester (Degree Clearance Phase)"
        degree_phase = "مرحلة التدقيق واستيفاء شروط التخرج النهائية" if is_ar else "Final Graduation Clearance"
    elif est_semesters <= 2:
        projected_grad = "العام الأكاديمي القادم (المرحلة المتقدمة)" if is_ar else "Next Academic Year (Senior Phase)"
        degree_phase = "مرحلة التخرج ومشاريع التخرج (السنة النهائية)" if is_ar else "Upper-Division Capstone & Senior Electives"
    elif est_semesters <= 4:
        projected_grad = f"خلال ~{est_semesters} فصول دراسية (مرحلة التخصص)" if is_ar else f"Within ~{est_semesters} Semesters (Junior Phase)"
        degree_phase = "مرحلة التخصص الأساسي (السنة الثالثة)" if is_ar else "Core Major Specialization"
    else:
        projected_grad = f"خلال ~{est_semesters} فصول دراسية" if is_ar else f"Within ~{est_semesters} Semesters"
        degree_phase = "مرحلة المقررات العامة والتأسيسية" if is_ar else "Foundation & Intermediate Core"

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
    crit_course = critical_repeats[0]['code'] if critical_repeats else ('المقررات السابقة' if is_ar else 'previous terms')
    
    if archetype_key in ['high_risk_probation', 'probation_struggler']:
        if is_ar:
            advisor_tone = "حازم ومباشر ومنهجي، مع حواجز أمان غير قابلة للتفاوض بشأن المتطلبات السابقة وسقف الساعات."
            meeting_cadence = "متابعة دورية إلزامية كل أسبوعين (الأسابيع 2 و 4 و 7 و 10)"
            opening_statement = f"مرحباً {student.name}، أولويتنا القصوى هي حماية وضعك الأكاديمي وضمان استمرارك بالجامعة. دعنا نراجع جدول التعافي المحدد بـ 12 ساعة معتمدة وخطة حضور مختبرات التقوية."
            suggested_questions = [
                f"ما هي الصعوبات المحددة التي واجهتك في مساق {crit_course} خلال الفصول السابقة؟",
                "كم ساعة تخصصها يومياً للمذاكرة ومراجعة المواد خارج أوقات المحاضرات؟",
                "هل يمكنك الالتزام التام بحضور مختبرات التقوية يومي الثلاثاء والخميس أسبوعياً؟"
            ]
        else:
            advisor_tone = "Firm, direct, and structured with non-negotiable prerequisite guardrails."
            meeting_cadence = "Mandatory Bi-Weekly check-in (Weeks 2, 4, 7, 10)"
            opening_statement = f"Hello {student.name}, our priority is strictly safeguarding your enrollment status. Let us review your 12-credit recovery schedule and lab attendance agreement."
            suggested_questions = [
                f"What specific hurdles caused you difficulty in {critical_repeats[0]['code'] if critical_repeats else 'previous terms'}?",
                "How many hours each day do you allocate to study outside of scheduled class hours?",
                "Can you commit to attending the tutorial labs every Tuesday and Thursday afternoon?"
            ]
    elif archetype_key == 'probation_fighter':
        if is_ar:
            advisor_tone = "مشجع ومحفز للبناء على الزخم الإيجابي، مع التركيز على المسؤولية الذاتية والانضباط."
            meeting_cadence = "متابعة دورية كل ثلاثة أسابيع (الأسابيع 3 و 7 و 10)"
            opening_statement = f"أهلاً بك يا {student.name}! تقدمك في الفصل الماضي أثبت امتلاكك القدرة على تجاوز الملاحظة واستعادة وضعك الطبيعي. نحن هنا اليوم لتثبيت هذا النجاح ومواصلة الصعود."
            suggested_questions = [
                "ما هي أساليب وطرق المذاكرة التي أثبتت نجاحها معك وحققت بها هذا التحسن في الفصل الماضي؟",
                "هل هناك أي مساق في هذا الفصل تشعر أن درجاتك فيه قد تنخفض عن 70%؟",
                "هل اطلعت على حساب نقاط استبدال الدرجة وكيف تسهم المادة 18 في رفع معدلك التراكمي؟"
            ]
        else:
            advisor_tone = "Encouraging, momentum-building, and accountability-oriented."
            meeting_cadence = "Tri-weekly check-in (Weeks 3, 7, 10)"
            opening_statement = f"Welcome {student.name}! Your progress last term proved you have the capability to clear probation. We are here to lock in that success this term."
            suggested_questions = [
                "What study routines worked best for you during your improvement last semester?",
                "Are there any courses this term where you feel quiz scores might dip below 70%?",
                "Have you reviewed the grade replacement points calculation under DU Article 18?"
            ]
    elif archetype_key == 'prereq_bottleneck':
        crit_math = critical_repeats[0]['code'] if critical_repeats else ('مساقات الرياضيات الأساسية' if is_ar else 'core math')
        if is_ar:
            advisor_tone = "تشخيصي يركز على حل المشكلات الأكاديمية وإزالة العقبات في الخطة الدراسية."
            meeting_cadence = "مراجعة قبل التسجيل + متابعة منتصف الفصل في الأسبوع السابع"
            opening_statement = f"مرحباً {student.name}، أداؤك جيد في معظم المساقات، لكننا بحاجة لمعالجة التعثر في مساق {crit_math} حتى تفتح أمامك المقررات المتقدمة بالخطة."
            suggested_questions = [
                f"أين تكمن الصعوبة تحديداً عند دراسة مساق {crit_math} (فهم المحاضرات، حل الواجبات، أم ضيق وقت الاختبار)؟",
                "هل تسجيل هذا المساق مع مقررات عامة خفيفة يوفر لك الوقت والتركيز الكافي لاجتيازه؟",
                "هل تشارك في مجموعات دراسية أو تستفيد من الساعات المكتبية لمدرس المادة؟"
            ]
        else:
            advisor_tone = "Diagnostic, problem-solving, and curriculum-focused."
            meeting_cadence = "Pre-registration review + Week 7 midterm check-in"
            opening_statement = f"Hello {student.name}, you are doing well in your broader courses, but we need to solve the bottleneck in {critical_repeats[0]['code'] if critical_repeats else 'core math'} so your upper-level courses unlock."
            suggested_questions = [
                f"Where exactly does the gap emerge when studying {critical_repeats[0]['code'] if critical_repeats else 'this course'} (lectures, assignments, or exam timing)?",
                "Would pairing this course with lighter electives give you the study bandwidth you need?",
                "Are you working with a study partner or attending the Department instructor office hours?"
            ]
    elif archetype_key == 'high_achiever':
        if is_ar:
            advisor_tone = "توجيهي وتطويري، يركز على التميز والفرص البحثية والمستقبل المهني."
            meeting_cadence = "جلسة افتتاحية ببداية الفصل + توجيه لمشروع التخرج والتدريب"
            opening_statement = f"أهلاً وسهلاً بك يا {student.name}. مسارك الأكاديمي متميز ومصدر فخر للقسم. دعنا نتحدث عن الأبحاث وفرص التدريب العملي المتقدم وتعزيز محفظتك الأكاديمية."
            suggested_questions = [
                "هل لديك اهتمام بالمشاركة في الأبحاث الطلابية أو المسابقات البرمجية الإقليمية؟",
                "هل بدأت باستكشاف فرص التدريب الميداني الصيفي في كبرى المؤسسات والشركات التقنية؟",
                "كيف يمكن للقسم دعم طموحاتك في الدراسات العليا أو الحصول على شهادات احترافية دولية؟"
            ]
        else:
            advisor_tone = "Mentoring, acceleration-oriented, and aspirational."
            meeting_cadence = "Semester kickoff & Capstone/Internship guidance"
            opening_statement = f"Great to see you {student.name}. Your academic trajectory is outstanding. Let us talk about research, internships, and maximizing your honors portfolio."
            suggested_questions = [
                "Are you interested in undergraduate research or participating in regional student competitions?",
                "Have you started exploring industry internship opportunities for the upcoming summer?",
                "How can the Department support your postgraduate or career placement goals?"
            ]
    else:
        if is_ar:
            advisor_tone = "داعم ومنهجي، يركز على انسيابية التقدم الدراسي نحو التخرج."
            meeting_cadence = "فترة التسجيل المعتادة + متابعة منتصف الفصل في الأسبوع السابع"
            opening_statement = f"مرحباً {student.name}. دعنا نراجع خطتك الدراسية لضمان أن تسجيلك للفصل القادم يبقيك على المسار الأيسر والأسرع نحو التخرج."
            suggested_questions = [
                "ما رأيك في توازن العبء الدراسي والمواد في جدولك لهذا الفصل؟",
                "هل توجد مساقات اختيارية محددة في التخصص ترغب بالتركيز عليها وتسجيلها مستقبلاً؟",
                "هل يتوافق جدول المحاضرات الحالي مع مواعيد تنقلك وجدولك اليومي؟"
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
