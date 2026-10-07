import fitz, re, json

def parse_semester_courses_exact(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = '\n'.join(page.get_text() for page in doc)
    text = ' '.join(full_text.split())
    
    term_pattern = r'((?:Term\d+\s+\d{4}-\d{4}\s*\([^\)]+\)|(?:Fall|Spring|Summer)\s+\d{2}-\d{2}(?:\s*\([^\)]+\))?))'
    term_matches = list(re.finditer(term_pattern, text))
    
    semesters = []
    for idx, tm in enumerate(term_matches):
        term_name = tm.group(1).strip()
        start = tm.end()
        end = term_matches[idx+1].start() if idx+1 < len(term_matches) else len(text)
        chunk = text[start:end]
        
        att_pos = chunk.find('Att. Cr')
        courses_chunk = chunk[:att_pos] if att_pos != -1 else chunk
        
        course_re = r'([A-Z]{2,5}\s+\d{3}[A-Z]?)\s+(.*?)\s+(\d+)\s+(\d+(?:\.\d+)?|\(R:\d+\)|[A-Z\+]+)(?=\s+[A-Z]{2,5}\s+\d{3}|$)'
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
        for std in ['Academic Probation Removal', 'First Probation', 'Second Probation', 'Second Strict Probation', 'Third/Strict Probation', 'Very Good Standing', 'Good Standing']:
            if std in chunk:
                standing = std
                break
                
        season = 'Spring' if 'Spring' in term_name else 'Fall' if 'Fall' in term_name else 'Summer' if 'Summer' in term_name else 'Foundation'
        
        if courses or sem_gpa is not None:
            semesters.append({
                'term': term_name,
                'season': season,
                'courses': courses,
                'semester_gpa': sem_gpa,
                'cumulative_gpa': cum_gpa,
                'standing': standing
            })
            
    return semesters

if __name__ == '__main__':
    res = parse_semester_courses_exact('data/transcripts/202120056_transcript.pdf')
    print(f'Total semesters parsed: {len(res)}')
    for s in res:
        print(f"=== {s['term']} ({s['season']}) | Sem GPA: {s['semester_gpa']} | Cum GPA: {s['cumulative_gpa']} | {s['standing']} ===")
        for c in s['courses']:
            print(f"   - {c['code']}: {c['name']} ({c['credits']} Cr) -> Grade: {c['grade']}")
