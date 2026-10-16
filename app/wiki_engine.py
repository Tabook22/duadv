"""
Academic Advising Wiki & LLM Intelligence Engine for Dhofar University
Provides structured synthesis of all university regulations, degree plans of study,
and interactive question-answering with policy citations.
"""

import os
import re
from typing import Dict, List, Any, Optional
from app.utils import load_policies_from_file, search_policy_documents
from app.study_plans_registry import get_all_registered_study_plans

def get_wiki_knowledge_base(lang: Optional[str] = None) -> Dict[str, Any]:
    """
    Compile comprehensive Dhofar University Academic Advising Knowledge Base
    synthesized from official regulations, degree roadmaps, and advising handbooks.
    """
    if lang is None:
        try:
            from app.i18n import get_current_language
            lang = get_current_language()
        except Exception:
            lang = 'en'
    is_ar = (lang == 'ar')
    from app.i18n import (
        localize_program, localize_degree_type, localize_course_name,
        localize_category, localize_year
    )
    import copy

    raw_plans = copy.deepcopy(get_all_registered_study_plans())
    if is_ar:
        plan_iter = raw_plans if isinstance(raw_plans, list) else raw_plans.values()
        for plan in plan_iter:
            plan['program_title'] = localize_program(plan.get('program_title', ''), lang='ar')
            plan['degree_type'] = localize_degree_type(plan.get('degree_type', ''), lang='ar')
            plan['source_document'] = (
                'الخطة الدراسية الرسمية المعتمدة بجامعة ظفار'
                if 'Plan of Study' in plan.get('source_document', '') else
                'متطلبات دراسة دبلوم علوم الحاسوب بجامعة ظفار'
            )
            if plan.get('bridge_to_bachelor'):
                plan['bridge_to_bachelor']['eligible_programs'] = [
                    localize_program(ep, lang='ar') for ep in plan['bridge_to_bachelor'].get('eligible_programs', [])
                ]
                plan['bridge_to_bachelor']['description'] = (
                    'يؤهل الحصول على معدل تراكمي >= 75% في الدبلوم للانتقال المباشر (التجسير) إلى السنة الثالثة في برامج البكالوريوس بجامعة ظفار.'
                )
            for c in plan.get('curriculum', []):
                c['name'] = localize_course_name(c.get('name', ''), lang='ar')
                c['category'] = localize_category(c.get('category', ''), lang='ar')
                c['term_recommended'] = localize_year(c.get('term_recommended', ''), lang='ar')

    if is_ar:
        policy_modules = [
            {
                "id": "probation_standing",
                "title": "لوائح الوضع الأكاديمي والملاحظة الأكاديمية والفصل",
                "article": "المادة ١٤ والمادة ١٥",
                "source_doc": "لوائح الدراسات الجامعية الأولى بجامعة ظفار",
                "icon": "fa-exclamation-triangle",
                "badge_color": "danger",
                "summary": "اللوائح الإلزامية المنظمة لحدود المعدل التراكمي، ومراحل تصاعد الملاحظة الأكاديمية، وضوابط الفصل الأكاديمي.",
                "rules": [
                    {
                        "title": "حد الوضع الأكاديمي السليم (٦٥.٠٪)",
                        "clause": "يجب على جميع طلبة البكالوريوس والدبلوم الحفاظ على معدل تراكمي (CGPA) لا يقل عن ٦٥.٠٪ للبقاء في الوضع الأكاديمي السليم.",
                        "citation": "المادة ١٤.١"
                    },
                    {
                        "title": "الملاحظة الأكاديمية الأولى",
                        "clause": "يوضع الطالب الذي ينخفض معدله التراكمي عن ٦٥.٠٪ بنهاية أي فصل دراسي اعتيادي (خريف أو ربيع) تحت الملاحظة الأكاديمية الأولى، ويُقيد عبؤه الدراسي بحد أقصى ١٢ ساعة معتمدة.",
                        "citation": "المادة ١٤.٢"
                    },
                    {
                        "title": "الملاحظة الأكاديمية الثانية",
                        "clause": "إذا أخفق الطالب الخاضع للملاحظة الأولى في تحقيق معدل فصلي >= ٦٥.٠٪ وظل معدله التراكمي أقل من ٦٥.٠٪، ينتقل إلى الملاحظة الأكاديمية الثانية.",
                        "citation": "المادة ١٤.٣"
                    },
                    {
                        "title": "الملاحظة الأكاديمية الصارمة (الثانية / الثالثة)",
                        "clause": "يؤدي استمرار تدني المعدل إلى الملاحظة الأكاديمية الصارمة ويكون الطالب تحت إنذار مباشر بالفصل الأكاديمي، مع إلزامية المتابعة الإرشادية كل أسبوعين وسقف ١٢ ساعة معتمدة.",
                        "citation": "المادة ١٤.٤"
                    },
                    {
                        "title": "رفع الملاحظة واستعادة الوضع السليم",
                        "clause": "عندما يرفع الطالب معدله التراكمي إلى ٦٥.٠٪ فأعلى، تُرفع عنه الملاحظة الأكاديمية ويعود للوضع السليم ويسمح له بالعبء الاعتيادي (١٥–١٨ ساعة).",
                        "citation": "المادة ١٤.٥"
                    }
                ]
            },
            {
                "id": "course_repetition",
                "title": "لوائح إعادة المقررات واستبدال الدرجات",
                "article": "المادة ١٨",
                "source_doc": "لوائح الدراسات الجامعية الأولى بجامعة ظفار",
                "icon": "fa-redo-alt",
                "badge_color": "warning",
                "summary": "القواعد المنظمة لإعادة المساقات ذات التقديرات المتدنية أو الراسبة لرفع المعدل التراكمي.",
                "rules": [
                    {
                        "title": "المقررات المؤهلة للإعادة",
                        "clause": "يجوز لطالب المرحلة الجامعية الأولى إعادة أي مقرر حصل فيه على تقدير F أو D أو D+.",
                        "citation": "المادة ١٨.١"
                    },
                    {
                        "title": "استبدال الدرجة في المعدل التراكمي",
                        "clause": "عند إعادة الطالب لمقرر دراسي، تُحتسب الدرجة الأعلى المحققة في حساب المعدل التراكمي، مع بقاء جميع المحاولات مدونة في السجل الأكاديمي الرسمي.",
                        "citation": "المادة ١٨.٢"
                    },
                    {
                        "title": "أولوية إعادة المتطلبات السابقة",
                        "clause": "يلتزم المرشدون الأكاديميون بإعطاء الأولوية لإعادة المتطلبات السابقة الراسبة أو ذات التقدير المتدني قبل السماح بالتسجيل في المقررات المتقدمة.",
                        "citation": "المادة ١٨.٣"
                    }
                ]
            },
            {
                "id": "registration_credit_limits",
                "title": "تسجيل المقررات والحد الأقصى للساعات المعتمدة",
                "article": "المادة ٢٢",
                "source_doc": "لوائح الدراسات الجامعية الأولى بجامعة ظفار",
                "icon": "fa-calendar-check",
                "badge_color": "primary",
                "summary": "ضوابط الساعات المعتمدة الفصلية بناءً على الوضع الأكاديمي للطالب.",
                "rules": [
                    {
                        "title": "العبء الدراسي الاعتيادي",
                        "clause": "يتراوح العبء الدراسي الفصلي الاعتيادي لطلبة البكالوريوس والدبلوم بين ١٥ و١٨ ساعة معتمدة في الفصل الاعتيادي.",
                        "citation": "المادة ٢٢.١"
                    },
                    {
                        "title": "سقف الملاحظة الأكاديمية (١٢ ساعة معتمدة)",
                        "clause": "لا يجوز للطلبة الخاضعين لأي مرحلة من مراحل الملاحظة الأكاديمية التسجيل لأكثر من ١٢ ساعة معتمدة دون استثناء خطي رسمي من عميد الكلية.",
                        "citation": "المادة ٢٢.٢"
                    },
                    {
                        "title": "العبء الإضافي لطلبة فصل التخرج",
                        "clause": "يجوز لطلبة السنة النهائية في فصل تخرجهم التسجيل لما يصل إلى ١٩–٢١ ساعة معتمدة بموافقة عميد الكلية.",
                        "citation": "المادة ٢٢.٣"
                    }
                ]
            },
            {
                "id": "add_drop_withdrawal",
                "title": "تقويم الحذف والإضافة والانسحاب (W/WF) والدرجة غير المكتملة",
                "article": "القسم ٢ و ٣",
                "source_doc": "دليل الإرشاد الأكاديمي بجامعة ظفار",
                "icon": "fa-exchange-alt",
                "badge_color": "info",
                "summary": "المواعيد النهائية لتعديل الجداول، وعقوبات الانسحاب غير الرسمي، وتسوية الدرجات غير المكتملة.",
                "rules": [
                    {
                        "title": "أسبوع الحذف والإضافة",
                        "clause": "يُسمح بإضافة المقررات وتعديل الشعب فقط خلال الأسبوع الأول الرسمي من الفصل الدراسي عبر بوابة نظام معلومات الطلبة.",
                        "citation": "دليل الإرشاد ٢.١"
                    },
                    {
                        "title": "الانسحاب النظامي من المقرر (W)",
                        "clause": "يجوز للطالب الانسحاب من المقرر بتقدير (W) قبل نهاية الأسبوع العاشر بموافقة المرشد الأكاديمي، ولا يؤثر تقدير W في حساب المعدل التراكمي.",
                        "citation": "دليل الإرشاد ٢.٢"
                    },
                    {
                        "title": "عقوبة الانسحاب غير الرسمي أو الحرمان (WF)",
                        "clause": "الانقطاع عن الحضور بعد الأسبوع العاشر دون انسحاب رسمي يؤدي لرصد تقدير (WF) ويُحسب صفراً (٠٪ / F) في المعدل التراكمي.",
                        "citation": "دليل الإرشاد ٢.٣"
                    },
                    {
                        "title": "تسوية الدرجة غير المكتملة (I)",
                        "clause": "يجب استكمال متطلبات الدرجة غير المكتملة (I) خلال أربعة أسابيع من بداية الفصل الاعتيادي التالي، وإلا تتحول تلقائياً إلى راسب (F).",
                        "citation": "دليل الإرشاد ٣.١"
                    }
                ]
            },
            {
                "id": "diploma_to_bachelor",
                "title": "شروط القبول والاستمرار بالدبلوم والتجسير إلى البكالوريوس",
                "article": "الأقسام ١ و ٢ و ٣",
                "source_doc": "متطلبات دراسة دبلوم علوم الحاسوب بجامعة ظفار",
                "icon": "fa-project-diagram",
                "badge_color": "success",
                "summary": "المتطلبات السابقة، وشروط التخرج، وضوابط تجسير خريجي الدبلوم إلى برامج البكالوريوس.",
                "rules": [
                    {
                        "title": "الوضع السليم لطلبة الدبلوم",
                        "clause": "يجب على طلبة الدبلوم الحفاظ على معدل تراكمي لا يقل عن ٦٥.٠٪، وإجمالي الساعات المطلوبة للتخرج هو ٦٥ ساعة معتمدة.",
                        "citation": "دليل الدبلوم - قسم ٢"
                    },
                    {
                        "title": "التجسير للبكالوريوس (المعدل التراكمي >= ٧٥٪)",
                        "clause": "يتأهل خريجو دبلوم علوم الحاسوب الحاصلون على معدل تراكمي >= ٧٥.٠٪ للانتقال المباشر ومعادلة المقررات في بكالوريوس علوم الحاسوب أو الأمن السيبراني أو علم البيانات.",
                        "citation": "دليل الدبلوم - قسم ٣"
                    },
                    {
                        "title": "معادلة الساعات المعتمدة",
                        "clause": "تُعادل جميع المقررات الجامعية المجتازة بدرجة >= ٦٠٪ ضمن خطة البكالوريوس، مما يختصر متطلبات البكالوريوس بما يصل إلى ٦٠ ساعة معتمدة.",
                        "citation": "دليل الدبلوم - قسم ٣.٢"
                    }
                ]
            }
        ]
    else:
        policy_modules = [
            {
                "id": "probation_standing",
                "title": "Academic Standing, Probation & Dismissal Bylaws",
                "article": "Article 14 & Article 15",
                "source_doc": "DU Undergraduate Academic Regulations",
                "icon": "fa-exclamation-triangle",
                "badge_color": "danger",
                "summary": "Mandatory bylaws governing cumulative GPA thresholds, probation escalation stages, and dismissal criteria.",
                "rules": [
                    {
                        "title": "Good Standing Threshold",
                        "clause": "All undergraduate and diploma students must maintain a cumulative Grade Point Average (CGPA) of at least 65.0%.",
                        "citation": "Article 14.1"
                    },
                    {
                        "title": "First Academic Probation",
                        "clause": "A student whose CGPA falls below 65.0% at the end of any regular semester (Fall or Spring) is placed on First Probation. Course load is restricted to a maximum of 12 credit hours.",
                        "citation": "Article 14.2"
                    },
                    {
                        "title": "Second Academic Probation",
                        "clause": "If a student on First Probation fails to achieve a semester average >= 65.0% and cumulative GPA remains < 65.0%, they escalate to Second Probation.",
                        "citation": "Article 14.3"
                    },
                    {
                        "title": "Strict Academic Probation (2nd / 3rd)",
                        "clause": "Continued failure to remediate GPA leads to Strict Probation. The student is under imminent academic dismissal warning. Mandatory bi-weekly advising reviews and maximum 12 credit hours limit.",
                        "citation": "Article 14.4"
                    },
                    {
                        "title": "Probation Removal & Recovery",
                        "clause": "When a student elevates their cumulative GPA to >= 65.0%, they are cleared to Normal / Good Standing and standard 15-18 credit load allowances are restored.",
                        "citation": "Article 14.5"
                    }
                ]
            },
            {
                "id": "course_repetition",
                "title": "Course Repetition & Grade Replacement Bylaws",
                "article": "Article 18",
                "source_doc": "DU Undergraduate Academic Regulations",
                "icon": "fa-redo-alt",
                "badge_color": "warning",
                "summary": "Rules for repeating courses with low or failing grades to remediate cumulative GPA.",
                "rules": [
                    {
                        "title": "Eligible Courses for Repetition",
                        "clause": "An undergraduate student may repeat any course in which they received an F, D, or D+ grade.",
                        "citation": "Article 18.1"
                    },
                    {
                        "title": "Grade Replacement in CGPA",
                        "clause": "When a student repeats a course, the highest grade achieved is calculated in the cumulative GPA. All previous attempts remain noted on the student's official transcript.",
                        "citation": "Article 18.2"
                    },
                    {
                        "title": "Prerequisite Repetition Priority",
                        "clause": "Academic advisors must mandate repeating failed or low-grade prerequisite courses before authorizing enrollment in advanced sequence courses.",
                        "citation": "Article 18.3"
                    }
                ]
            },
            {
                "id": "registration_credit_limits",
                "title": "Course Registration, Credit Limits & Overloads",
                "article": "Article 22",
                "source_doc": "DU Undergraduate Academic Regulations",
                "icon": "fa-calendar-check",
                "badge_color": "primary",
                "summary": "Semester credit hour boundaries based on student academic standing.",
                "rules": [
                    {
                        "title": "Standard Full-Time Load",
                        "clause": "Standard undergraduate semester course load is 15 to 18 credit hours per regular semester.",
                        "citation": "Article 22.1"
                    },
                    {
                        "title": "Probation Cap (12 Credit Hours)",
                        "clause": "Students placed on any stage of academic probation cannot register for more than 12 credit hours without formal written exemption from the Dean.",
                        "citation": "Article 22.2"
                    },
                    {
                        "title": "Graduating Senior Overload",
                        "clause": "Graduating seniors in their final semester before graduation may register for up to 19 to 21 credit hours with Dean approval.",
                        "citation": "Article 22.3"
                    }
                ]
            },
            {
                "id": "add_drop_withdrawal",
                "title": "Add/Drop Calendar, Withdrawal (W/WF) & Incompletes",
                "article": "Section 2 & 3",
                "source_doc": "DU Academic Advising Handbook",
                "icon": "fa-exchange-alt",
                "badge_color": "info",
                "summary": "Deadlines for course schedule changes, withdrawal penalties, and resolving incomplete grades.",
                "rules": [
                    {
                        "title": "Add/Drop Week",
                        "clause": "Course additions and section adjustments are permitted only during the first official week of the semester via the SIS portal.",
                        "citation": "Handbook Sec 2.1"
                    },
                    {
                        "title": "Course Withdrawal (W)",
                        "clause": "A student may withdraw from a course with a grade of 'W' prior to the end of the 10th week with academic advisor approval. A grade of W carries 0 credit points and does not impact GPA.",
                        "citation": "Handbook Sec 2.2"
                    },
                    {
                        "title": "Unofficial Withdrawal Penalty (WF)",
                        "clause": "Discontinuing attendance after the 10th week without official withdrawal results in a recorded grade of 'WF' (Withdrawn Failing), calculated as 0% (F) in cumulative GPA.",
                        "citation": "Handbook Sec 2.3"
                    },
                    {
                        "title": "Incomplete (I) Grade Resolution",
                        "clause": "An incomplete grade must be resolved within four weeks of the start of the subsequent regular semester, or it automatically converts to an F.",
                        "citation": "Handbook Sec 3.1"
                    }
                ]
            },
            {
                "id": "diploma_to_bachelor",
                "title": "Diploma Admission, Continuation & Bridge to Bachelor",
                "article": "Section 1, 2 & 3",
                "source_doc": "Requirements for Studying Computer Science Diploma",
                "icon": "fa-project-diagram",
                "badge_color": "success",
                "summary": "Prerequisites, graduation criteria, and articulation requirements for Diploma graduates bridging to B.Sc.",
                "rules": [
                    {
                        "title": "Diploma Good Standing",
                        "clause": "Diploma students must maintain a minimum cumulative GPA of 65.0%. Total required credit hours to graduate: 65 Credit Hours.",
                        "citation": "Diploma Guide Sec 2"
                    },
                    {
                        "title": "Bridge Articulation to Bachelor (GPA >= 75%)",
                        "clause": "Graduates of the Computer Science Diploma program who achieve a cumulative GPA of >= 75.0% qualify for direct articulation and course transfer into the B.Sc. in Computer Science, Cybersecurity, or Data Science.",
                        "citation": "Diploma Guide Sec 3"
                    },
                    {
                        "title": "Transferable Credits",
                        "clause": "All college-level courses with grades of >= 60% are transferable towards the Bachelor degree, reducing the Bachelor completion requirement by up to 60 credit hours.",
                        "citation": "Diploma Guide Sec 3.2"
                    }
                ]
            }
        ]
    
    return {
        "study_plans": raw_plans,
        "policy_modules": policy_modules,
        "total_documents": len(load_policies_from_file())
    }

def ask_advising_wiki(question: str, lang: Optional[str] = None) -> Dict[str, Any]:
    """
    Intelligent Academic Advising Assistant:
    Answers advisor questions using full-text search across policy books,
    synthesizing exact answers and citing DU regulations.
    """
    if lang is None:
        try:
            from app.i18n import get_current_language
            lang = get_current_language()
        except Exception:
            lang = 'en'
    is_ar = (lang == 'ar')

    if not question or not question.strip():
        return {
            "status": "error",
            "message": "لا يمكن أن يكون حقل السؤال فارغاً." if is_ar else "Question query cannot be empty."
        }
        
    q_clean = question.strip()
    q_lower = q_clean.lower()
    
    # 1. First retrieve direct matches from uploaded PDFs
    doc_matches = search_policy_documents(q_clean)
    
    # 2. Check for LLM API Key (e.g. Gemini)
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            context_text = ""
            for dm in doc_matches[:3]:
                context_text += f"\nDocument: {dm['title']}\n"
                for m in dm.get('matches', []):
                    context_text += f"- Page {m['page']}: {m['snippet']}\n"
                    
            lang_instruction = "Respond in professional academic Arabic." if is_ar else "Provide a clear, structured advising response in English."
            prompt = (
                "You are the Dhofar University Academic Advising AI Assistant for Dr. Nasser Tabook. "
                "Answer the following advisor question accurately based on Dhofar University regulations and study plans. "
                f"Quote exact article numbers and policy guidelines where applicable. {lang_instruction}\n\n"
                f"Context from University Documents:\n{context_text}\n\n"
                f"Question: {q_clean}\n\n"
            )
            resp = model.generate_content(prompt)
            if resp and resp.text:
                return {
                    "status": "success",
                    "answer": resp.text.strip(),
                    "sources": doc_matches[:3],
                    "engine": "محرك الذكاء الاصطناعي لجامعة ظفار (متصل)" if is_ar else "Google Gemini AI (Online)"
                }
        except Exception:
            pass
            
    # 3. High-Fidelity Local Semantic Synthesis Engine (Offline Fallback)
    answer_parts = []
    citations = []
    
    if any(k in q_lower for k in ["probation", "strict", "standing", "warning", "dismissal", "gpa 65", "ملاحظة", "انذار", "إنذار", "فصل", "معدل", "صارمة"]):
        if is_ar:
            answer_parts.append(
                "### لوائح الوضع الأكاديمي والملاحظة الأكاديمية بجامعة ظفار\n\n"
                "* **حد الوضع الأكاديمي السليم:** بموجب **المادة ١٤.١**، يجب على جميع طلبة البكالوريوس والدبلوم الحفاظ على معدل تراكمي لا يقل عن **٦٥.٠٪**.\n"
                "* **الملاحظة الأكاديمية الأولى:** تُطبق عند انخفاض المعدل التراكمي عن ٦٥.٠٪ بنهاية أي فصل اعتيادي، ويُقيد العبء الدراسي بحد أقصى **١٢ ساعة معتمدة** (المادتان ١٤.٢ و٢٢.٢).\n"
                "* **الملاحظة الأكاديمية الثانية:** إذا لم يحقق الطالب الخاضع للملاحظة الأولى معدلاً فصلياً >= ٦٥.٠٪ وظل معدله التراكمي دون ٦٥.٠٪ ينتقل للملاحظة الثانية.\n"
                "* **الملاحظة الأكاديمية الصارمة (الثانية / الثالثة):** استمرار التعثر يصعد الحالة إلى الملاحظة الصارمة مع إنذار بالفصل الأكاديمي وإلزامية المتابعة الإرشادية كل أسبوعين.\n"
                "* **رفع الملاحظة:** عند رفع المعدل التراكمي إلى ٦٥.٠٪ فأعلى، تُرفع الملاحظة ويعود الطالب للوضع الأكاديمي السليم."
            )
            citations.append("لوائح الدراسات الجامعية الأولى بجامعة ظفار، المادتان ١٤ و٢٢")
        else:
            answer_parts.append(
                "### Dhofar University Academic Standing & Probation Rules\n\n"
                "* **Cumulative GPA Threshold:** Under **Article 14.1**, all undergraduate and diploma students must maintain a cumulative GPA of at least **65.0%** to remain in Good Standing.\n"
                "* **First Probation:** Triggered when CGPA falls below 65.0% at the end of any regular semester. Course load is strictly capped at **12 credit hours** (Article 14.2 & 22.2).\n"
                "* **Second Probation:** If a student on First Probation does not achieve a semester average of at least 65.0% and their cumulative GPA remains below 65.0%, they advance to Second Probation.\n"
                "* **Strict Probation (2nd / 3rd):** Continued deficiency escalates the student to Strict Probation with imminent academic dismissal warning. The advisor must hold mandatory bi-weekly counseling and formulate an Academic Recovery Plan.\n"
                "* **Probation Removal:** When a student elevates their cumulative GPA to >= 65.0%, they are cleared to Normal Standing."
            )
            citations.append("Dhofar University Undergraduate Academic Regulations, Article 14 & 22")
        
    elif any(k in q_lower for k in ["repeat", "repeating", "replace", "grade replacement", "d grade", "f grade", "اعادة", "إعادة", "استبدال", "رسوب"]):
        if is_ar:
            answer_parts.append(
                "### لوائح إعادة المقررات واستبدال الدرجات (المادة ١٨)\n\n"
                "* **المقررات المسموح بإعادتها:** بموجب **المادة ١٨.١**، يجوز للطالب إعادة أي مقرر حصل فيه على تقدير **F أو D أو D+**.\n"
                "* **احتساب الدرجة الأعلى:** عند إعادة المقرر، يتم احتساب **الدرجة الأعلى المحققة** في المعدل التراكمي (المادة ١٨.٢)، مع بقاء المحاولات السابقة ظاهرة في السجل الأكاديمي.\n"
                "* **القاعدة الإرشادية:** يجب إعطاء الأولوية لإعادة المتطلبات السابقة المتعثرة قبل السماح بالتسجيل في المقررات المتقدمة."
            )
            citations.append("لوائح الدراسات الجامعية الأولى بجامعة ظفار، المادة ١٨")
        else:
            answer_parts.append(
                "### Course Repetition & Grade Replacement Bylaws\n\n"
                "* **Eligible Grades:** Under **Article 18.1**, a student may repeat any course in which they received a grade of **F, D, or D+**.\n"
                "* **Highest Grade Counts:** When repeating a course, the **highest grade obtained** is used in the calculation of the cumulative GPA (Article 18.2). All historical attempts remain visible on the official transcript.\n"
                "* **Advising Rule:** Advisors must prioritize repeating prerequisite courses with low grades before allowing students to enroll in advanced downstream subjects."
            )
            citations.append("Dhofar University Undergraduate Academic Regulations, Article 18")

    elif any(k in q_lower for k in ["credit", "limit", "overload", "maximum", "load", "hours", "ساعات", "عبء", "سقف"]):
        if is_ar:
            answer_parts.append(
                "### العبء الدراسي والحد الأقصى للساعات المعتمدة (المادة ٢٢)\n\n"
                "* **طلبة الملاحظة الأكاديمية:** يُحدد سقف التسجيل بـ **١٢ ساعة معتمدة** كحد أقصى في الفصل الدراسي (**المادة ٢٢.٢**).\n"
                "* **الوضع الأكاديمي السليم:** العبء الدراسي الاعتيادي هو **١٥ إلى ١٨ ساعة معتمدة** (**المادة ٢٢.١**).\n"
                "* **طلبة فصل التخرج:** يجوز لهم التسجيل لما يصل إلى **١٩–٢١ ساعة معتمدة** في فصل التخرج النهائي بموافقة عميد الكلية (**المادة ٢٢.٣**)."
            )
            citations.append("لوائح الدراسات الجامعية الأولى بجامعة ظفار، المادة ٢٢")
        else:
            answer_parts.append(
                "### Course Load & Credit Limits\n\n"
                "* **Probation Students:** Strictly capped at a maximum of **12 credit hours** per semester (**Article 22.2**). No overloads permitted without written Dean authorization.\n"
                "* **Normal Good Standing:** Standard undergraduate full-time course load is **15 to 18 credit hours** (**Article 22.1**).\n"
                "* **Graduating Seniors:** May register for up to **19–21 credit hours** in their final graduating semester with Dean approval (**Article 22.3**)."
            )
            citations.append("Dhofar University Undergraduate Academic Regulations, Article 22")

    elif any(k in q_lower for k in ["bridge", "diploma to bachelor", "articulation", "transfer", "تجسير", "دبلوم", "انتقال"]):
        if is_ar:
            answer_parts.append(
                "### شروط التجسير من الدبلوم إلى البكالوريوس\n\n"
                "* **الحد الأدنى للمعدل التراكمي:** بموجب **القسم ٣ من متطلبات دبلوم علوم الحاسوب**، يجب تحقيق معدل تراكمي لا يقل عن **٧٥.٠٪** للتأهل للانتقال المباشر إلى برامج البكالوريوس.\n"
                "* **مسارات التجسير المتاحة:**\n"
                "  ١. بكالوريوس العلوم في علوم الحاسوب\n"
                "  ٢. بكالوريوس العلوم في الأمن السيبراني\n"
                "  ٣. بكالوريوس العلوم في علم البيانات\n"
                "* **معادلة الساعات:** تُعادل كافة مقررات الدبلوم المجتازة بدرجة >= ٦٠٪ بما يختصر متطلبات البكالوريوس بنحو ٦٠ ساعة معتمدة."
            )
            citations.append("متطلبات دراسة دبلوم علوم الحاسوب، القسم ٣")
        else:
            answer_parts.append(
                "### Bridge Requirements from Diploma to Bachelor's Degree\n\n"
                "* **Minimum GPA Required:** Under **Section 3 of the CS Diploma Requirements**, graduates must achieve a cumulative GPA of at least **75.0%** to qualify for direct articulation into B.Sc. degree programs.\n"
                "* **Available Articulation Pathways:** Graduates can bridge into:\n"
                "  1. Bachelor of Science in Computer Science\n"
                "  2. Bachelor of Science in Cybersecurity\n"
                "  3. Bachelor of Science in Data Science\n"
                "* **Credit Articulation:** All completed diploma courses with grades >= 60% are transferred, reducing Bachelor requirements by approximately 60 credit hours."
            )
            citations.append("Requirements for Studying Computer Science Diploma, Section 3")

    elif any(k in q_lower for k in ["cyber", "cybersecurity", "سيبراني", "أمن"]):
        if is_ar:
            answer_parts.append(
                "### نظرة عامة على بكالوريوس العلوم في الأمن السيبراني\n\n"
                "* **إجمالي الساعات:** ١٢٤ ساعة معتمدة موزعة على ٨ فصول دراسية (٤ سنوات).\n"
                "* **السنة الأولى:** أساسيات الحوسبة والبرمجة والرياضيات (CMPS 100B، CMPS 110N، CMPS 150، CMPS 180، التفاضل والتكامل ١ و٢، الرياضيات المتقطعة).\n"
                "* **السنة الثانية:** هياكل البيانات، تنظيم الحاسوب، الشبكات، نظم التشغيل، قواعد البيانات، وأساسيات الأمن السيبراني (CSEC 210).\n"
                "* **السنة الثالثة:** أمن الشبكات، التشفير، البرمجيات الآمنة، الاختراق الأخلاقي، والتحقيق الجنائي الرقمي.\n"
                "* **السنة الرابعة:** أمن السحابة، أخلاقيات وتشريعات الفضاء السيبراني، مشروع التخرج ١ و٢، والتدريب الميداني."
            )
            citations.append("الخطة الدراسية لبكالوريوس الأمن السيبراني")
        else:
            answer_parts.append(
                "### Bachelor of Science in Cybersecurity Overview\n\n"
                "* **Total Credits:** 124 Credit Hours across 8 standard semesters (4 years).\n"
                "* **Year 1:** Foundational computing (CMPS 100B, CMPS 110N, CMPS 150, CMPS 180, Calculus I & II, Discrete Math).\n"
                "* **Year 2:** Systems & Security Core (Data Structures, Assembly, Networks, OS, Database Systems, Fundamentals of Cybersecurity CSEC 210).\n"
                "* **Year 3:** Advanced Security (Network & Perimeter Security, Cryptography, Secure Software, Ethical Hacking, Digital Forensics, SOC operations).\n"
                "* **Year 4:** Cloud Security, Cyber Law & Ethics, Senior Capstone Project I & II, and Industrial Internship."
            )
            citations.append("Cybersecurity Plan of Study (B.Sc.)")

    elif any(k in q_lower for k in ["data science", "data", "machine learning", "بيانات", "تعلم الآلة"]):
        if is_ar:
            answer_parts.append(
                "### نظرة عامة على بكالوريوس العلوم في علم البيانات\n\n"
                "* **إجمالي الساعات:** ١٢٤ ساعة معتمدة موزعة على ٨ فصول دراسية (٤ سنوات).\n"
                "* **الكفاءات الأساسية:** البرمجة بلغة بايثون، معالجة البيانات، الاستدلال الإحصائي، هندسة البيانات الضخمة، تعلم الآلة، التعلم العميق، معالجة اللغات الطبيعية، وتصور البيانات.\n"
                "* **تسلسل المتطلبات السابقة:** CMPS 110N -> DSCI 110 -> DSCI 210 -> DSCI 310 -> DSCI 330."
            )
            citations.append("الخطة الدراسية لبكالوريوس علم البيانات")
        else:
            answer_parts.append(
                "### Bachelor of Science in Data Science Overview\n\n"
                "* **Total Credits:** 124 Credit Hours across 8 standard semesters (4 years).\n"
                "* **Core Competencies:** Python Programming, Data Wrangling, Statistical Inference, Big Data Engineering, Machine Learning, Deep Learning, NLP, and Data Visualization.\n"
                "* **Prerequisites Flow:** CMPS 110N -> DSCI 110 -> DSCI 210 -> DSCI 310 (Machine Learning) -> DSCI 330 (Deep Learning)."
            )
            citations.append("Data Science Plan of Study (B.Sc.)")

    elif any(k in q_lower for k in ["withdraw", "withdrawal", "drop", "add", "w grade", "wf", "انسحاب", "حذف", "إضافة"]):
        if is_ar:
            answer_parts.append(
                "### لوائح الحذف والإضافة والانسحاب من المقررات\n\n"
                "* **فترة الحذف والإضافة:** يُسمح بها فقط خلال **الأسبوع الأول** من الفصل الدراسي عبر بوابة الطالب.\n"
                "* **الانسحاب النظامي (W):** يجوز للطالب الانسحاب من المقرر بتقدير رسمي (W) قبل نهاية **الأسبوع العاشر** بموافقة المرشد الأكاديمي.\n"
                "* **عقوبة الانقطاع غير الرسمي (WF):** التوقف عن الحضور بعد الأسبوع العاشر دون انسحاب رسمي يؤدي لرصد تقدير **WF** (يُحسب صفراً / راسب في المعدل التراكمي)."
            )
            citations.append("دليل الإرشاد الأكاديمي بجامعة ظفار، القسم ٢")
        else:
            answer_parts.append(
                "### Add/Drop & Course Withdrawal Regulations\n\n"
                "* **Add/Drop Window:** Permitted only during the **first week** of the semester via the student portal.\n"
                "* **Course Withdrawal (W):** A student may withdraw from a course with an official grade of 'W' prior to the **10th week** of classes with academic advisor approval.\n"
                "* **Unofficial Drop Penalty (WF):** Leaving classes after Week 10 without official withdrawal results in a recorded grade of **WF** (calculated as 0% / F in CGPA)."
            )
            citations.append("DU Academic Advising Handbook, Section 2")

    else:
        if doc_matches:
            top = doc_matches[0]
            if is_ar:
                answer_parts.append(f"### مقتطف من الوثيقة المرجعية: '{top['title']}'\n\n")
                for m in top.get('matches', [])[:3]:
                    answer_parts.append(f"* **صفحة {m['page']} (مطابقة '{m['matched_term']}'):** {m['snippet']}\n")
            else:
                answer_parts.append(f"### Relevant Policy Extract from '{top['title']}'\n\n")
                for m in top.get('matches', [])[:3]:
                    answer_parts.append(f"* **Page {m['page']} (Matching '{m['matched_term']}'):** {m['snippet']}\n")
            citations.append(top['title'])
        else:
            if is_ar:
                answer_parts.append(
                    "### ملخص التوجيه الإرشادي الأكاديمي\n\n"
                    "بموجب اللوائح الأكاديمية لجامعة ظفار:\n"
                    "* يجب الحفاظ على معدل تراكمي >= ٦٥.٠٪ للبقاء في الوضع الأكاديمي السليم.\n"
                    "* يُقيد الطلبة الخاضعون للملاحظة الأكاديمية بسقف ١٢ ساعة معتمدة كحد أقصى.\n"
                    "* يجوز إعادة المقررات ذات التقدير F أو D أو D+ وتُحتسب الدرجة الأعلى في المعدل التراكمي."
                )
                citations.append("لوائح الدراسات الجامعية الأولى بجامعة ظفار")
            else:
                answer_parts.append(
                    "### Advisor Guidance Overview\n\n"
                    "Under Dhofar University academic regulations:\n"
                    "* Students must maintain cumulative GPA >= 65.0% for Good Standing.\n"
                    "* Students on probation are capped at 12 credit hours maximum.\n"
                    "* F, D, and D+ courses may be repeated, with the highest grade replacing earlier attempts in CGPA calculation."
                )
                citations.append("DU Undergraduate Academic Regulations")

    return {
        "status": "success",
        "answer": "".join(answer_parts),
        "citations": citations,
        "sources": doc_matches[:3],
        "engine": (
            "محرك الذكاء الإرشادي الأكاديمي بجامعة ظفار (مبني على اللوائح المعتمدة)"
            if is_ar else
            "Dhofar University Advising Intelligence Engine (Offline Rule-Based)"
        )
    }