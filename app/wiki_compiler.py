"""
Andrej Karpathy LLM Wiki Compiler & Second Brain Engine for Dhofar University
Maintains a persistent, compounding, interlinked markdown vault in `wiki/`.
Handles Layer 1 (Raw Sources), Layer 2 (The Wiki), and Layer 3 (The Schema).
"""

import os
import re
import json
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI_DIR = os.path.join(PROJECT_ROOT, 'wiki')

# -------------------------------------------------------------------------
# Layer 3: The Schema (Constitution)
# -------------------------------------------------------------------------

SCHEMA_CONTENT = """---
title: Dhofar University Academic Advising Wiki Schema
type: schema
version: 1.0.0
last_updated: {date}
maintainer: LLM Agent & Dr. Nasser Tabook
---

# Dhofar University Academic Advising Wiki Schema

This document defines the constitution, naming conventions, directory structure,
and workflows for the Dhofar University Academic Advising LLM Wiki.
Inspired by the Andrej Karpathy LLM Wiki pattern, this wiki serves as a persistent,
compounding Second Brain for academic advising.

## 1. Directory Structure

- `schema.md`: This file. The constitution and operational rules.
- `index.md`: Content-oriented catalog of all pages with one-line summaries and wikilinks.
- `log.md`: Chronological append-only audit trail (`## [YYYY-MM-DD] action | Title`).
- `raw/`: Immutable source documents (regulations, study plans, student transcripts).
- `sources/`: Extracted summaries and key takeaways of raw sources.
- `concepts/`: University bylaws, grading policies, probation thresholds, and credit rules.
- `programs/`: Degree curricula, graduation requirements, and semester-by-semester roadmaps.
- `courses/`: Course entity pages with credit hours, category, prerequisites, and unlocks.
- `students/`: Individual student advising dossiers tracking term chronologies, deficiencies, and recovery schedules.
- `synthesis/`: Compounding cross-document analyses (e.g. Students at Risk, Prerequisite Graph).

## 2. Page Conventions

1. **Format**: Standard GitHub Flavored Markdown with YAML frontmatter.
2. **Wikilinks**: Use Obsidian-standard `[[Page_Name]]` or `[[Page_Name|Display Text]]`.
3. **Immutability of Raw**: The `raw/` directory is never modified; it is the ground truth.
4. **Compounding Artifact**: When a new source or transcript is ingested, existing entity pages are updated rather than creating duplicate fragments.

## 3. Workflows

- **Ingest**: Extract key data from a raw source, create/update entity pages in `sources/`, `students/`, `courses/`, update `index.md`, and append an entry to `log.md`.
- **Query**: Read directly from the compiled wiki pages; file significant answers back into `synthesis/`.
- **Lint**: Regularly check for broken wikilinks, orphan pages, or out-of-date standings.
"""

def ensure_wiki_dirs():
    """Ensure all wiki subdirectories exist"""
    dirs = [
        WIKI_DIR,
        os.path.join(WIKI_DIR, 'raw', 'regulations'),
        os.path.join(WIKI_DIR, 'raw', 'study_plans'),
        os.path.join(WIKI_DIR, 'raw', 'transcripts'),
        os.path.join(WIKI_DIR, 'sources'),
        os.path.join(WIKI_DIR, 'concepts'),
        os.path.join(WIKI_DIR, 'programs'),
        os.path.join(WIKI_DIR, 'courses'),
        os.path.join(WIKI_DIR, 'students'),
        os.path.join(WIKI_DIR, 'synthesis'),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def append_to_log(action: str, title: str, details: str = ""):
    """Append entry to wiki/log.md in Karpathy format: ## [YYYY-MM-DD] action | title"""
    log_path = os.path.join(WIKI_DIR, 'log.md')
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n## [{date_str}] {action} | {title}\n"
    if details:
        entry += f"{details.strip()}\n"
        
    if not os.path.exists(log_path):
        header = "# Dhofar University Advising Wiki Audit Log\n\nChronological record of all wiki ingests, updates, and maintenance operations.\n"
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(header + entry)
    else:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(entry)

def compile_schema():
    """Write schema.md"""
    ensure_wiki_dirs()
    schema_path = os.path.join(WIKI_DIR, 'schema.md')
    date_str = datetime.now().strftime("%Y-%m-%d")
    with open(schema_path, 'w', encoding='utf-8') as f:
        f.write(SCHEMA_CONTENT.format(date=date_str).strip() + '\n')

def sync_raw_sources():
    """Copy raw source PDFs from data/ into wiki/raw/ to establish Layer 1"""
    ensure_wiki_dirs()
    data_policies_dir = os.path.join(PROJECT_ROOT, 'data', 'policies')
    raw_reg_dir = os.path.join(WIKI_DIR, 'raw', 'regulations')
    raw_sp_dir = os.path.join(WIKI_DIR, 'raw', 'study_plans')
    
    if os.path.exists(data_policies_dir):
        for fname in os.listdir(data_policies_dir):
            src = os.path.join(data_policies_dir, fname)
            if not os.path.isfile(src):
                continue
            if any(k in fname.lower() for k in ['plan', 'requirement']):
                dst = os.path.join(raw_sp_dir, fname)
            else:
                dst = os.path.join(raw_reg_dir, fname)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
                
    data_transcripts_dir = os.path.join(PROJECT_ROOT, 'data', 'transcripts')
    raw_tr_dir = os.path.join(WIKI_DIR, 'raw', 'transcripts')
    if os.path.exists(data_transcripts_dir):
        for fname in os.listdir(data_transcripts_dir):
            if fname.endswith('.pdf'):
                src = os.path.join(data_transcripts_dir, fname)
                dst = os.path.join(raw_tr_dir, fname)
                if not os.path.exists(dst):
                    shutil.copy2(src, dst)

def compile_concept_pages():
    """Compile core university concepts in wiki/concepts/"""
    ensure_wiki_dirs()
    c_dir = os.path.join(WIKI_DIR, 'concepts')
    
    concepts = [
        {
            "filename": "Academic_Probation.md",
            "title": "Academic Probation Bylaws",
            "article": "Article 14",
            "content": """---
title: Academic Probation Bylaws
type: concept
category: academic_standing
article: Article 14
governing_doc: "[[DU_Undergraduate_Academic_Regulations]]"
threshold_gpa: 65.0
max_credits: 12
---

# Academic Probation Bylaws (Article 14)

Under official Dhofar University regulations, academic standing is evaluated at the conclusion of every regular semester (Fall and Spring).

## Thresholds & Stages

1. **Good Standing (Normal)**: All undergraduate and diploma students must maintain a cumulative Grade Point Average (CGPA) of at least **65.0%**.
2. **First Academic Probation**: Placed when cumulative GPA falls below 65.0%. Course load is strictly capped at **12 credit hours** (see [[Course_Load_Limits]]).
3. **Second Academic Probation**: Occurs if a student on First Probation fails to achieve a semester average >= 65.0% and their cumulative GPA remains below 65.0%.
4. **Strict Academic Probation (Second / Third Strict)**: Continued deficiency leads to Strict Probation with imminent academic dismissal risk. Mandatory bi-weekly advising with Dr. Nasser Tabook is enforced.
5. **Probation Removal**: When cumulative GPA reaches **65.0% or above**, probation is cleared and normal credit allowances (15-18 CH) are restored.

## Advising Actions
- Consult [[Course_Repetition]] to replace F, D, or D+ grades.
- Check [[Students_at_Risk_Dossier]] for all currently affected advisees.
"""
        },
        {
            "filename": "Course_Repetition.md",
            "title": "Course Repetition & Grade Replacement Bylaws",
            "article": "Article 18",
            "content": """---
title: Course Repetition & Grade Replacement Bylaws
type: concept
category: grading_policy
article: Article 18
governing_doc: "[[DU_Undergraduate_Academic_Regulations]]"
---

# Course Repetition & Grade Replacement (Article 18)

Dhofar University permits course repetition to remediate academic deficiency and recover cumulative GPA.

## Rules & Provisions

1. **Eligible Grades**: A student may repeat any course in which they received a grade of **F, D, or D+** (scores < 65%).
2. **Highest Grade Calculated**: When a course is repeated, the **highest grade obtained** is computed into the cumulative GPA calculation.
3. **Transcript Notation**: All attempts remain recorded on the official transcript with repetition notations e.g. `(R:2)`.
4. **Prerequisite Priority**: Advisors must mandate repeating failed prerequisite courses before allowing registration in advanced downstream courses.

## Cross-References
- Governed by [[Academic_Probation]].
- Applied in [[Course_Load_Limits]].
"""
        },
        {
            "filename": "Course_Load_Limits.md",
            "title": "Course Registration, Credit Limits & Overloads",
            "article": "Article 22",
            "content": """---
title: Course Registration, Credit Limits & Overloads
type: concept
category: registration
article: Article 22
governing_doc: "[[DU_Undergraduate_Academic_Regulations]]"
---

# Course Load Limits (Article 22)

Registration credit boundaries depend directly on the student's standing.

## Credit Allowances

1. **Normal Good Standing**: Standard full-time semester load is **15 to 18 credit hours**.
2. **Probation Load (Cap: 12 CH)**: Any student on First, Second, or Strict [[Academic_Probation]] cannot exceed **12 credit hours** without written Dean authorization.
3. **Graduating Senior Overload**: Graduating seniors in their final semester before graduation may register for up to **19 to 21 credit hours** with Dean approval.

## Cross-References
- Related to [[Academic_Probation]] and [[Course_Repetition]].
"""
        },
        {
            "filename": "Add_Drop_and_Withdrawal.md",
            "title": "Add/Drop Calendar, Withdrawal (W/WF) & Incompletes",
            "article": "Handbook Sections 2 & 3",
            "content": """---
title: Add/Drop Calendar, Withdrawal (W/WF) & Incompletes
type: concept
category: registration_calendar
governing_doc: "[[DU_Academic_Advising_Handbook]]"
---

# Add/Drop & Course Withdrawal Bylaws

Official procedures for modifying semester schedules and withdrawing from courses.

## Procedures & Deadlines

1. **Add/Drop Period**: Course adds, drops, and section changes are permitted only during the **first week** of the semester.
2. **Course Withdrawal (W)**: Students may withdraw with a grade of `W` up to the **10th week** with academic advisor approval. A `W` grade carries 0 points and has no GPA penalty.
3. **Unofficial Withdrawal Penalty (WF)**: Ceasing attendance after Week 10 without official withdrawal results in a recorded grade of `WF` (Withdrawn Failing), calculated as 0% (F) in the cumulative GPA.
4. **Incomplete (I) Grades**: Incomplete grades must be resolved within **4 weeks** of the subsequent regular semester, or they automatically convert to an `F`.
"""
        },
        {
            "filename": "Diploma_Articulation.md",
            "title": "Diploma Admission, Continuation & Bridge to Bachelor",
            "article": "Section 3",
            "content": """---
title: Diploma Admission, Continuation & Bridge to Bachelor
type: concept
category: degree_progression
governing_doc: "[[Requirements_for_Studying_Computer_Science_Diploma]]"
min_bridge_gpa: 75.0
---

# Diploma to Bachelor Articulation Bridge

Dhofar University establishes a direct articulation bridge for graduates of the [[Diploma_in_Computer_Science]].

## Articulation Criteria

1. **Minimum Bridge CGPA**: A diploma graduate must achieve a graduation cumulative GPA of **>= 75.0%**.
2. **Eligible Degree Programs**:
   - [[BSc_Computer_Science]]
   - [[BSc_Cybersecurity]]
   - [[BSc_Data_Science]]
3. **Credit Transfer**: All diploma courses with grades >= 60% transfer directly, transferring approximately **60 credit hours** and allowing completion of the Bachelor degree in approximately 4 additional semesters.
"""
        }
    ]
    
    for c in concepts:
        p = os.path.join(c_dir, c["filename"])
        with open(p, 'w', encoding='utf-8') as f:
            f.write(c["content"].strip() + '\n')

def compile_source_summaries():
    """Compile structured summary pages in wiki/sources/"""
    ensure_wiki_dirs()
    s_dir = os.path.join(WIKI_DIR, 'sources')
    
    sources = [
        {
            "filename": "DU_Undergraduate_Academic_Regulations.md",
            "content": """---
title: Dhofar University Undergraduate Academic Regulations
type: source
category: regulations
raw_file: "raw/regulations/DU_Undergraduate_Academic_Regulations.pdf"
key_articles: ["Article 14", "Article 18", "Article 22"]
---

# Dhofar University Undergraduate Academic Regulations

Official institutional bylaws governing student academic progression, grading, and probation.

## Key Articles

- **Article 14**: Establishes the 65.0% CGPA threshold and stages of [[Academic_Probation]].
- **Article 18**: Establishes [[Course_Repetition]] where highest grade replaces previous attempts in CGPA.
- **Article 22**: Establishes [[Course_Load_Limits]] with a strict 12 credit hours cap for students on probation.
"""
        },
        {
            "filename": "DU_Academic_Advising_Handbook.md",
            "content": """---
title: DU Academic Advising Handbook & Registration Guidance Manual
type: source
category: handbook
raw_file: "raw/regulations/DU_Academic_Advising_Handbook.pdf"
key_sections: ["Section 1", "Section 2", "Section 3"]
---

# DU Academic Advising Handbook

Guidance manual for academic advisors detailing advising responsibilities, registration approval, and early warning interventions.

## Key Sections

- **Section 1**: Advisor responsibilities in degree audits and academic recovery formulation.
- **Section 2**: [[Add_Drop_and_Withdrawal]] calendar, Week 10 W deadline, and WF penalties.
- **Section 3**: Incomplete grade handling and grade appeal deadlines.
"""
        },
        {
            "filename": "Cybersecurity_Plan_of_Study.md",
            "content": """---
title: Cybersecurity Plan of Study (B.Sc.)
type: source
category: study_plan
raw_file: "raw/study_plans/Cybersecurity_Plan_of_Study.pdf"
degree_program: "[[BSc_Cybersecurity]]"
total_credits: 124
---

# Cybersecurity Plan of Study (B.Sc.)

Four-year undergraduate curriculum roadmap for the Bachelor of Science in Cybersecurity.

## Overview
- Total credit hours: **124 Credit Hours**.
- Core domains: Network Security, Cryptography, Secure Coding, Ethical Hacking, Digital Forensics, and Cloud Security.
- Detailed roadmap maintained in [[BSc_Cybersecurity]].
"""
        },
        {
            "filename": "Diploma_in_Computer_Science_Plan_of_Study.md",
            "content": """---
title: Diploma in Computer Science Plan of Study
type: source
category: study_plan
raw_file: "raw/study_plans/Diploma_in_Computer_Science_Plan_of_Study.pdf"
degree_program: "[[Diploma_in_Computer_Science]]"
total_credits: 65
---

# Diploma in Computer Science Plan of Study

Two-year academic program curriculum designed to deliver technical programming, database, and networking skills.

## Overview
- Total credit hours: **65 Credit Hours** across 4 standard semesters.
- Provides direct articulation to Bachelor programs via [[Diploma_Articulation]].
- Detailed roadmap maintained in [[Diploma_in_Computer_Science]].
"""
        },
        {
            "filename": "Requirements_for_Studying_Computer_Science_Diploma.md",
            "content": """---
title: Requirements for Studying Computer Science Diploma
type: source
category: requirements
raw_file: "raw/study_plans/Requirements_for_Studying_Computer_Science_Diploma.pdf"
key_sections: ["Admission Criteria", "Academic Standing", "Bridge to Bachelor"]
---

# Requirements for Studying Computer Science Diploma

Official admission criteria, prerequisite requirements, and articulation bylaws for diploma students.

## Key Takeaways
- Admission requires General Education Diploma with pure or applied mathematics >= 65%.
- Establishes [[Diploma_Articulation]] bridge (CGPA >= 75.0% for Bachelor transition).
"""
        },
        {
            "filename": "Data_Science_Plan_of_Study.md",
            "content": """---
title: Data Science Plan of Study (B.Sc.)
type: source
category: study_plan
raw_file: "raw/study_plans/Data_Science_Plan_of_Study.pdf"
degree_program: "[[BSc_Data_Science]]"
total_credits: 124
---

# Data Science Plan of Study (B.Sc.)

Four-year curriculum for the Bachelor of Science in Data Science covering Python programming, machine learning, statistical inference, big data, and neural networks.

## Overview
- Total credit hours: **124 Credit Hours**.
- Detailed roadmap maintained in [[BSc_Data_Science]].
"""
        }
    ]
    
    for s in sources:
        p = os.path.join(s_dir, s["filename"])
        with open(p, 'w', encoding='utf-8') as f:
            f.write(s["content"].strip() + '\n')

def compile_program_pages():
    """Compile degree program roadmaps in wiki/programs/"""
    ensure_wiki_dirs()
    p_dir = os.path.join(WIKI_DIR, 'programs')
    from app.study_plans_registry import get_all_registered_study_plans
    plans = get_all_registered_study_plans()
    
    for plan in plans:
        title = plan["program_title"]
        slug = re.sub(r'[^a-zA-Z0-9_]', '_', title).replace('___', '_').replace('__', '_')
        if "Cyber" in title: slug = "BSc_Cybersecurity"
        elif "Data" in title: slug = "BSc_Data_Science"
        elif "Diploma" in title: slug = "Diploma_in_Computer_Science"
        elif "Computer Science" in title: slug = "BSc_Computer_Science"
        
        md_lines = [
            "---",
            f"title: {title}",
            "type: program",
            f"degree_type: {plan['degree_type']}",
            f"total_credits: {plan['total_credits']}",
            f"semesters: {plan['standard_semesters']}",
            "---",
            "",
            f"# {title}",
            "",
            f"**Degree Type:** {plan['degree_type']} | **Total Credit Hours:** {plan['total_credits']} | **Duration:** {plan['standard_semesters']} Semesters",
            ""
        ]
        
        if plan.get("bridge_to_bachelor"):
            md_lines.extend([
                "## Articulation to Bachelor's Degree",
                f"Graduates with CGPA >= {plan['bridge_to_bachelor']['min_gpa']}% qualify for direct transfer to Bachelor programs. See [[Diploma_Articulation]].",
                ""
            ])
            
        md_lines.append("## Curriculum Roadmap & Required Courses\n")
        md_lines.append("| Code | Course Title | Credits | Category | Recommended Term | Prerequisites |")
        md_lines.append("| :--- | :--- | :---: | :--- | :--- | :--- |")
        
        for c in plan["curriculum"]:
            c_code = c["code"]
            c_slug = c_code.replace(' ', '_')
            c_link = f"[[{c_slug}|{c_code}]]"
            pr_links = []
            for pr in c.get("prerequisites", []):
                pr_slug = pr.replace(' ', '_')
                pr_links.append(f"[[{pr_slug}|{pr}]]")
            pr_str = ", ".join(pr_links) if pr_links else "None"
            md_lines.append(f"| {c_link} | {c['name']} | {c['credits']} | {c['category']} | {c['term_recommended']} | {pr_str} |")
            
        md_lines.append("")
        md_lines.append("## Related Concepts\n")
        md_lines.append("- Evaluated against [[Academic_Probation]]")
        md_lines.append("- Repetitions governed by [[Course_Repetition]]")
        md_lines.append("- Semester caps governed by [[Course_Load_Limits]]")
        
        with open(os.path.join(p_dir, f"{slug}.md"), 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines).strip() + '\n')

def compile_course_pages():
    """Compile individual course entity pages in wiki/courses/"""
    ensure_wiki_dirs()
    c_dir = os.path.join(WIKI_DIR, 'courses')
    from app.study_plans_registry import get_all_registered_study_plans
    plans = get_all_registered_study_plans()
    
    all_courses = {}
    unlocks = {}
    
    for plan in plans:
        for c in plan["curriculum"]:
            code = c["code"]
            slug = code.replace(' ', '_')
            if slug not in all_courses:
                all_courses[slug] = c
                all_courses[slug]["programs"] = [plan["program_title"]]
            else:
                if plan["program_title"] not in all_courses[slug]["programs"]:
                    all_courses[slug]["programs"].append(plan["program_title"])
                    
            for pr in c.get("prerequisites", []):
                pr_slug = pr.replace(' ', '_')
                if pr_slug not in unlocks:
                    unlocks[pr_slug] = []
                if slug not in unlocks[pr_slug]:
                    unlocks[pr_slug].append(slug)
                    
    for slug, c in all_courses.items():
        code = c["code"]
        c_unlocks = unlocks.get(slug, [])
        
        pr_links = [f"[[{pr.replace(' ', '_')}|{pr}]]" for pr in c.get("prerequisites", [])]
        pr_str = ", ".join(pr_links) if pr_links else "None (Direct Entry)"
        
        un_links = [f"[[{un}|{un.replace('_', ' ')}]]" for un in c_unlocks]
        un_str = ", ".join(un_links) if un_links else "None (Terminal Course)"
        
        md_lines = [
            "---",
            f"title: {code} - {c['name']}",
            "type: course",
            f'code: "{code}"',
            f"credits: {c['credits']}",
            f'category: "{c["category"]}"',
            "---",
            "",
            f"# {code}: {c['name']}",
            "",
            f"**Credit Hours:** {c['credits']} | **Category:** {c['category']}",
            "",
            f"**Programs Offering:** {', '.join(c['programs'])}",
            "",
            "## Prerequisite Requirements",
            f"- **Required Prerequisites:** {pr_str}",
            f"- **Unlocks Downstream:** {un_str}",
            "",
            "## Academic Advising Significance",
            f"If a student fails {code}, it must be repeated under [[Course_Repetition]] before enrolling in downstream courses: {un_str}.",
            ""
        ]
        with open(os.path.join(c_dir, f"{slug}.md"), 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines).strip() + '\n')

def compile_student_dossiers():
    """
    Compile rich, persistent student advising dossiers in wiki/students/<student_id>_<name>.md
    Includes term-by-term chronology, passed courses, unresolved deficiencies, and action plan.
    """
    ensure_wiki_dirs()
    s_dir = os.path.join(WIKI_DIR, 'students')
    from app.utils import load_students_from_file, get_student_semesters
    from app.advising_engine import audit_student_degree, generate_student_advising_dossier
    
    students = load_students_from_file()
    compiled_count = 0
    
    for student in students:
        sid = student.id
        s_name_slug = re.sub(r'[^a-zA-Z0-9_]', '_', student.name).replace('___', '_').replace('__', '_')
        filename = f"{sid}_{s_name_slug}.md"
        
        try:
            audit = audit_student_degree(sid)
            dossier = generate_student_advising_dossier(sid)
            semesters = get_student_semesters(sid)
        except Exception:
            continue
            
        gpa_str = f"{audit['current_gpa']:.2f}" if audit['current_gpa'] else "N/A"
        
        md_lines = [
            "---",
            f'title: "{student.name} ({sid})"',
            "type: student_dossier",
            f'student_id: "{sid}"',
            f'student_name: "{student.name}"',
            f'program: "{audit["program_title"]}"',
            f'standing: "{student.status or "Normal / Good Standing"}"',
            f"gpa: {audit['current_gpa']}",
            f"credits_completed: {audit['completed_credits']}",
            f"credits_required: {audit['total_plan_credits']}",
            f"credit_cap: {audit['credit_cap']}",
            f'urgency: "{dossier["urgency_level"]}"',
            f'cgpa: {audit["current_gpa"]}',
            f'semester_gpa: {student.semester_gpa if student.semester_gpa is not None else "null"}',
            f'last_updated: "{datetime.now().strftime("%Y-%m-%d")}"',
            "---",
            "",
            f"# Student Advising Dossier: {student.name}",
            "",
            f"**Student ID:** `{sid}` | **Program:** [[{audit['program_title'].replace(' ', '_')}|{audit['program_title']}]] | **Advisor:** Dr. Nasser Tabook",
            "",
            f"**Current Academic Standing:** `{student.status or 'Normal / Good Standing'}`  ",
            f"**Cumulative GPA (CGPA):** **{gpa_str}%** (Dhofar University Graduation Requirement: &ge; 65.0%)  ",
            f"**Latest Semester GPA (SGPA):** **{f'{student.semester_gpa:.2f}%' if student.semester_gpa is not None else 'N/A'}** (Academic Probation Progression Metric &mdash; Article 14)  ",
            f"**Degree Completion Progress:** **{audit['completed_credits']} / {audit['total_plan_credits']} Credit Hours** ({audit['completion_percentage']}%)  ",
            f"**Semester Credit Cap:** **{audit['credit_cap']} Credit Hours Max** (Governed by [[Course_Load_Limits]])",
            "",
            "## 1. Executive Situation Assessment",
            ""
        ]
        
        for p in dossier['analysis_summary']:
            # Replace course codes and concepts with wikilinks
            clean_p = p.replace('**', '**')
            md_lines.append(f"{clean_p}\n")
            
        md_lines.append("## 2. Unresolved Deficiencies & Mandatory Course Repeats\n")
        if audit['critical_repeats']:
            md_lines.append("| Course | Title | Last Grade | Attempted Term | Advising Rule |")
            md_lines.append("| :--- | :--- | :---: | :--- | :--- |")
            for cr in audit['critical_repeats']:
                c_link = f"[[{cr['code'].replace(' ', '_')}|{cr['code']}]]"
                md_lines.append(f"| {c_link} | {cr['name']} | **{cr['last_grade']}** | {cr['last_term']} | Mandatory repeat under [[Course_Repetition]] |")
            md_lines.append("")
        else:
            md_lines.append("*No unresolved failing course attempts recorded.*\n")
            
        # Progression & Root Cause Breakdown
        prog = dossier.get('progression', {})
        if prog and prog.get('terms'):
            md_lines.append(f"## 3. Semester-by-Semester Academic Trajectory & Root-Cause Breakdown\n")
            md_lines.append(f"**Overall Trajectory:** `{prog['overall_trend']}` | **Peak CGPA:** `{prog['highest_gpa']}%` | **Lowest CGPA:** `{prog['lowest_gpa']}%`\n")
            md_lines.append("| Academic Term | Term GPA (Δ) | Cum. GPA (Δ) | Standing & Credits | Root-Cause Performance Diagnosis |")
            md_lines.append("| :--- | :---: | :---: | :--- | :--- |")
            for t in prog['terms']:
                sem_str = f"**{t['semester_gpa']:.2f}%**" if t.get('semester_gpa') else "N/A"
                if t.get('delta_semester_gpa') is not None:
                    sem_str += f" ({'+' if t['delta_semester_gpa'] > 0 else ''}{t['delta_semester_gpa']}%)"
                cum_str = f"**{t['cumulative_gpa']:.2f}%**" if t.get('cumulative_gpa') else "N/A"
                if t.get('delta_cumulative_gpa') is not None:
                    cum_str += f" ({'+' if t['delta_cumulative_gpa'] > 0 else ''}{t['delta_cumulative_gpa']}%)"
                md_lines.append(f"| {t['term']} | {sem_str} | {cum_str} | `{t['standing']}` ({t['total_credits']} cr) | {t['root_cause_explanation']} |")
            md_lines.append("")

        # GPA Recovery Action Plan
        rec = dossier.get('recovery_plan', {})
        if rec:
            md_lines.append("## 4. What the Student Must Do to Increase GPA (DU Article 18 Recovery Blueprint)\n")
            md_lines.append("Under [[Course_Repetition|Article 18]], repeating failed courses replaces the lower grade in cumulative GPA:\n")
            if rec.get('repeat_items'):
                md_lines.append("| Course | Credits | Last Grade | Gain at 75% | Gain at 80% | Recovery Priority |")
                md_lines.append("| :--- | :---: | :---: | :---: | :---: | :--- |")
                for r in rec['repeat_items']:
                    c_link = f"[[{r['code'].replace(' ', '_')}|{r['code']}]]"
                    md_lines.append(f"| {c_link} | {r['credits']} | **{r['old_grade']}** | +{r['projected_gain_75']}% | +{r['projected_gain_80']}% | {r['priority']} |")
                md_lines.append("")
                md_lines.append(f"**Projected Outcome:** Scoring 75% in repeated courses yields an estimated **+{rec['total_potential_gain']}%** to cumulative GPA, projecting **{rec['projected_cgpa_at_75']}%**.\n")
            for act in rec.get('action_steps', []):
                md_lines.append(f"- {act}")
            md_lines.append("")

        # Advisor Consultation Protocol & Counseling Script
        cg = dossier.get('consultation_guide', {})
        if cg:
            md_lines.append(f"## 5. Academic Advisor Consultation Protocol & Counseling Script\n")
            md_lines.append(f"- **Consultation Directive:** `{cg['urgency']}`")
            md_lines.append(f"- **Mandatory Window:** {cg['schedule_window']}")
            md_lines.append(f"- **Meeting Cadence:** {cg['frequency']}\n")
            md_lines.append("### What Dr. Nasser Tabook (Advisor) Should Say to the Student:\n")
            for sp in cg.get('advisor_script', []):
                md_lines.append(f"**{sp['phase']} ({sp['speaker']}):**")
                md_lines.append(f"> \"{sp['dialogue']}\"\n")
            md_lines.append("### What the Student Must Prepare & Inquire:\n")
            for stp in cg.get('student_talking_points', []):
                md_lines.append(f"- {stp}")
            md_lines.append("")

        md_lines.append("## 6. Recommended Next-Semester Registration Plan\n")
        md_lines.append(f"**Course Load Cap:** {audit['credit_cap']} Credit Hours Maximum (Strictly enforced under [[Academic_Probation]]).\n")
        md_lines.append("| Course | Title | Credits | Priority | Advising Rationale |")
        md_lines.append("| :--- | :--- | :---: | :--- | :--- |")
        for sc in dossier['recommended_schedule']:
            c_link = f"[[{sc['code'].replace(' ', '_')}|{sc['code']}]]"
            md_lines.append(f"| {c_link} | {sc['name']} | {sc['credits']} | {sc['priority']} | {sc['reason']} |")
        md_lines.append("")
        md_lines.append(f"**Total Recommended Load:** **{dossier['total_recommended_credits']} Credit Hours**.\n")
        
        md_lines.append("## 7. Historical Transcript Chronology\n")
        if semesters:
            for sem in semesters:
                s_gpa = f"{sem['semester_gpa']:.2f}%" if sem.get('semester_gpa') else "N/A"
                c_gpa = f"{sem['cumulative_gpa']:.2f}%" if sem.get('cumulative_gpa') else "N/A"
                md_lines.append(f"### {sem['term']} ({sem['season']})")
                md_lines.append(f"**Standing:** `{sem.get('standing', 'Normal')}` | **Term GPA:** {s_gpa} | **Cum. GPA:** {c_gpa}\n")
                if sem.get('courses'):
                    md_lines.append("| Code | Course Title | Credits | Grade | Status |")
                    md_lines.append("| :--- | :--- | :---: | :---: | :--- |")
                    for c in sem['courses']:
                        c_link = f"[[{c['code'].replace(' ', '_')}|{c['code']}]]"
                        g = str(c.get('grade', ''))
                        is_p = any(digit in g for digit in ['6','7','8','9']) or 'P' in g
                        st_badge = "Passed" if is_p else "Failed / Repeat Needed"
                        md_lines.append(f"| {c_link} | {c['name']} | {c['credits']} | {g} | {st_badge} |")
                    md_lines.append("")
        else:
            md_lines.append("*No semester transcript records parsed.*\n")
            
        md_lines.append("## 8. Applied Bylaws & Citations\n")
        for pol in dossier['policy_citations']:
            md_lines.append(f"- **{pol['bylaw']}**: {pol['summary']}")
        md_lines.append("")
        
        filepath = os.path.join(s_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines).strip() + '\n')
        compiled_count += 1
        
    return compiled_count


def compile_schedule_wiki(sections: List[Dict[str, Any]] = None, semester: str = "Fall 2026-2027"):
    """
    Compile Section Schedule source and synthesis pages into the Karpathy Second Brain:
    - wiki/sources/Section_Schedule_<semester>.md
    - wiki/synthesis/Course_Offerings_<semester>.md
    """
    ensure_wiki_dirs()
    if sections is None:
        try:
            from app.schedule_engine import load_section_schedule
            data = load_section_schedule()
            sections = data.get('sections', [])
            semester = data.get('semester', semester)
        except Exception:
            sections = []

    if not sections:
        return

    sem_slug = re.sub(r'[^a-zA-Z0-9]', '_', semester).strip('_')
    
    # 1. Source Page: wiki/sources/Section_Schedule_<sem_slug>.md
    src_path = os.path.join(WIKI_DIR, 'sources', f"Section_Schedule_{sem_slug}.md")
    src_lines = [
        "---",
        f'title: "Official Section Schedule - {semester}"',
        'type: source',
        'category: "Course Offerings & Section Schedule"',
        f'semester: "{semester}"',
        f'total_sections: {len(sections)}',
        "---",
        "",
        f"# Dhofar University Section Schedule ({semester})",
        "",
        f"**Official Course Offerings, Sections, Timetable, and Classroom Venues** extracted from the Dhofar University Student Information System (SIS `web.du.edu.om`).",
        "",
        f"- **Total Course Sections Offered:** `{len(sections)}`",
        f"- **Primary Academic Term:** `{semester}`",
        f"- **Landscape PDF Artifact:** `raw/Section_Schedule_{sem_slug}.pdf`",
        "",
        "## Key Course Offerings Snapshot",
        "| Course Code | Title | Sec | Days | Time | Room | Instructor | Cap | Enr |",
        "| :--- | :--- | :---: | :---: | :--- | :---: | :--- | :---: | :---: |"
    ]
    for s in sections[:35]:
        c_link = f"[[{s['course_code'].replace(' ', '_')}|{s['course_code']}]]"
        src_lines.append(f"| {c_link} | {s['title']} | {s['section']} | {s['days']} | {s['time']} | {s['room']} | {s['instructor']} | {s['capacity']} | {s['enrolled']} |")
    if len(sections) > 35:
        src_lines.append(f"| *...and {len(sections) - 35} additional course sections.* | | | | | | | | |")
    src_lines.append("")
    src_lines.append("## Academic Advising Significance")
    src_lines.append("This section schedule provides the active constraints for degree audit registration planning:")
    src_lines.append("1. **Section Time Conflict Detection**: Ensures advisees are not registered for overlapping time slots.")
    src_lines.append("2. **Seat Capacity Protection**: Flags full sections so advisors can petition for section capacity increases or select alternative morning/evening sections.")
    src_lines.append("3. **Prerequisite Sequencing**: Directly cross-referenced with [[Prerequisite_Graph]] and individual [[Students_at_Risk]] recovery action plans.")
    src_lines.append("")

    with open(src_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(src_lines).strip() + '\n')

    # 2. Synthesis Page: wiki/synthesis/Course_Offerings_<sem_slug>.md
    syn_path = os.path.join(WIKI_DIR, 'synthesis', f"Course_Offerings_{sem_slug}.md")
    
    # Department breakdown
    depts = {}
    total_cap = 0
    total_enr = 0
    for s in sections:
        d = s['course_code'].split()[0]
        depts.setdefault(d, []).append(s)
        total_cap += s.get('capacity', 0)
        total_enr += s.get('enrolled', 0)

    syn_lines = [
        "---",
        f'title: "Departmental Course Offerings & Seat Availability ({semester})"',
        'type: synthesis',
        f'semester: "{semester}"',
        f'total_sections: {len(sections)}',
        "---",
        "",
        f"# Departmental Course Offerings Analysis — {semester}",
        "",
        f"Cross-curriculum synthesis of active teaching sections, capacity utilization, and advisor scheduling bottlenecks for **{semester}**.",
        "",
        f"**Aggregate Metrics:**",
        f"- **Total Sections Active:** `{len(sections)}` across `{len(depts)}` departments",
        f"- **Total University Seat Capacity:** `{total_cap}` seats",
        f"- **Total Students Enrolled:** `{total_enr}` enrolled (`{round((total_enr/total_cap)*100, 1) if total_cap > 0 else 0}%` overall utilization)",
        f"- **Open Registration Slots:** `{total_cap - total_enr}` seats",
        "",
        "## Departmental Offerings Breakdown",
        "| Department | Sections Offered | Total Seats | Enrolled | Utilization | Primary Subjects |",
        "| :--- | :---: | :---: | :---: | :---: | :--- |"
    ]
    for d, d_secs in sorted(depts.items()):
        d_cap = sum(x.get('capacity', 0) for x in d_secs)
        d_enr = sum(x.get('enrolled', 0) for x in d_secs)
        util = f"{round((d_enr/d_cap)*100, 1)}%" if d_cap > 0 else "0%"
        sample_codes = ', '.join(sorted(list(set(x['course_code'] for x in d_secs)))[:4])
        syn_lines.append(f"| **{d}** | {len(d_secs)} | {d_cap} | {d_enr} | {util} | {sample_codes} |")
    syn_lines.append("")
    syn_lines.append("## Related Academic Policies & Pages")
    syn_lines.append(f"- [[Section_Schedule_{sem_slug}|Official Section Schedule Source Page]]")
    syn_lines.append("- [[Students_at_Risk|Students at Risk Recovery Synthesis]]")
    syn_lines.append("- [[Course_Repetition|Course Repetition (Article 18)]]")
    syn_lines.append("- [[Prerequisite_Graph|Department Prerequisite Dependency Graph]]")
    syn_lines.append("")

    with open(syn_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(syn_lines).strip() + '\n')

    append_to_log("INGEST", f"Course Section Schedule {semester}", f"Ingested {len(sections)} sections ({total_enr}/{total_cap} seats) across {len(depts)} departments.")


def compile_synthesis_pages():
    compile_schedule_wiki()
    """Compile cross-cutting synthesis pages in wiki/synthesis/"""
    ensure_wiki_dirs()
    sy_dir = os.path.join(WIKI_DIR, 'synthesis')
    from app.utils import get_students_at_risk_breakdown
    
    breakdown = get_students_at_risk_breakdown()
    
    md_lines = [
        "---",
        "title: Students at Risk Academic Synthesis",
        "type: synthesis",
        f"total_advisees: {breakdown['total_advisees']}",
        f"total_at_risk: {breakdown['total_at_risk']}",
        f"strict_count: {breakdown['counts']['strict']}",
        f"second_count: {breakdown['counts']['second']}",
        f"first_count: {breakdown['counts']['first']}",
        "---",
        "",
        "# Students at Risk Academic Synthesis",
        "",
        f"**Total Advisees:** {breakdown['total_advisees']} | **Total Students at Risk:** {breakdown['total_at_risk']} ({round(breakdown['total_at_risk']/breakdown['total_advisees']*100, 1)}%)",
        "",
        "## Summary by Probation Stage",
        "",
        f"- **Strict Probation (2nd / 3rd)**: `{breakdown['counts']['strict']} advisees` (High risk of dismissal; see [[Academic_Probation]])",
        f"- **Second Probation**: `{breakdown['counts']['second']} advisees` (Max 12 credit load; see [[Course_Load_Limits]])",
        f"- **First Probation**: `{breakdown['counts']['first']} advisees` (Early warning; repeating D/F courses; see [[Course_Repetition]])",
        "",
        "## Student Rosters & Individual Second-Brain Dossiers\n"
    ]
    
    def _add_section(title, st_list):
        md_lines.append(f"### {title}\n")
        md_lines.append("| Student ID | Full Name | Major | GPA | Earned Cr | Dossier Link |")
        md_lines.append("| :--- | :--- | :--- | :---: | :---: | :--- |")
        for s in st_list:
            slug = f"{s.id}_{re.sub(r'[^a-zA-Z0-9_]', '_', s.name).replace('___', '_').replace('__', '_')}"
            link = f"[[{slug}|View Dossier]]"
            gpa_s = f"{s.gpa:.2f}%" if s.gpa else "N/A"
            md_lines.append(f"| `{s.id}` | {s.name} | {s.program} | **{gpa_s}** | {s.credits} | {link} |")
        md_lines.append("")
        
    _add_section("Strict Academic Probation", breakdown['strict_probation'])
    _add_section("Second Academic Probation", breakdown['second_probation'])
    _add_section("First Academic Probation", breakdown['first_probation'])
    
    with open(os.path.join(sy_dir, "Students_at_Risk_Dossier.md"), 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines).strip() + '\n')

def build_index_file():
    """Build content-oriented catalog in wiki/index.md"""
    ensure_wiki_dirs()
    index_path = os.path.join(WIKI_DIR, 'index.md')
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lines = [
        "---",
        "title: Dhofar University Academic Advising Wiki Index",
        "type: index",
        f'last_compiled: "{date_str}"',
        "---",
        "",
        "# Dhofar University Academic Advising Wiki Index",
        "",
        "Welcome to your persistent, compounding **Second Brain** for Dhofar University academic advising. "
        "Every page is an Obsidian-compatible markdown document interlinked via `[[wikilinks]]`.",
        "",
        "## 🧭 Wiki Navigation & Key Hubs",
        "- [[schema|Constitution & Wiki Schema (schema.md)]]",
        "- [[log|Changelog & Audit Trail (log.md)]]",
        "- [[Students_at_Risk_Dossier|Students at Risk Synthesis Dossier]]",
        "",
        "## 📜 Academic Concepts & University Bylaws",
    ]
    
    c_dir = os.path.join(WIKI_DIR, 'concepts')
    if os.path.exists(c_dir):
        for f in sorted(os.listdir(c_dir)):
            if f.endswith('.md'):
                name = f[:-3]
                title = name.replace('_', ' ')
                lines.append(f"- [[{name}|{title}]]")
    lines.append("")
    
    lines.append("## 🎓 Degree Programs & Study Plans")
    p_dir = os.path.join(WIKI_DIR, 'programs')
    if os.path.exists(p_dir):
        for f in sorted(os.listdir(p_dir)):
            if f.endswith('.md'):
                name = f[:-3]
                title = name.replace('_', ' ')
                lines.append(f"- [[{name}|{title}]]")
    lines.append("")
    
    lines.append("## 📄 Ingested Raw Sources & Handbooks")
    s_dir = os.path.join(WIKI_DIR, 'sources')
    if os.path.exists(s_dir):
        for f in sorted(os.listdir(s_dir)):
            if f.endswith('.md'):
                name = f[:-3]
                title = name.replace('_', ' ')
                lines.append(f"- [[{name}|{title}]]")
    lines.append("")
    
    lines.append("## 🧑‍🎓 Student Advising Dossiers")
    st_dir = os.path.join(WIKI_DIR, 'students')
    if os.path.exists(st_dir):
        st_files = sorted(os.listdir(st_dir))
        for f in st_files[:20]:  # Highlight top 20
            if f.endswith('.md'):
                name = f[:-3]
                display = name.replace('_', ' ')
                lines.append(f"- [[{name}|{display}]]")
        if len(st_files) > 20:
            lines.append(f"- *...and {len(st_files) - 20} additional student dossiers.*")
    lines.append("")
    
    lines.append("## 💻 Core Curriculum Courses")
    cr_dir = os.path.join(WIKI_DIR, 'courses')
    if os.path.exists(cr_dir):
        cr_files = sorted(os.listdir(cr_dir))
        for f in cr_files[:15]:
            if f.endswith('.md'):
                name = f[:-3]
                lines.append(f"- [[{name}|{name.replace('_', ' ')}]]")
        if len(cr_files) > 15:
            lines.append(f"- *...and {len(cr_files) - 15} additional curriculum courses.*")
    lines.append("")
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines).strip() + '\n')

def full_wiki_recompile() -> Dict[str, Any]:
    """Execute complete compilation pipeline of the Karpathy LLM Wiki"""
    ensure_wiki_dirs()
    compile_schema()
    sync_raw_sources()
    compile_concept_pages()
    compile_source_summaries()
    compile_program_pages()
    compile_course_pages()
    student_count = compile_student_dossiers()
    compile_synthesis_pages()
    build_index_file()
    
    append_to_log(
        "recompile",
        "Full Wiki Vault Recompilation",
        f"Recompiled Schema, 5 Concept pages, 6 Source summaries, 4 Program roadmaps, {student_count} Student dossiers, and updated index.md."
    )
    
    return {
        "status": "success",
        "student_dossiers_compiled": student_count,
        "timestamp": datetime.now().isoformat(),
        "wiki_dir": WIKI_DIR
    }

def get_wiki_tree() -> Dict[str, Any]:
    """Return file tree structure of wiki vault for UI sidebar"""
    ensure_wiki_dirs()
    
    categories = [
        {"id": "root", "name": "Vault Root", "files": ["index.md", "schema.md", "log.md"]},
        {"id": "concepts", "name": "Academic Bylaws & Concepts", "dir": "concepts"},
        {"id": "programs", "name": "Degree Study Plans", "dir": "programs"},
        {"id": "students", "name": "Student Dossiers", "dir": "students"},
        {"id": "sources", "name": "Source Summaries", "dir": "sources"},
        {"id": "synthesis", "name": "Syntheses & Rosters", "dir": "synthesis"},
        {"id": "courses", "name": "Course Entities", "dir": "courses"}
    ]
    
    tree = []
    for cat in categories:
        items = []
        if cat.get("files"):
            for fname in cat["files"]:
                p = os.path.join(WIKI_DIR, fname)
                if os.path.exists(p):
                    items.append({
                        "filename": fname,
                        "rel_path": fname,
                        "title": fname.replace('_', ' ').replace('.md', ''),
                        "size": os.path.getsize(p)
                    })
        elif cat.get("dir"):
            dpath = os.path.join(WIKI_DIR, cat["dir"])
            if os.path.exists(dpath):
                for fname in sorted(os.listdir(dpath)):
                    if fname.endswith('.md'):
                        p = os.path.join(dpath, fname)
                        items.append({
                            "filename": fname,
                            "rel_path": f"{cat['dir']}/{fname}",
                            "title": fname.replace('_', ' ').replace('.md', ''),
                            "size": os.path.getsize(p)
                        })
        tree.append({
            "id": cat["id"],
            "name": cat["name"],
            "count": len(items),
            "items": items
        })
    return {"tree": tree}

def read_wiki_page(rel_path: str) -> Dict[str, Any]:
    """Read a markdown file from wiki/, extract frontmatter, backlinks, and rendered HTML"""
    safe_rel = rel_path.strip().lstrip('/\\')
    full_path = os.path.join(WIKI_DIR, safe_rel)
    
    if not os.path.exists(full_path) or not full_path.endswith('.md'):
        # Try to resolve by base filename across subdirs
        base = os.path.basename(safe_rel)
        if not base.endswith('.md'):
            base += '.md'
        found = None
        for root, dirs, files in os.walk(WIKI_DIR):
            if base in files:
                found = os.path.join(root, base)
                safe_rel = os.path.relpath(found, WIKI_DIR).replace('\\', '/')
                full_path = found
                break
        if not found:
            raise FileNotFoundError(f"Page '{rel_path}' not found in wiki vault.")
            
    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
        raw_text = f.read()
        
    # Extract YAML frontmatter
    frontmatter = {}
    content = raw_text
    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', raw_text, re.DOTALL)
    if fm_match:
        fm_text = fm_match.group(1)
        content = fm_match.group(2)
        for line in fm_text.split('\n'):
            if ':' in line:
                k, v = line.split(':', 1)
                frontmatter[k.strip()] = v.strip().strip('"\'')
                
    # Find backlinks (other pages linking to this page)
    page_name = os.path.splitext(os.path.basename(safe_rel))[0]
    backlinks = []
    
    for root, dirs, files in os.walk(WIKI_DIR):
        for f in files:
            if f.endswith('.md'):
                f_path = os.path.join(root, f)
                if f_path == full_path:
                    continue
                try:
                    with open(f_path, 'r', encoding='utf-8', errors='ignore') as of:
                        txt = of.read()
                        if f"[[{page_name}]]" in txt or f"[[{page_name}|" in txt:
                            rel = os.path.relpath(f_path, WIKI_DIR).replace('\\', '/')
                            backlinks.append({
                                "filename": f,
                                "rel_path": rel,
                                "title": f[:-3].replace('_', ' ')
                            })
                except Exception:
                    pass
                    
    return {
        "rel_path": safe_rel,
        "filename": os.path.basename(safe_rel),
        "title": frontmatter.get("title", page_name.replace('_', ' ')),
        "frontmatter": frontmatter,
        "content_markdown": content,
        "backlinks": backlinks,
        "last_modified": datetime.fromtimestamp(os.path.getmtime(full_path)).strftime("%Y-%m-%d %H:%M")
    }

def lint_wiki_vault() -> Dict[str, Any]:
    """Health check the wiki for broken links, orphan pages, and gaps"""
    ensure_wiki_dirs()
    all_pages = set()
    all_links = []
    
    for root, dirs, files in os.walk(WIKI_DIR):
        for f in files:
            if f.endswith('.md'):
                all_pages.add(f[:-3])
                
    broken_links = []
    for root, dirs, files in os.walk(WIKI_DIR):
        for f in files:
            if f.endswith('.md'):
                f_path = os.path.join(root, f)
                with open(f_path, 'r', encoding='utf-8', errors='ignore') as rf:
                    txt = rf.read()
                    matches = re.findall(r'\[\[([a-zA-Z0-9_\s\-]+)(?:\|([^\]]+))?\]\]', txt)
                    for target, _ in matches:
                        t_norm = target.strip().replace(' ', '_')
                        if t_norm not in all_pages:
                            broken_links.append({
                                "source": f,
                                "target": target
                            })
                            
    return {
        "status": "healthy" if len(broken_links) == 0 else "warnings",
        "total_pages": len(all_pages),
        "broken_links_count": len(broken_links),
        "broken_links": broken_links[:10]
    }