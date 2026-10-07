"""
Dhofar University Section Schedule Intelligence Engine
Handles parsing, storage, PDF generation, and advising course matching
for offered university course sections (e.g. Fall 2026-2027).
"""

import os
import re
import json
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
SCHEDULE_JSON_PATH = os.path.join(DATA_DIR, 'section_schedule.json')
POLICIES_JSON_PATH = os.path.join(DATA_DIR, 'policies.json')
POLICIES_DIR = os.path.join(DATA_DIR, 'policies')
WIKI_RAW_DIR = os.path.join(PROJECT_ROOT, 'wiki', 'raw')


def normalize_course_code(code: str) -> str:
    """Normalize course code (e.g., 'CMPS 110' -> 'CMPS110')"""
    if not code:
        return ""
    return re.sub(r'[\s\-_]+', '', code).upper()


def get_default_fall_2026_sections() -> List[Dict[str, Any]]:
    """
    Realistic Dhofar University Department of Computer Science & Engineering
    Section Schedule for Fall 2026-2027 with sections, instructors, rooms, days, and capacity.
    """
    default_sections = [
        # CMPS 110
        {"course_code": "CMPS 110", "title": "Introduction to Computer Science", "credits": 3, "section": "1", "session_type": "Morning", "language": "English", "capacity": 30, "enrolled": 24, "instructor": "Dr. Nasser Tabook", "room": "CC-102", "days": "SunTueThu", "time": "09:00 - 09:50", "remark": "Lecture + Lab"},
        {"course_code": "CMPS 110", "title": "Introduction to Computer Science", "credits": 3, "section": "2", "session_type": "Morning", "language": "English", "capacity": 30, "enrolled": 29, "instructor": "Dr. Nasser Tabook", "room": "CC-104", "days": "SunTueThu", "time": "11:00 - 11:50", "remark": "Lecture + Lab"},
        {"course_code": "CMPS 110", "title": "Introduction to Computer Science", "credits": 3, "section": "3", "session_type": "Morning", "language": "English", "capacity": 30, "enrolled": 18, "instructor": "Dr. Ahmed Al-Mahri", "room": "CC-102", "days": "MonWed", "time": "10:00 - 11:15", "remark": "Lecture + Lab"},
        
        # CMPS 111
        {"course_code": "CMPS 111", "title": "Computer Programming II (OOP)", "credits": 3, "section": "1", "session_type": "Morning", "language": "English", "capacity": 28, "enrolled": 22, "instructor": "Dr. Said Salim", "room": "CC-201", "days": "SunTueThu", "time": "10:00 - 10:50", "remark": "Prereq: CMPS 110"},
        {"course_code": "CMPS 111", "title": "Computer Programming II (OOP)", "credits": 3, "section": "2", "session_type": "Evening", "language": "English", "capacity": 25, "enrolled": 16, "instructor": "Dr. Said Salim", "room": "CC-201", "days": "MonWed", "time": "16:00 - 17:15", "remark": "Prereq: CMPS 110"},

        # CMPS 210
        {"course_code": "CMPS 210", "title": "Digital Logic Design", "credits": 3, "section": "1", "session_type": "Morning", "language": "English", "capacity": 30, "enrolled": 27, "instructor": "Dr. Tariq Al-Shanfari", "room": "CC-108", "days": "SunTueThu", "time": "08:00 - 08:50", "remark": "Prereq: MATH 199"},
        {"course_code": "CMPS 210", "title": "Digital Logic Design", "credits": 3, "section": "2", "session_type": "Morning", "language": "English", "capacity": 30, "enrolled": 19, "instructor": "Dr. Tariq Al-Shanfari", "room": "CC-108", "days": "MonWed", "time": "11:30 - 12:45", "remark": "Prereq: MATH 199"},

        # CMPS 220
        {"course_code": "CMPS 220", "title": "Data Structures & Algorithms", "credits": 3, "section": "1", "session_type": "Morning", "language": "English", "capacity": 28, "enrolled": 26, "instructor": "Dr. Nasser Tabook", "room": "CC-205", "days": "SunTueThu", "time": "12:00 - 12:50", "remark": "Prereq: CMPS 111"},
        {"course_code": "CMPS 220", "title": "Data Structures & Algorithms", "credits": 3, "section": "2", "session_type": "Morning", "language": "English", "capacity": 28, "enrolled": 20, "instructor": "Dr. Ahmed Al-Mahri", "room": "CC-205", "days": "MonWed", "time": "08:30 - 09:45", "remark": "Prereq: CMPS 111"},

        # CMPS 230
        {"course_code": "CMPS 230", "title": "Computer Architecture", "credits": 3, "section": "1", "session_type": "Morning", "language": "English", "capacity": 30, "enrolled": 25, "instructor": "Dr. Tariq Al-Shanfari", "room": "CC-110", "days": "SunTueThu", "time": "13:00 - 13:50", "remark": "Prereq: CMPS 210"},

        # CMPS 310
        {"course_code": "CMPS 310", "title": "Operating Systems", "credits": 3, "section": "1", "session_type": "Morning", "language": "English", "capacity": 30, "enrolled": 28, "instructor": "Dr. Said Salim", "room": "CC-204", "days": "SunTueThu", "time": "11:00 - 11:50", "remark": "Prereq: CMPS 220 & CMPS 230"},

        # CMPS 340
        {"course_code": "CMPS 340", "title": "Database Management Systems", "credits": 3, "section": "1", "session_type": "Morning", "language": "English", "capacity": 30, "enrolled": 29, "instructor": "Dr. Ahmed Al-Mahri", "room": "CC-106", "days": "SunTueThu", "time": "10:00 - 10:50", "remark": "Prereq: CMPS 220"},
        {"course_code": "CMPS 340", "title": "Database Management Systems", "credits": 3, "section": "2", "session_type": "Evening", "language": "English", "capacity": 25, "enrolled": 15, "instructor": "Dr. Ahmed Al-Mahri", "room": "CC-106", "days": "MonWed", "time": "17:30 - 18:45", "remark": "Prereq: CMPS 220"},

        # CMPS 350
        {"course_code": "CMPS 350", "title": "Software Engineering", "credits": 3, "section": "1", "session_type": "Morning", "language": "English", "capacity": 30, "enrolled": 21, "instructor": "Dr. Nasser Tabook", "room": "CC-104", "days": "MonWed", "time": "13:00 - 14:15", "remark": "Prereq: CMPS 220"},

        # CMPS 360
        {"course_code": "CMPS 360", "title": "Web Application Development", "credits": 3, "section": "1", "session_type": "Morning", "language": "English", "capacity": 28, "enrolled": 27, "instructor": "Eng. Khalid Al-Amri", "room": "LAB-301", "days": "SunTueThu", "time": "14:00 - 14:50", "remark": "Prereq: CMPS 340"},

        # CMPS 410
        {"course_code": "CMPS 410", "title": "Computer Networks", "credits": 3, "section": "1", "session_type": "Morning", "language": "English", "capacity": 30, "enrolled": 26, "instructor": "Dr. Tariq Al-Shanfari", "room": "CC-202", "days": "SunTueThu", "time": "09:00 - 09:50", "remark": "Prereq: CMPS 310"},

        # CMPS 420
        {"course_code": "CMPS 420", "title": "Internet Programming and Web Design", "credits": 3, "section": "3", "session_type": "Morning", "language": "English", "capacity": 10, "enrolled": 0, "instructor": "Thabit Sabbah", "room": "CAAS-104C", "days": "SunTueThu", "time": "09:00 - 09:50", "remark": "Prereq: CMPS 220, CMPS 270"},

        # CMPS 480 & 490A
        {"course_code": "CMPS 480", "title": "Field Training", "credits": 3, "section": "1", "session_type": "Morning", "language": "English", "capacity": 30, "enrolled": 15, "instructor": "Dr. Nasser Tabook", "room": "OFF-CAMPUS", "days": "SunTueThu", "time": "08:00 - 14:00", "remark": "Senior Standing / Internship"},
        {"course_code": "CMPS 490A", "title": "Final Year Project I", "credits": 1, "section": "1", "session_type": "Morning", "language": "English", "capacity": 20, "enrolled": 18, "instructor": "Dr. Nasser Tabook", "room": "CC-LAB2", "days": "MonWed", "time": "14:30 - 15:20", "remark": "Senior Standing (Completed >= 90 Cr)"},
        {"course_code": "CMPS 490B", "title": "Final Year Project II", "credits": 2, "section": "1", "session_type": "Morning", "language": "English", "capacity": 20, "enrolled": 14, "instructor": "Dr. Nasser Tabook", "room": "CC-LAB2", "days": "SunTue", "time": "14:00 - 15:15", "remark": "Prereq: CMPS 490A"},

        # STAT 230
        {"course_code": "STAT 230", "title": "Probability and Statistics", "credits": 3, "section": "1", "session_type": "Morning", "language": "English", "capacity": 35, "enrolled": 30, "instructor": "Dr. Mohammed Al-Rawas", "room": "SC-102", "days": "SunTueThu", "time": "13:00 - 13:50", "remark": "Prereq: MATH 199"},
        {"course_code": "STAT 230", "title": "Probability and Statistics", "credits": 3, "section": "2", "session_type": "Morning", "language": "English", "capacity": 35, "enrolled": 24, "instructor": "Dr. Fatima Al-Harthi", "room": "SC-102", "days": "MonWed", "time": "14:30 - 15:45", "remark": "Prereq: MATH 199"},

        # MATH 199
        {"course_code": "MATH 199", "title": "Calculus I", "credits": 3, "section": "1", "session_type": "Morning", "language": "English", "capacity": 35, "enrolled": 34, "instructor": "Dr. Mohammed Al-Rawas", "room": "SC-101", "days": "SunTueThu", "time": "08:00 - 08:50", "remark": "Department Requirement"},
        {"course_code": "MATH 199", "title": "Calculus I", "credits": 3, "section": "2", "session_type": "Morning", "language": "English", "capacity": 35, "enrolled": 31, "instructor": "Dr. Mohammed Al-Rawas", "room": "SC-101", "days": "SunTueThu", "time": "10:00 - 10:50", "remark": "Department Requirement"},
        {"course_code": "MATH 199", "title": "Calculus I", "credits": 3, "section": "3", "session_type": "Morning", "language": "English", "capacity": 35, "enrolled": 25, "instructor": "Dr. Fatima Al-Harthi", "room": "SC-103", "days": "MonWed", "time": "10:00 - 11:15", "remark": "Department Requirement"},

        # MATH 200
        {"course_code": "MATH 200", "title": "Calculus II", "credits": 3, "section": "1", "session_type": "Morning", "language": "English", "capacity": 35, "enrolled": 30, "instructor": "Dr. Fatima Al-Harthi", "room": "SC-103", "days": "SunTueThu", "time": "11:00 - 11:50", "remark": "Prereq: MATH 199"},

        # MATH 201
        {"course_code": "MATH 201", "title": "Linear Algebra", "credits": 3, "section": "1", "session_type": "Morning", "language": "English", "capacity": 35, "enrolled": 32, "instructor": "Dr. Mohammed Al-Rawas", "room": "SC-102", "days": "SunTueThu", "time": "12:00 - 12:50", "remark": "Prereq: MATH 199"},
        {"course_code": "MATH 201", "title": "Linear Algebra", "credits": 3, "section": "2", "session_type": "Morning", "language": "English", "capacity": 35, "enrolled": 28, "instructor": "Dr. Fatima Al-Harthi", "room": "SC-102", "days": "MonWed", "time": "13:00 - 14:15", "remark": "Prereq: MATH 199"},

        # MATH 202
        {"course_code": "MATH 202", "title": "Discrete Mathematics", "credits": 3, "section": "1", "session_type": "Morning", "language": "English", "capacity": 35, "enrolled": 29, "instructor": "Dr. Mohammed Al-Rawas", "room": "SC-101", "days": "MonWed", "time": "08:30 - 09:45", "remark": "Prereq: MATH 199"},

        # PHYS 170 & 171
        {"course_code": "PHYS 170", "title": "Fundamentals of Physics I", "credits": 3, "section": "1", "session_type": "Morning", "language": "English", "capacity": 35, "enrolled": 30, "instructor": "Dr. Salim Al-Kathiri", "room": "SC-201", "days": "SunTueThu", "time": "09:00 - 09:50", "remark": "Coreq: PHYS 171"},
        {"course_code": "PHYS 171", "title": "Physics Laboratory I", "credits": 1, "section": "1", "session_type": "Morning", "language": "English", "capacity": 20, "enrolled": 19, "instructor": "Eng. Noor Al-Yafai", "room": "PHYS-LAB", "days": "Sun", "time": "13:00 - 15:50", "remark": "Coreq: PHYS 170"},
        {"course_code": "PHYS 171", "title": "Physics Laboratory I", "credits": 1, "section": "2", "session_type": "Morning", "language": "English", "capacity": 20, "enrolled": 17, "instructor": "Eng. Noor Al-Yafai", "room": "PHYS-LAB", "days": "Tue", "time": "13:00 - 15:50", "remark": "Coreq: PHYS 170"},

        # EECE 210
        {"course_code": "EECE 210", "title": "Electric Circuits I", "credits": 3, "section": "1", "session_type": "Morning", "language": "English", "capacity": 30, "enrolled": 25, "instructor": "Dr. Abdullah Al-Busaidi", "room": "ENG-105", "days": "SunTueThu", "time": "10:00 - 10:50", "remark": "Prereq: PHYS 170"},

        # ENGL 101 & 203
        {"course_code": "ENGL 101", "title": "Basic Academic English", "credits": 3, "section": "1", "session_type": "Morning", "language": "English", "capacity": 30, "enrolled": 28, "instructor": "Dr. John Davies", "room": "LANG-201", "days": "SunTueThu", "time": "08:00 - 08:50", "remark": "University Requirement"},
        {"course_code": "ENGL 101", "title": "Basic Academic English", "credits": 3, "section": "2", "session_type": "Morning", "language": "English", "capacity": 30, "enrolled": 26, "instructor": "Dr. Sarah Johnson", "room": "LANG-202", "days": "SunTueThu", "time": "11:00 - 11:50", "remark": "University Requirement"},
        {"course_code": "ENGL 203", "title": "Advanced Academic English & Technical Writing", "credits": 3, "section": "1", "session_type": "Morning", "language": "English", "capacity": 30, "enrolled": 29, "instructor": "Dr. John Davies", "room": "LANG-201", "days": "SunTueThu", "time": "12:00 - 12:50", "remark": "Prereq: ENGL 101"},
        {"course_code": "ENGL 203", "title": "Advanced Academic English & Technical Writing", "credits": 3, "section": "2", "session_type": "Morning", "language": "English", "capacity": 30, "enrolled": 23, "instructor": "Dr. Sarah Johnson", "room": "LANG-202", "days": "MonWed", "time": "10:00 - 11:15", "remark": "Prereq: ENGL 101"},

        # ARAB 101 & SOCS 102 & ENTR 200
        {"course_code": "ARAB 101", "title": "Academic Arabic Language Skills", "credits": 3, "section": "1", "session_type": "Morning", "language": "Arabic", "capacity": 35, "enrolled": 30, "instructor": "Dr. Ali Al-Maashani", "room": "ARTS-101", "days": "SunTueThu", "time": "13:00 - 13:50", "remark": "University Requirement"},
        {"course_code": "SOCS 102", "title": "Omani Society & Civilization", "credits": 3, "section": "1", "session_type": "Morning", "language": "Arabic", "capacity": 40, "enrolled": 38, "instructor": "Dr. Maryam Al-Shehri", "room": "ARTS-105", "days": "MonWed", "time": "11:30 - 12:45", "remark": "University Requirement"},
        {"course_code": "ENTR 200", "title": "Innovation and Entrepreneurship", "credits": 3, "section": "1", "session_type": "Morning", "language": "English", "capacity": 35, "enrolled": 27, "instructor": "Dr. Hamed Al-Ghassani", "room": "BUS-204", "days": "SunTueThu", "time": "14:00 - 14:50", "remark": "University Requirement"}
    ]
    for s in default_sections:
        s['semester'] = "Fall 2026-2027"
    return default_sections


def load_section_schedule() -> Dict[str, Any]:
    """Load section schedule data from disk or initialize with default if not found"""
    if os.path.exists(SCHEDULE_JSON_PATH):
        try:
            with open(SCHEDULE_JSON_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'sections' in data:
                    return data
        except Exception:
            pass

    # Initialize default
    sections = get_default_fall_2026_sections()
    data = {
        "semester": "Fall 2026-2027",
        "last_updated": datetime.now().isoformat(),
        "total_sections": len(sections),
        "source": "Dhofar University SIS (web.du.edu.om)",
        "sections": sections
    }
    save_section_schedule(sections, semester="Fall 2026-2027")
    return data


def save_section_schedule(sections: List[Dict[str, Any]], semester: str = "Fall 2026-2027") -> str:
    """Save sections list to section_schedule.json and generate official PDF"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(POLICIES_DIR, exist_ok=True)
    os.makedirs(WIKI_RAW_DIR, exist_ok=True)

    data = {
        "semester": semester,
        "last_updated": datetime.now().isoformat(),
        "total_sections": len(sections),
        "source": "Dhofar University SIS (web.du.edu.om)",
        "sections": sections
    }

    with open(SCHEDULE_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Generate Landscape PDF
    clean_sem = re.sub(r'[^a-zA-Z0-9]', '_', semester)
    pdf_filename = f"Section_Schedule_{clean_sem}.pdf"
    pdf_path = os.path.join(POLICIES_DIR, pdf_filename)
    
    generate_section_schedule_pdf(sections, pdf_path, semester=semester)

    # Sync to wiki/raw
    wiki_pdf_path = os.path.join(WIKI_RAW_DIR, pdf_filename)
    try:
        shutil.copy2(pdf_path, wiki_pdf_path)
    except Exception:
        pass

    # Register into policies.json
    register_schedule_in_policies(pdf_path, semester=semester)

    return SCHEDULE_JSON_PATH


def generate_section_schedule_pdf(sections: List[Dict[str, Any]], output_pdf: str, semester: str = "Fall 2026-2027") -> str:
    """Generate high-fidelity landscape PDF for the section schedule using ReportLab"""
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.pdfgen import canvas

    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)

    class NumberedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            num_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.draw_page_number(num_pages)
                canvas.Canvas.showPage(self)
            canvas.Canvas.save(self)

        def draw_page_number(self, page_count):
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(36, 20, "Dhofar University • Department of Computer Science & Engineering • Official Section Schedule")
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(842 - 36, 20, page_text)
            self.restoreState()

    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=landscape(A4),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0F172A')
    )
    sub_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#475569')
    )
    th_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1
    )
    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#1E293B')
    )
    cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#0F172A')
    )
    cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        alignment=1,
        textColor=colors.HexColor('#1E293B')
    )

    story = []
    story.append(Paragraph(f"DHOFAR UNIVERSITY — OFFICIAL SECTION SCHEDULE ({semester.upper()})", title_style))
    now_str = datetime.now().strftime("%B %d, %Y at %H:%M")
    story.append(Paragraph(
        f"<b>Source:</b> Student Information System (web.du.edu.om) &nbsp;|&nbsp; <b>Total Course Offerings:</b> {len(sections)} sections &nbsp;|&nbsp; <b>Generated:</b> {now_str}",
        sub_style
    ))
    story.append(Spacer(1, 14))

    headers = [
        Paragraph("<b>Crs. #</b>", th_style),
        Paragraph("<b>Course Title</b>", th_style),
        Paragraph("<b>Cr</b>", th_style),
        Paragraph("<b>Sec</b>", th_style),
        Paragraph("<b>Session</b>", th_style),
        Paragraph("<b>Lang</b>", th_style),
        Paragraph("<b>Cap</b>", th_style),
        Paragraph("<b>Enr</b>", th_style),
        Paragraph("<b>Instructor</b>", th_style),
        Paragraph("<b>Room</b>", th_style),
        Paragraph("<b>Days</b>", th_style),
        Paragraph("<b>Time</b>", th_style),
        Paragraph("<b>Remark / Prereq</b>", th_style)
    ]

    table_data = [headers]

    for sec in sections:
        c_code = sec.get('course_code', '')
        title = sec.get('title', '')
        cr = str(sec.get('credits', 3))
        sec_num = str(sec.get('section', '1'))
        sess = sec.get('session_type', 'Morning')
        lang = sec.get('language', 'English')
        cap = str(sec.get('capacity', 30))
        enr = str(sec.get('enrolled', 0))
        inst = sec.get('instructor', 'TBA')
        rm = sec.get('room', 'TBA')
        days = sec.get('days', 'TBA')
        t_slot = sec.get('time', 'TBA')
        rmk = sec.get('remark', '')

        row = [
            Paragraph(f"<b>{c_code}</b>", cell_bold),
            Paragraph(title, cell_style),
            Paragraph(cr, cell_center),
            Paragraph(sec_num, cell_center),
            Paragraph(sess, cell_center),
            Paragraph(lang, cell_center),
            Paragraph(cap, cell_center),
            Paragraph(enr, cell_center),
            Paragraph(inst, cell_style),
            Paragraph(rm, cell_center),
            Paragraph(days, cell_center),
            Paragraph(t_slot, cell_style),
            Paragraph(rmk, cell_style)
        ]
        table_data.append(row)

    col_widths = [55, 125, 20, 22, 45, 38, 24, 24, 85, 45, 55, 75, 185]

    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))

    story.append(t)
    doc.build(story, canvasmaker=NumberedCanvas)
    return output_pdf


def register_schedule_in_policies(pdf_path: str, semester: str = "Fall 2026-2027"):
    """Register or update section schedule in data/policies.json under 'Course Offerings & Section Schedule'"""
    policies = []
    if os.path.exists(POLICIES_JSON_PATH):
        try:
            with open(POLICIES_JSON_PATH, 'r', encoding='utf-8') as f:
                policies = json.load(f)
        except Exception:
            policies = []

    filename = os.path.basename(pdf_path)
    file_size_bytes = os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0
    if file_size_bytes > 1024 * 1024:
        size_str = f"{file_size_bytes / (1024 * 1024):.1f} MB"
    elif file_size_bytes > 1024:
        size_str = f"{file_size_bytes / 1024:.1f} KB"
    else:
        size_str = f"{file_size_bytes} B"

    page_count = 1
    try:
        import fitz
        doc = fitz.open(pdf_path)
        page_count = len(doc)
        doc.close()
    except Exception:
        pass

    policy_id = f"pol_schedule_{re.sub(r'[^a-zA-Z0-9]', '_', semester).lower()}"
    policy_entry = {
        "id": policy_id,
        "title": f"Official Course Section Schedule - {semester}",
        "category": "Course Offerings & Section Schedule",
        "filename": filename,
        "original_filename": filename,
        "file_size": size_str,
        "file_type": "pdf",
        "description": f"Official course offerings, sections, session types, instructors, meeting rooms, days, times, and capacity caps for {semester}.",
        "tags": ["schedule", "offerings", "sections", semester.lower().replace(" ", "-"), "registration"],
        "page_count": page_count,
        "uploaded_at": datetime.now().isoformat()
    }

    existing_idx = next((i for i, p in enumerate(policies) if p.get('id') == policy_id or p.get('filename') == filename), -1)
    if existing_idx >= 0:
        policies[existing_idx] = policy_entry
    else:
        policies.insert(0, policy_entry)

    with open(POLICIES_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(policies, f, indent=2, ensure_ascii=False)


def parse_sections_from_html(html_content: str, semester: str = "Fall 2026-2027") -> List[Dict[str, Any]]:
    """Parse offered course sections from DU SIS Section Schedule HTML report table"""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    sections = []

    tables = soup.find_all('table')
    target_table = None
    for tbl in tables:
        headers = [th.get_text(strip=True).upper() for th in tbl.find_all(['th', 'td'])]
        if any('CRS.#' in h or 'TITLE' in h or 'SECTION' in h or 'INSTRUCTOR' in h for h in headers):
            target_table = tbl
            break

    if not target_table and tables:
        target_table = tables[0]

    if target_table:
        rows = target_table.find_all('tr')
        current_crs_code = ""
        current_title = ""
        current_credits = "3"

        for row in rows:
            cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
            if len(cells) >= 8 and not any('CRS.#' in c.upper() for c in cells):
                crs_code = cells[0] if len(cells) > 0 else ""
                title = cells[1] if len(cells) > 1 else ""
                credits = cells[2] if len(cells) > 2 else ""
                sec_num = cells[3] if len(cells) > 3 else "1"
                session_type = cells[4] if len(cells) > 4 else "Morning"
                lang = cells[5] if len(cells) > 5 else "English"
                cap = cells[6] if len(cells) > 6 else "30"
                enr = cells[7] if len(cells) > 7 else "0"
                instructor = cells[8] if len(cells) > 8 else "TBA"
                room = cells[9] if len(cells) > 9 else "TBA"
                days = cells[10] if len(cells) > 10 else "TBA"
                time_slot = cells[11] if len(cells) > 11 else "TBA"
                remark = cells[12] if len(cells) > 12 else ""

                if crs_code and any(c.isdigit() for c in crs_code):
                    current_crs_code = crs_code
                    current_title = title
                    current_credits = credits if credits else "3"

                if current_crs_code and sec_num:
                    sections.append({
                        'course_code': current_crs_code,
                        'title': current_title,
                        'credits': int(current_credits) if str(current_credits).isdigit() else 3,
                        'section': sec_num,
                        'session_type': session_type or "Morning",
                        'language': lang or "English",
                        'capacity': int(cap) if str(cap).isdigit() else 30,
                        'enrolled': int(enr) if str(enr).isdigit() else 0,
                        'instructor': instructor,
                        'room': room,
                        'days': days,
                        'time': time_slot,
                        'remark': remark,
                        'semester': semester
                    })

    return sections


def parse_sections_from_pdf(pdf_path: str, semester: str = "Fall 2026-2027") -> List[Dict[str, Any]]:
    """Extract sections from PDF using PyMuPDF (fitz)"""
    import fitz
    sections = []
    doc = fitz.open(pdf_path)

    course_pattern = re.compile(r'([A-Z]{3,4}\s*\d{3}[A-Z]?)\s+(.*?)\s+(\d)\s+(\d+)\s+(Morning|Evening)?\s*(English|Arabic)?\s*(\d+)\s+(\d+)\s+(.*?)\s+([A-Z0-9\-_]+)\s+([A-Za-z]+)\s+(\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2})', re.IGNORECASE)

    for page in doc:
        text = page.get_text()
        for line in text.splitlines():
            line_str = line.strip()
            match = course_pattern.search(line_str)
            if match:
                sections.append({
                    'course_code': match.group(1).strip(),
                    'title': match.group(2).strip(),
                    'credits': int(match.group(3)),
                    'section': match.group(4).strip(),
                    'session_type': match.group(5) or 'Morning',
                    'language': match.group(6) or 'English',
                    'capacity': int(match.group(7)),
                    'enrolled': int(match.group(8)),
                    'instructor': match.group(9).strip(),
                    'room': match.group(10).strip(),
                    'days': match.group(11).strip(),
                    'time': match.group(12).strip(),
                    'remark': '',
                    'semester': semester
                })

    doc.close()
    return sections


def is_course_code_match(target_code: str, sec_code: str) -> bool:
    """Check if course codes match, accounting for Dhofar University curriculum variants (e.g. CMPS 110 vs CMPS 110N/110D)"""
    t = normalize_course_code(target_code)
    s = normalize_course_code(sec_code)
    if t == s:
        return True
    if s in (t + 'N', t + 'D', t + 'A', t + 'B'):
        return True
    if t in (s + 'N', s + 'D', s + 'A', s + 'B'):
        return True
    return False


def get_sections_for_course(course_code: str) -> List[Dict[str, Any]]:
    """Return all offered sections matching a given course code (including N/D equivalent variants)"""
    data = load_section_schedule()
    matched = []
    for s in data.get('sections', []):
        if is_course_code_match(course_code, s.get('course_code', '')):
            matched.append(s)
    return matched


def match_recommended_schedule_to_sections(recommended_schedule: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enrich an advisee's recommended course list with live offered sections,
    meeting times, instructors, rooms, and seat availability.
    """
    enriched = []
    data = load_section_schedule()
    all_sections = data.get('sections', [])

    for rec in recommended_schedule:
        c_code = rec.get('code', '')
        offered = [s for s in all_sections if is_course_code_match(c_code, s.get('course_code', ''))]

        rec_copy = dict(rec)
        rec_copy['is_offered'] = len(offered) > 0
        rec_copy['offered_sections_count'] = len(offered)
        rec_copy['sections'] = offered

        if offered:
            open_secs = [s for s in offered if s.get('enrolled', 0) < s.get('capacity', 30)]
            best_sec = open_secs[0] if open_secs else offered[0]
            rec_copy['primary_section'] = best_sec
            rec_copy['primary_slot'] = f"Sec {best_sec.get('section')} | {best_sec.get('days')} {best_sec.get('time')} | Room: {best_sec.get('room')} | {best_sec.get('instructor')}"
            seats_left = max(0, best_sec.get('capacity', 30) - best_sec.get('enrolled', 0))
            rec_copy['seats_available'] = seats_left
            rec_copy['seat_status'] = "Open" if seats_left > 0 else "Full"
        else:
            rec_copy['primary_section'] = None
            rec_copy['primary_slot'] = "Not Offered in Current Term"
            rec_copy['seats_available'] = 0
            rec_copy['seat_status'] = "Not Offered"

        enriched.append(rec_copy)

    return enriched
