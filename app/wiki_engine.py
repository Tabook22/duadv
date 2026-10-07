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

def get_wiki_knowledge_base() -> Dict[str, Any]:
    """
    Compile comprehensive Dhofar University Academic Advising Knowledge Base
    synthesized from official regulations, degree roadmaps, and advising handbooks.
    """
    study_plans = get_all_registered_study_plans()
    
    # Core Policy Modules
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
        "study_plans": study_plans,
        "policy_modules": policy_modules,
        "total_documents": len(load_policies_from_file())
    }

def ask_advising_wiki(question: str) -> Dict[str, Any]:
    """
    Intelligent Academic Advising Assistant:
    Answers advisor questions using full-text search across policy books,
    synthesizing exact answers and citing DU regulations.
    """
    if not question or not question.strip():
        return {
            "status": "error",
            "message": "Question query cannot be empty."
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
                    
            prompt = (
                "You are the Dhofar University Academic Advising AI Assistant for Dr. Nasser Tabook. "
                "Answer the following advisor question accurately based on Dhofar University regulations and study plans. "
                "Quote exact article numbers and policy guidelines where applicable.\n\n"
                f"Context from University Documents:\n{context_text}\n\n"
                f"Question: {q_clean}\n\n"
                "Provide a clear, structured advising response with bullet points and policy citations."
            )
            resp = model.generate_content(prompt)
            if resp and resp.text:
                return {
                    "status": "success",
                    "answer": resp.text.strip(),
                    "sources": doc_matches[:3],
                    "engine": "Google Gemini AI (Online)"
                }
        except Exception as e:
            # Fallback to intelligent local heuristic engine
            pass
            
    # 3. High-Fidelity Local Semantic Synthesis Engine (Offline Fallback)
    answer_parts = []
    citations = []
    
    if any(k in q_lower for k in ["probation", "strict", "standing", "warning", "dismissal", "gpa 65"]):
        answer_parts.append(
            "### Dhofar University Academic Standing & Probation Rules\n\n"
            "* **Cumulative GPA Threshold:** Under **Article 14.1**, all undergraduate and diploma students must maintain a cumulative GPA of at least **65.0%** to remain in Good Standing.\n"
            "* **First Probation:** Triggered when CGPA falls below 65.0% at the end of any regular semester. Course load is strictly capped at **12 credit hours** (Article 14.2 & 22.2).\n"
            "* **Second Probation:** If a student on First Probation does not achieve a semester average of at least 65.0% and their cumulative GPA remains below 65.0%, they advance to Second Probation.\n"
            "* **Strict Probation (2nd / 3rd):** Continued deficiency escalates the student to Strict Probation with imminent academic dismissal warning. The advisor must hold mandatory bi-weekly counseling and formulate an Academic Recovery Plan.\n"
            "* **Probation Removal:** When a student elevates their cumulative GPA to >= 65.0%, they are cleared to Normal Standing."
        )
        citations.append("Dhofar University Undergraduate Academic Regulations, Article 14 & 22")
        
    elif any(k in q_lower for k in ["repeat", "repeating", "replace", "grade replacement", "d grade", "f grade"]):
        answer_parts.append(
            "### Course Repetition & Grade Replacement Bylaws\n\n"
            "* **Eligible Grades:** Under **Article 18.1**, a student may repeat any course in which they received a grade of **F, D, or D+**.\n"
            "* **Highest Grade Counts:** When repeating a course, the **highest grade obtained** is used in the calculation of the cumulative GPA (Article 18.2). All historical attempts remain visible on the official transcript.\n"
            "* **Advising Rule:** Advisors must prioritize repeating prerequisite courses with low grades before allowing students to enroll in advanced downstream subjects."
        )
        citations.append("Dhofar University Undergraduate Academic Regulations, Article 18")

    elif any(k in q_lower for k in ["credit", "limit", "overload", "maximum", "load", "hours"]):
        answer_parts.append(
            "### Course Load & Credit Limits\n\n"
            "* **Probation Students:** Strictly capped at a maximum of **12 credit hours** per semester (**Article 22.2**). No overloads permitted without written Dean authorization.\n"
            "* **Normal Good Standing:** Standard undergraduate full-time course load is **15 to 18 credit hours** (**Article 22.1**).\n"
            "* **Graduating Seniors:** May register for up to **19–21 credit hours** in their final graduating semester with Dean approval (**Article 22.3**)."
        )
        citations.append("Dhofar University Undergraduate Academic Regulations, Article 22")

    elif any(k in q_lower for k in ["bridge", "diploma to bachelor", "articulation", "transfer"]):
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

    elif any(k in q_lower for k in ["cyber", "cybersecurity"]):
        answer_parts.append(
            "### Bachelor of Science in Cybersecurity Overview\n\n"
            "* **Total Credits:** 124 Credit Hours across 8 standard semesters (4 years).\n"
            "* **Year 1:** Foundational computing (CMPS 100B, CMPS 110N, CMPS 150, CMPS 180, Calculus I & II, Discrete Math).\n"
            "* **Year 2:** Systems & Security Core (Data Structures, Assembly, Networks, OS, Database Systems, Fundamentals of Cybersecurity CSEC 210).\n"
            "* **Year 3:** Advanced Security (Network & Perimeter Security, Cryptography, Secure Software, Ethical Hacking, Digital Forensics, SOC operations).\n"
            "* **Year 4:** Cloud Security, Cyber Law & Ethics, Senior Capstone Project I & II, and Industrial Internship."
        )
        citations.append("Cybersecurity Plan of Study (B.Sc.)")

    elif any(k in q_lower for k in ["data science", "data", "machine learning"]):
        answer_parts.append(
            "### Bachelor of Science in Data Science Overview\n\n"
            "* **Total Credits:** 124 Credit Hours across 8 standard semesters (4 years).\n"
            "* **Core Competencies:** Python Programming, Data Wrangling, Statistical Inference, Big Data Engineering, Machine Learning, Deep Learning, NLP, and Data Visualization.\n"
            "* **Prerequisites Flow:** CMPS 110N -> DSCI 110 -> DSCI 210 -> DSCI 310 (Machine Learning) -> DSCI 330 (Deep Learning)."
        )
        citations.append("Data Science Plan of Study (B.Sc.)")

    elif any(k in q_lower for k in ["withdraw", "withdrawal", "drop", "add", "w grade", "wf"]):
        answer_parts.append(
            "### Add/Drop & Course Withdrawal Regulations\n\n"
            "* **Add/Drop Window:** Permitted only during the **first week** of the semester via the student portal.\n"
            "* **Course Withdrawal (W):** A student may withdraw from a course with an official grade of 'W' prior to the **10th week** of classes with academic advisor approval.\n"
            "* **Unofficial Drop Penalty (WF):** Leaving classes after Week 10 without official withdrawal results in a recorded grade of **WF** (calculated as 0% / F in CGPA)."
        )
        citations.append("DU Academic Advising Handbook, Section 2")

    else:
        # Generic match based on searched doc matches
        if doc_matches:
            top = doc_matches[0]
            answer_parts.append(f"### Relevant Policy Extract from '{top['title']}'\n\n")
            for m in top.get('matches', [])[:3]:
                answer_parts.append(f"* **Page {m['page']} (Matching '{m['matched_term']}'):** {m['snippet']}\n")
            citations.append(top['title'])
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
        "engine": "Dhofar University Advising Intelligence Engine (Offline Rule-Based)"
    }