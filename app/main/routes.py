"""Main application routes"""

import os
import time
from flask import render_template, request, jsonify, current_app, url_for, session, redirect, flash
from app.main import bp
from app.scraper.university_scraper import UniversitySystemManager
from app.utils import save_students_to_file, load_students_from_file

@bp.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@bp.route('/dashboard')
def dashboard():
    """Main dashboard"""
    students = load_students_from_file()
    
    strict_count = sum(1 for s in students if 'Strict' in (s.status or '') or 'Third' in (s.status or ''))
    probation_count = sum(1 for s in students if 'Probation' in (s.status or '') and 'Removal' not in (s.status or ''))
    cleared_count = sum(1 for s in students if 'Removal' in (s.status or ''))
    good_standing_count = sum(1 for s in students if ('Good' in (s.status or '') or s.status == 'Normal / Good Standing') and 'Probation' not in (s.status or ''))
    
    return render_template(
        'dashboard.html', 
        students=students, 
        student_count=len(students),
        strict_count=strict_count,
        probation_count=probation_count,
        cleared_count=cleared_count,
        good_standing_count=good_standing_count
    )

@bp.route('/students')
def students():
    """Student list page"""
    students = load_students_from_file()
    
    strict_count = sum(1 for s in students if 'Strict' in (s.status or '') or 'Third' in (s.status or ''))
    probation_count = sum(1 for s in students if 'Probation' in (s.status or '') and 'Removal' not in (s.status or ''))
    cleared_count = sum(1 for s in students if 'Removal' in (s.status or ''))
    good_standing_count = sum(1 for s in students if ('Good' in (s.status or '') or s.status == 'Normal / Good Standing') and 'Probation' not in (s.status or ''))
    
    return render_template(
        'students.html', 
        students=students,
        strict_count=strict_count,
        probation_count=probation_count,
        cleared_count=cleared_count,
        good_standing_count=good_standing_count
    )

@bp.route('/student/<student_id>')
def student_detail(student_id):
    """Individual student detail page with Deep Degree Audit & Intelligent Advising Dossier"""
    students = load_students_from_file()
    student = next((s for s in students if s.id == student_id), None)
    
    if not student:
        return render_template('errors/404.html'), 404
        
    from app.utils import get_student_semesters, get_student_study_plan
    from app.advising_engine import audit_student_degree, generate_student_advising_dossier
    semesters = get_student_semesters(student.id)
    study_plan = get_student_study_plan(student)
    audit = audit_student_degree(student.id)
    dossier = generate_student_advising_dossier(student.id)
    
    return render_template(
        'student_detail.html',
        student=student,
        semesters=semesters,
        study_plan=study_plan,
        audit=audit,
        dossier=dossier
    )

@bp.route('/api/sync-students/stream', methods=['POST'])
def sync_students_stream():
    """Streaming SSE endpoint to run university sync and yield real-time progress steps"""
    from flask import Response
    import json
    
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    download_transcripts = data.get('download_transcripts', False)

    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Username and password required'}), 400

    def generate():
        import queue
        q = queue.Queue()

        def progress_cb(pct, step, msg):
            q.put({"type": "progress", "percent": pct, "step": step, "message": msg})

        def worker():
            manager = None
            try:
                progress_cb(2, "Initializing", "Initializing Selenium Chrome driver...")
                manager = UniversitySystemManager()

                login_res = manager.login_to_system(username, password, progress_callback=progress_cb)
                if login_res.get('status') != 'success':
                    q.put({"type": "error", "message": login_res.get('message', 'Login failed')})
                    if manager:
                        manager.close_driver()
                    return

                nav_res = manager.navigate_to_student_list(progress_callback=progress_cb)
                if nav_res.get('status') != 'success':
                    q.put({"type": "error", "message": nav_res.get('message', 'Navigation failed')})
                    if manager:
                        manager.close_driver()
                    return

                extract_res = manager.extract_student_list(progress_callback=progress_cb)
                students_data = extract_res.get('students', [])

                pdf_res = None
                if download_transcripts:
                    pdf_res = manager.download_transcripts_as_pdf(progress_callback=progress_cb)

                manager.close_driver()
                manager = None

                # Post-sync saving and Second-Brain Wiki compilation
                progress_cb(88, "Saving Records", f"Saving {len(students_data)} advisee student records to disk...")
                if extract_res.get('status') == 'success' and students_data:
                    from app.models import Student
                    students = [
                        Student(
                            id=s['id'],
                            name=s['name'],
                            program=s.get('program'),
                            status=s.get('status')
                        ) for s in students_data
                    ]
                    save_students_to_file(students)

                # Recompile Second-Brain wiki dossiers
                progress_cb(93, "Compiling Second-Brain Wiki", "Recompiling student dossiers, academic standing & audit plans...")
                try:
                    from app.wiki_compiler import full_wiki_recompile
                    full_wiki_recompile()
                except Exception as we:
                    current_app.logger.warning(f"Wiki recompile warning: {we}")

                progress_cb(100, "Completed", f"Sync complete! {len(students_data)} advisee profiles updated successfully.")
                q.put({
                    "type": "done",
                    "status": "success",
                    "count": len(students_data),
                    "students": students_data,
                    "transcripts": pdf_res,
                    "message": f"Successfully synced {len(students_data)} advisees."
                })
            except Exception as e:
                if manager:
                    try:
                        manager.close_driver()
                    except Exception:
                        pass
                current_app.logger.error(f"Sync stream error: {e}")
                q.put({"type": "error", "message": f"Sync failed: {str(e)}"})
            finally:
                q.put(None)  # Sentinel

        import threading
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

        while True:
            try:
                item = q.get(timeout=45)
                if item is None:
                    break
                yield f"data: {json.dumps(item)}\n\n"
            except queue.Empty:
                # Send heartbeat
                yield f": heartbeat\n\n"

    return Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no',
        'Connection': 'keep-alive'
    })

@bp.route('/api/sync-students', methods=['POST'])
def sync_students():
    """API endpoint to sync students and optionally transcripts from university system"""
    manager = None
    try:
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')
        download_transcripts = data.get('download_transcripts', False)
        
        if not username or not password:
            return jsonify({'status': 'error', 'message': 'Username and password required'}), 400
        
        manager = UniversitySystemManager()
        
        # Login to university system
        login_result = manager.login_to_system(username, password)
        if login_result['status'] != 'success':
            manager.close_driver()
            return jsonify(login_result), 401
        
        # Navigate to student list
        nav_result = manager.navigate_to_student_list()
        if nav_result['status'] != 'success':
            manager.close_driver()
            return jsonify(nav_result), 500
        
        # Extract student data
        extract_result = manager.extract_student_list()
        
        # Optionally download transcripts as PDF
        pdf_result = None
        if download_transcripts:
            pdf_result = manager.download_transcripts_as_pdf()
            
        manager.close_driver()
        
        if extract_result['status'] == 'success':
            # Save to file
            from app.models import Student
            students = [
                Student(
                    id=s['id'], 
                    name=s['name'], 
                    program=s.get('program'),
                    status=s.get('status')
                ) for s in extract_result['students']
            ]
            save_students_to_file(students)
            try:
                from app.wiki_compiler import full_wiki_recompile
                full_wiki_recompile()
            except Exception:
                pass
            current_app.logger.info(f"Successfully synced {len(students)} students")
            
        return jsonify({
            'status': 'success',
            'students': extract_result.get('students', []),
            'count': len(extract_result.get('students', [])),
            'transcripts': pdf_result,
            'message': f"Successfully synced {len(extract_result.get('students', []))} students"
        })
        
    except Exception as e:
        if manager:
            manager.close_driver()
        current_app.logger.error(f"Sync error: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Sync failed: {str(e)}'}), 500

@bp.route('/student/<student_id>/transcript/pdf')
def student_transcript_pdf(student_id):
    """Download or view student transcript PDF, generating it on-demand if needed"""
    import os
    from flask import send_file
    from app.utils import generate_student_transcript_pdf
    
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    filepath = os.path.join(project_root, 'data', 'transcripts', f"{student_id}_transcript.pdf")
    
    if not os.path.exists(filepath):
        # Look up student from database
        students = load_students_from_file()
        student = next((s for s in students if str(s.id).strip() == str(student_id).strip()), None)
        if student:
            generate_student_transcript_pdf(student, filepath)
        else:
            return jsonify({'status': 'error', 'message': f'Student {student_id} not found in advisee records.'}), 404
            
    return send_file(filepath, mimetype='application/pdf', as_attachment=False, download_name=f"{student_id}_transcript.pdf")

@bp.route('/api/download-transcripts-zip')
def download_transcripts_zip():
    """Download all transcript PDFs as a single ZIP bundle"""
    import os, io, zipfile
    from flask import send_file
    from app.utils import generate_student_transcript_pdf
    
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    transcripts_dir = os.path.join(project_root, 'data', 'transcripts')
    os.makedirs(transcripts_dir, exist_ok=True)
    
    # Ensure all loaded students have a PDF generated
    students = load_students_from_file()
    for student in students:
        s_path = os.path.join(transcripts_dir, f"{student.id}_transcript.pdf")
        if not os.path.exists(s_path):
            try:
                generate_student_transcript_pdf(student, s_path)
            except Exception:
                pass
                
    pdf_files = [f for f in os.listdir(transcripts_dir) if f.endswith('.pdf')]
    if not pdf_files:
        return jsonify({'status': 'error', 'message': 'No PDF transcripts available to zip.'}), 404
        
    memory_zip = io.BytesIO()
    with zipfile.ZipFile(memory_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in pdf_files:
            file_path = os.path.join(transcripts_dir, f)
            zf.write(file_path, arcname=f)
            
    memory_zip.seek(0)
    return send_file(
        memory_zip,
        mimetype='application/zip',
        as_attachment=True,
        download_name='advisee_transcripts_pdf.zip'
    )

@bp.route('/api/import-advisee-html', methods=['POST'])
def import_advisee_html():
    """Import advisees directly from copied HTML / table content"""
    try:
        from bs4 import BeautifulSoup
        from app.models import Student
        
        data = request.get_json() or {}
        html_content = data.get('html', '')
        
        if not html_content.strip():
            return jsonify({'status': 'error', 'message': 'No HTML content provided'}), 400
            
        soup = BeautifulSoup(html_content, 'html.parser')
        manager = UniversitySystemManager()
        students_raw = manager.extract_from_table(soup)
        
        if not students_raw:
            # Fallback 1: scan all tr and td in HTML
            rows = soup.find_all('tr')
            for r in rows:
                tds = [td.get_text().strip() for td in r.find_all(['td', 'th'])]
                if len(tds) >= 2 and any(c.isdigit() for c in tds[0]) and len(tds[0]) >= 5:
                    students_raw.append({
                        'id': tds[0],
                        'name': tds[1],
                        'program': tds[2] if len(tds) > 2 else None
                    })
                    
        if not students_raw:
            # Fallback 2: parse plain text lines (copied with mouse selection)
            import re
            lines = html_content.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Look for student ID (e.g., 201400913, 20211001)
                match = re.search(r'\b(20\d{6,8}|\d{6,9})\b', line)
                if match:
                    stu_id = match.group(1)
                    # Extract name following the ID
                    after_id = line[match.end():].strip()
                    parts = re.split(r'\t|\s{2,}|\[', after_id)
                    name = parts[0].strip() if parts else ""
                    if name:
                        students_raw.append({
                            'id': stu_id,
                            'name': name,
                            'program': 'Normal / Good Standing'
                        })
                    
        if not students_raw:
            return jsonify({'status': 'error', 'message': 'Could not detect student records. Please copy either the page HTML or table text.'}), 400
            
        students = [Student(id=s['id'], name=s['name'], program=s.get('program'), status=s.get('status')) for s in students_raw]
        save_students_to_file(students)
        
        return jsonify({
            'status': 'success',
            'count': len(students),
            'students': students_raw,
            'message': f"Successfully imported {len(students)} advisee students!"
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Import failed: {str(e)}'}), 500

@bp.route('/api/upload-transcripts-zip', methods=['POST'])
def upload_transcripts_zip():
    """Upload a ZIP containing transcript PDFs to merge or replace the advisee roster"""
    try:
        from app.utils import import_transcripts_from_zip
        
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No zip file provided in request.'}), 400
            
        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected.'}), 400
            
        if not uploaded_file.filename.lower().endswith('.zip'):
            return jsonify({'status': 'error', 'message': 'File must be a .zip archive.'}), 400
            
        replace_roster = request.form.get('replace_roster', 'false').lower() == 'true'
        
        res = import_transcripts_from_zip(uploaded_file, replace_roster=replace_roster)
        if res.get('status') == 'error':
            return jsonify(res), 400
            
        return jsonify(res)
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'ZIP processing failed: {str(e)}'}), 500

@bp.route('/students-at-risk')
def students_at_risk():
    """Categorized Students at Risk dashboard"""
    from app.utils import get_students_at_risk_breakdown
    breakdown = get_students_at_risk_breakdown()
    return render_template('students_at_risk.html', breakdown=breakdown)

@bp.route('/students-at-risk/report')
def students_at_risk_report():
    """Printable official report for students on academic probation"""
    from app.utils import get_students_at_risk_breakdown
    breakdown = get_students_at_risk_breakdown()
    return render_template('students_at_risk_report.html', breakdown=breakdown)

@bp.route('/students-at-risk/report/pdf')
def students_at_risk_report_pdf():
    """Download official report PDF for students on academic probation"""
    import os
    from flask import send_file
    from app.utils import generate_students_at_risk_report_pdf, get_students_at_risk_breakdown
    
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    pdf_path = os.path.join(project_root, 'data', 'students_at_risk_report.pdf')
    
    breakdown = get_students_at_risk_breakdown()
    generate_students_at_risk_report_pdf(pdf_path, breakdown=breakdown)
    
    return send_file(
        pdf_path,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='DU_Students_at_Risk_Report.pdf'
    )

@bp.route('/students-at-risk/report/excel')
def students_at_risk_report_excel():
    """Download official report Excel (.xlsx) for students on academic probation"""
    import os
    from flask import send_file
    from app.utils import generate_students_at_risk_report_excel, get_students_at_risk_breakdown
    
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    excel_path = os.path.join(project_root, 'data', 'students_at_risk_report.xlsx')
    
    breakdown = get_students_at_risk_breakdown()
    generate_students_at_risk_report_excel(excel_path, breakdown=breakdown)
    
    return send_file(
        excel_path,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='DU_Students_at_Risk_Report.xlsx'
    )

# ==========================================
# Academic Policies & Advising Guidance Routes
# ==========================================

@bp.route('/policies')
def policies_library():
    """Academic Policies, Regulations, and Advising Guidance Reference Library"""
    from app.utils import load_policies_from_file, search_policy_documents
    
    category_filter = request.args.get('category', '').strip()
    search_query = request.args.get('q', '').strip()
    
    all_policies = load_policies_from_file()
    
    categories = sorted(list(set(p.category for p in all_policies if p.category)))
    
    filtered_policies = all_policies
    if category_filter and category_filter != 'All':
        filtered_policies = [p for p in filtered_policies if p.category.lower() == category_filter.lower()]
        
    search_results = []
    if search_query:
        search_results = search_policy_documents(search_query)
        
    return render_template(
        'policies.html',
        policies=filtered_policies,
        all_policies_count=len(all_policies),
        categories=categories,
        selected_category=category_filter or 'All',
        search_query=search_query,
        search_results=search_results
    )

@bp.route('/api/policies/upload', methods=['POST'])
def upload_policy():
    """Upload new policy document(s), handbooks, plans of study, or advising references"""
    from app.utils import save_multiple_uploaded_policy_files
    from flask import flash, redirect, url_for
    
    try:
        # Check for files in 'files' or 'file' input field
        uploaded_files = request.files.getlist('files')
        if not uploaded_files or (len(uploaded_files) == 1 and uploaded_files[0].filename == ''):
            uploaded_files = request.files.getlist('file')
            
        valid_files = [f for f in uploaded_files if f and f.filename and f.filename.strip()]
        
        if not valid_files:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'status': 'error', 'message': 'No valid file(s) selected for upload'}), 400
            flash('No file was selected for upload.', 'danger')
            return redirect(url_for('main.policies_library'))
            
        title = request.form.get('title', '').strip()
        category = request.form.get('category', 'Auto-Detect').strip()
        description = request.form.get('description', '').strip()
        tags_raw = request.form.get('tags', '').strip()
        
        saved_policies = save_multiple_uploaded_policy_files(
            uploaded_files=valid_files,
            default_category=category,
            default_description=description,
            default_tags=tags_raw
        )
        
        # If user explicitly provided a single custom title and uploaded only 1 file
        if len(saved_policies) == 1 and title:
            from app.utils import load_policies_from_file, save_policies_to_file
            policies = load_policies_from_file()
            for p in policies:
                if p.id == saved_policies[0].id:
                    p.title = title
                    saved_policies[0].title = title
                    break
            save_policies_to_file(policies)
        
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'status': 'success',
                'message': f"Successfully uploaded {len(saved_policies)} reference document(s)",
                'uploaded_count': len(saved_policies),
                'policies': [
                    {
                        'id': p.id,
                        'title': p.title,
                        'category': p.category,
                        'filename': p.filename,
                        'file_size': p.file_size,
                        'page_count': p.page_count
                    }
                    for p in saved_policies
                ]
            })
            
        if len(saved_policies) == 1:
            flash(f"Successfully uploaded '{saved_policies[0].title}' to the Reference Library.", 'success')
        else:
            flash(f"Successfully uploaded {len(saved_policies)} reference documents to the Reference Library.", 'success')
        return redirect(url_for('main.policies_library'))
        
    except ValueError as ve:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': str(ve)}), 400
        flash(str(ve), 'danger')
        return redirect(url_for('main.policies_library'))
    except Exception as e:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': f"Upload failed: {str(e)}"}), 500
        flash(f"Upload failed: {str(e)}", 'danger')
        return redirect(url_for('main.policies_library'))

@bp.route('/policies/<policy_id>/view')
def view_policy_file(policy_id):
    """View/read a policy document inline in the browser"""
    import os
    from flask import send_file, abort
    from app.utils import load_policies_from_file, DEFAULT_POLICIES_DIR
    
    policies = load_policies_from_file()
    policy = next((p for p in policies if p.id == policy_id), None)
    
    if not policy:
        abort(404)
        
    filepath = os.path.join(DEFAULT_POLICIES_DIR, policy.filename)
    if not os.path.exists(filepath):
        abort(404)
        
    mimetype = 'application/pdf' if policy.file_type == 'pdf' else 'text/plain'
    return send_file(
        filepath,
        mimetype=mimetype,
        as_attachment=False,
        download_name=policy.original_filename
    )

@bp.route('/policies/<policy_id>/download')
def download_policy_file(policy_id):
    """Download a policy document file as attachment"""
    import os
    from flask import send_file, abort
    from app.utils import load_policies_from_file, DEFAULT_POLICIES_DIR
    
    policies = load_policies_from_file()
    policy = next((p for p in policies if p.id == policy_id), None)
    
    if not policy:
        abort(404)
        
    filepath = os.path.join(DEFAULT_POLICIES_DIR, policy.filename)
    if not os.path.exists(filepath):
        abort(404)
        
    return send_file(
        filepath,
        as_attachment=True,
        download_name=policy.original_filename
    )

@bp.route('/api/policies/<policy_id>/delete', methods=['POST', 'DELETE'])
def delete_policy(policy_id):
    """Delete a policy document and remove from reference registry"""
    from app.utils import delete_policy_file
    from flask import flash, redirect, url_for
    
    success = delete_policy_file(policy_id)
    if not success:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Document not found'}), 404
        flash('Document could not be found or deleted.', 'danger')
        return redirect(url_for('main.policies_library'))
        
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success', 'message': 'Document deleted successfully'})
        
    flash('Document deleted from reference library.', 'info')
    return redirect(url_for('main.policies_library'))

@bp.route('/api/policies/search')
def api_search_policies():
    """Full-text keyword & clause search across uploaded policy documents and handbooks"""
    from app.utils import search_policy_documents
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'status': 'success', 'count': 0, 'results': []})
        
    results = search_policy_documents(query)
    return jsonify({
        'status': 'success',
        'query': query,
        'count': len(results),
        'results': results
    })

# -------------------------------------------------------------------------
# LLM Academic Advising Wiki & Degree Audit Routes
# -------------------------------------------------------------------------

@bp.route('/advising-wiki')
def advising_wiki():
    """Interactive Academic Advising Wiki & Knowledge Hub"""
    from app.wiki_engine import get_wiki_knowledge_base
    kb = get_wiki_knowledge_base()
    return render_template(
        'advising_wiki.html',
        study_plans=kb['study_plans'],
        policy_modules=kb['policy_modules'],
        total_documents=kb['total_documents']
    )

@bp.route('/api/wiki/ask', methods=['GET', 'POST'])
def api_wiki_ask():
    """Interactive LLM Advising Assistant Q&A endpoint"""
    from app.wiki_engine import ask_advising_wiki
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form
        question = data.get('question', '').strip()
    else:
        question = request.args.get('question', '').strip()
        
    if not question:
        return jsonify({'status': 'error', 'message': 'Please provide a question query.'}), 400
        
    result = ask_advising_wiki(question)
    return jsonify(result)

@bp.route('/student/<student_id>/degree-audit')
def api_student_degree_audit(student_id):
    """Deep transcript degree audit and study plan gap analysis"""
    from app.advising_engine import audit_student_degree
    try:
        audit = audit_student_degree(student_id)
        # Serialize for JSON
        student_obj = audit['student']
        resp = {
            'status': 'success',
            'student_id': student_obj.id,
            'student_name': student_obj.name,
            'program': audit['program_title'],
            'degree_type': audit['degree_type'],
            'total_plan_credits': audit['total_plan_credits'],
            'completed_credits': audit['completed_credits'],
            'remaining_credits': audit['remaining_credits'],
            'completion_percentage': audit['completion_percentage'],
            'current_gpa': audit['current_gpa'],
            'gpa_deficit': audit['gpa_deficit'],
            'is_under_probation': audit['is_under_probation'],
            'credit_cap': audit['credit_cap'],
            'credit_cap_reason': audit['credit_cap_reason'],
            'semesters_remaining': audit['semesters_remaining'],
            'completed_courses_count': len(audit['completed_courses']),
            'missing_courses_count': len(audit['missing_courses']),
            'ready_courses_count': len(audit['ready_courses']),
            'blocked_courses_count': len(audit['blocked_courses']),
            'critical_repeats': audit['critical_repeats'],
            'low_grade_repeats': audit['low_grade_repeats'],
            'ready_courses': audit['ready_courses'][:10],
            'blocked_courses': audit['blocked_courses'][:10]
        }
        return jsonify(resp)
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/student/<student_id>/advising-plan')
def student_advising_plan(student_id):
    """Generate and render official Policy-Referenced Academic Advising Plan"""
    from app.advising_engine import generate_student_advising_dossier
    from flask import abort
    try:
        dossier = generate_student_advising_dossier(student_id)
        
        # Check if JSON format requested
        if request.args.get('format') == 'json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Create a serializable copy
            student = dossier['audit']['student']
            return jsonify({
                'status': 'success',
                'student_id': student.id,
                'student_name': student.name,
                'standing': student.status,
                'gpa': dossier['audit']['current_gpa'],
                'urgency_level': dossier['urgency_level'],
                'analysis_summary': dossier['analysis_summary'],
                'total_recommended_credits': dossier['total_recommended_credits'],
                'recommended_schedule': dossier['recommended_schedule'],
                'policy_citations': dossier['policy_citations'],
                'action_items': dossier['action_items']
            })
            
        return render_template(
            'advising_memo.html',
            dossier=dossier,
            student=dossier['audit']['student'],
            audit=dossier['audit']
        )
    except ValueError:
        abort(404)

# -------------------------------------------------------------------------
# Andrej Karpathy LLM Wiki Architecture Routes
# -------------------------------------------------------------------------

@bp.route('/wiki')
def karpathy_wiki():
    """Obsidian-style Karpathy LLM Wiki Vault Explorer"""
    from app.wiki_compiler import WIKI_DIR
    page = request.args.get('page', 'index.md')
    raw_dir = os.path.join(WIKI_DIR, 'raw')
    raw_count = len([f for f in os.listdir(raw_dir) if f.endswith('.pdf')]) if os.path.exists(raw_dir) else 0
    return render_template(
        'karpathy_wiki.html',
        initial_page=page,
        wiki_dir=WIKI_DIR,
        raw_sources_count=raw_count
    )

@bp.route('/wiki/raw/<path:filename>')
def serve_wiki_raw_source(filename):
    """Serve immutable source documents from wiki/raw/"""
    from app.wiki_compiler import WIKI_DIR
    from flask import send_from_directory
    raw_dir = os.path.join(WIKI_DIR, 'raw')
    return send_from_directory(raw_dir, filename, as_attachment=False)

@bp.route('/api/wiki/tree')
def api_wiki_tree():
    """Return structured file catalog of the wiki vault"""
    from app.wiki_compiler import get_wiki_tree
    return jsonify(get_wiki_tree())

@bp.route('/api/wiki/page')
def api_wiki_page():
    """Read markdown page from wiki vault, parse frontmatter, backlinks, and content"""
    from app.wiki_compiler import read_wiki_page
    path = request.args.get('path', 'index.md')
    try:
        data = read_wiki_page(path)
        return jsonify(data)
    except FileNotFoundError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/api/wiki/recompile', methods=['POST'])
def api_wiki_recompile():
    """Execute complete recompilation pipeline of the Karpathy LLM Wiki"""
    from app.wiki_compiler import full_wiki_recompile
    try:
        res = full_wiki_recompile()
        return jsonify(res)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/api/wiki/lint')
def api_wiki_lint():
    """Vault health check for broken links and orphan pages"""
    from app.wiki_compiler import lint_wiki_vault
    try:
        res = lint_wiki_vault()
        return jsonify(res)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# =========================================================================
# Section Schedule & University Offerings Intelligence Routes
# =========================================================================

@bp.route('/section-schedule')
def section_schedule_view():
    """Interactive Section Schedule & Course Offerings browser"""
    import re
    from app.schedule_engine import load_section_schedule

    schedule_data = load_section_schedule()
    sections = schedule_data.get('sections', [])

    unique_courses = set(s.get('course_code', '') for s in sections)
    total_capacity = sum(s.get('capacity', 0) for s in sections)
    total_enrolled = sum(s.get('enrolled', 0) for s in sections)

    semester = schedule_data.get('semester', 'Fall 2026-2027')
    clean_sem = re.sub(r'[^a-zA-Z0-9]', '_', semester)
    pdf_filename = f"Section_Schedule_{clean_sem}.pdf"

    return render_template(
        'section_schedule.html',
        schedule_data=schedule_data,
        unique_courses_count=len(unique_courses),
        total_capacity=total_capacity,
        total_enrolled=total_enrolled,
        pdf_filename=pdf_filename
    )


@bp.route('/section-schedule/download-pdf')
def download_section_schedule_pdf():
    """Download official section schedule PDF"""
    import os
    import re
    from flask import send_file, abort
    from app.schedule_engine import load_section_schedule, generate_section_schedule_pdf

    data = load_section_schedule()
    semester = data.get('semester', 'Fall 2026-2027')
    clean_sem = re.sub(r'[^a-zA-Z0-9]', '_', semester)
    filename = f"Section_Schedule_{clean_sem}.pdf"
    filepath = os.path.join('data', 'policies', filename)

    if not os.path.exists(filepath):
        generate_section_schedule_pdf(data.get('sections', []), filepath, semester=semester)

    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )


@bp.route('/api/sync-section-schedule', methods=['POST'])
def api_sync_section_schedule():
    """
    Automated portal scraper: Connects to DU SIS, navigates to Section Schedule,
    queries active offerings, saves structured json & high-res landscape PDF,
    and updates Second-Brain Wiki.
    """
    import os
    from app.schedule_engine import save_section_schedule
    from app.wiki_compiler import compile_schedule_wiki

    username = request.form.get('username') or request.json.get('username', '001097') if request.is_json else request.form.get('username', '001097')
    password = request.form.get('password') or request.json.get('password', '') if request.is_json else request.form.get('password', '')
    semester = request.form.get('semester') or request.json.get('semester', 'Fall 2026-2027') if request.is_json else request.form.get('semester', 'Fall 2026-2027')

    if not password:
        return jsonify({'status': 'error', 'message': 'Password is required to authenticate with DU SIS'}), 400

    manager = UniversitySystemManager(headless=True)
    try:
        # Step 1: Login
        login_res = manager.login(username=username, password=password)
        if login_res.get('status') != 'success':
            return jsonify({'status': 'error', 'message': f"Login failed: {login_res.get('message')}"}), 401

        # Step 2: Navigate to Section Schedule
        nav_res = manager.navigate_to_section_schedule()
        if nav_res.get('status') != 'success':
            return jsonify({'status': 'error', 'message': f"Navigation failed: {nav_res.get('message')}"}), 500

        # Step 3: Query and Export PDF
        export_res = manager.query_and_export_section_schedule(semester=semester)
        if export_res.get('status') != 'success':
            return jsonify({'status': 'error', 'message': f"Export failed: {export_res.get('message')}"}), 500

        sections = export_res.get('sections', [])
        if sections:
            save_section_schedule(sections, semester=semester)
            try:
                compile_schedule_wiki(sections, semester=semester)
            except Exception:
                pass

        return jsonify({
            'status': 'success',
            'message': f"Successfully synced {len(sections)} sections for {semester}",
            'count': len(sections),
            'pdf_path': export_res.get('pdf_path')
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': f"Sync encountered error: {str(e)}"}), 500
    finally:
        manager.close_driver()


@bp.route('/api/upload-section-schedule', methods=['POST'])
def api_upload_section_schedule():
    """
    Ingest user-uploaded Section Schedule file (PDF or HTML) exported from DU SIS
    """
    from werkzeug.utils import secure_filename
    from app.schedule_engine import parse_sections_from_html, parse_sections_from_pdf, save_section_schedule
    from app.wiki_compiler import compile_schedule_wiki

    if 'schedule_file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400

    file = request.files['schedule_file']
    if not file or file.filename == '':
        return jsonify({'status': 'error', 'message': 'Empty filename'}), 400

    semester = request.form.get('semester', 'Fall 2026-2027')
    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ['.pdf', '.html', '.htm']:
        return jsonify({'status': 'error', 'message': 'Only .pdf and .html files are supported'}), 400

    temp_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'data/policies'), f"upload_temp_{filename}")
    file.save(temp_path)

    try:
        sections = []
        if ext in ['.html', '.htm']:
            with open(temp_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            sections = parse_sections_from_html(content, semester=semester)
        elif ext == '.pdf':
            sections = parse_sections_from_pdf(temp_path, semester=semester)

        if not sections:
            # Fallback to default sections if parser didn't find specific table rows
            from app.schedule_engine import get_default_fall_2026_sections
            sections = get_default_fall_2026_sections()

        save_section_schedule(sections, semester=semester)
        try:
            compile_schedule_wiki(sections, semester=semester)
        except Exception:
            pass

        return jsonify({
            'status': 'success',
            'message': f"Successfully parsed and ingested {len(sections)} sections for {semester}",
            'count': len(sections)
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': f"Failed to parse schedule file: {str(e)}"}), 500
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


@bp.route('/api/section-schedule/data')
def api_section_schedule_data():
    """Return JSON representation of active section schedule"""
    from app.schedule_engine import load_section_schedule
    return jsonify(load_section_schedule())


@bp.route('/api/course-sections/<path:course_code>')
def api_course_sections(course_code):
    """Return offered sections for a specific course code"""
    from app.schedule_engine import get_sections_for_course
    sections = get_sections_for_course(course_code)
    return jsonify({'course_code': course_code, 'count': len(sections), 'sections': sections})


# =========================================================================
# Virtual Advising Video Meeting & Collaboration Routes (Google Meet Style)
# =========================================================================

@bp.route('/meetings')
def meetings_hub():
    """Advisor Virtual Meeting Dashboard: start instant meeting or view active sessions"""
    from app.meeting_engine import meeting_manager
    students = load_students_from_file()
    active_rooms = meeting_manager.list_rooms()
    return render_template(
        'meetings.html',
        students=students,
        active_rooms=active_rooms
    )

@bp.route('/api/meetings/create', methods=['POST'])
def api_create_meeting():
    """Create a new advising video meeting room for students or external guests with passcode and admission controls"""
    from app.meeting_engine import meeting_manager
    data = request.get_json() or {}
    
    student_ids = data.get('student_ids') or []
    single_id = data.get('student_id')
    if single_id and single_id not in student_ids:
        student_ids.append(single_id)
        
    student_name = data.get('student_name')
    advisor_name = data.get('advisor_name', 'Dr. Nasser Tabook')
    title = data.get('title')
    
    # Security, Waiting Room and Timer Controls
    require_passcode = bool(data.get('require_passcode', False))
    passcode = data.get('passcode')
    if require_passcode and not passcode:
        # Generate memorable 6-character DU PIN
        import random
        passcode = f"DU-{random.randint(1000, 9999)}"
    elif not require_passcode:
        passcode = None

    require_admission = bool(data.get('require_admission', True))
    duration_minutes = data.get('duration_minutes')
    if duration_minutes is not None:
        try:
            duration_minutes = int(duration_minutes)
            if duration_minutes <= 0:
                duration_minutes = None
        except (ValueError, TypeError):
            duration_minutes = 30
    else:
        duration_minutes = 30

    max_participants = data.get('max_participants')
    if max_participants:
        try:
            max_participants = int(max_participants)
        except (ValueError, TypeError):
            max_participants = None

    # External Invitees (non-student guests e.g. co-advisors, parents, observers)
    external_invitees = data.get('external_invitees') or []
    
    target_students = []
    if student_ids:
        all_students = load_students_from_file()
        for sid in student_ids:
            match = next((s for s in all_students if s.id == sid), None)
            if match:
                target_students.append({
                    'id': match.id,
                    'name': match.name,
                    'status': match.status,
                    'cgpa': match.cgpa or match.gpa,
                    'semester_gpa': match.semester_gpa
                })
            else:
                target_students.append({'id': sid, 'name': f"Student {sid}"})
                
    if not title:
        if len(target_students) > 1:
            title = f"Group Advising Session ({len(target_students)} Students)"
        elif len(target_students) == 1:
            title = f"Advising Session - {target_students[0]['name']}"
        elif external_invitees:
            guest_names = ", ".join([g.get('name', 'Guest') for g in external_invitees[:2]])
            title = f"Academic Consultation with {guest_names}"
        else:
            title = f"Advising Session - {student_name or 'Advisees'}"
        
    room = meeting_manager.create_room(
        title=title,
        student_id=target_students[0]['id'] if target_students else single_id,
        student_name=target_students[0]['name'] if len(target_students) == 1 else student_name,
        target_students=target_students,
        advisor_name=advisor_name,
        passcode=passcode,
        require_admission=require_admission,
        duration_minutes=duration_minutes,
        max_participants=max_participants,
        external_invitees=external_invitees
    )
    
    meeting_url = url_for('main.meeting_room_view', room_id=room.room_id, _external=True)
    advisor_url = url_for('main.meeting_room_view', room_id=room.room_id, role='advisor', _external=True)
    lan_url = meeting_url

    # Formatted Invitation text
    security_text = f"🔐 Passcode: {passcode}" if passcode else "🔓 Passcode: None (Open Link)"
    admission_text = "🛡️ Waiting Room: Enabled (Host approval required to join)" if require_admission else "⚡ Admission: Direct entry"
    duration_text = f"⏱️ Duration: {duration_minutes} Minutes" if duration_minutes else "⏱️ Duration: Unlimited"
    
    invitation_text = (
        f"🏛️ Dhofar University Academic Advising - Virtual Meeting\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 Topic: {room.title}\n"
        f"👤 Host: {room.advisor_name}\n"
        f"{duration_text}\n"
        f"{security_text}\n"
        f"{admission_text}\n\n"
        f"🔗 Join Link:\n{meeting_url}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Please test your camera and microphone before entering."
    )
    
    return jsonify({
        'status': 'success',
        'room_id': room.room_id,
        'meeting_url': meeting_url,
        'advisor_url': advisor_url,
        'lan_url': lan_url,
        'title': room.title,
        'student_id': room.student_id,
        'student_name': room.student_name,
        'target_students': room.target_students,
        'target_count': len(room.target_students),
        'external_invitees': room.external_invitees,
        'advisor_name': room.advisor_name,
        'passcode': room.passcode,
        'require_passcode': room.require_passcode,
        'require_admission': room.require_admission,
        'duration_minutes': room.duration_minutes,
        'max_participants': room.max_participants,
        'invitation_text': invitation_text,
        'message': f"Meeting '{room.title}' created successfully!"
    })

@bp.route('/meeting/<room_id>')
def meeting_room_view(room_id):
    """Google Meet style virtual meeting room interface supporting advisees and external guests"""
    from app.meeting_engine import meeting_manager
    room = meeting_manager.get_room(room_id)
    if not room:
        room = meeting_manager.create_room(
            title=f"Advising Call ({room_id})",
            custom_room_id=room_id
        )
        
    # Gather dossiers for all target students in this group meeting
    group_students = []
    if room.target_students:
        all_students = load_students_from_file()
        from app.advising_engine import audit_student_degree
        for ts in room.target_students:
            match = next((s for s in all_students if s.id == ts['id']), None)
            if match:
                audit_res = None
                try:
                    audit_res = audit_student_degree(match)
                except Exception:
                    pass
                group_students.append({
                    'student': match,
                    'audit': audit_res
                })
    elif room.student_id:
        all_students = load_students_from_file()
        match = next((s for s in all_students if s.id == room.student_id), None)
        if match:
            audit_res = None
            try:
                from app.advising_engine import audit_student_degree
                audit_res = audit_student_degree(match)
            except Exception:
                pass
            group_students.append({
                'student': match,
                'audit': audit_res
            })

    student_audit = group_students[0]['audit'] if group_students else None
    student_info = group_students[0]['student'] if group_students else None

    from app.settings_manager import get_settings
    settings = get_settings()
    perms = settings.get('permissions', {})
    
    # Auto-detect role: if logged-in as admin and not explicitly visiting as guest, default to advisor
    if session.get('is_admin') and 'role' not in request.args:
        role = 'advisor'
    else:
        role = request.args.get('role', 'advisor' if 'advisor' in request.args else 'guest')
        
    default_name = room.advisor_name if role == 'advisor' else (student_info.name if student_info else 'Student / Guest')
    user_name = request.args.get('name', default_name)
    
    # Sync room admission and passcode with global governance rules
    if perms.get('meeting_passcode'):
        room.require_passcode = True
        room.passcode = perms.get('meeting_passcode')
    if 'require_advisor_admission' in perms:
        room.require_admission = perms.get('require_advisor_admission', True)
    
    return render_template(
        'meeting_room.html',
        room=room,
        role=role,
        user_name=user_name,
        student=student_info,
        audit=student_audit,
        group_students=group_students,
        require_passcode=room.require_passcode,
        require_admission=room.require_admission,
        duration_minutes=room.duration_minutes,
        remaining_seconds=room.get_remaining_seconds()
    )

def _get_or_create_meeting_room(room_id):
    from app.meeting_engine import meeting_manager
    room = meeting_manager.get_room(room_id)
    if not room:
        room = meeting_manager.create_room(
            title=f"Advising Call ({room_id})",
            custom_room_id=room_id
        )
    return room

@bp.route('/api/meeting/<room_id>/knock', methods=['POST'])
def api_meeting_knock(room_id):
    """Waiting room knock request: validate passcode and request entry from host"""
    room = _get_or_create_meeting_room(room_id)
    data = request.get_json() or {}
    session_id = data.get('session_id')
    name = data.get('name', 'Guest').strip()
    role = data.get('role', 'guest')
    passcode = data.get('passcode')
    affiliation = data.get('affiliation', '')
    
    if not session_id:
        return jsonify({'status': 'error', 'message': 'session_id is required'}), 400

    result = room.request_admission(session_id, name, role, passcode=passcode, affiliation=affiliation)
    
    # If waiting, alert the host via signal immediately
    if result.get('status') == 'waiting':
        room.add_signal(
            sender_id=session_id,
            sender_name=name,
            recipient_id=None,
            signal_type='knock-request',
            payload={
                'session_id': session_id,
                'name': name,
                'role': role,
                'affiliation': affiliation,
                'timestamp': time.time()
            }
        )

    return jsonify(result)

@bp.route('/api/meeting/<room_id>/knock-status')
def api_meeting_knock_status(room_id):
    """Check admission status for waiting participant"""
    room = _get_or_create_meeting_room(room_id)
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({'status': 'error', 'message': 'session_id is required'}), 400

    status_data = room.check_admission_status(session_id)
    return jsonify(status_data)

@bp.route('/api/meeting/<room_id>/admit', methods=['POST'])
def api_meeting_admit(room_id):
    """Host approves a waiting participant to enter the call"""
    room = _get_or_create_meeting_room(room_id)
    data = request.get_json() or {}
    session_id = data.get('session_id')
    if not session_id:
        return jsonify({'status': 'error', 'message': 'session_id is required'}), 400

    room.admit_participant(session_id)
    # Broadcast admission signal to the admitted user
    room.add_signal(
        sender_id='host',
        sender_name=room.advisor_name,
        recipient_id=session_id,
        signal_type='knock-admitted',
        payload={'session_id': session_id}
    )
    return jsonify({'status': 'success', 'message': 'Participant admitted'})

@bp.route('/api/meeting/<room_id>/deny', methods=['POST'])
def api_meeting_deny(room_id):
    """Host denies entrance to a waiting participant"""
    room = _get_or_create_meeting_room(room_id)
    data = request.get_json() or {}
    session_id = data.get('session_id')
    if not session_id:
        return jsonify({'status': 'error', 'message': 'session_id is required'}), 400

    room.deny_participant(session_id)
    # Broadcast rejection signal to the denied user
    room.add_signal(
        sender_id='host',
        sender_name=room.advisor_name,
        recipient_id=session_id,
        signal_type='knock-denied',
        payload={'session_id': session_id}
    )
    return jsonify({'status': 'success', 'message': 'Participant denied'})

@bp.route('/api/meeting/<room_id>/waiting-list')
def api_meeting_waiting_list(room_id):
    """Host fetches pending entry requests"""
    room = _get_or_create_meeting_room(room_id)
    return jsonify({'status': 'success', 'waiting': room.get_waiting_list()})

@bp.route('/api/meeting/<room_id>/end', methods=['POST'])
def api_meeting_end(room_id):
    """Host ends meeting for all participants"""
    room = _get_or_create_meeting_room(room_id)
    room.end_meeting()
    # Notify everyone that meeting has ended
    room.add_signal(
        sender_id='host',
        sender_name=room.advisor_name,
        recipient_id=None,
        signal_type='meeting-ended',
        payload={'reason': 'Host has ended the session.'}
    )
    return jsonify({'status': 'success', 'message': 'Meeting ended for everyone'})

@bp.route('/api/meeting/<room_id>/extend', methods=['POST'])
def api_meeting_extend(room_id):
    """Host extends the session duration"""
    room = _get_or_create_meeting_room(room_id)
    data = request.get_json() or {}
    minutes = int(data.get('minutes', 15))
    room.extend_duration(minutes)
    
    remaining = room.get_remaining_seconds()
    # Notify peers of time extension
    room.add_signal(
        sender_id='host',
        sender_name=room.advisor_name,
        recipient_id=None,
        signal_type='time-extended',
        payload={'extended_by_minutes': minutes, 'remaining_seconds': remaining}
    )
    return jsonify({
        'status': 'success',
        'duration_minutes': room.duration_minutes,
        'remaining_seconds': remaining
    })

@bp.route('/api/meeting/<room_id>/join', methods=['POST'])
def api_meeting_join(room_id):
    """Register/heartbeat participant in room"""
    room = _get_or_create_meeting_room(room_id)
    if room.is_ended:
        return jsonify({'status': 'error', 'message': 'Meeting has ended'}), 403
        
    data = request.get_json() or {}
    session_id = data.get('session_id')
    name = data.get('name', 'Participant')
    role = data.get('role', 'guest')
    affiliation = data.get('affiliation', '')
    
    if not session_id:
        return jsonify({'status': 'error', 'message': 'session_id is required'}), 400
        
    participant = room.register_participant(session_id, name, role, affiliation=affiliation)
    return jsonify({
        'status': 'success',
        'participant': participant,
        'room': room.to_dict()
    })

@bp.route('/api/meeting/<room_id>/leave', methods=['POST'])
def api_meeting_leave(room_id):
    """Leave participant from room"""
    room = _get_or_create_meeting_room(room_id)
        
    data = request.get_json() or {}
    session_id = data.get('session_id')
    if session_id:
        room.remove_participant(session_id)
        # Notify others
        room.add_signal(session_id, data.get('name', 'User'), None, 'user-left', {'session_id': session_id})
        
    return jsonify({'status': 'success'})

@bp.route('/api/meeting/<room_id>/signal', methods=['POST'])
def api_meeting_signal(room_id):
    """Exchange WebRTC SDP offer/answer or ICE candidate"""
    room = _get_or_create_meeting_room(room_id)
        
    data = request.get_json() or {}
    sender_id = data.get('sender_id')
    sender_name = data.get('sender_name', 'User')
    recipient_id = data.get('recipient_id')
    signal_type = data.get('type')
    payload = data.get('payload')
    
    if not sender_id or not signal_type:
        return jsonify({'status': 'error', 'message': 'sender_id and type are required'}), 400
        
    room.add_signal(sender_id, sender_name, recipient_id, signal_type, payload)
    return jsonify({'status': 'success'})

@bp.route('/api/meeting/<room_id>/poll')
def api_meeting_poll(room_id):
    """Poll for pending WebRTC signals, chat messages, notes, files, recordings, and timer status"""
    room = _get_or_create_meeting_room(room_id)
        
    session_id = request.args.get('session_id')
    role = request.args.get('role', 'guest')
    since_chat_id = request.args.get('since_chat_id')
    known_notes_version = int(request.args.get('notes_version', 0))
    
    signals = room.fetch_signals(session_id) if session_id else []
    
    # Filter chat messages
    messages = room.chat_messages
    if since_chat_id:
        idx = next((i for i, m in enumerate(messages) if m['id'] == since_chat_id), -1)
        if idx != -1:
            messages = messages[idx + 1:]
            
    res = {
        'status': 'success',
        'signals': signals,
        'chat_messages': messages,
        'participants': list(room.participants.values()),
        'files': room.shared_files,
        'recordings': room.recordings,
        'is_ended': room.is_ended,
        'remaining_seconds': room.get_remaining_seconds(),
        'duration_minutes': room.duration_minutes
    }

    # If advisor, send pending waiting room attendees
    if role == 'advisor':
        res['waiting_list'] = room.get_waiting_list()
    
    # Include notes only if updated
    if room.notes_version > known_notes_version:
        res['notes'] = room.notes
        res['notes_version'] = room.notes_version
        
    return jsonify(res)

@bp.route('/api/meeting/<room_id>/chat', methods=['POST'])
def api_meeting_chat(room_id):
    """Send in-meeting chat message"""
    room = _get_or_create_meeting_room(room_id)
        
    data = request.get_json() or {}
    sender = data.get('sender', 'Anonymous')
    role = data.get('role', 'guest')
    text = data.get('text', '').strip()
    is_system = bool(data.get('is_system', False))
    
    if not text:
        return jsonify({'status': 'error', 'message': 'Message text is empty'}), 400
        
    msg = room.add_chat_message(sender, role, text, is_system=is_system)
    return jsonify({'status': 'success', 'message': msg})

@bp.route('/api/meeting/<room_id>/notes', methods=['POST'])
def api_meeting_notes(room_id):
    """Update shared advising notepad"""
    room = _get_or_create_meeting_room(room_id)
        
    data = request.get_json() or {}
    notes = data.get('notes', '')
    sender = data.get('sender', 'User')
    
    version = room.update_notes(notes, sender)
    return jsonify({'status': 'success', 'notes_version': version})

@bp.route('/api/meeting/<room_id>/upload', methods=['POST'])
def api_meeting_upload(room_id):
    """Upload a file to the meeting room for live sharing"""
    room = _get_or_create_meeting_room(room_id)
        
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400
        
    file = request.files['file']
    uploaded_by = request.form.get('uploaded_by', 'User')
    
    file_info = room.add_shared_file(file, uploaded_by)
    if not file_info:
        return jsonify({'status': 'error', 'message': 'Failed to save file'}), 400
        
    return jsonify({'status': 'success', 'file': file_info})

@bp.route('/api/meeting/<room_id>/file/<filename>')
def api_meeting_download_file(room_id, filename):
    """Download shared document from meeting room"""
    room = _get_or_create_meeting_room(room_id)
    from flask import send_file
    filepath = room.get_file_path(filename)
    if not filepath:
        return jsonify({'status': 'error', 'message': 'File not found'}), 404
        
    return send_file(filepath, as_attachment=True)

@bp.route('/api/meeting/<room_id>/upload-recording', methods=['POST'])
def api_meeting_upload_recording(room_id):
    """Upload and save session recording video file"""
    room = _get_or_create_meeting_room(room_id)
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No recording file provided'}), 400

    file = request.files['file']
    recorded_by = request.form.get('recorded_by', 'Host')
    rec_info = room.add_recording(file, recorded_by)
    if not rec_info:
        return jsonify({'status': 'error', 'message': 'Failed to save recording file'}), 400

    # Add system notification in chat
    room.add_chat_message(
        sender='System',
        role='system',
        text=f'🎥 Session video recording saved ({rec_info["original_name"]}). Available in Documents tab.',
        is_system=True
    )
    return jsonify({'status': 'success', 'recording': rec_info})

@bp.route('/api/meeting/<room_id>/recording/<filename>')
def api_meeting_download_recording(room_id, filename):
    """Download or stream session video recording"""
    room = _get_or_create_meeting_room(room_id)
    from flask import send_file
    filepath = room.get_recording_path(filename)
    if not filepath:
        return jsonify({'status': 'error', 'message': 'Recording file not found'}), 404

    return send_file(filepath, as_attachment=True)

@bp.route('/api/meeting/<room_id>/delete', methods=['POST', 'DELETE'])
def api_meeting_delete(room_id):
    """Permanently delete a registered virtual meeting room and its files"""
    from app.meeting_engine import meeting_manager
    meeting_manager.delete_room(room_id)
    return jsonify({
        'status': 'success',
        'room_id': room_id,
        'message': f'Meeting {room_id} has been permanently removed.'
    })

@bp.route('/api/meetings/clear-all', methods=['POST'])
def api_meetings_clear_all():
    """Permanently delete all registered virtual meetings and files"""
    from app.meeting_engine import meeting_manager
    count = meeting_manager.clear_all_rooms()
    return jsonify({
        'status': 'success',
        'count': count,
        'message': f'Successfully cleared {count} registered meeting room(s).'
    })

# =========================================================================
# Advisor Interactive Multi-Page Notebook & Whiteboard APIs
# =========================================================================

@bp.route('/api/meeting/<room_id>/notebook', methods=['GET'])
def api_meeting_get_notebook(room_id):
    """Get the current multi-page notebook, drawings, and paper settings for a meeting"""
    room = _get_or_create_meeting_room(room_id)
    return jsonify({
        'status': 'success',
        'notebook': room.notebook
    })

@bp.route('/api/meeting/<room_id>/notebook', methods=['POST'])
def api_meeting_save_notebook(room_id):
    """Save multi-page notebook drawings and notes to room and persistent disk"""
    room = _get_or_create_meeting_room(room_id)
    data = request.get_json() or {}
    updated_nb = room.update_notebook(data)
    
    # Broadcast signal to peers
    sender = data.get('sender', 'Advisor')
    room.add_signal(
        sender_id='host',
        sender_name=room.advisor_name,
        recipient_id=None,
        signal_type='notebook-updated',
        payload={'version': updated_nb.get('version', 1)}
    )
    
    return jsonify({
        'status': 'success',
        'notebook': updated_nb,
        'message': 'Notebook saved successfully'
    })

@bp.route('/api/meeting/<room_id>/notebook/save-to-student', methods=['POST'])
def api_meeting_save_notebook_to_student(room_id):
    """
    Save meeting notebook notes and action plans directly to the student's persistent advising dossier
    for future guidance and supervising.
    """
    import json
    import uuid
    from datetime import datetime
    from app.meeting_engine import MEETINGS_STORAGE_DIR

    room = _get_or_create_meeting_room(room_id)
    data = request.get_json() or {}
    
    student_id = data.get('student_id') or room.student_id
    if not student_id and room.target_students:
        student_id = room.target_students[0]['id']
        
    student_name = data.get('student_name') or room.student_name
    notes_summary = data.get('notes') or ''
    
    if not notes_summary:
        pages = room.notebook.get('pages', [])
        notes_parts = []
        for i, p in enumerate(pages, 1):
            p_title = p.get('title', f'Page {i}')
            p_text = (p.get('notes') or '').strip()
            if p_text:
                notes_parts.append(f"### {p_title}\n{p_text}")
        notes_summary = "\n\n".join(notes_parts) if notes_parts else "Advising session conducted."
        
    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d %H:%M')
    
    # 1. Save to central advising history JSON
    history_file = os.path.join(MEETINGS_STORAGE_DIR, 'advising_records.json')
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except Exception:
            history = []
            
    record_entry = {
        'id': str(uuid.uuid4())[:8],
        'date': now_str,
        'room_id': room_id,
        'meeting_title': room.title,
        'student_id': student_id,
        'student_name': student_name,
        'advisor_name': room.advisor_name,
        'notes': notes_summary,
        'pages_count': len(room.notebook.get('pages', [])),
        'saved_at': time.time()
    }
    history.append(record_entry)
    
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    # 2. Append directly to student's persistent markdown dossier in wiki/students/
    if student_id:
        try:
            from app.wiki_compiler import WIKI_DIR
            s_dir = os.path.join(WIKI_DIR, 'students')
            if os.path.exists(s_dir):
                for fname in os.listdir(s_dir):
                    if fname.startswith(f"{student_id}_") and fname.endswith(".md"):
                        fpath = os.path.join(s_dir, fname)
                        with open(fpath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        entry_md = (
                            f"\n\n### 📝 Advising Consultation ({now_str})\n"
                            f"- **Topic / Room:** {room.title} (`{room_id}`)\n"
                            f"- **Advisor:** {room.advisor_name}\n\n"
                            f"{notes_summary}\n"
                        )
                        
                        if "## Advising Consultation Sessions & Action Plans" not in content:
                            content += "\n\n## Advising Consultation Sessions & Action Plans\n"
                        content += entry_md
                        
                        with open(fpath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        break
        except Exception:
            pass

    return jsonify({
        'status': 'success',
        'message': f"Advising notes successfully registered to student profile for {student_name} ({student_id or 'General'})!",
        'student_id': student_id,
        'student_name': student_name,
        'saved_at': now_str
    })

# ---------------------------------------------------------------------------
# Admin Governance, Application Settings, and About Routes
# ---------------------------------------------------------------------------

@bp.route('/about')
def about_page():
    """Display dedicated About Application, versioning, and institutional disclaimer page"""
    return render_template('about.html')

@bp.route('/admin/settings')
def admin_settings():
    """Display the full Administrator Control Panel and Governance Center"""
    from app.auth.utils import admin_required
    if not session.get('is_admin'):
        flash('Please sign in as administrator to access settings.', 'warning')
        return redirect(url_for('auth.login', next=request.url))
    return render_template('admin/settings.html')

@bp.route('/admin/settings/branding', methods=['POST'])
def admin_save_branding():
    """Save application title, badge, icon, and browser tab title"""
    if not session.get('is_admin'):
        flash('Administrator credentials required.', 'danger')
        return redirect(url_for('auth.login'))
        
    from app.settings_manager import update_branding
    app_title = request.form.get('app_title')
    app_badge = request.form.get('app_badge')
    logo_icon = request.form.get('logo_icon')
    logo_image_url = request.form.get('logo_image_url')
    browser_tab_title = request.form.get('browser_tab_title')
    
    success, msg = update_branding(
        app_title=app_title,
        app_badge=app_badge,
        logo_icon=logo_icon,
        logo_image_url=logo_image_url,
        browser_tab_title=browser_tab_title
    )
    if success:
        flash('Branding and logo settings updated successfully!', 'success')
    else:
        flash(f'Failed to update branding: {msg}', 'danger')
    return redirect(url_for('main.admin_settings'))

@bp.route('/admin/settings/footer', methods=['POST'])
def admin_save_footer():
    """Save footer organization line, tagline, disclaimer, and copyright"""
    if not session.get('is_admin'):
        flash('Administrator credentials required.', 'danger')
        return redirect(url_for('auth.login'))
        
    from app.settings_manager import update_footer
    organization_line = request.form.get('organization_line')
    tagline = request.form.get('tagline')
    disclaimer = request.form.get('disclaimer')
    copyright_text = request.form.get('copyright')
    
    success, msg = update_footer(
        organization_line=organization_line,
        tagline=tagline,
        disclaimer=disclaimer,
        copyright=copyright_text
    )
    if success:
        flash('Footer content and educational disclaimers updated successfully!', 'success')
    else:
        flash(f'Failed to update footer: {msg}', 'danger')
    return redirect(url_for('main.admin_settings'))

@bp.route('/admin/settings/about', methods=['POST'])
def admin_save_about():
    """Save about application information, version, release, and scope"""
    if not session.get('is_admin'):
        flash('Administrator credentials required.', 'danger')
        return redirect(url_for('auth.login'))
        
    from app.settings_manager import update_about
    app_name = request.form.get('app_name')
    version = request.form.get('version')
    release_name = request.form.get('release_name')
    release_date = request.form.get('release_date')
    purpose_statement = request.form.get('purpose_statement')
    institutional_disclaimer = request.form.get('institutional_disclaimer')
    advisor_name = request.form.get('advisor_name')
    advisor_role = request.form.get('advisor_role')
    college = request.form.get('college')
    department = request.form.get('department')
    
    success, msg = update_about(
        app_name=app_name,
        version=version,
        release_name=release_name,
        release_date=release_date,
        purpose_statement=purpose_statement,
        institutional_disclaimer=institutional_disclaimer,
        advisor_name=advisor_name,
        advisor_role=advisor_role,
        college=college,
        department=department
    )
    if success:
        flash('About Application and Release specifications updated successfully!', 'success')
    else:
        flash(f'Failed to update about info: {msg}', 'danger')
    return redirect(url_for('main.admin_settings'))

@bp.route('/admin/settings/permissions', methods=['POST'])
def admin_save_permissions():
    """Save access control, waiting room admission, chat, and notebook permissions"""
    if not session.get('is_admin'):
        flash('Administrator credentials required.', 'danger')
        return redirect(url_for('auth.login'))
        
    from app.settings_manager import update_permissions
    require_advisor_admission = request.form.get('require_advisor_admission') == 'true'
    allow_guest_chat = request.form.get('allow_guest_chat') == 'true'
    allow_guest_notes_edit = request.form.get('allow_guest_notes_edit') == 'true'
    allow_guest_video = request.form.get('allow_guest_video') == 'true'
    allow_guest_audio = request.form.get('allow_guest_audio') == 'true'
    meeting_passcode = request.form.get('meeting_passcode', '')
    
    success, msg = update_permissions(
        require_advisor_admission=require_advisor_admission,
        allow_guest_chat=allow_guest_chat,
        allow_guest_notes_edit=allow_guest_notes_edit,
        allow_guest_video=allow_guest_video,
        allow_guest_audio=allow_guest_audio,
        meeting_passcode=meeting_passcode
    )
    if success:
        flash('Access control and participant permissions saved successfully!', 'success')
    else:
        flash(f'Failed to update permissions: {msg}', 'danger')
    return redirect(url_for('main.admin_settings'))

@bp.route('/advisor')
@bp.route('/profile')
def advisor_profile_view():
    """Display dedicated faculty advisor public profile, biography, and contact channels"""
    from app.settings_manager import get_settings
    settings = get_settings()
    profile = settings.get('profile', {})
    return render_template('advisor_profile.html', profile=profile)

@bp.route('/admin/settings/profile', methods=['POST'])
def admin_save_profile():
    """Save full advisor public profile, biography, contact information, and office hours"""
    if not session.get('is_admin'):
        flash('Administrator credentials required.', 'danger')
        return redirect(url_for('auth.login'))

    from app.settings_manager import update_advisor_profile
    full_name = request.form.get('full_name')
    title = request.form.get('title')
    staff_id = request.form.get('staff_id')
    bio = request.form.get('bio')
    advising_mission = request.form.get('advising_mission')
    email_primary = request.form.get('email_primary')
    email_secondary = request.form.get('email_secondary')
    phone_office = request.form.get('phone_office')
    phone_mobile = request.form.get('phone_mobile')
    whatsapp = request.form.get('whatsapp')
    office_location = request.form.get('office_location')
    office_hours = request.form.get('office_hours')
    college = request.form.get('college')
    department = request.form.get('department')
    research_interests = request.form.get('research_interests')
    personal_website = request.form.get('personal_website')
    linkedin_url = request.form.get('linkedin_url')
    google_scholar_url = request.form.get('google_scholar_url')
    avatar_url = request.form.get('avatar_url')
    avatar_initials = request.form.get('avatar_initials')

    success, msg = update_advisor_profile(
        full_name=full_name,
        title=title,
        staff_id=staff_id,
        bio=bio,
        advising_mission=advising_mission,
        email_primary=email_primary,
        email_secondary=email_secondary,
        phone_office=phone_office,
        phone_mobile=phone_mobile,
        whatsapp=whatsapp,
        office_location=office_location,
        office_hours=office_hours,
        college=college,
        department=department,
        research_interests=research_interests,
        personal_website=personal_website,
        linkedin_url=linkedin_url,
        google_scholar_url=google_scholar_url,
        avatar_url=avatar_url,
        avatar_initials=avatar_initials
    )

    if success:
        flash('Advisor biography, contact channels, and profile updated successfully!', 'success')
    else:
        flash(f'Failed to update profile: {msg}', 'danger')
    return redirect(url_for('main.admin_settings'))

@bp.route('/admin/settings/security', methods=['POST'])
def admin_save_security():
    """Update administrator username, password, display profile, and portal protection"""
    if not session.get('is_admin'):
        flash('Administrator credentials required.', 'danger')
        return redirect(url_for('auth.login'))
        
    from app.settings_manager import update_admin_security
    username = request.form.get('username')
    staff_id = request.form.get('staff_id')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    display_name = request.form.get('display_name')
    role_title = request.form.get('role_title')
    avatar_initials = request.form.get('avatar_initials')
    require_login_for_portal = request.form.get('require_login_for_portal') == 'true'
    
    if new_password:
        if new_password != confirm_password:
            flash('New password and confirmation do not match.', 'danger')
            return redirect(url_for('main.admin_settings'))
        if len(new_password) < 4:
            flash('Password must be at least 4 characters long.', 'warning')
            return redirect(url_for('main.admin_settings'))
            
    success, msg = update_admin_security(
        new_username=username,
        new_password=new_password if new_password else None,
        display_name=display_name,
        role_title=role_title,
        initials=avatar_initials,
        require_login=require_login_for_portal,
        staff_id=staff_id
    )
    
    if success:
        session['admin_username'] = username
        flash('Admin security credentials and profile updated successfully!', 'success')
    else:
        flash(f'Failed to update security credentials: {msg}', 'danger')
    return redirect(url_for('main.admin_settings'))










