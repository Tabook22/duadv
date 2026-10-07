"""Utility functions"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
from app.models import Student, PolicyReference

DEFAULT_DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'students.json')
DEFAULT_POLICIES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'policies')
DEFAULT_POLICIES_JSON = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'policies.json')


def save_students_to_file(students: List[Student], filepath: str = DEFAULT_DATA_FILE):
    """Save student data to JSON file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    students_data = []
    for student in students:
        student_dict = {
            'id': student.id,
            'name': student.name,
            'email': student.email,
            'phone': student.phone,
            'program': student.program,
            'status': student.status,
            'year': student.year,
            'gpa': student.gpa,
            'credits': student.credits,
            'advisor': student.advisor,
            'last_updated': datetime.now().isoformat()
        }
        students_data.append(student_dict)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(students_data, f, indent=2, ensure_ascii=False)

def parse_transcript_pdf(pdf_path: str) -> dict:
    """Parse major, advisor, gpa, year, and academic standing from downloaded PDF transcript"""
    import re
    try:
        import fitz
        doc = fitz.open(pdf_path)
        text = '\n'.join(page.get_text() for page in doc)
        
        major_m = re.search(r'Major:\s*([^\n\r]+)', text)
        major = major_m.group(1).strip() if major_m else None
        
        adv_m = re.search(r'Advisor:\s*([^\n\r]+)', text)
        advisor = adv_m.group(1).strip() if adv_m else 'Nasser Tabook'
        
        cr_m = re.search(r'Earn\s*Cr:\s*(\d+)', text)
        earn_cr = int(cr_m.group(1)) if cr_m else 0
        
        # Cumulative GPA search
        gpa = None
        cum_matches = list(re.finditer(r'Cumulative:\s*([\d\.\s]+)', text))
        if cum_matches:
            for cm in reversed(cum_matches):
                nums = cm.group(1).split()
                if nums:
                    try:
                        val = float(nums[-1])
                        if 0 < val <= 100:
                            gpa = val
                            break
                    except ValueError:
                        pass
                        
        if not gpa or gpa == 0:
            sem_matches = list(re.finditer(r'GPA\s*Semester:\s*([\d\.\s]+)', text))
            for sm in reversed(sem_matches):
                nums = sm.group(1).split()
                if nums:
                    try:
                        val = float(nums[-1])
                        if 0 < val <= 100:
                            gpa = val
                            break
                    except ValueError:
                        pass
                        
        year = 'Freshman (Year 1)'
        if earn_cr >= 90:
            year = 'Senior (Year 4)'
        elif earn_cr >= 60:
            year = 'Junior (Year 3)'
        elif earn_cr >= 30:
            year = 'Sophomore (Year 2)'
        else:
            year = 'Freshman (Year 1)'
            
        # Extract chronological academic standing / probation
        standings_hierarchy = [
            'Third/Strict Probation',
            'Second Strict Probation',
            'Strict Probation',
            'Second Probation',
            'First Probation',
            'Academic Probation Removal',
            'Very Good Standing',
            'Good Standing',
            'Normal/Good Standing'
        ]
        
        def _term_order(term_name):
            sm = re.search(r'(Fall|Spring|Summer)\s+(\d{2})-(\d{2})', term_name, re.I)
            if sm:
                season = sm.group(1).capitalize()
                y1 = int(sm.group(2))
                s_order = {'Fall': 1, 'Spring': 2, 'Summer': 3}.get(season, 0)
                return (y1, s_order)
            tm2 = re.search(r'Term(\d+)\s+(\d{4})-(\d{4})', term_name, re.I)
            if tm2:
                t_num = int(tm2.group(1))
                y = int(tm2.group(2)) % 100
                return (y, 0.1 * t_num)
            return (0, 0)

        clean_text = ' '.join(text.split())
        term_pattern = r'((?:Term\d+\s+\d{4}-\d{4}\s*\([^\)]+\)|(?:Fall|Spring|Summer)\s+\d{2}-\d{2}\s*\([^\)]+\)))'
        term_matches = list(re.finditer(term_pattern, clean_text))
        
        parsed_terms = []
        for idx, tm in enumerate(term_matches):
            t_name = tm.group(1).strip()
            t_start = tm.end()
            t_end = term_matches[idx+1].start() if idx+1 < len(term_matches) else len(clean_text)
            t_chunk = clean_text[t_start:t_end]
            
            t_standing = None
            for std in standings_hierarchy:
                if std in t_chunk:
                    t_standing = 'Second Strict Probation' if std == 'Strict Probation' else std
                    break
                    
            parsed_terms.append({
                'term': t_name,
                'order': _term_order(t_name),
                'standing': t_standing
            })
            
        parsed_terms.sort(key=lambda x: x['order'])
        
        latest_standing = 'Normal / Good Standing'
        for pt in parsed_terms:
            if pt['standing']:
                latest_standing = pt['standing']
                
        if latest_standing in ['Good Standing', 'Normal/Good Standing']:
            latest_standing = 'Normal / Good Standing'
            
        return {
            'program': major,
            'advisor': advisor,
            'gpa': gpa,
            'year': year,
            'credits': earn_cr,
            'status': latest_standing
        }
    except Exception:
        return {}

def get_student_semesters(student_id: str, transcripts_dir: str = None) -> List[Dict[str, Any]]:
    """Extract all semesters, courses, and term performance for a student from their PDF transcript"""
    import re
    if transcripts_dir is None:
        transcripts_dir = os.path.join(os.path.dirname(DEFAULT_DATA_FILE), 'transcripts')
    
    pdf_path = os.path.join(transcripts_dir, f"{student_id}_transcript.pdf")
    if not os.path.exists(pdf_path):
        return []
        
    try:
        import fitz
        doc = fitz.open(pdf_path)
        full_text = '\n'.join(page.get_text() for page in doc)
        text = ' '.join(full_text.split())
        
        def _term_order(tname):
            sm = re.search(r'(Fall|Spring|Summer)\s+(\d{2})-(\d{2})', tname, re.I)
            if sm:
                season = sm.group(1).capitalize()
                y1 = int(sm.group(2))
                s_order = {'Fall': 1, 'Spring': 2, 'Summer': 3}.get(season, 0)
                return (y1, s_order)
            tm2 = re.search(r'Term(\d+)\s+(\d{4})-(\d{4})', tname, re.I)
            if tm2:
                t_num = int(tm2.group(1))
                y = int(tm2.group(2)) % 100
                return (y, 0.1 * t_num)
            return (0, 0)

        term_pattern = r'((?:Term\d+\s+\d{4}-\d{4}\s*\([^\)]+\)|(?:Fall|Spring|Summer)\s+\d{2}-\d{2}\s*\([^\)]+\)))'
        term_matches = list(re.finditer(term_pattern, text))
        
        semesters = []
        for idx, tm in enumerate(term_matches):
            term_name = tm.group(1).strip()
            start = tm.end()
            end = term_matches[idx+1].start() if idx+1 < len(term_matches) else len(text)
            chunk = text[start:end]
            
            att_pos = chunk.find('Att. Cr')
            courses_chunk = chunk[:att_pos] if att_pos != -1 else chunk
            
            course_re = r'([A-Z]{2,5}\s+\d{3}[A-Z]?)\s+(.*?)\s+([0-4])\s+(\d+(?:\.\d+)?(?:\s*\(R:\d+\))?|\(R:\d+\)|[A-Z\+]+)(?=\s+[A-Z]{2,5}\s+\d{3}|\s*$)'
            courses = []
            for cm in re.finditer(course_re, courses_chunk):
                ccode = cm.group(1).strip()
                cname = cm.group(2).strip()
                crd = int(cm.group(3))
                grd = cm.group(4).strip()
                courses.append({
                    'code': ccode,
                    'name': cname,
                    'credits': crd,
                    'grade': grd
                })
                
            sem_gpa = None
            cum_gpa = None
            
            sem_m = re.search(r'Semester:\s*(\d+)\s+(\d+)\s+(\d+)\s+([\d\.]+)\s+([\d\.]+)', chunk)
            if sem_m:
                try:
                    sem_gpa = float(sem_m.group(5))
                except ValueError:
                    pass
                    
            cum_m = re.search(r'Cumulative:\s*(\d+)\s+(\d+)\s+(\d+)\s+([\d\.]+)\s+([\d\.]+)', chunk)
            if cum_m:
                try:
                    cum_gpa = float(cum_m.group(5))
                except ValueError:
                    pass
                    
            standing = 'Normal / Good Standing'
            standings_check = [
                'Third/Strict Probation',
                'Second Strict Probation',
                'Strict Probation',
                'Second Probation',
                'First Probation',
                'Academic Probation Removal',
                'Very Good Standing',
                'Good Standing',
                'Normal/Good Standing'
            ]
            for std in standings_check:
                if std in chunk:
                    standing = 'Second Strict Probation' if std == 'Strict Probation' else std
                    break
                    
            if standing in ['Good Standing', 'Normal/Good Standing']:
                standing = 'Normal / Good Standing'
                    
            season = 'Spring' if 'Spring' in term_name else 'Fall' if 'Fall' in term_name else 'Summer' if 'Summer' in term_name else 'Foundation'
            
            if courses or sem_gpa is not None:
                semesters.append({
                    'term': term_name,
                    'order': _term_order(term_name),
                    'season': season,
                    'courses': courses,
                    'semester_gpa': sem_gpa,
                    'cumulative_gpa': cum_gpa,
                    'standing': standing,
                    'total_credits': sum(c['credits'] for c in courses)
                })
                
        semesters.sort(key=lambda x: x['order'])
        return semesters
    except Exception as e:
        print(f"Error parsing semesters for {student_id}: {e}")
        return []

def get_student_latest_term_info(student_id: str, transcripts_dir: str = None) -> Dict[str, Any]:
    """Extract latest recorded semester GPA (SGPA), cumulative GPA (CGPA), term, and standing from transcript"""
    semesters = get_student_semesters(student_id, transcripts_dir)
    if not semesters:
        return {}
    latest = semesters[-1]
    return {
        'term': latest.get('term'),
        'season': latest.get('season'),
        'semester_gpa': latest.get('semester_gpa'),
        'cumulative_gpa': latest.get('cumulative_gpa'),
        'standing': latest.get('standing'),
        'total_credits': latest.get('total_credits')
    }

def get_student_study_plan(student: Student, transcripts_dir: str = None) -> Dict[str, Any]:
    """Calculate degree study plan progress: total credit hours, completed hours, remaining hours, and course status"""
    is_diploma = 'diploma' in (student.program or '').lower()
    total_plan_credits = 60 if is_diploma else 120
    
    semesters = get_student_semesters(student.id, transcripts_dir)
    
    # Map of taken courses
    taken = {}
    for s in semesters:
        for c in s['courses']:
            code_norm = c['code'].replace(' ', '').upper()
            taken[code_norm] = {
                'code': c['code'],
                'name': c['name'],
                'credits': c['credits'],
                'grade': c['grade'],
                'term': s['term']
            }
            
    # Standard Curriculum
    curriculum = [
        {'code': 'ENGL 101', 'name': 'Basic Academic English', 'credits': 3, 'category': 'University Requirement'},
        {'code': 'ARAB 101', 'name': 'Academic Writing in Arabic', 'credits': 3, 'category': 'University Requirement'},
        {'code': 'SOCS 102', 'name': 'Omani Society', 'credits': 3, 'category': 'University Requirement'},
        {'code': 'ENTR 200', 'name': 'Entrepreneurship: Innovation and Creativity', 'credits': 3, 'category': 'University Requirement'},
        {'code': 'MATH 199', 'name': 'Calculus I', 'credits': 3, 'category': 'College Requirement'},
        {'code': 'MATH 200', 'name': 'Calculus II', 'credits': 3, 'category': 'College Requirement'},
        {'code': 'MATH 320', 'name': 'Linear Algebra I', 'credits': 3, 'category': 'College Requirement'},
        {'code': 'MATH 370', 'name': 'Discrete Mathematics', 'credits': 3, 'category': 'College Requirement'},
        {'code': 'CMPS 100B', 'name': 'Introduction to Technical Computing for the Sciences', 'credits': 3, 'category': 'Major Core'},
        {'code': 'CMPS 110', 'name': 'Introduction to Programming', 'credits': 3, 'category': 'Major Core'},
        {'code': 'CMPS 150', 'name': 'Computer Programming', 'credits': 3, 'category': 'Major Core'},
        {'code': 'CMPS 180', 'name': 'Digital System Design', 'credits': 3, 'category': 'Major Core'},
        {'code': 'CMPS 215', 'name': 'Computer Organization with Assembly Language', 'credits': 3, 'category': 'Major Core'},
        {'code': 'CMPS 220', 'name': 'Data Structures', 'credits': 3, 'category': 'Major Core'},
        {'code': 'CMPS 240', 'name': 'Analysis of Algorithms', 'credits': 3, 'category': 'Major Core'},
        {'code': 'CMPS 250', 'name': 'Computer Networks', 'credits': 3, 'category': 'Major Core'},
        {'code': 'CMPS 255', 'name': 'Graphical User Interface', 'credits': 3, 'category': 'Major Core'},
        {'code': 'CMPS 260', 'name': 'Operating Systems', 'credits': 3, 'category': 'Major Core'},
        {'code': 'CMPS 270', 'name': 'Database Systems', 'credits': 3, 'category': 'Major Core'},
        {'code': 'CMPS 300', 'name': 'Human Computer Interaction', 'credits': 3, 'category': 'Major Core'},
        {'code': 'CMPS 310N', 'name': 'Programming Languages', 'credits': 3, 'category': 'Major Core'},
        {'code': 'CMPS 340', 'name': 'Advanced Programming in Java', 'credits': 3, 'category': 'Major Core'},
        {'code': 'CMPS 365', 'name': 'Artificial Intelligence', 'credits': 3, 'category': 'Major Core'},
        {'code': 'CMPS 410N', 'name': 'Software Engineering', 'credits': 3, 'category': 'Major Core'},
        {'code': 'CMPS 490', 'name': 'Senior Project / Capstone', 'credits': 3, 'category': 'Major Core'},
    ]
    
    plan_courses = []
    for pc in curriculum:
        c_norm = pc['code'].replace(' ', '').upper()
        if c_norm in taken:
            t_info = taken[c_norm]
            plan_courses.append({
                'code': pc['code'],
                'name': pc['name'],
                'credits': pc['credits'],
                'category': pc['category'],
                'status': 'Completed',
                'grade': t_info['grade'],
                'term': t_info['term']
            })
        else:
            plan_courses.append({
                'code': pc['code'],
                'name': pc['name'],
                'credits': pc['credits'],
                'category': pc['category'],
                'status': 'Remaining',
                'grade': None,
                'term': None
            })
            
    completed_credits = student.credits if student.credits is not None else sum(c['credits'] for c in plan_courses if c['status'] == 'Completed')
    remaining_credits = max(0, total_plan_credits - completed_credits)
    pct = min(100.0, round((completed_credits / total_plan_credits) * 100, 1)) if total_plan_credits > 0 else 0
    
    return {
        'program': student.program or ('Diploma in Computer Science' if is_diploma else 'Bachelor of Science in Computer Science'),
        'degree_type': 'Diploma' if is_diploma else 'Bachelor of Science',
        'total_plan_credits': total_plan_credits,
        'completed_credits': completed_credits,
        'remaining_credits': remaining_credits,
        'completion_percentage': pct,
        'plan_courses': plan_courses,
        'completed_count': sum(1 for c in plan_courses if c['status'] == 'Completed'),
        'remaining_count': sum(1 for c in plan_courses if c['status'] == 'Remaining')
    }

def load_students_from_file(filepath: str = DEFAULT_DATA_FILE) -> List[Student]:
    """Load student data from JSON file and enrich from downloaded transcript PDFs if present"""
    if not os.path.exists(filepath):
        return []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            students_data = json.load(f)
        
        transcripts_dir = os.path.join(os.path.dirname(filepath), 'transcripts')
        students = []
        for data in students_data:
            sid = str(data['id']).strip()
            
            # Enrich from PDF if available
            pdf_path = os.path.join(transcripts_dir, f"{sid}_transcript.pdf")
            program = data.get('program')
            status = data.get('status')
            advisor = data.get('advisor')
            gpa = data.get('gpa')
            cgpa = data.get('cgpa') or gpa
            semester_gpa = data.get('semester_gpa')
            year = data.get('year')
            credits = data.get('credits')
            
            if os.path.exists(pdf_path):
                parsed = parse_transcript_pdf(pdf_path)
                if parsed.get('program'):
                    program = parsed['program']
                if parsed.get('advisor'):
                    advisor = parsed['advisor']
                if parsed.get('gpa') is not None:
                    gpa = parsed['gpa']
                    cgpa = parsed['gpa']
                if parsed.get('year'):
                    year = parsed['year']
                if parsed.get('credits') is not None:
                    credits = parsed['credits']
                if parsed.get('status'):
                    status = parsed['status']
                    
                term_info = get_student_latest_term_info(sid, transcripts_dir)
                if term_info.get('semester_gpa') is not None:
                    semester_gpa = term_info['semester_gpa']
                if term_info.get('cumulative_gpa') is not None:
                    cgpa = term_info['cumulative_gpa']
                    gpa = cgpa
                    
            email = data.get('email') or f"{sid}@du.edu.om"
            
            student = Student(
                id=sid,
                name=data['name'],
                email=email,
                phone=data.get('phone'),
                program=program or 'Computer Science',
                status=status or 'Normal / Good Standing',
                year=year or 'N/A',
                gpa=gpa,
                cgpa=cgpa,
                semester_gpa=semester_gpa,
                credits=credits,
                advisor=advisor or "Nasser Tabook",
                last_updated=datetime.fromisoformat(data['last_updated']) if data.get('last_updated') else None
            )
            students.append(student)
        
        return students
    except Exception as e:
        print(f"Error loading students: {e}")
        return []

def format_student_name(name: str) -> str:
    """Format student name properly"""
    if not name:
        return ""
    return ' '.join(word.capitalize() for word in name.strip().split())

def validate_student_id(student_id: str) -> bool:
    """Validate student ID format"""
    return bool(student_id and len(student_id.strip()) >= 5)

def generate_student_transcript_pdf(student: Student, filepath: str):
    """Generate an official academic transcript PDF for a student"""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    elements = []
    elements.append(Paragraph('<b>DHOFAR UNIVERSITY</b>', styles['Title']))
    elements.append(Paragraph('Student Information System - Official Academic Record', styles['Heading3']))
    elements.append(Spacer(1, 12))
    
    info_data = [
        ['Student ID:', str(student.id), 'Academic Standing:', str(student.program or 'Normal / Good Standing')],
        ['Student Name:', str(student.name), 'Academic Advisor:', str(student.advisor or 'Nasser Tabook')],
        ['Faculty:', 'College of Arts and Applied Sciences', 'Status:', 'Enrolled / Active']
    ]
    info_table = Table(info_data, colWidths=[100, 180, 110, 150])
    info_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
        ('FONTNAME', (3,0), (3,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 15))
    
    # Summary Table
    summary_data = [
        ['Academic Status', 'Total Earned Credits', 'Advisor Notes', 'Degree Status'],
        [str(student.program or 'Good Standing'), 'In Progress', 'Advised for Current Semester', 'Active Degree Student']
    ]
    summary_table = Table(summary_data, colWidths=[140, 120, 150, 130])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white])
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph('<i>Official transcript generated automatically from Dhofar University Advisor Records.</i>', styles['Italic']))
    
    doc.build(elements)
    return filepath

def import_transcripts_from_zip(zip_source, replace_roster: bool = False, transcripts_dir: str = None, json_path: str = DEFAULT_DATA_FILE) -> Dict[str, Any]:
    """
    Extracts student transcript PDFs from a ZIP archive or file stream, parses
    student identity and chronological academic standings, and merges or replaces
    the roster in data/students.json.
    """
    import zipfile, re, fitz
    
    if transcripts_dir is None:
        transcripts_dir = os.path.join(os.path.dirname(json_path), 'transcripts')
    os.makedirs(transcripts_dir, exist_ok=True)
    
    if isinstance(zip_source, (str, bytes, os.PathLike)):
        zf = zipfile.ZipFile(zip_source, 'r')
    else:
        zf = zipfile.ZipFile(zip_source)
        
    extracted_students = []
    with zf:
        pdf_names = [n for n in zf.namelist() if n.lower().endswith('.pdf') and not n.startswith('__MACOSX')]
        if not pdf_names:
            return {'status': 'error', 'message': 'No PDF transcript files found in the ZIP archive.'}
            
        for name in pdf_names:
            pdf_bytes = zf.read(name)
            
            try:
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                text = '\n'.join(page.get_text() for page in doc)
            except Exception:
                continue
                
            id_m = re.search(r'ID:\s*(\d{6,9})\s+([^\n\r]+)', text)
            if id_m:
                sid = id_m.group(1).strip()
                sname = id_m.group(2).strip()
            else:
                fn_match = re.search(r'(\d{6,9})', os.path.basename(name))
                if fn_match:
                    sid = fn_match.group(1)
                    sname = f"Student {sid}"
                else:
                    continue
                    
            dest_pdf_path = os.path.join(transcripts_dir, f"{sid}_transcript.pdf")
            with open(dest_pdf_path, 'wb') as f_out:
                f_out.write(pdf_bytes)
                
            parsed = parse_transcript_pdf(dest_pdf_path)
            
            student = Student(
                id=sid,
                name=sname,
                email=f"{sid}@du.edu.om",
                phone=None,
                program=parsed.get('program') or 'Computer Science',
                status=parsed.get('status') or 'Normal / Good Standing',
                year=parsed.get('year') or 'N/A',
                gpa=parsed.get('gpa'),
                credits=parsed.get('credits'),
                advisor=parsed.get('advisor') or 'Nasser Tabook',
                last_updated=datetime.now()
            )
            extracted_students.append(student)
            
    if not extracted_students:
        return {'status': 'error', 'message': 'Could not extract valid student transcripts from the ZIP.'}
        
    if replace_roster:
        final_students = extracted_students
    else:
        existing_students = load_students_from_file(json_path)
        existing_map = {s.id: s for s in existing_students}
        for s in extracted_students:
            existing_map[s.id] = s
        final_students = list(existing_map.values())
        
    final_students.sort(key=lambda s: s.id)
    save_students_to_file(final_students, filepath=json_path)
    
    strict_count = sum(1 for s in final_students if 'Strict' in (s.status or '') or 'Third' in (s.status or ''))
    probation_count = sum(1 for s in final_students if 'Probation' in (s.status or '') and 'Removal' not in (s.status or ''))
    cleared_count = sum(1 for s in final_students if 'Removal' in (s.status or ''))
    good_standing_count = sum(1 for s in final_students if ('Good' in (s.status or '') or s.status == 'Normal / Good Standing') and 'Probation' not in (s.status or ''))
    
    return {
        'status': 'success',
        'imported_count': len(extracted_students),
        'total_count': len(final_students),
        'mode': 'replaced' if replace_roster else 'merged',
        'stats': {
            'strict': strict_count,
            'probation': probation_count,
            'cleared': cleared_count,
            'good_standing': good_standing_count
        },
        'message': f"Successfully {'replaced roster with' if replace_roster else 'imported and merged'} {len(extracted_students)} transcript(s). Total advisees: {len(final_students)}."
    }

def get_students_at_risk_breakdown(students: List[Student] = None) -> Dict[str, Any]:
    """
    Categorize advisees into Students at Risk groups:
    1. Strict Probation (Second/Third Strict Probation)
    2. Second Probation
    3. First Probation
    4. Pre-Probation Warning (GPA < 65% but not formally on probation)
    """
    if students is None:
        students = load_students_from_file()
        
    strict_probation = []
    second_probation = []
    first_probation = []
    low_gpa_warning = []
    
    for s in students:
        st = s.status or ''
        gpa = s.gpa
        
        if 'Strict' in st or 'Third' in st:
            strict_probation.append(s)
        elif 'Second Probation' in st:
            second_probation.append(s)
        elif 'First Probation' in st or ('Probation' in st and 'Removal' not in st):
            first_probation.append(s)
        elif gpa is not None and gpa < 65.0 and 'Removal' not in st and 'Good' not in st:
            low_gpa_warning.append(s)
            
    # Sort students by GPA ascending (most urgent first)
    strict_probation.sort(key=lambda s: (s.gpa if s.gpa is not None else 999))
    second_probation.sort(key=lambda s: (s.gpa if s.gpa is not None else 999))
    first_probation.sort(key=lambda s: (s.gpa if s.gpa is not None else 999))
    low_gpa_warning.sort(key=lambda s: (s.gpa if s.gpa is not None else 999))
    
    total_at_risk = len(strict_probation) + len(second_probation) + len(first_probation) + len(low_gpa_warning)
    
    return {
        'total_advisees': len(students),
        'total_at_risk': total_at_risk,
        'strict_probation': strict_probation,
        'second_probation': second_probation,
        'first_probation': first_probation,
        'low_gpa_warning': low_gpa_warning,
        'counts': {
            'strict': len(strict_probation),
            'second': len(second_probation),
            'first': len(first_probation),
            'warning': len(low_gpa_warning),
            'total': total_at_risk
        }
    }

def generate_students_at_risk_report_pdf(filepath: str, breakdown: Dict[str, Any] = None):
    """
    Generate an official Dhofar University Advisor Report for Students at Risk.
    Uses ReportLab to produce a structured, clean PDF report.
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    
    if breakdown is None:
        breakdown = get_students_at_risk_breakdown()
        
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Title'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1e3a8a')
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Heading2'],
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#334155'),
        alignment=1
    )
    h3_danger = ParagraphStyle('H3Danger', parent=styles['Heading3'], fontSize=11, textColor=colors.HexColor('#b91c1c'))
    h3_warning = ParagraphStyle('H3Warning', parent=styles['Heading3'], fontSize=11, textColor=colors.HexColor('#c2410c'))
    h3_first = ParagraphStyle('H3First', parent=styles['Heading3'], fontSize=11, textColor=colors.HexColor('#854d0e'))
    
    elements = []
    
    # Header
    elements.append(Paragraph('<b>DHOFAR UNIVERSITY</b>', title_style))
    elements.append(Paragraph('Department of Computer Science &mdash; Academic Advising Unit', subtitle_style))
    elements.append(Paragraph('<b>OFFICIAL REPORT: STUDENTS AT RISK (ACADEMIC PROBATION)</b>', subtitle_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=12))
    
    # Metadata info table
    now_str = datetime.now().strftime("%B %d, %Y")
    pct_str = f"{round(breakdown['total_at_risk']/breakdown['total_advisees']*100, 1)}%" if breakdown['total_advisees'] > 0 else "0%"
    meta_data = [
        ['Academic Advisor:', 'Dr. Nasser Tabook (001097)', 'Report Date:', now_str],
        ['Faculty:', 'College of Arts & Applied Sciences', 'Academic Term:', 'Academic Year 2025/2026'],
        ['Total Advisees:', str(breakdown['total_advisees']), 'Total Students at Risk:', f"{breakdown['total_at_risk']} ({pct_str})"]
    ]
    meta_table = Table(meta_data, colWidths=[110, 180, 120, 130])
    meta_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 12))
    
    # Summary Table of Categories
    summary_matrix = [
        ['Probation Stage', 'Risk Level', 'Student Count', 'Recommended Advising Action'],
        ['Strict Probation (2nd / 3rd)', 'CRITICAL', str(breakdown['counts']['strict']), 'Mandatory max 12 credits, repeating failed courses, weekly follow-up'],
        ['Second Probation', 'HIGH', str(breakdown['counts']['second']), 'Max 12-15 credits, prioritize major requirements with low grades'],
        ['First Probation', 'MODERATE', str(breakdown['counts']['first']), 'Academic warning advising, retake D/F grade courses, study plan adjustment']
    ]
    if breakdown['counts']['warning'] > 0:
        summary_matrix.append(['Pre-Probation Warning (GPA < 65)', 'MONITOR', str(breakdown['counts']['warning']), 'Monitor upcoming midterm results before probation threshold'])
        
    sum_table = Table(summary_matrix, colWidths=[140, 70, 75, 255])
    sum_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TEXTCOLOR', (1,1), (1,1), colors.HexColor('#b91c1c')),
        ('TEXTCOLOR', (1,2), (1,2), colors.HexColor('#c2410c')),
        ('TEXTCOLOR', (1,3), (1,3), colors.HexColor('#854d0e')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f8fafc'), colors.white])
    ]))
    elements.append(sum_table)
    elements.append(Spacer(1, 15))
    
    def _create_student_table(student_list, bg_color):
        t_data = [['Student ID', 'Student Full Name', 'Degree Program', 'CGPA', 'SGPA', 'Credits', 'Current Standing']]
        for st in student_list:
            cgpa_val = st.cgpa if st.cgpa is not None else st.gpa
            cgpa_s = f"{cgpa_val:.2f}%" if cgpa_val is not None else "N/A"
            sgpa_s = f"{st.semester_gpa:.2f}%" if st.semester_gpa is not None else "N/A"
            cr_s = f"{st.credits} hrs" if st.credits is not None else "N/A"
            t_data.append([st.id, st.name[:28], st.program or 'Computer Science', cgpa_s, sgpa_s, cr_s, st.status or 'At Risk'])
        t = Table(t_data, colWidths=[65, 140, 115, 48, 48, 48, 76])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), bg_color),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f8fafc'), colors.white])
        ]))
        return t
        
    # 1. Strict Probation Section
    if breakdown['strict_probation']:
        elements.append(Paragraph(f"<b>1. Critical Risk: Strict Probation ({len(breakdown['strict_probation'])} Students)</b>", h3_danger))
        elements.append(Spacer(1, 4))
        elements.append(_create_student_table(breakdown['strict_probation'], colors.HexColor('#b91c1c')))
        elements.append(Spacer(1, 12))
        
    # 2. Second Probation Section
    if breakdown['second_probation']:
        elements.append(Paragraph(f"<b>2. High Risk: Second Probation ({len(breakdown['second_probation'])} Students)</b>", h3_warning))
        elements.append(Spacer(1, 4))
        elements.append(_create_student_table(breakdown['second_probation'], colors.HexColor('#c2410c')))
        elements.append(Spacer(1, 12))
        
    # 3. First Probation Section
    if breakdown['first_probation']:
        elements.append(Paragraph(f"<b>3. Moderate Risk: First Probation ({len(breakdown['first_probation'])} Students)</b>", h3_first))
        elements.append(Spacer(1, 4))
        elements.append(_create_student_table(breakdown['first_probation'], colors.HexColor('#a16207')))
        elements.append(Spacer(1, 12))
        
    # 4. Low GPA Warning Section (if any)
    if breakdown['low_gpa_warning']:
        elements.append(Paragraph(f"<b>4. Pre-Probation Warning (GPA &lt; 65%) ({len(breakdown['low_gpa_warning'])} Students)</b>", styles['Heading4']))
        elements.append(Spacer(1, 4))
        elements.append(_create_student_table(breakdown['low_gpa_warning'], colors.HexColor('#475569')))
        elements.append(Spacer(1, 12))
        
    # Signatures block
    elements.append(Spacer(1, 15))
    sig_data = [
        ['OFFICIAL VERIFICATION & SIGNATURES'],
        ['Academic Advisor: Dr. Nasser Tabook'],
        ['Signature: __________________________________________________']
    ]
    sig_table = Table(sig_data, colWidths=[540])
    sig_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#1e293b')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
        ('FONTNAME', (0,2), (-1,2), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(sig_table)

    
    doc.build(elements)
    return filepath

def generate_students_at_risk_report_excel(filepath: str, breakdown: Dict[str, Any] = None) -> str:
    """
    Generate an official Dhofar University Excel (.xlsx) Report for Students at Risk.
    Includes two worksheets:
    1. 'Students at Risk Report': Formatted executive report with KPIs, grouped probation categories, and signature blocks.
    2. 'All At-Risk Data (Filterable)': Tabular flat data suitable for Excel filtering, sorting, and pivot tables.
    """
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    if breakdown is None:
        breakdown = get_students_at_risk_breakdown()
        
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    wb = openpyxl.Workbook()
    
    # Sheet 1: Categorized Report
    ws = wb.active
    ws.title = "Students at Risk Report"
    ws.views.sheetView[0].showGridLines = True
    
    font_title = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    font_sub = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    font_meta = Font(name="Calibri", size=10, italic=True, color="334155")
    font_sec_hdr = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    font_tbl_hdr = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_data = Font(name="Calibri", size=10)
    font_data_bold = Font(name="Calibri", size=10, bold=True)
    font_kpi_lbl = Font(name="Calibri", size=9, bold=True, color="64748B")
    
    fill_navy = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    fill_slate = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
    fill_strict = PatternFill(start_color="DC2626", end_color="DC2626", fill_type="solid")
    fill_second = PatternFill(start_color="EA580C", end_color="EA580C", fill_type="solid")
    fill_first = PatternFill(start_color="D97706", end_color="D97706", fill_type="solid")
    fill_warn = PatternFill(start_color="475569", end_color="475569", fill_type="solid")
    
    fill_hdr_gray = PatternFill(start_color="475569", end_color="475569", fill_type="solid")
    fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    
    thin_gray = Side(style='thin', color='CBD5E1')
    border_cell = Border(left=thin_gray, right=thin_gray, top=thin_gray, bottom=thin_gray)
    
    align_center = Alignment(horizontal='center', vertical='center')
    align_left = Alignment(horizontal='left', vertical='center')
    
    def style_range(ws_obj, cell_range, font=None, fill=None, alignment=None, border=None):
        for row in ws_obj[cell_range]:
            for cell in row:
                if font: cell.font = font
                if fill: cell.fill = fill
                if alignment: cell.alignment = alignment
                if border: cell.border = border

    # Title Banner (Row 1: Dhofar University • College • Department)
    ws.merge_cells('A1:H1')
    ws['A1'] = "DHOFAR UNIVERSITY  •  COLLEGE OF ARTS AND APPLIED SCIENCES  •  COMPUTER SCIENCES DEPARTMENT"
    font_title_img = Font(name="Calibri", size=12, bold=True, color="FFFFFF")
    style_range(ws, 'A1:H1', font=font_title_img, fill=fill_navy, alignment=align_center)
    ws.row_dimensions[1].height = 26
    
    # Subtitle Banner (Row 2: Academic Advising Report: Students at Academic Risk)
    ws.merge_cells('A2:H2')
    ws['A2'] = "ACADEMIC ADVISING REPORT: STUDENTS AT ACADEMIC RISK"
    font_sub_img = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    style_range(ws, 'A2:H2', font=font_sub_img, fill=fill_slate, alignment=align_center)
    ws.row_dimensions[2].height = 22
    
    # Metadata Line (Row 3: Advisor, Generated Date, Policy)
    now_str = datetime.now().strftime("%B %d, %Y - %H:%M")
    ws.merge_cells('A3:H3')
    ws['A3'] = f"Advisor: Dr. Nasser Tabook   |   Generated: {now_str}   |   Graduation Requirement: CGPA >= 65.0%   |   Article 14 Probation"
    font_meta_img = Font(name="Calibri", size=9.5, italic=True, color="334155")
    border_row3 = Border(bottom=thin_gray)
    style_range(ws, 'A3:H3', font=font_meta_img, alignment=align_center, border=border_row3)
    ws.row_dimensions[3].height = 20
    
    # Blank row 4
    ws.row_dimensions[4].height = 10

    # Summary KPI Cards (Row 5 & 6)
    kpi_layout = [
        ('A', 'B', "TOTAL ADVISEES", breakdown['total_advisees'], "1E3A8A"),
        ('C', 'C', "TOTAL AT RISK", breakdown['total_at_risk'], "DC2626"),
        ('D', 'D', "STRICT PROBATION", breakdown['counts']['strict'], "DC2626"),
        ('E', 'F', "SECOND PROBATION", breakdown['counts']['second'], "EA580C"),
        ('G', 'H', "FIRST PROBATION", breakdown['counts']['first'], "D97706"),
    ]
    
    for c_start, c_end, lbl, val, col_hex in kpi_layout:
        if c_start != c_end:
            ws.merge_cells(f"{c_start}5:{c_end}5")
            ws.merge_cells(f"{c_start}6:{c_end}6")
        top_cell = ws[f"{c_start}5"]
        val_cell = ws[f"{c_start}6"]
        
        top_cell.value = lbl
        top_cell.font = font_kpi_lbl
        top_cell.alignment = align_center
        top_cell.fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
        
        val_cell.value = val
        val_cell.font = Font(name="Calibri", size=16, bold=True, color=col_hex)
        val_cell.alignment = align_center
        val_cell.fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        
        for col_letter in [c_start, c_end]:
            ws[f"{col_letter}5"].border = border_cell
            ws[f"{col_letter}6"].border = border_cell
            
    ws.row_dimensions[5].height = 18
    ws.row_dimensions[6].height = 26
    ws.row_dimensions[7].height = 12
    
    current_row = 8
    
    def add_section(category_title, count, header_fill, student_list, default_recommendation):
        nonlocal current_row
        ws.merge_cells(f"A{current_row}:H{current_row}")
        banner_cell = ws[f"A{current_row}"]
        banner_cell.value = f"{category_title.upper()} ({count} Students)"
        banner_cell.font = font_sec_hdr
        banner_cell.fill = header_fill
        banner_cell.alignment = Alignment(horizontal='left', vertical='center', indent=1)
        ws.row_dimensions[current_row].height = 24
        current_row += 1
        
        headers = [
            ("Student ID", align_center),
            ("Student Full Name", align_left),
            ("Degree Program", align_left),
            ("Cumulative GPA (CGPA)", align_center),
            ("Semester GPA (SGPA)", align_center),
            ("Credits", align_center),
            ("Academic Standing", align_left),
            ("Advisory Action & Recommended Plan", align_left)
        ]
        
        for col_idx, (h_name, h_align) in enumerate(headers, start=1):
            cell = ws.cell(row=current_row, column=col_idx, value=h_name)
            cell.font = font_tbl_hdr
            cell.fill = fill_hdr_gray
            cell.alignment = h_align
            cell.border = border_cell
        ws.row_dimensions[current_row].height = 20
        current_row += 1
        
        if not student_list:
            ws.merge_cells(f"A{current_row}:H{current_row}")
            none_cell = ws[f"A{current_row}"]
            none_cell.value = "No students currently in this category."
            none_cell.font = Font(name="Calibri", size=10, italic=True, color="64748B")
            none_cell.alignment = align_center
            none_cell.border = border_cell
            ws.row_dimensions[current_row].height = 20
            current_row += 2
            return
            
        for idx, st in enumerate(student_list):
            is_even = (idx % 2 == 0)
            row_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid") if is_even else fill_zebra
            
            c_id = ws.cell(row=current_row, column=1, value=int(st.id) if st.id.isdigit() else st.id)
            c_id.font = font_data_bold
            c_id.alignment = align_center
            
            c_name = ws.cell(row=current_row, column=2, value=st.name)
            c_name.font = font_data_bold
            c_name.alignment = align_left
            
            c_prog = ws.cell(row=current_row, column=3, value=st.program or "Computer Science")
            c_prog.font = font_data
            c_prog.alignment = align_left
            
            cgpa_val = st.cgpa if st.cgpa is not None else st.gpa
            c_cgpa = ws.cell(row=current_row, column=4, value=cgpa_val if cgpa_val is not None else "N/A")
            c_cgpa.font = Font(name="Calibri", size=10, bold=True, color="DC2626" if (cgpa_val and cgpa_val < 65) else "000000")
            c_cgpa.alignment = align_center
            if isinstance(cgpa_val, (int, float)):
                c_cgpa.number_format = '0.00"%"'
                
            sgpa_val = st.semester_gpa
            c_sgpa = ws.cell(row=current_row, column=5, value=sgpa_val if sgpa_val is not None else "N/A")
            c_sgpa.font = Font(name="Calibri", size=10, bold=True, color="DC2626" if (sgpa_val and sgpa_val < 65) else "16A34A" if (sgpa_val and sgpa_val >= 65) else "000000")
            c_sgpa.alignment = align_center
            if isinstance(sgpa_val, (int, float)):
                c_sgpa.number_format = '0.00"%"'
                
            c_cr = ws.cell(row=current_row, column=6, value=st.credits if st.credits is not None else "-")
            c_cr.font = font_data
            c_cr.alignment = align_center
            
            c_st = ws.cell(row=current_row, column=7, value=st.status or "At Risk")
            c_st.font = font_data_bold
            c_st.alignment = align_left
            
            c_rec = ws.cell(row=current_row, column=8, value=default_recommendation)
            c_rec.font = font_data
            c_rec.alignment = align_left
            
            for col_i in range(1, 9):
                cell_i = ws.cell(row=current_row, column=col_i)
                cell_i.fill = row_fill
                cell_i.border = border_cell
                
            ws.row_dimensions[current_row].height = 20
            current_row += 1
            
        current_row += 1
        
    add_section(
        "Category 1: Strict Probation (Second / Third Strict)",
        len(breakdown['strict_probation']),
        fill_strict,
        breakdown['strict_probation'],
        "CRITICAL: Limit to max 12 credit hours. Immediately repeat failed (F) and low (D) courses. Bi-weekly advising required."
    )
    
    add_section(
        "Category 2: Second Academic Probation",
        len(breakdown['second_probation']),
        fill_second,
        breakdown['second_probation'],
        "HIGH RISK: Limit course load to 12-14 credits. Prioritize repeating prerequisite courses to raise cumulative GPA >= 65%."
    )
    
    add_section(
        "Category 3: First Academic Probation",
        len(breakdown['first_probation']),
        fill_first,
        breakdown['first_probation'],
        "MODERATE RISK: Academic counseling intervention. Adjust study plan, pair challenging courses with general electives."
    )
    
    if breakdown['low_gpa_warning']:
        add_section(
            "Category 4: Pre-Probation GPA Warning (Cumulative GPA < 65%)",
            len(breakdown['low_gpa_warning']),
            fill_warn,
            breakdown['low_gpa_warning'],
            "MONITORING: Cumulative GPA is below 65.0% threshold. Monitor continuous assessment to prevent entering formal probation."
        )
        
    current_row += 1
    ws.merge_cells(f"A{current_row}:H{current_row}")
    ws[f"A{current_row}"] = "OFFICIAL VERIFICATION & SIGNATURES"
    font_verif_hdr = Font(name="Calibri", size=11, bold=True, color="1E293B")
    fill_verif_hdr = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")
    style_range(ws, f"A{current_row}:H{current_row}", font=font_verif_hdr, fill=fill_verif_hdr, alignment=Alignment(horizontal='left', vertical='center', indent=1))
    ws.row_dimensions[current_row].height = 24
    current_row += 1
    
    ws.merge_cells(f"A{current_row}:H{current_row}")
    ws[f"A{current_row}"] = "Academic Advisor: Dr. Nasser Tabook"
    ws[f"A{current_row}"].font = Font(name="Calibri", size=11, bold=True, color="000000")
    ws[f"A{current_row}"].alignment = Alignment(horizontal='left', vertical='center', indent=1)
    ws.row_dimensions[current_row].height = 22
    current_row += 1
    
    ws.merge_cells(f"A{current_row}:H{current_row}")
    ws[f"A{current_row}"] = "Signature: __________________________________________________"
    ws[f"A{current_row}"].font = Font(name="Calibri", size=11, bold=False, color="000000")
    ws[f"A{current_row}"].alignment = Alignment(horizontal='left', vertical='center', indent=1)
    ws.row_dimensions[current_row].height = 24

    
    # Sheet 2: Flat Data for Filtering & Pivot Tables
    ws_flat = wb.create_sheet(title="All At-Risk Data (Filterable)")
    ws_flat.views.sheetView[0].showGridLines = True
    
    flat_headers = ["Category", "Risk Level", "Student ID", "Student Name", "Degree Program", "Cumulative GPA (CGPA %)", "Semester GPA (SGPA %)", "Earned Credits", "Academic Standing", "Recommended Action"]
    for col_idx, h_text in enumerate(flat_headers, start=1):
        cell = ws_flat.cell(row=1, column=col_idx, value=h_text)
        cell.font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        cell.fill = fill_navy
        cell.alignment = align_center
        cell.border = border_cell
    ws_flat.row_dimensions[1].height = 22
    
    flat_row = 2
    categories_flat = [
        ("Strict Probation", "CRITICAL", breakdown['strict_probation'], "Limit to max 12 credit hours. Immediately repeat F/D courses."),
        ("Second Probation", "HIGH", breakdown['second_probation'], "Limit course load to 12-14 credits. Prioritize repeating courses."),
        ("First Probation", "MODERATE", breakdown['first_probation'], "Academic counseling intervention. Study plan adjustment."),
        ("Pre-Probation Warning", "MONITOR", breakdown['low_gpa_warning'], "Cumulative GPA < 65%. Continuous assessment monitoring.")
    ]
    
    for cat_name, risk_lvl, st_list, rec_text in categories_flat:
        for st in st_list:
            ws_flat.cell(row=flat_row, column=1, value=cat_name).alignment = align_left
            c_risk = ws_flat.cell(row=flat_row, column=2, value=risk_lvl)
            c_risk.alignment = align_center
            if risk_lvl == "CRITICAL":
                c_risk.font = Font(name="Calibri", size=10, bold=True, color="DC2626")
            elif risk_lvl == "HIGH":
                c_risk.font = Font(name="Calibri", size=10, bold=True, color="EA580C")
            elif risk_lvl == "MODERATE":
                c_risk.font = Font(name="Calibri", size=10, bold=True, color="D97706")
                
            c_id = ws_flat.cell(row=flat_row, column=3, value=int(st.id) if st.id.isdigit() else st.id)
            c_id.alignment = align_center
            ws_flat.cell(row=flat_row, column=4, value=st.name).alignment = align_left
            ws_flat.cell(row=flat_row, column=5, value=st.program or "Computer Science").alignment = align_left
            
            cgpa_v = st.cgpa if st.cgpa is not None else st.gpa
            c_gpa = ws_flat.cell(row=flat_row, column=6, value=cgpa_v if cgpa_v is not None else "")
            c_gpa.alignment = align_center
            if isinstance(cgpa_v, (int, float)):
                c_gpa.number_format = '0.00"%"'
                if cgpa_v < 65.0:
                    c_gpa.font = Font(name="Calibri", size=10, bold=True, color="DC2626")
                    
            sgpa_v = st.semester_gpa
            c_sgpa_cell = ws_flat.cell(row=flat_row, column=7, value=sgpa_v if sgpa_v is not None else "")
            c_sgpa_cell.alignment = align_center
            if isinstance(sgpa_v, (int, float)):
                c_sgpa_cell.number_format = '0.00"%"'
                if sgpa_v < 65.0:
                    c_sgpa_cell.font = Font(name="Calibri", size=10, bold=True, color="DC2626")
                elif sgpa_v >= 65.0:
                    c_sgpa_cell.font = Font(name="Calibri", size=10, bold=True, color="16A34A")
                
            ws_flat.cell(row=flat_row, column=8, value=st.credits if st.credits is not None else "").alignment = align_center
            ws_flat.cell(row=flat_row, column=9, value=st.status or "").alignment = align_left
            ws_flat.cell(row=flat_row, column=10, value=rec_text).alignment = align_left
            
            for col_i in range(1, 11):
                ws_flat.cell(row=flat_row, column=col_i).border = border_cell
            ws_flat.row_dimensions[flat_row].height = 19
            flat_row += 1
            
    # Refined column widths
    ws.column_dimensions['A'].width = 13
    ws.column_dimensions['B'].width = 28
    ws.column_dimensions['C'].width = 22
    ws.column_dimensions['D'].width = 18
    ws.column_dimensions['E'].width = 18
    ws.column_dimensions['F'].width = 11
    ws.column_dimensions['G'].width = 24
    ws.column_dimensions['H'].width = 46
    
    ws_flat.column_dimensions['A'].width = 18
    ws_flat.column_dimensions['B'].width = 13
    ws_flat.column_dimensions['C'].width = 13
    ws_flat.column_dimensions['D'].width = 28
    ws_flat.column_dimensions['E'].width = 22
    ws_flat.column_dimensions['F'].width = 18
    ws_flat.column_dimensions['G'].width = 18
    ws_flat.column_dimensions['H'].width = 12
    ws_flat.column_dimensions['I'].width = 22
    ws_flat.column_dimensions['J'].width = 44
    
    wb.save(filepath)
    return filepath

def format_file_size(size_bytes: int) -> str:
    """Format bytes into readable size string"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def load_policies_from_file(filepath: str = DEFAULT_POLICIES_JSON, policies_dir: str = DEFAULT_POLICIES_DIR) -> List[PolicyReference]:
    """Load policy reference documents from JSON; initialize default DU regulations if missing"""
    if not os.path.exists(filepath):
        initialize_default_du_policies(policies_dir=policies_dir, json_path=filepath)
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        policies = []
        for item in data:
            up_dt = None
            if item.get('uploaded_at'):
                try:
                    up_dt = datetime.fromisoformat(item['uploaded_at'])
                except Exception:
                    up_dt = datetime.now()
                    
            pol = PolicyReference(
                id=item['id'],
                title=item['title'],
                category=item.get('category') or 'General Guidance',
                filename=item['filename'],
                original_filename=item.get('original_filename') or item['filename'],
                file_size=item.get('file_size') or 'N/A',
                file_type=item.get('file_type') or 'pdf',
                description=item.get('description') or '',
                tags=item.get('tags') or [],
                page_count=item.get('page_count'),
                uploaded_at=up_dt
            )
            policies.append(pol)
        return policies
    except Exception as e:
        print(f"Error loading policies: {e}")
        return []

def save_policies_to_file(policies: List[PolicyReference], filepath: str = DEFAULT_POLICIES_JSON):
    """Save policy reference list to JSON"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    serialized = []
    for p in policies:
        serialized.append({
            'id': p.id,
            'title': p.title,
            'category': p.category,
            'filename': p.filename,
            'original_filename': p.original_filename,
            'file_size': p.file_size,
            'file_type': p.file_type,
            'description': p.description or '',
            'tags': p.tags or [],
            'page_count': p.page_count,
            'uploaded_at': p.uploaded_at.isoformat() if p.uploaded_at else datetime.now().isoformat()
        })
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(serialized, f, indent=2, ensure_ascii=False)

def infer_policy_category(filename: str, default_category: str = "General Guidance") -> str:
    """Infer policy / guide category from filename keywords if Auto-Detect is chosen"""
    fn_lower = filename.lower().replace('_', ' ').replace('-', ' ')
    if any(k in fn_lower for k in ['plan of study', 'study plan', 'degree plan', 'pos']):
        return 'Plan of Study'
    elif any(k in fn_lower for k in ['requirement', 'prerequisite', 'eligibility', 'admission']):
        return 'Degree Requirements'
    elif any(k in fn_lower for k in ['probation', 'strict', 'warning', 'dismissal']):
        return 'Academic Probation & Standing'
    elif any(k in fn_lower for k in ['regulation', 'bylaw', 'code', 'constitution', 'policy']):
        return 'Academic Regulations'
    elif any(k in fn_lower for k in ['handbook', 'guide', 'guideline', 'manual']):
        return 'Study Guides & Guidelines'
    elif any(k in fn_lower for k in ['add drop', 'withdrawal', 'registration', 'course schedule']):
        return 'Registration & Add/Drop Bylaws'
    elif any(k in fn_lower for k in ['grading', 'exam', 'assessment', 'gpa']):
        return 'Grading & Examination Policy'
    return default_category if default_category and default_category != 'Auto-Detect' else 'General Guidance'

def save_multiple_uploaded_policy_files(uploaded_files, default_category: str = "Auto-Detect", default_description: str = "", default_tags: List[str] = None, policies_dir: str = DEFAULT_POLICIES_DIR, json_path: str = DEFAULT_POLICIES_JSON) -> List[PolicyReference]:
    """Process and save multiple uploaded policy/plan-of-study/guidance documents at once"""
    import re
    from werkzeug.utils import secure_filename
    
    os.makedirs(policies_dir, exist_ok=True)
    saved_policies = []
    existing = load_policies_from_file(filepath=json_path, policies_dir=policies_dir)
    
    for idx, uploaded_file in enumerate(uploaded_files):
        if not uploaded_file or not uploaded_file.filename:
            continue
            
        orig_name = uploaded_file.filename
        ext = orig_name.rsplit('.', 1)[-1].lower() if '.' in orig_name else 'pdf'
        if ext not in ['pdf', 'docx', 'doc', 'txt', 'rtf']:
            continue
            
        now_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_base = secure_filename(orig_name.rsplit('.', 1)[0]) or f"doc_{idx}"
        stored_filename = f"{now_ts}_{idx}_{safe_base}.{ext}"
        dest_path = os.path.join(policies_dir, stored_filename)
        
        uploaded_file.save(dest_path)
        file_bytes = os.path.getsize(dest_path)
        file_size_str = format_file_size(file_bytes)
        
        page_count = None
        if ext == 'pdf':
            try:
                import fitz
                doc = fitz.open(dest_path)
                page_count = len(doc)
            except Exception:
                page_count = 1
                
        policy_id = f"pol_{now_ts}_{idx}_{int(datetime.now().timestamp() % 10000)}"
        
        # Clean title from filename
        clean_title = orig_name.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ').strip()
        clean_title = ' '.join(w.capitalize() if not w.isupper() else w for w in clean_title.split())
        
        # Resolve Category
        if not default_category or default_category == 'Auto-Detect':
            category = infer_policy_category(orig_name, default_category='General Guidance')
        else:
            category = default_category
            
        # Tags extraction
        tag_list = []
        if isinstance(default_tags, str) and default_tags.strip():
            tag_list = [t.strip() for t in re.split(r'[,;\s]+', default_tags) if t.strip()]
        elif isinstance(default_tags, list):
            tag_list = default_tags[:]
            
        fn_l = orig_name.lower()
        if 'cyber' in fn_l and 'cybersecurity' not in tag_list:
            tag_list.append('cybersecurity')
        if 'data science' in fn_l and 'data science' not in tag_list:
            tag_list.append('data science')
        if 'diploma' in fn_l and 'diploma' not in tag_list:
            tag_list.append('diploma')
        if 'computer science' in fn_l and 'computer science' not in tag_list:
            tag_list.append('computer science')
        if any(k in fn_l for k in ['plan of study', 'study plan']) and 'plan of study' not in tag_list:
            tag_list.append('plan of study')
            
        desc = default_description.strip() if default_description else f"Official {category} reference guide"
        
        policy = PolicyReference(
            id=policy_id,
            title=clean_title,
            category=category,
            filename=stored_filename,
            original_filename=orig_name,
            file_size=file_size_str,
            file_type=ext,
            description=desc,
            tags=tag_list,
            page_count=page_count,
            uploaded_at=datetime.now()
        )
        saved_policies.append(policy)
        existing.insert(0, policy)
        
    if saved_policies:
        save_policies_to_file(existing, filepath=json_path)
        
    return saved_policies

def save_uploaded_policy_file(uploaded_file, title: str, category: str, description: str = "", tags: List[str] = None, policies_dir: str = DEFAULT_POLICIES_DIR, json_path: str = DEFAULT_POLICIES_JSON) -> PolicyReference:
    """Save an uploaded policy document, extract metadata & page count, and save to registry"""
    res = save_multiple_uploaded_policy_files(
        [uploaded_file],
        default_category=category,
        default_description=description,
        default_tags=tags,
        policies_dir=policies_dir,
        json_path=json_path
    )
    if not res:
        raise ValueError("Unsupported or invalid file format.")
    if title and title.strip():
        res[0].title = title.strip()
        existing = load_policies_from_file(filepath=json_path, policies_dir=policies_dir)
        for p in existing:
            if p.id == res[0].id:
                p.title = title.strip()
                break
        save_policies_to_file(existing, filepath=json_path)
    return res[0]


def delete_policy_file(policy_id: str, policies_dir: str = DEFAULT_POLICIES_DIR, json_path: str = DEFAULT_POLICIES_JSON) -> bool:
    """Delete a policy document and remove its registry entry"""
    policies = load_policies_from_file(filepath=json_path, policies_dir=policies_dir)
    target = None
    remaining = []
    for p in policies:
        if p.id == policy_id:
            target = p
        else:
            remaining.append(p)
            
    if not target:
        return False
        
    target_file = os.path.join(policies_dir, target.filename)
    if os.path.exists(target_file):
        try:
            os.remove(target_file)
        except Exception:
            pass
            
    save_policies_to_file(remaining, filepath=json_path)
    return True

def search_policy_documents(query: str, policies_dir: str = DEFAULT_POLICIES_DIR, json_path: str = DEFAULT_POLICIES_JSON) -> List[Dict[str, Any]]:
    """
    Full-text keyword & clause search across all registered Dhofar University policy guides and handbooks.
    Uses PyMuPDF (fitz) to extract matching paragraphs, exact page numbers, and highlighted snippets.
    """
    import re
    if not query or not query.strip():
        return []
        
    query_clean = query.strip()
    keywords = [k.lower() for k in re.split(r'\s+', query_clean) if len(k) > 1]
    if not keywords:
        keywords = [query_clean.lower()]
        
    policies = load_policies_from_file(filepath=json_path, policies_dir=policies_dir)
    results = []
    
    for p in policies:
        file_path = os.path.join(policies_dir, p.filename)
        doc_matches = []
        
        meta_score = 0
        if any(k in p.title.lower() for k in keywords):
            meta_score += 15
        if any(k in (p.description or '').lower() for k in keywords):
            meta_score += 10
        if any(k in [t.lower() for t in (p.tags or [])] for k in keywords):
            meta_score += 12
            
        if p.file_type == 'pdf' and os.path.exists(file_path):
            try:
                import fitz
                doc = fitz.open(file_path)
                for page_idx in range(len(doc)):
                    page_text = doc[page_idx].get_text()
                    page_lower = page_text.lower()
                    
                    for kw in keywords:
                        match_pos = page_lower.find(kw)
                        if match_pos != -1:
                            start_idx = max(0, match_pos - 80)
                            end_idx = min(len(page_text), match_pos + len(kw) + 120)
                            snippet = page_text[start_idx:end_idx].replace('\n', ' ').strip()
                            
                            doc_matches.append({
                                'page': page_idx + 1,
                                'matched_term': kw,
                                'snippet': f"...{snippet}..."
                            })
                            break
            except Exception:
                pass
                
        elif p.file_type == 'txt' and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as tf:
                    lines = tf.readlines()
                    for line_idx, line in enumerate(lines):
                        line_lower = line.lower()
                        for kw in keywords:
                            if kw in line_lower:
                                doc_matches.append({
                                    'page': 1,
                                    'matched_term': kw,
                                    'snippet': line.strip()[:200]
                                })
                                break
            except Exception:
                pass
                
        if doc_matches or meta_score > 0:
            results.append({
                'policy_id': p.id,
                'title': p.title,
                'category': p.category,
                'filename': p.filename,
                'file_type': p.file_type,
                'file_size': p.file_size,
                'page_count': p.page_count,
                'description': p.description,
                'matches': doc_matches[:4],
                'match_count': len(doc_matches)
            })
            
    return results

def initialize_default_du_policies(policies_dir: str = DEFAULT_POLICIES_DIR, json_path: str = DEFAULT_POLICIES_JSON):
    """
    Generate official Dhofar University starter policy reference documents:
    1. DU Undergraduate Academic Regulations & Probation Bylaws
    2. DU Academic Advising Handbook & Course Registration Bylaws
    """
    os.makedirs(policies_dir, exist_ok=True)
    
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', parent=styles['Title'], fontSize=16, leading=20, textColor=colors.HexColor('#1e3a8a'))
    h2_style = ParagraphStyle('DocH2', parent=styles['Heading2'], fontSize=11, leading=15, textColor=colors.HexColor('#1e3a8a'))
    body_style = ParagraphStyle('DocBody', parent=styles['BodyText'], fontSize=9.5, leading=13.5, textColor=colors.HexColor('#1e293b'))

    fn1 = "DU_Undergraduate_Academic_Regulations.pdf"
    p1_path = os.path.join(policies_dir, fn1)
    if not os.path.exists(p1_path):
        doc1 = SimpleDocTemplate(p1_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        elements1 = [
            Paragraph('<b>DHOFAR UNIVERSITY</b>', title_style),
            Paragraph('<b>Undergraduate Academic Regulations &amp; Academic Probation Bylaws</b>', h2_style),
            Paragraph('<i>Official Reference Guide for Academic Advisors, Department Chairs, and Faculty</i>', body_style),
            Spacer(1, 8),
            HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=10),
            Paragraph('<b>Article 14: Academic Probation and Good Standing Thresholds</b>', h2_style),
            Paragraph(
                '1. Any undergraduate student whose cumulative Grade Point Average (CGPA) falls below <b>65.0%</b> '
                'at the conclusion of any regular semester (Fall or Spring) shall be placed on Academic Probation.<br/>'
                '2. <b>First Probation:</b> The student is officially notified of academic jeopardy and course load is restricted '
                'to a maximum of <b>12 credit hours</b> in the subsequent semester.<br/>'
                '3. <b>Second Probation:</b> If a student on First Probation fails to achieve a semester average of &ge; 65.0% '
                'and their cumulative GPA remains below 65.0%, they proceed to Second Probation.<br/>'
                '4. <b>Strict Probation (2nd / 3rd):</b> Continued failure to recover GPA leads to Strict Probation with mandatory bi-weekly '
                'advising meetings and imminent dismissal warning if academic performance does not substantially improve.<br/>'
                '5. <b>Probation Removal:</b> When a student on probation elevates their cumulative GPA to &ge; 65.0%, they are cleared to Normal / Good Standing.',
                body_style
            ),
            Spacer(1, 10),
            Paragraph('<b>Article 18: Course Repetition Policy &amp; Grade Replacement</b>', h2_style),
            Paragraph(
                '1. A student may repeat any course in which they received a grade of <b>F</b>, <b>D</b>, or <b>D+</b>.<br/>'
                '2. When repeating a course, the highest grade obtained is counted in the calculation of the cumulative GPA, '
                'though all recorded attempts remain noted on the student\'s official transcript.<br/>'
                '3. Advisors must mandate repeating prerequisite courses with low grades before allowing enrollment in advanced courses.',
                body_style
            ),
            Spacer(1, 10),
            Paragraph('<b>Article 22: Course Registration Limits &amp; Overloads</b>', h2_style),
            Paragraph(
                '1. Standard full-time undergraduate course load is <b>15 to 18 credit hours</b> per semester.<br/>'
                '2. Students on probation cannot exceed <b>12 credit hours</b> without written approval from the Dean.<br/>'
                '3. Graduating seniors in their final semester may register for up to 19–21 credits with Dean authorization.',
                body_style
            )
        ]
        doc1.build(elements1)

    fn2 = "DU_Academic_Advising_Handbook.pdf"
    p2_path = os.path.join(policies_dir, fn2)
    if not os.path.exists(p2_path):
        doc2 = SimpleDocTemplate(p2_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        elements2 = [
            Paragraph('<b>DHOFAR UNIVERSITY</b>', title_style),
            Paragraph('<b>Academic Advising Handbook &amp; Student Guidance Manual</b>', h2_style),
            Paragraph('<i>Guidelines for Academic Advisors: Degree Audits, Add/Drop, and Early Warning Intervention</i>', body_style),
            Spacer(1, 8),
            HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=10),
            Paragraph('<b>Section 1: Academic Advisor Responsibilities</b>', h2_style),
            Paragraph(
                '1. Academic advisors are assigned to guide students through their degree plans, course selections, and university policies.<br/>'
                '2. Advisors must review the student\'s transcript and prerequisite compliance prior to approving semester registrations.<br/>'
                '3. For students on probation, advisors must formulate an Academic Recovery Plan restricting registration to 12 credit hours.',
                body_style
            ),
            Spacer(1, 10),
            Paragraph('<b>Section 2: Add/Drop &amp; Course Withdrawal Regulations</b>', h2_style),
            Paragraph(
                '1. Course changes (Add/Drop) are permitted only during the first week of classes via the student portal.<br/>'
                '2. Students may withdraw from a course with a grade of <b>W</b> prior to the 10th week of the semester with advisor consent.<br/>'
                '3. Unofficial withdrawal after the deadline results in a recorded grade of <b>WF</b> (Withdrawn Failing), calculated as 0% (F).',
                body_style
            ),
            Spacer(1, 10),
            Paragraph('<b>Section 3: Incomplete (I) Grades and Grade Appeals</b>', h2_style),
            Paragraph(
                '1. A grade of <b>I</b> may be granted when a student with satisfactory standing is prevented from completing final exams due to documented emergencies.<br/>'
                '2. Incomplete coursework must be completed within four weeks of the start of the following semester; otherwise, the grade becomes F.<br/>'
                '3. Grade appeal petitions must be submitted within two weeks of official semester grade publication.',
                body_style
            )
        ]
        doc2.build(elements2)

    # Document 3: Cybersecurity Plan of Study
    fn3 = "Cybersecurity_Plan_of_Study.pdf"
    p3_path = os.path.join(policies_dir, fn3)
    if not os.path.exists(p3_path):
        doc3 = SimpleDocTemplate(p3_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        elements3 = [
            Paragraph('<b>DHOFAR UNIVERSITY</b>', title_style),
            Paragraph('<b>Bachelor of Science in Cybersecurity &mdash; Official Plan of Study</b>', h2_style),
            Paragraph('<i>Department of Computer Science &bull; College of Arts and Applied Sciences</i>', body_style),
            Spacer(1, 8),
            HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=10),
            Paragraph('<b>Year 1 (Freshman): Foundation &amp; Core Computing</b>', h2_style),
            Paragraph('Fall: Intro to Computer Science (3), Calculus I (3), English Comm I (3), DU Elective (3), Islamic Studies (3).<br/>'
                      'Spring: Object-Oriented Programming (3), Discrete Mathematics (3), English Comm II (3), Physics I (3), Oman Civilization (3).', body_style),
            Spacer(1, 8),
            Paragraph('<b>Year 2 (Sophomore): Systems &amp; Networking</b>', h2_style),
            Paragraph('Fall: Data Structures &amp; Algorithms (3), Computer Architecture (3), Network Fundamentals (3), Linear Algebra (3).<br/>'
                      'Spring: Operating Systems (3), Database Systems (3), Cryptography Basics (3), Web Development (3).', body_style),
            Spacer(1, 8),
            Paragraph('<b>Year 3 (Junior): Advanced Cybersecurity Core</b>', h2_style),
            Paragraph('Fall: Network &amp; Perimeter Security (3), Secure Software Development (3), Cyber Laws &amp; Ethics (3), Statistics (3).<br/>'
                      'Spring: Ethical Hacking &amp; Penetration Testing (3), Digital Forensics (3), Security Operations (3), Major Elective (3).', body_style),
            Spacer(1, 8),
            Paragraph('<b>Year 4 (Senior): Capstone &amp; Professional Practice</b>', h2_style),
            Paragraph('Fall: Cloud Security (3), Industrial Internship (3), Senior Project I (3), Free Elective (3).<br/>'
                      'Spring: Incident Response (3), Senior Project II (3), Advanced Security Elective (3). Total: 124 Credit Hours.', body_style)
        ]
        doc3.build(elements3)

    # Document 4: Diploma in Computer Science Plan of Study
    fn4 = "Diploma_in_Computer_Science_Plan_of_Study.pdf"
    p4_path = os.path.join(policies_dir, fn4)
    if not os.path.exists(p4_path):
        doc4 = SimpleDocTemplate(p4_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        elements4 = [
            Paragraph('<b>DHOFAR UNIVERSITY</b>', title_style),
            Paragraph('<b>Diploma in Computer Science &mdash; Official Plan of Study</b>', h2_style),
            Paragraph('<i>Two-Year Degree Program &bull; Department of Computer Science</i>', body_style),
            Spacer(1, 8),
            HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=10),
            Paragraph('<b>Year 1 (Level 1): Core Foundations</b>', h2_style),
            Paragraph('Semester 1: Computer Programming I (3), Intro to Computing (3), College Algebra (3), English I (3), Arabic (3).<br/>'
                      'Semester 2: Computer Programming II (3), Web Development Basics (3), Discrete Mathematics (3), English II (3).', body_style),
            Spacer(1, 8),
            Paragraph('<b>Year 2 (Level 2): Applied Technical Skills</b>', h2_style),
            Paragraph('Semester 3: Data Structures (3), Database Management Systems (3), Computer Networks (3), University Elective (3).<br/>'
                      'Semester 4: Software Engineering (3), Operating Systems (3), Diploma Graduation Project (3). Total: 65 Credit Hours.', body_style)
        ]
        doc4.build(elements4)

    # Document 5: Requirements for Studying Computer Science Diploma
    fn5 = "Requirements_for_Studying_Computer_Science_Diploma.pdf"
    p5_path = os.path.join(policies_dir, fn5)
    if not os.path.exists(p5_path):
        doc5 = SimpleDocTemplate(p5_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        elements5 = [
            Paragraph('<b>DHOFAR UNIVERSITY</b>', title_style),
            Paragraph('<b>Requirements for Studying Computer Science Diploma</b>', h2_style),
            Paragraph('<i>Admission Criteria, Prerequisite Rules, and Continuation Policies</i>', body_style),
            Spacer(1, 8),
            HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=10),
            Paragraph('<b>1. General Admission Criteria</b>', h2_style),
            Paragraph('Applicants must hold a General Education Diploma (Thanawiya) with minimum 65% in Pure or Applied Mathematics and English proficiency test clearance.', body_style),
            Spacer(1, 8),
            Paragraph('<b>2. Academic Progression &amp; Good Standing</b>', h2_style),
            Paragraph('Diploma students must maintain a minimum cumulative GPA of 65.0%. Students with CGPA below 65% will be placed on Academic Probation with a 12-credit cap.', body_style),
            Spacer(1, 8),
            Paragraph('<b>3. Bridge to Bachelor\'s Degree</b>', h2_style),
            Paragraph('Graduates with a Diploma GPA &ge; 75% are eligible for direct articulation and course transfer into the B.Sc. in Computer Science, Cybersecurity, or Data Science.', body_style)
        ]
        doc5.build(elements5)

    # Document 6: Data Science Plan of Study
    fn6 = "Data_Science_Plan_of_Study.pdf"
    p6_path = os.path.join(policies_dir, fn6)
    if not os.path.exists(p6_path):
        doc6 = SimpleDocTemplate(p6_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        elements6 = [
            Paragraph('<b>DHOFAR UNIVERSITY</b>', title_style),
            Paragraph('<b>Bachelor of Science in Data Science &mdash; Official Plan of Study</b>', h2_style),
            Paragraph('<i>Four-Year Curriculum &bull; Department of Computer Science</i>', body_style),
            Spacer(1, 8),
            HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=10),
            Paragraph('<b>Curriculum Highlights</b>', h2_style),
            Paragraph('Covers Python Programming, Machine Learning, Statistical Inference, Big Data Analytics, Neural Networks, and Capstone Data Science Research Project. Total: 124 Credit Hours.', body_style)
        ]
        doc6.build(elements6)

    now = datetime.now()
    default_records = [
        PolicyReference(
            id="pol_du_undergrad_regulations",
            title="Dhofar University Undergraduate Academic Regulations & Probation Bylaws",
            category="Academic Regulations",
            filename=fn1,
            original_filename=fn1,
            file_size=format_file_size(os.path.getsize(p1_path)) if os.path.exists(p1_path) else "25 KB",
            file_type="pdf",
            description="Official DU academic policies governing cumulative GPA thresholds, Academic Probation stages, max 12 credit limits, and repeating D/F courses.",
            tags=["probation", "strict probation", "gpa 65%", "credit limit", "repeat course", "regulations"],
            page_count=1,
            uploaded_at=now
        ),
        PolicyReference(
            id="pol_du_advising_handbook",
            title="DU Academic Advising Handbook & Registration Guidance Manual",
            category="Study Guides & Guidelines",
            filename=fn2,
            original_filename=fn2,
            file_size=format_file_size(os.path.getsize(p2_path)) if os.path.exists(p2_path) else "25 KB",
            file_type="pdf",
            description="Advisor guide for student degree audits, prerequisite verification, Add/Drop calendar, W/WF withdrawal, and incomplete (I) grade procedures.",
            tags=["advising", "handbook", "add drop", "withdrawal", "incomplete grade", "registration"],
            page_count=1,
            uploaded_at=now
        ),
        PolicyReference(
            id="pol_cybersecurity_plan_of_study",
            title="Cybersecurity Plan of Study (B.Sc.)",
            category="Plan of Study",
            filename=fn3,
            original_filename=fn3,
            file_size=format_file_size(os.path.getsize(p3_path)) if os.path.exists(p3_path) else "25 KB",
            file_type="pdf",
            description="Four-year study plan for B.Sc. in Cybersecurity, detailing semester-by-semester courses, prerequisites, and credit distribution.",
            tags=["cybersecurity", "plan of study", "degree plan", "network security", "cryptography"],
            page_count=1,
            uploaded_at=now
        ),
        PolicyReference(
            id="pol_diploma_cs_plan_of_study",
            title="Diploma in Computer Science Plan of Study",
            category="Plan of Study",
            filename=fn4,
            original_filename=fn4,
            file_size=format_file_size(os.path.getsize(p4_path)) if os.path.exists(p4_path) else "20 KB",
            file_type="pdf",
            description="Official two-year academic curriculum for Diploma in Computer Science covering core programming, networks, and databases.",
            tags=["diploma", "computer science", "plan of study", "programming"],
            page_count=1,
            uploaded_at=now
        ),
        PolicyReference(
            id="pol_requirements_diploma_cs",
            title="Requirements for Studying Computer Science Diploma",
            category="Degree Requirements",
            filename=fn5,
            original_filename=fn5,
            file_size=format_file_size(os.path.getsize(p5_path)) if os.path.exists(p5_path) else "18 KB",
            file_type="pdf",
            description="Admission criteria, prerequisite completion, GPA thresholds, and bridge requirements for Computer Science Diploma.",
            tags=["diploma", "computer science", "requirements", "admission", "prerequisites"],
            page_count=1,
            uploaded_at=now
        ),
        PolicyReference(
            id="pol_data_science_plan_of_study",
            title="Data Science Plan of Study (B.Sc.)",
            category="Plan of Study",
            filename=fn6,
            original_filename=fn6,
            file_size=format_file_size(os.path.getsize(p6_path)) if os.path.exists(p6_path) else "20 KB",
            file_type="pdf",
            description="Four-year curriculum plan for Bachelor of Science in Data Science, including machine learning, big data, and statistics.",
            tags=["data science", "plan of study", "degree plan", "machine learning"],
            page_count=1,
            uploaded_at=now
        )
    ]
    save_policies_to_file(default_records, filepath=json_path)
    return default_records




