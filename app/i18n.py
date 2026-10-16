"""Internationalization (i18n) and Bilingual Engine for Dhofar University Advising Portal.
Supports English (LTR) and Arabic (RTL) with academic terminology tailored for DU advising bylaws.
"""

import re
from flask import session, request

# Comprehensive Bilingual Dictionary
TRANSLATIONS = {
    'en': {
        # Global Navigation & Header
        'app_title': 'Dhofar University',
        'app_badge': 'ADVISING',
        'dashboard': 'Dashboard',
        'advisees': 'Advisees',
        'my_advisees': 'My Advisees Roster',
        'schedule': 'Schedule',
        'policies': 'Policies',
        'advising_wiki': 'Advising Wiki',
        'virtual_office': 'Virtual Office',
        'advisor_profile': 'Advisor',
        'about': 'About',
        'students_at_risk': 'Students at Risk',
        'dark_mode': 'Dark',
        'light_mode': 'Light',
        'theme_toggle': 'Toggle Theme',
        'admin_settings': 'Admin Settings',
        'sign_in': 'Sign In',
        'sign_out': 'Sign Out',
        'switch_to_arabic': 'العربية',
        'switch_to_english': 'English',
        'language': 'Language',
        'search_placeholder': 'Search by name, ID, or program...',
        
        # Dashboard Strings
        'supervisor_dashboard': 'Supervisor Dashboard',
        'academic_year': 'Academic Year 2026-2027',
        'sync_roster': 'Sync Roster',
        'office_hours_hub': 'Office Hours Hub',
        'total_advisees': 'Total Advisees',
        'active_cohort': 'Active registered cohort',
        'view_roster': 'View roster',
        'good_standing_cleared': 'Good Standing & Cleared',
        'academic_probation': 'Academic Probation',
        'strict_probation': 'Strict Probation',
        'credit_cap_enforced': '12-credit cap enforced',
        'article_14_warning': 'Article 14 Warning',
        'dismissal_threshold': 'Dismissal threshold',
        'intervene_now': 'Intervene now',
        'cohort_health_distribution': 'Cohort Academic Health Distribution',
        'cgpa_threshold_label': 'CGPA ≥ 65%',
        
        # Priority Action & Triage
        'priority_actions_title': 'Immediate Advisory Action Required',
        'priority_actions_subtitle': 'Advisees requiring urgent academic intervention, credit load adjustment, or repeat registration',
        'action_required': 'Action Required',
        'resolve_case': 'Open Dossier',
        
        # Notice Board & Notes Drawer
        'notice_board_title': 'Advisor Action & Sticky Deskpad',
        'notice_board_subtitle': 'Prioritize advising tasks, pin student follow-ups, and organize semester plans',
        'toggle_notes_drawer': 'Sticky Notes Deskpad',
        'add_sticky_note': 'Add Note',
        'all_notes': 'All Notes',
        'pinned_only': 'Pinned Only',
        'auto_detect_risk': 'Auto-Detect At-Risk',
        'interactive_studio': 'Interactive Studio',
        'filter_by_keyword': 'Filter notes by keyword, student name or ID...',
        'urgent': 'URGENT',
        
        # Advisees Table & Roster
        'advisee_cohort_overview': 'Advisee Cohort Overview',
        'showing_advisees': 'Showing',
        'full_directory': 'Full Directory',
        'student_id': 'Student ID',
        'name': 'Name',
        'program_major': 'Program / Major',
        'standing_status': 'Status / Standing',
        'cgpa': 'CGPA',
        'sgpa': 'SGPA',
        'actions': 'Actions',
        'profile': 'Profile',
        'transcript_pdf': 'Transcript PDF',
        'meet_now': 'Meet Now',
        'advising_plan': 'Advising Action Plan',
        
        # Academic Standings
        'status_normal': 'Normal / Good Standing',
        'status_cleared': 'Probation Removal',
        'status_first_probation': 'First Probation',
        'status_second_probation': 'Second Probation',
        'status_strict_probation': 'Strict Probation',
        'status_dismissal_risk': 'Critical Dismissal Risk',
        'status_pre_probation_warning': 'Pre-Probation Warning (CGPA < 65%)',
        
        # Students at Risk View
        'at_risk_subtitle': 'Advisees requiring academic advising intervention due to probation status or GPA < 65%',
        'du_probation_policies': 'DU Probation Policies',
        'view_print_report': 'View / Print Report',
        'download_excel': 'Download Excel (.xlsx)',
        'download_report_pdf': 'Download Report PDF',
        'stage_1_strict': 'Stage 1: Strict Probation (Critical Risk)',
        'stage_2_second': 'Stage 2: Second Probation (High Risk)',
        'stage_3_first': 'Stage 3: First Probation (Moderate Risk)',
        'probation_advising_note': 'Students in this group are at immediate risk of academic dismissal. Mandatory maximum credit limit is 12 credit hours. Priority must be given to repeating failed and low-grade courses.',
        'second_probation_note': 'Student has spent 2 consecutive terms on probation. If GPA does not rise above 65.0, they will advance to Strict Probation. Course load restricted to 12-15 credit hours.',
        'first_probation_note': 'Student entered probation due to semester/cumulative GPA falling below 65.0. Immediate advising review needed to repeat failed subjects before probation elevates.',
        'chair_briefing_letter_btn': 'Official Letter to Dept Chair',
        'batch_outreach_hub_btn': 'Batch Outreach & Notices Hub',
        
        # Student Detail & Degree Audit Top Actions
        'meet_with_student': 'Meet with Student',
        'official_notice_email': 'Official Notice & Email',
        'advising_action_plan': 'Advising Action Plan',
        'advising_wiki_dossier': 'Advising Wiki Dossier',
        'generate_recovery_schedule': 'Generate Recovery Schedule',
        'consult_probation_bylaws': 'Consult DU Strict Probation Bylaws',
        'view_recommended_plan': 'View Recommended 12-Credit Plan',
        
        # Academic & Contact Cards
        'student_details_title': 'Student Academic Dossier',
        'academic_information': 'Academic Information',
        'contact_system_details': 'Contact & System Details',
        'degree_progress': 'Degree Progress & Audit',
        'academic_history': 'Academic History & Transcript',
        'recovery_plan': 'Action Plan & Recommended Courses',
        'meeting_notes': 'Meeting Notes & Interaction Log',
        'mandatory_repeats_required': 'Mandatory Course Repeats Required (Dhofar University Bylaws Article 18)',
        'mandatory_repeats_desc': 'The student has unresolved course attempt(s) that were not passed. These courses block downstream prerequisites and weigh down the cumulative GPA. Under university regulations, repeating these courses replaces previous failing scores in the CGPA calculation:',
        'course_code': 'Course Code',
        'course_title': 'Course Title',
        'credits': 'Credits',
        'attempted_term': 'Attempted Term',
        'recorded_grade': 'Recorded Grade',
        'advising_action': 'Advising Action',
        'mandatory_repeat_action': 'Mandatory Repeat for Upcoming Term',
        'prerequisites': 'Prerequisites',
        'earned_credits': 'Earned Credits',
        'remaining_credits': 'Remaining Credits',
        'current_cgpa': 'Current CGPA',
        'gpa_deficit': 'GPA Deficit',
        'academic_year_label': 'Academic Year:',
        'advisor_label': 'Advisor:',
        'email_label': 'Email:',
        'phone_label': 'Phone:',
        'not_provided': 'Not Provided',
        'credit_cap_label': 'Semester Credit Cap:',
        'credit_cap_rule_label': 'Credit Cap Rule:',
        'pace_to_graduate_label': 'Pace to Graduate:',
        'semesters_remaining_count': '~{count} semester(s) remaining',
        'graduation_req_label': 'Graduation Req: ≥ 65.0%',
        'meets_graduation_threshold': '(Meets Graduation Threshold)',
        'probation_metric_label': 'Probation Metric (Art. 14)',
        'recovery_badge': '+{gain}% vs CGPA (Recovery)',
        
        # 360 Persona Labels
        'academic_persona': 'Academic Persona',
        'risk_level': 'Risk Level',
        'degree_horizon': 'Degree Horizon',
        'terms_to_completion': '~{terms} terms to completion',
        'primary_archetype': 'Primary Archetype',
        'recommended_load': 'Recommended Load',
        'credits_max': '{credits} Credits Max',
        'target_semester_gpa': 'Target Semester GPA',
        'projected_graduation': 'Projected Graduation',
        'what_the_student_does': 'What The Student Does',
        'what_the_student_does_subtitle': 'Observed academic habits, pacing & registration patterns',
        'demonstrated_strengths': 'Demonstrated Strengths',
        'what_the_student_must_do': 'What The Student MUST Do',
        'what_the_student_must_do_subtitle': 'Prescriptive action plan & degree continuation mandates',
        'action_directives': 'Action Directives',
        'bottlenecks_blindspots': 'Bottlenecks & Academic Blind Spots',
        'discipline_competency_breakdown': 'Academic Discipline Competency Breakdown',
        'advisor_consultation_playbook': 'Advisor Consultation Playbook (Dr. Nasser Tabook)',
        'advisor_playbook_subtitle': 'Tailored communication strategy for this specific student persona',
        'dispatch_official_notice': 'Dispatch Official Notice',
        'recommended_advising_tone': 'Recommended Advising Tone',
        'meeting_opening_dialogue': 'Meeting Opening Dialogue',
        'diagnostic_questions_to_ask': 'Key Diagnostic Questions To Ask The Student',
        'pass_rate': 'Pass Rate',
        'courses_count': '{count} courses',
        'average_short': 'Avg',
        
        # Recommendations & Action Plan Section
        'intelligent_advising_plan': 'Intelligent Advising Action Plan & Recommended Schedule',
        'intelligent_advising_subtitle': 'Evidence-based recommendation derived from transcript audit and DU Academic Regulations',
        'priority': 'Priority',
        'print_official_memo': 'Print Official Memo',
        'academic_diagnosis_assessment': 'Academic Diagnosis & Situation Assessment',
        'semester_progression_trajectory': 'Semester-by-Semester GPA Trajectory & Academic Progress',
        'benchmark_good_standing': 'Benchmark: 65.0% Good Standing',
        'current_cgpa_label': 'CURRENT CGPA',
        'peak_cgpa_label': 'PEAK CUMULATIVE GPA',
        'lowest_gpa_label': 'LOWEST RECORDED GPA',
        'latest_delta_label': 'LATEST TERM DELTA (Δ)',
        'baseline': 'Baseline',
        'term_gpa_legend': 'Term GPA',
        'cum_gpa_legend': 'Cumulative GPA',
        'good_standing_threshold_65': 'Good Standing Threshold (65.0%)',
        'trajectory_root_cause_breakdown': 'Semester-by-Semester Trajectory & Root-Cause Performance Breakdown',
        'trajectory_subtitle': 'Detailed analysis of why GPA improved or declined',
        'academic_term_col': 'Academic Term',
        'term_gpa_col': 'Term GPA (Δ)',
        'cum_gpa_col': 'Cum. GPA (Δ)',
        'standing_load_col': 'Standing & Load',
        'root_cause_outcome_col': 'Root-Cause Performance Analysis & Outcome',
        'what_student_must_do_increase_gpa': 'What the Student Must Do to Increase GPA (DU Article 18 Recovery Blueprint)',
        'article_18_multiplier_subtitle': 'Leverage the Highest Grade Replacement rule to mathematically lift cumulative GPA',
        'course_repeat_simulation': 'Course Repeat Grade Replacement Simulation:',
        'repeat_simulation_intro': 'Under Dhofar University Article 18, repeating a course with a grade of F or D replaces the previous score in the cumulative GPA calculation. This creates a powerful multiplier effect:',
        'gain_if_75': 'Gain if 75% achieved',
        'gain_if_80': 'Gain if 80% achieved',
        'projected_outcome': 'Projected Outcome:',
        'recovers_good_standing_alert': 'Recovers Good Standing! (>= 65.0%)',
        'step_toward_good_standing': 'Significant step toward 65.0% Good Standing',
        'no_critical_repeats_message': 'No critical course failures on record. Maintain consistent semester average above 70.0% across all curriculum requirements.',
        'mandatory_checklist_student': 'Mandatory Action Checklist for Student:',
        'advisor_consultation_protocol': 'Academic Advisor Consultation Protocol & Counseling Script',
        'dialogue_script_subtitle': 'Mandatory consultation directives and exact structured dialogue for advising sessions',
        'consultation_required': 'Consultation Required:',
        'consultation_required_desc': 'The student must meet with Academic Advisor {advisor} during: {window}.',
        'mandatory_frequency': 'Mandatory Frequency: {frequency}',
        'summon_student': 'Summon Student',
        'what_advisor_should_say': 'What Dr. Nasser Tabook (Advisor) Should Say to the Student:',
        'what_student_must_prepare': 'What the Student Must Prepare and Ask Dr. Nasser:',
        'recommended_next_semester_schedule': 'Recommended Next-Semester Schedule (Cap: {cap} CH Max)',
        'ch_total': '{total} Credit Hours Total',
        'schedule_priority_note': 'Prioritizes repeating deficient prerequisite courses first (DU Article 18), followed by eligible core curriculum requirements.',
        'offered_section_timetable': 'Offered Section & Timetable',
        'advising_priority_rationale': 'Advising Priority & Rationale',
        'section_short': 'Sec',
        'open': 'Open',
        'closed': 'Closed',
        'seats_available': '{seats} seats',
        'not_offered_current_term': 'Not Offered in Fall 2026-2027',
        'total_load': 'Total Semester Registration Load:',
        'ready_to_register': 'Ready to Register ({count})',
        'locked_courses': 'Locked Courses ({count})',
        'prerequisites_satisfied': 'Prerequisites Satisfied',
        'prerequisites_missing': 'Prerequisites Missing',
        'missing_prereqs_label': 'Missing: {prereqs}',
        'official_policies_applied': 'Official Dhofar University Policy Citations Applied:',
        'action_items_agreement': 'Action Items & Advising Agreement',
        'academic_advisor_signature': 'Academic Advisor',
        'student_signature_agreement': 'Student Signature of Agreement',
        'chairperson_signature': 'Department Chairperson',
        'dept_cs': 'Department of Computer Science',
        'caas': 'College of Arts and Applied Sciences',
        'date_placeholder': 'Date: _____ / _____ / 2026',
        
        # Degree Progress Checklist
        'degree_study_plan_progress': 'Degree Study Plan Progress: {program}',
        'total_plan_required': 'Total Plan Required',
        'completed_earned': 'Completed / Earned',
        'pct_degree_completed': '{pct}% of degree completed',
        'remaining_to_graduate': 'Remaining to Graduate',
        'degree_completion_progress': 'Degree Completion Progress',
        'curriculum_requirements_checklist': 'Curriculum Requirements Checklist',
        'all_plan_courses': 'All Plan Courses ({count})',
        'completed_courses_btn': 'Completed ({count})',
        'remaining_courses_btn': 'Remaining ({count})',
        'requirement_category': 'Requirement Category',
        'degree_status': 'Degree Status',
        'completed_badge': 'Completed',
        'grade_badge': 'Grade: {grade}',
        'ready_to_register_badge': 'Ready to Register',
        'locked_badge': 'Locked',
        
        # Historical Semesters
        'historical_semesters': 'Historical Semesters & Transcript Performance',
        'all_terms_btn': 'All Terms ({count})',
        'fall': 'Fall',
        'spring': 'Spring',
        'summer': 'Summer',
        'foundation': 'Foundation',
        'term_gpa_label': 'Term GPA: {gpa}%',
        'cum_gpa_label': 'Cum. GPA: {gpa}%',
        'no_semesters_message': 'No semester transcript records parsed yet. Click View Transcript PDF to see the raw document.',
        
        # Notice & Outreach Dispatch
        'official_student_notice': 'Official Student Notice: {urgency}',
        'open_in_email_client': 'Open in Email Client',
        'copy_email_text': 'Copy Email Text',
        'print_save_pdf': 'Print / Save PDF',
        'official_notice_letter_tab': 'Official Academic Notice Letter (Print & PDF)',
        'email_dispatch_tab': 'Email Dispatch Format (Ready-to-Send)',
        'update_advising_status': 'Update Advising Status',
        'notice_sent_email': 'Notice Sent via Email',
        'student_responded': 'Student Responded',
        'meeting_completed': 'Meeting Completed',
        'plan_signed_approved': 'Plan Signed & Approved',
        'pending_outreach': 'Pending Outreach',
        'advisor_outreach_touchpoints': 'Advisor Outreach & Consultation Touchpoints',
        'log_advising_meeting': 'Log Advising Meeting',
        'email_text_copied': 'Official Email Text Copied!',
        'back_to_student_profile': 'Back to Student Profile',
        'batch_outreach_hub': 'Batch Outreach Hub',
        
        # Chairman Report
        'official_letter_to_chair': 'Official Advising Briefing to Department Chair',
        'copy_letter_text': 'Copy Letter Text',
        'download_excel_roster': 'Download Excel Roster',
        'back_to_at_risk_roster': 'Back to At-Risk Roster',
        'category_a_strict': 'CATEGORY A: STRICT / THIRD PROBATION — CRITICAL DISMISSAL STAGE',
        'category_b_second': 'CATEGORY B: SECOND PROBATION — ESCALATING WARNING STAGE',
        'category_c_first': 'CATEGORY C: FIRST PROBATION — EARLY INTERVENTION STAGE',
        'institutional_recommendations_chair': 'Institutional Recommendations for the Department Chairperson',
        'chairperson_acknowledgement': 'CHAIRPERSON ACKNOWLEDGEMENT',
        'approved_action_initiated': 'Approved / Action Initiated',
        
        # Virtual Office / Meetings
        'virtual_office_title': 'Virtual Advising Conference Rooms',
        'virtual_office_subtitle': 'Professional Google Meet style virtual conference platform with waiting room lobby, session recording, and live document exchange',
        'instant_call': 'Instant Advising Call',
        'instant_call_desc': 'Launch room with 1-click and share invite link',
        'start_instant_meeting': 'Start Instant Meeting',
        'select_advisee': 'Select Advisee Student',
        'invite_guests': 'Invite External Guests',
        'active_rooms': 'Active Advising Conference Rooms',
        
        # Policies Library
        'policies_title': 'Academic Policies & Guidance Library',
        'policies_subtitle': 'Official university policy books, student handbooks, and academic regulations used as advisor references',
        'search_policies': 'Search Academic Regulations & Guidance',
        'upload_document': 'Upload Reference Document',
        
        # Footer & Institutional
        'educational_disclaimer_title': 'Educational Disclaimer',
        'institutional_disclaimer': 'This system is an academic advisory portal for faculty supervisors and students at Dhofar University. Official records remain on the central University SIS (web.du.edu.om).',
        'rights_reserved': 'All rights reserved.',
        
        # Common UI Controls
        'back': 'Back',
        'save': 'Save',
        'cancel': 'Cancel',
        'close': 'Close',
        'filter': 'Filter',
        'all': 'All',
        'view': 'View',
        'edit': 'Edit',
        'delete': 'Delete',
        'confirm': 'Confirm',
        'loading': 'Loading...',
        'success': 'Success',
        'warning': 'Warning',
        'error': 'Error',
        'notice': 'Notice',

        # Alias & Missing Template Keys
        'student_name': 'Student Name',
        'standing': 'Academic Standing',
        'program': 'Program / Major',
        'semester_gpa': 'Semester GPA',
        'dhofar_university': 'Dhofar University',
        'degree_plan': 'Degree Plan',
        'brand_title': 'Dhofar University',
        'year': 'Academic Year',
        'advisor': 'Academic Advisor'
    },
    'ar': {
        # Global Navigation & Header
        'app_title': 'جامعة ظفار',
        'app_badge': 'الإرشاد الأكاديمي',
        'dashboard': 'لوحة التحكم',
        'advisees': 'الطلبة المُرشَدون',
        'my_advisees': 'قائمة الطلبة المُرشَدين',
        'schedule': 'الجدول والمقررات',
        'policies': 'اللوائح والأنظمة',
        'advising_wiki': 'ويكي الإرشاد',
        'virtual_office': 'المكتب الافتراضي',
        'advisor_profile': 'ملف المرشد',
        'about': 'عن المنصة',
        'students_at_risk': 'الطلبة تحت الملاحظة',
        'dark_mode': 'داكن',
        'light_mode': 'فاتح',
        'theme_toggle': 'تبديل المظهر',
        'admin_settings': 'إعدادات المشرف',
        'sign_in': 'تسجيل الدخول',
        'sign_out': 'تسجيل الخروج',
        'switch_to_arabic': 'العربية',
        'switch_to_english': 'English',
        'language': 'اللغة',
        'search_placeholder': 'البحث بالاسم، الرقم الجامعي، أو التخصص...',
        
        # Dashboard Strings
        'supervisor_dashboard': 'لوحة تحكم المرشد الأكاديمي',
        'academic_year': 'العام الأكاديمي ٢٠٢٦-٢٠٢٧',
        'sync_roster': 'مزامنة القائمة',
        'office_hours_hub': 'مركز الساعات المكتبية',
        'total_advisees': 'إجمالي الطلبة',
        'active_cohort': 'الدفعة المسجلة النشطة',
        'view_roster': 'عرض القائمة',
        'good_standing_cleared': 'الوضع السليم والمرفوعة ملاحظاتهم',
        'academic_probation': 'الملاحظة الأكاديمية',
        'strict_probation': 'الملاحظة الصارمة',
        'credit_cap_enforced': 'الحد الأقصى ١٢ ساعة معتمدة إلزامي',
        'article_14_warning': 'تحذير المادة ١٤',
        'dismissal_threshold': 'حد الفصل الأكاديمي',
        'intervene_now': 'التدخل والمتابعة',
        'cohort_health_distribution': 'توزيع الحالة الأكاديمية للدفعة',
        'cgpa_threshold_label': 'المعدل التراكمي ≥ ٦٥٪',
        
        # Priority Action & Triage
        'priority_actions_title': 'إجراءات إرشادية عاجلة ومطلوبة فوراً',
        'priority_actions_subtitle': 'طلبة يتطلب وضعهم تدخلاً إرشادياً سريعاً لضبط الساعات المعتمدة أو تسجيل المقررات المعادة',
        'action_required': 'إجراء مطلوب',
        'resolve_case': 'فتح الملف الأكاديمي',
        
        # Notice Board & Notes Drawer
        'notice_board_title': 'لوحة مهام وملاحظات المرشد الأكاديمي',
        'notice_board_subtitle': 'تنظيم مهام الإرشاد، تثبيت متابعات الطلبة، وإعداد خطط الفصل القادم',
        'toggle_notes_drawer': 'لوحة الملاحظات السريعة',
        'add_sticky_note': 'إضافة ملاحظة',
        'all_notes': 'كافة الملاحظات',
        'pinned_only': 'المثبتة فقط',
        'auto_detect_risk': 'الكشف التلقائي عن الحالات الحرجة',
        'interactive_studio': 'استوديو اللوحة الكاملة',
        'filter_by_keyword': 'تصفية الملاحظات بالكلمة المفتاحية، اسم الطالب أو رقمه...',
        'urgent': 'عاجل',
        
        # Advisees Table & Roster
        'advisee_cohort_overview': 'نظرة عامة على دفعة الطلبة',
        'showing_advisees': 'عرض',
        'full_directory': 'دليل الطلبة الكامل',
        'student_id': 'الرقم الجامعي',
        'name': 'اسم الطالب',
        'program_major': 'التخصص الأكاديمي',
        'standing_status': 'الوضع الأكاديمي',
        'cgpa': 'المعدل التراكمي',
        'sgpa': 'المعدل الفصلي',
        'actions': 'الإجراءات',
        'profile': 'الملف الأكاديمي',
        'transcript_pdf': 'السجل الأكاديمي (PDF)',
        'meet_now': 'بدء اجتماع',
        'advising_plan': 'خطة الإرشاد والتسجيل',
        
        # Academic Standings
        'status_normal': 'وضع أكاديمي سليم / اعتيادي',
        'status_cleared': 'رفع الملاحظة الأكاديمية',
        'status_first_probation': 'ملاحظة أكاديمية أولى',
        'status_second_probation': 'ملاحظة أكاديمية ثانية',
        'status_strict_probation': 'ملاحظة أكاديمية صارمة',
        'status_dismissal_risk': 'خطر الفصل الأكاديمي',
        'status_pre_probation_warning': 'إنذار ما قبل الملاحظة (أقل من ٦٥٪)',
        
        # Students at Risk View
        'at_risk_subtitle': 'الطلبة الخاضعون للملاحظة الأكاديمية أو الذين يقل معدلهم التراكمي عن ٦٥٪',
        'du_probation_policies': 'لوائح الملاحظة الأكاديمية بجامعة ظفار',
        'view_print_report': 'عرض / طباعة التقرير',
        'download_excel': 'تنزيل ملف إكسل (.xlsx)',
        'download_report_pdf': 'تنزيل تقرير الحالات (PDF)',
        'stage_1_strict': 'المرحلة الأولى: ملاحظة أكاديمية صارمة (خطر حرج)',
        'stage_2_second': 'المرحلة الثانية: ملاحظة أكاديمية ثانية (خطر مرتفع)',
        'stage_3_first': 'المرحلة الثالثة: ملاحظة أكاديمية أولى (خطر متوسط)',
        'probation_advising_note': 'الطلبة في هذه الفئة معرضون للفصل الأكاديمي الفوري. الحد الأقصى للتسجيل هو ١٢ ساعة معتمدة إجبارياً، مع أولوية إعادة المقررات الراسب فيها لتحسين المعدل.',
        'second_probation_note': 'أمضى الطالب فصلين متتاليين تحت الملاحظة. وفي حال عدم رفع المعدل التراكمي فوق ٦٥٪، سيتم تصعيده إلى الملاحظة الصارمة. العبء الدراسي محدد بـ ١٢-١٥ ساعة.',
        'first_probation_note': 'دخل الطالب تحت الملاحظة الأكاديمية لهبوط المعدل التراكمي أو الفصلي دون ٦٥٪. المراجعة الإرشادية الفورية مطلوبة لإعادة المقررات المتعثرة قبل تفاقم الوضع.',
        'chair_briefing_letter_btn': 'الخطاب الرسمي لرئيس القسم',
        'batch_outreach_hub_btn': 'مركز التواصل والإخطارات الجماعية',
        
        # Student Detail & Degree Audit Top Actions
        'meet_with_student': 'بدء اجتماع مع الطالب',
        'official_notice_email': 'الإخطار الرسمي والبريد',
        'advising_action_plan': 'خطة الإرشاد المعتمدة',
        'advising_wiki_dossier': 'ملف الويكي الإرشادي',
        'generate_recovery_schedule': 'إعداد جدول خطة التعافي',
        'consult_probation_bylaws': 'مراجعة لوائح الملاحظة الصارمة',
        'view_recommended_plan': 'عرض خطة الـ ١٢ ساعة الموصى بها',
        
        # Academic & Contact Cards
        'student_details_title': 'الملف الأكاديمي الشامل للطالب',
        'academic_information': 'البيانات الأكاديمية',
        'contact_system_details': 'بيانات الاتصال والنظام',
        'degree_progress': 'التدقيق الأكاديمي ونسبة الإنجاز',
        'academic_history': 'السجل والفصول الدراسية',
        'recovery_plan': 'خطة التعافي والمقررات المقترحة',
        'meeting_notes': 'سجل الجلسات وملاحظات الإرشاد',
        'mandatory_repeats_required': 'مقررات معادة إجبارية (المادة ١٨ من لوائح جامعة ظفار)',
        'mandatory_repeats_desc': 'لدى الطالب محاولات غير مجتازة لمقررات تؤثر سلباً على المعدل التراكمي وتعيق المتطلبات السابقة. بموجب اللوائح الجامعية، فإن إعادة هذه المقررات تستبدل الدرجات الراسبة السابقة في احتساب المعدل التراكمي:',
        'course_code': 'رمز المقرر',
        'course_title': 'اسم المقرر',
        'credits': 'الساعات',
        'attempted_term': 'فصل المحاولة',
        'recorded_grade': 'الدرجة المسجلة',
        'advising_action': 'الإجراء الإرشادي',
        'mandatory_repeat_action': 'إعادة إجبارية في الفصل القادم',
        'prerequisites': 'المتطلبات السابقة',
        'earned_credits': 'الساعات المنجزة',
        'remaining_credits': 'الساعات المتبقية',
        'current_cgpa': 'المعدل التراكمي الحالي',
        'gpa_deficit': 'عجز النقاط عن ٦٥٪',
        'academic_year_label': 'العام الأكاديمي:',
        'advisor_label': 'المرشد الأكاديمي:',
        'email_label': 'البريد الإلكتروني:',
        'phone_label': 'رقم الهاتف:',
        'not_provided': 'غير متوفر',
        'credit_cap_label': 'الحد الأقصى للساعات الفصلي:',
        'credit_cap_rule_label': 'سند تحديد الساعات:',
        'pace_to_graduate_label': 'الوتيرة المتوقعة للتخرج:',
        'semesters_remaining_count': '~{count} فصول دراسية متبقية',
        'graduation_req_label': 'شرط التخرج: ≥ ٦٥.٠٪',
        'meets_graduation_threshold': '(مستوفٍ لشرط التخرج)',
        'probation_metric_label': 'معيار الملاحظة (المادة ١٤)',
        'recovery_badge': '+{gain}٪ عن التراكمي (تعافٍ)',
        
        # 360 Persona Labels
        'academic_persona': 'الشخصية والنمط الأكاديمي',
        'risk_level': 'مستوى الخطورة',
        'degree_horizon': 'المسار الزمني للتخرج',
        'terms_to_completion': '~{terms} فصول حتى استكمال الدرجة',
        'primary_archetype': 'النمط الأكاديمي الرئيسي',
        'recommended_load': 'العبء الدراسي الموصى به',
        'credits_max': '{credits} ساعة كحد أقصى',
        'target_semester_gpa': 'المعدل الفصلي المستهدف',
        'projected_graduation': 'التخرج المتوقع',
        'what_the_student_does': 'النمط السلوكي والأكاديمي للطالب',
        'what_the_student_does_subtitle': 'عادات الدراسة والوتيرة وأنماط تسجيل المقررات المرصودة',
        'demonstrated_strengths': 'نقاط القوة الأكاديمية المثبتة',
        'what_the_student_must_do': 'ما يجب على الطالب فعله إلزامياً',
        'what_the_student_must_do_subtitle': 'التوجيهات والقرارات الإلزامية لاستمرار واستكمال الدرجة',
        'action_directives': 'توجيهات إجرائية',
        'bottlenecks_blindspots': 'العقبات ونقاط التعثر الأكاديمية الحرجة',
        'discipline_competency_breakdown': 'تحليل الكفاءة والمستوى في المجالات الأكاديمية',
        'advisor_consultation_playbook': 'دليل وخطة المقابلة الإرشادية (د. ناصر تبوك)',
        'advisor_playbook_subtitle': 'استراتيجية تواصل إرشادية مخصصة لهذا النمط الأكاديمي',
        'dispatch_official_notice': 'إرسال الإخطار الرسمي',
        'recommended_advising_tone': 'أسلوب ونبرة الإرشاد المقترحة',
        'meeting_opening_dialogue': 'العبارة الافتتاحية للمقابلة الإرشادية',
        'diagnostic_questions_to_ask': 'الأسئلة التشخيصية الأساسية لتوجيهها للطالب',
        'pass_rate': 'نسبة الاجتياز',
        'courses_count': '{count} مقررات',
        'average_short': 'المعدل',
        
        # Recommendations & Action Plan Section
        'intelligent_advising_plan': 'خطة الإرشاد الأكاديمي الذكية والمقررات المقترحة',
        'intelligent_advising_subtitle': 'توصيات مبنية على التدقيق الأكاديمي التفصيلي ولوائح جامعة ظفار',
        'priority': 'الأولوية',
        'print_official_memo': 'طباعة المذكرة الرسمية',
        'academic_diagnosis_assessment': 'التشخيص الأكاديمي وتقييم الوضع الدراسي',
        'semester_progression_trajectory': 'مسار المعدل التراكمي وتطور الأداء الفصلي',
        'benchmark_good_standing': 'المعيار المرجعي: ٦٥.٠٪ للوضع السليم',
        'current_cgpa_label': 'المعدل التراكمي الحالي',
        'peak_cgpa_label': 'أعلى معدل تراكمي مسجل',
        'lowest_gpa_label': 'أدنى معدل تراكمي مسجل',
        'latest_delta_label': 'تغير الفصل الأخير (Δ)',
        'baseline': 'خط الأساس',
        'term_gpa_legend': 'المعدل الفصلي',
        'cum_gpa_legend': 'المعدل التراكمي',
        'good_standing_threshold_65': 'حد الوضع السليم (٦٥.٠٪)',
        'trajectory_root_cause_breakdown': 'تتبع الفصول الدراسية والتحليل السببي لتحسن أو تراجع الأداء',
        'trajectory_subtitle': 'تحليل تفصيلي لأسباب ارتفاع أو انخفاض المعدل التراكمي',
        'academic_term_col': 'الفصل الدراسي',
        'term_gpa_col': 'المعدل الفصلي (Δ)',
        'cum_gpa_col': 'المعدل التراكمي (Δ)',
        'standing_load_col': 'الوضع الأكاديمي والعبء',
        'root_cause_outcome_col': 'التحليل السببي للأداء والنتائج الأكاديمية',
        'what_student_must_do_increase_gpa': 'ما يجب على الطالب فعله لرفع المعدل التراكمي (خطة التعافي وفق المادة ١٨)',
        'article_18_multiplier_subtitle': 'الاستفادة من قاعدة احتساب الدرجة الأعلى لاستبدال الرسوب ورفع المعدل حسابياً',
        'course_repeat_simulation': 'محاكاة أثر إعادة المقررات واستبدال الدرجات:',
        'repeat_simulation_intro': 'بموجب المادة ١٨ من لوائح جامعة ظفار، فإن إعادة المقرر الحاصل فيه الطالب على درجات F أو D تستبدل الدرجة السابقة في حساب المعدل التراكمي، مما يمنح قوة مضاعفة لرفع المعدل:',
        'gain_if_75': 'الزيادة عند تحقيق ٧٥٪',
        'gain_if_80': 'الزيادة عند تحقيق ٨٠٪',
        'projected_outcome': 'النتيجة المتوقعة:',
        'recovers_good_standing_alert': 'استعادة الوضع الأكاديمي السليم! (≥ ٦٥.٠٪)',
        'step_toward_good_standing': 'خطوة كبرى نحو استعادة الوضع السليم (٦٥.٠٪)',
        'no_critical_repeats_message': 'لا توجد مقررات رسوب حرجة مسجلة. حافظ على معدل فصلي منتظم فوق ٧٠.٠٪ عبر كافة متطلبات الخطة.',
        'mandatory_checklist_student': 'قائمة الإجراءات الإلزامية المطلوبة من الطالب:',
        'advisor_consultation_protocol': 'بروتوكول المقابلة الإرشادية ونص الحوار الموجه للطالب',
        'dialogue_script_subtitle': 'توجيهات المقابلة الإلزامية ومحاور الحوار الممنهج لجلسة الإرشاد',
        'consultation_required': 'مقابلة إرشادية إلزامية:',
        'consultation_required_desc': 'يجب على الطالب مراجعة المرشد الأكاديمي {advisor} خلال: {window}.',
        'mandatory_frequency': 'دورية المتابعة الإلزامية: {frequency}',
        'summon_student': 'استدعاء الطالب',
        'what_advisor_should_say': 'ما يجب أن يقوله المرشد الأكاديمي (د. ناصر تبوك) للطالب في المقابلة:',
        'what_student_must_prepare': 'ما يجب على الطالب تحضيره وسؤاله للمرشد الأكاديمي:',
        'recommended_next_semester_schedule': 'جدول المقررات الموصى به للفصل القادم (الحد الأقصى: {cap} ساعة)',
        'ch_total': 'إجمالي {total} ساعة معتمدة',
        'schedule_priority_note': 'يمنح الأولوية القصوى لإعادة المقررات الراسب فيها التي تعتبر متطلبات سابقة (المادة ١٨)، تليها متطلبات الخطة الأساسية المؤهلة.',
        'offered_section_timetable': 'الشعبة المطروحة ومواعيد المحاضرات',
        'advising_priority_rationale': 'الأولوية الإرشادية ومبررات التسجيل',
        'section_short': 'شعبة',
        'open': 'متاح',
        'closed': 'مغلق',
        'seats_available': '{seats} مقاعد',
        'not_offered_current_term': 'غير مطروح في خريف ٢٠٢٦-٢٠٢٧',
        'total_load': 'إجمالي العبء الدراسي الموصى به للفصل:',
        'ready_to_register': 'جاهزة للتسجيل ({count})',
        'locked_courses': 'مقررات معلقة ({count})',
        'prerequisites_satisfied': 'المتطلبات السابقة مستوفاة',
        'prerequisites_missing': 'المتطلبات السابقة غير مستوفاة',
        'missing_prereqs_label': 'المتطلب الناقص: {prereqs}',
        'official_policies_applied': 'اللوائح والأنظمة الرسمية المطبقة بجامعة ظفار:',
        'action_items_agreement': 'بنود العمل واتفاقية الالتزام الإرشادي',
        'academic_advisor_signature': 'المرشد الأكاديمي',
        'student_signature_agreement': 'توقيع الطالب بالموافقة والالتزام',
        'chairperson_signature': 'رئيس القسم الأكاديمي',
        'dept_cs': 'قسم علوم الحاسوب',
        'caas': 'كلية الآداب والعلوم التطبيقية',
        'date_placeholder': 'التاريخ: _____ / _____ / ٢٠٢٦',
        
        # Degree Progress Checklist
        'degree_study_plan_progress': 'نسبة إنجاز الخطة الدراسية: {program}',
        'total_plan_required': 'إجمالي ساعات الخطة',
        'completed_earned': 'الساعات المنجزة والمجتازة',
        'pct_degree_completed': '{pct}٪ من متطلبات الدرجة منجزة',
        'remaining_to_graduate': 'الساعات المتبقية للتخرج',
        'degree_completion_progress': 'مؤشر استكمال الدرجة العلمية',
        'curriculum_requirements_checklist': 'قائمة تدقيق مقررات الخطة الدراسية',
        'all_plan_courses': 'كافة مقررات الخطة ({count})',
        'completed_courses_btn': 'المجتازة ({count})',
        'remaining_courses_btn': 'المتبقية ({count})',
        'requirement_category': 'تصنيف المتطلب',
        'degree_status': 'الحالة بالخطة',
        'completed_badge': 'مجتاز',
        'grade_badge': 'الدرجة: {grade}',
        'ready_to_register_badge': 'جاهز للتسجيل',
        'locked_badge': 'معلق',
        
        # Historical Semesters
        'historical_semesters': 'السجل الأكاديمي وسجل الفصول السابقة',
        'all_terms_btn': 'كافة الفصول ({count})',
        'fall': 'خريف',
        'spring': 'ربيع',
        'summer': 'صيف',
        'foundation': 'البرنامج التأسيسي',
        'term_gpa_label': 'المعدل الفصلي: {gpa}٪',
        'cum_gpa_label': 'المعدل التراكمي: {gpa}٪',
        'no_semesters_message': 'لا توجد فصول أكاديمية مسجلة بعد. انقر على عرض السجل الأكاديمي PDF للاطلاع على الوثيقة الأصلية.',
        
        # Notice & Outreach Dispatch
        'official_student_notice': 'الإخطار الإرشادي الرسمي: {urgency}',
        'open_in_email_client': 'فتح في برنامج البريد',
        'copy_email_text': 'نسخ نص الرسالة',
        'print_save_pdf': 'طباعة / حفظ PDF',
        'official_notice_letter_tab': 'خطاب الإخطار الأكاديمي الرسمي (طباعة وPDF)',
        'email_dispatch_tab': 'صيغة البريد الإلكتروني (جاهز للإرسال)',
        'update_advising_status': 'تحديث حالة التواصل الإرشادي',
        'notice_sent_email': 'تم إرسال الإخطار بالبريد',
        'student_responded': 'استجاب الطالب / تم الرد',
        'meeting_completed': 'تمت المقابلة الإرشادية',
        'plan_signed_approved': 'تم توقيع واعتماد الخطة',
        'pending_outreach': 'بانتظار بدء التواصل',
        'advisor_outreach_touchpoints': 'سجل التواصل والمتابعات الإرشادية',
        'log_advising_meeting': 'تسجيل مقابلة إرشادية',
        'email_text_copied': 'تم نسخ نص البريد الرسمي بنجاح!',
        'back_to_student_profile': 'العودة للملف الأكاديمي',
        'batch_outreach_hub': 'مركز التواصل الجماعي',
        
        # Chairman Report
        'official_letter_to_chair': 'التقرير الإرشادي الأكاديمي الرسمي الموجه لرئيس القسم',
        'copy_letter_text': 'نسخ نص التقرير',
        'download_excel_roster': 'تنزيل كشف الإكسل',
        'back_to_at_risk_roster': 'العودة لقائمة الطلبة تحت الملاحظة',
        'category_a_strict': 'الفئة (أ): الملاحظة الأكاديمية الصارمة / الثالثة — مرحلة خطر الفصل الفوري',
        'category_b_second': 'الفئة (ب): الملاحظة الأكاديمية الثانية — مرحلة الإنذار المتتالي',
        'category_c_first': 'الفئة (ج): الملاحظة الأكاديمية الأولى — مرحلة التدخل المبكر',
        'institutional_recommendations_chair': 'توصيات إدارية وأكاديمية مقترحة لرئيس القسم',
        'chairperson_acknowledgement': 'إقرار واعتماد رئيس القسم',
        'approved_action_initiated': 'تم الاعتماد / بدء الإجراء',
        
        # Virtual Office / Meetings
        'virtual_office_title': 'غرف الإرشاد المرئي الافتراضي',
        'virtual_office_subtitle': 'منصة اجتماعات مرئية على طراز Google Meet مع غرف انتظار وتسجيل جلسات وتبادل وثائق فوري',
        'instant_call': 'جلسة إرشاد فورية',
        'instant_call_desc': 'إنشاء غرفة فورية بنقرة واحدة ومشاركة الرابط',
        'start_instant_meeting': 'بدء اجتماع فوري',
        'select_advisee': 'اختيار طالب للإرشاد',
        'invite_guests': 'دعوة ضيوف خارجيين',
        'active_rooms': 'غرف الإرشاد النشطة حالياً',
        
        # Policies Library
        'policies_title': 'مكتبة اللوائح والأنظمة الأكاديمية',
        'policies_subtitle': 'اللوائح الرسمية ودليل الطالب والأنظمة الأكاديمية المعتمدة للإرشاد بجامعة ظفار',
        'search_policies': 'البحث في الأنظمة واللوائح الأكاديمية',
        'upload_document': 'رفع وثيقة مرجعية',
        
        # Footer & Institutional
        'educational_disclaimer_title': 'إخلاء المسؤولية التعليمي',
        'institutional_disclaimer': 'هذا النظام هو بوابة إرشادية أكاديمية داخلية لأعضاء الهيئة التدريسية والطلبة بجامعة ظفار. وتظل السجلات الرسمية المعتمدة ضمن نظام معلومات الطلبة المركزي (web.du.edu.om).',
        'rights_reserved': 'جميع الحقوق محفوظة.',
        
        # Common UI Controls
        'back': 'رجوع',
        'save': 'حفظ',
        'cancel': 'إلغاء',
        'close': 'إغلاق',
        'filter': 'تصفية',
        'all': 'الكل',
        'view': 'عرض',
        'edit': 'تعديل',
        'delete': 'حذف',
        'confirm': 'تأكيد',
        'loading': 'جاري التحميل...',
        'success': 'تم بنجاح',
        'warning': 'تنبيه',
        'error': 'خطأ',
        'notice': 'ملاحظة',

        # Alias & Missing Template Keys
        'student_name': 'اسم الطالب',
        'standing': 'الوضع الأكاديمي',
        'program': 'التخصص الأكاديمي',
        'semester_gpa': 'المعدل الفصلي',
        'dhofar_university': 'جامعة ظفار',
        'degree_plan': 'الخطة الدراسية',
        'brand_title': 'جامعة ظفار',
        'year': 'السنة الدراسية',
        'advisor': 'المرشد الأكاديمي'
    }
}

def get_current_language():
    """Retrieve active language from session, query param, or fallback to 'en'."""
    try:
        if request and request.args and 'lang' in request.args:
            lang = request.args.get('lang', '').lower().strip()
            if lang in TRANSLATIONS:
                session['lang'] = lang
                return lang
    except Exception:
        pass
            
    try:
        lang = session.get('lang')
        if lang in TRANSLATIONS:
            return lang
    except Exception:
        pass
        
    return 'en'

def is_rtl():
    """Check if current active language uses right-to-left writing direction."""
    return get_current_language() == 'ar'

def translate(key, default=None, **kwargs):
    """Translate a dictionary key based on active language with fallback to English."""
    lang = get_current_language()
    val = TRANSLATIONS.get(lang, {}).get(key)
    if val is None:
        val = TRANSLATIONS.get('en', {}).get(key)
    if val is None:
        val = default if default is not None else key
        
    if kwargs and isinstance(val, str):
        try:
            return val.format(**kwargs)
        except Exception:
            return val
    return val

# Alias for concise template usage: t('key')
t = translate

# Specialized Localizers for Dynamic Data
def localize_standing(status_str, lang=None):
    """Localize academic standing status string."""
    lang = lang or get_current_language()
    if not status_str:
        return 'Normal / Good Standing' if lang != 'ar' else 'وضع أكاديمي سليم / اعتيادي'
    if lang != 'ar':
        return status_str
        
    st = str(status_str).strip()
    if 'Strict' in st or 'Third' in st:
        return 'ملاحظة أكاديمية صارمة (إنذار نهائي)'
    elif 'Second Probation' in st:
        return 'ملاحظة أكاديمية ثانية'
    elif 'First Probation' in st:
        return 'ملاحظة أكاديمية أولى'
    elif 'Probation' in st and 'Removal' not in st:
        return 'تحت الملاحظة الأكاديمية'
    elif 'Removal' in st:
        return 'رفع الملاحظة الأكاديمية'
    elif 'Very Good' in st:
        return 'وضع أكاديمي جيد جداً'
    elif 'Good' in st or 'Normal' in st:
        return 'وضع أكاديمي سليم / اعتيادي'
    elif 'At Risk' in st:
        return 'تحت الملاحظة الأكاديمية'
    return st

def localize_program(prog_str, lang=None):
    """Localize academic program or major name."""
    if not prog_str:
        return ''
    lang = lang or get_current_language()
    if lang != 'ar':
        return prog_str
        
    p = str(prog_str).strip()
    exact_map = {
        'Diploma in Computer Science': 'دبلوم في علوم الحاسوب',
        'Bachelor of Science in Computer Science': 'بكالوريوس العلوم في علوم الحاسوب',
        'Diploma in Information Technology': 'دبلوم في تقنية المعلومات',
        'Bachelor of Science in Cybersecurity': 'بكالوريوس العلوم في الأمن السيبراني',
        'Bachelor of Science in Data Science': 'بكالوريوس العلوم في علم البيانات',
        'Computer Science': 'علوم الحاسوب',
        'Cybersecurity': 'الأمن السيبراني',
        'Data Science': 'علم البيانات',
        'Diploma': 'دبلوم',
        'Bachelor of Science': 'بكالوريوس علوم'
    }
    if p in exact_map:
        return exact_map[p]
    for en_key, ar_val in exact_map.items():
        if en_key.lower() in p.lower():
            p = re.sub(re.escape(en_key), ar_val, p, flags=re.IGNORECASE)
    return p

def localize_degree_type(deg_str, lang=None):
    """Localize degree type (Diploma, Bachelor of Science)."""
    if not deg_str:
        return ''
    lang = lang or get_current_language()
    if lang != 'ar':
        return deg_str
    mapping = {
        'Diploma': 'دبلوم',
        'Bachelor of Science': 'بكالوريوس علوم',
        'Bachelor': 'بكالوريوس',
        'B.Sc.': 'بكالوريوس علوم'
    }
    return mapping.get(str(deg_str).strip(), deg_str)

def localize_year(year_str, lang=None):
    """Localize student academic year or recommended term."""
    if not year_str:
        return ''
    lang = lang or get_current_language()
    if lang != 'ar':
        return year_str
    y = str(year_str).strip()
    exact = {
        'Freshman (Year 1)': 'السنة الأولى (مستجد)',
        'Sophomore (Year 2)': 'السنة الثانية',
        'Junior (Year 3)': 'السنة الثالثة',
        'Senior (Year 4)': 'السنة الرابعة (خريج)',
        'Year 1': 'السنة الأولى',
        'Year 2': 'السنة الثانية',
        'Year 3': 'السنة الثالثة',
        'Year 4': 'السنة الرابعة',
        'First Year': 'السنة الأولى',
        'Second Year': 'السنة الثانية',
        'Third Year': 'السنة الثالثة',
        'Fourth Year': 'السنة الرابعة',
        'Year 1 Fall': 'السنة الأولى - خريف',
        'Year 1 Spring': 'السنة الأولى - ربيع',
        'Year 2 Fall': 'السنة الثانية - خريف',
        'Year 2 Spring': 'السنة الثانية - ربيع',
        'Year 3 Fall': 'السنة الثالثة - خريف',
        'Year 3 Spring': 'السنة الثالثة - ربيع',
        'Year 4 Fall': 'السنة الرابعة - خريف',
        'Year 4 Spring': 'السنة الرابعة - ربيع',
        'N/A': 'غير محدد'
    }
    if y in exact:
        return exact[y]
    y = re.sub(r'\bYear 1\b', 'السنة الأولى', y, flags=re.IGNORECASE)
    y = re.sub(r'\bYear 2\b', 'السنة الثانية', y, flags=re.IGNORECASE)
    y = re.sub(r'\bYear 3\b', 'السنة الثالثة', y, flags=re.IGNORECASE)
    y = re.sub(r'\bYear 4\b', 'السنة الرابعة', y, flags=re.IGNORECASE)
    y = re.sub(r'\bFall\b', 'خريف', y, flags=re.IGNORECASE)
    y = re.sub(r'\bSpring\b', 'ربيع', y, flags=re.IGNORECASE)
    y = re.sub(r'\bSummer\b', 'صيف', y, flags=re.IGNORECASE)
    return y

def localize_season(season_str, lang=None):
    """Localize semester season name (Fall, Spring, Summer, Foundation)."""
    if not season_str:
        return ''
    lang = lang or get_current_language()
    if lang != 'ar':
        return season_str
        
    mapping = {
        'Fall': 'خريف',
        'Spring': 'ربيع',
        'Summer': 'صيف',
        'Foundation': 'البرنامج التأسيسي'
    }
    return mapping.get(str(season_str).strip(), season_str)

def localize_term(term_str, lang=None):
    """Localize full term string (e.g., 'Fall 2026-2027 (Year 1)')."""
    if not term_str:
        return ''
    lang = lang or get_current_language()
    if lang != 'ar':
        return term_str
        
    t_str = str(term_str)
    t_str = re.sub(r'\bFall\b', 'خريف', t_str, flags=re.IGNORECASE)
    t_str = re.sub(r'\bSpring\b', 'ربيع', t_str, flags=re.IGNORECASE)
    t_str = re.sub(r'\bSummer\b', 'صيف', t_str, flags=re.IGNORECASE)
    t_str = re.sub(r'\bFoundation\b', 'البرنامج التأسيسي', t_str, flags=re.IGNORECASE)
    t_str = re.sub(r'\bTerm(\d+)\b', r'الفصل \1', t_str, flags=re.IGNORECASE)
    t_str = re.sub(r'\(Year 1\)', '(السنة الأولى)', t_str, flags=re.IGNORECASE)
    t_str = re.sub(r'\(Year 2\)', '(السنة الثانية)', t_str, flags=re.IGNORECASE)
    t_str = re.sub(r'\(Year 3\)', '(السنة الثالثة)', t_str, flags=re.IGNORECASE)
    t_str = re.sub(r'\(Year 4\)', '(السنة الرابعة)', t_str, flags=re.IGNORECASE)
    t_str = re.sub(r'\(Regular\)', '(انتظام)', t_str, flags=re.IGNORECASE)
    return t_str

def localize_priority(priority_str, lang=None):
    """Localize advising priority badges and tags."""
    if not priority_str:
        return ''
    lang = lang or get_current_language()
    if lang != 'ar':
        return priority_str
        
    mapping = {
        'URGENT': 'عاجل',
        'RECOMMENDED': 'موصى به',
        'CORE REQUIREMENT': 'متطلب أساسي بالخطة',
        'MANDATORY RULE': 'سقف إلزامي (لوائح)',
        'ACADEMIC SUPPORT': 'دعم ومختبرات تقوية',
        'ENRICHMENT': 'إثراء أكاديمي',
        'POLICY SAFEGUARD': 'إجراء وقائي نظامي',
        'High (Mandatory Repeat)': 'أولوية قصوى (إعادة إجبارية)',
        'Standard Core Requirement': 'متطلب تخصص أساسي',
        'Recommended GPA Recovery': 'موصى به لتحسين المعدل',
        'CRITICAL': 'حرج جداً',
        'HIGH': 'مرتفع',
        'MODERATE': 'متوسط',
        'NORMAL': 'اعتيادي',
        'LOW': 'منخفض'
    }
    return mapping.get(str(priority_str).strip(), priority_str)

def localize_risk_level(level_str, lang=None):
    """Localize persona risk levels."""
    if not level_str:
        return ''
    lang = lang or get_current_language()
    if lang != 'ar':
        return level_str
        
    mapping = {
        'CRITICAL': 'حرج جداً',
        'HIGH': 'مرتفع',
        'MODERATE TO HIGH': 'متوسط إلى مرتفع',
        'MODERATE': 'متوسط',
        'LOW TO MODERATE': 'منخفض إلى متوسط',
        'LOW': 'منخفض',
        'MINIMAL': 'ضئيل جداً'
    }
    return mapping.get(str(level_str).strip(), level_str)

def localize_outreach_status(status_str, lang=None):
    """Localize advising outreach and contact statuses."""
    if not status_str:
        return ''
    lang = lang or get_current_language()
    if lang != 'ar':
        return status_str
        
    mapping = {
        'Pending Outreach': 'بانتظار التواصل',
        'Notice Sent via Email': 'تم إرسال الإخطار بالبريد',
        'Student Responded': 'استجاب الطالب / تم الرد',
        'Meeting Completed': 'تمت المقابلة الإرشادية',
        'Plan Signed & Approved': 'تم توقيع واعتماد الخطة'
    }
    return mapping.get(str(status_str).strip(), status_str)

COURSE_NAMES_AR = {
    'basic academic english': 'اللغة الإنجليزية الأكاديمية الأساسية',
    'english for academic purposes i': 'اللغة الإنجليزية للأغراض الأكاديمية (١)',
    'english for academic purposes ii': 'اللغة الإنجليزية للأغراض الأكاديمية (٢)',
    'english for academic purposes iii': 'اللغة الإنجليزية للأغراض الأكاديمية (٣)',
    'academic writing in arabic': 'الكتابة الأكاديمية باللغة العربية',
    'arabic language': 'اللغة العربية',
    'islamic culture': 'الثقافة الإسلامية',
    'omani society': 'المجتمع العماني',
    'oman and islamic civilization': 'عمان والحضارة الإسلامية',
    'entrepreneurship: innovation and creativity': 'ريادة الأعمال: الابتكار والإبداع',
    'entrepreneurship: innovation & creativity': 'ريادة الأعمال: الابتكار والإبداع',
    'community service': 'خدمة المجتمع',
    'life and study skills': 'مهارات الحياة والدراسة',
    'calculus i': 'التفاضل والتكامل (١)',
    'calculus ii': 'التفاضل والتكامل (٢)',
    'linear algebra i': 'الجبر الخطي (١)',
    'linear algebra': 'الجبر الخطي',
    'discrete mathematics': 'الرياضيات المتقطعة',
    'probability and statistics': 'الاحتمالات والإحصاء',
    'general physics i': 'الفيزياء العامة (١)',
    'general physics ii': 'الفيزياء العامة (٢)',
    'general chemistry i': 'الكيمياء العامة (١)',
    'general biology i': 'الأحياء العامة (١)',
    'science elective i (physics/chemistry/biology)': 'متطلب علوم اختياري (١) (فيزياء/كيمياء/أحياء)',
    'science elective ii (physics/chemistry/biology)': 'متطلب علوم اختياري (٢) (فيزياء/كيمياء/أحياء)',
    'introduction to technical computing for the sciences': 'مقدمة في الحوسبة التقنية للعلوم',
    'introduction to programming': 'مقدمة في البرمجة',
    'computer programming': 'برمجة الحاسوب',
    'digital system design': 'تصميم الأنظمة الرقمية',
    'computer organization with assembly language': 'تنظيم الحاسوب ولغة التجميع',
    'data structures': 'هياكل البيانات',
    'analysis of algorithms': 'تحليل الخوارزميات',
    'computer networks': 'شبكات الحاسوب',
    'graphical user interface': 'واجهات المستخدم الرسومية',
    'operating systems': 'نظم التشغيل',
    'database systems': 'نظم قواعد البيانات',
    'web development': 'تطوير تطبيقات الويب',
    'internet software development': 'تطوير برمجيات الإنترنت',
    'mobile application development': 'تطوير تطبيقات الهواتف الذكية',
    'system analysis and design': 'تحليل وتصميم النظم',
    'human computer interaction': 'التفاعل بين الإنسان والحاسوب',
    'programming languages': 'لغات البرمجة',
    'advanced programming in java': 'البرمجة المتقدمة بلغة جافا',
    'artificial intelligence': 'الذكاء الاصطناعي',
    'software engineering': 'هندسة البرمجيات',
    'compiler design': 'تصميم المترجمات',
    'computer graphics': 'رسوميات الحاسوب',
    'parallel and distributed computing': 'الحوسبة المتوازية والموزعة',
    'computer and network security': 'أمن الحاسوب والشبكات',
    'computer security and privacy': 'أمن الحاسوب والخصوصية',
    'ethics and professional practice in computing': 'أخلاقيات المهنة والممارسة الاحترافية في الحوسبة',
    'diploma project': 'مشروع التخرج للدبلوم',
    'senior project / capstone': 'مشروع التخرج',
    'final year project i': 'مشروع التخرج (١)',
    'final year project ii': 'مشروع التخرج (٢)',
    'internship': 'التدريب الميداني',
    'practical training / internship': 'التدريب العملي / الميداني',
    'major elective i': 'مقرر تخصص اختياري (١)',
    'major elective ii': 'مقرر تخصص اختياري (٢)',
    'major elective iii': 'مقرر تخصص اختياري (٣)',
    'university elective': 'متطلب جامعة اختياري',
    'social science elective': 'متطلب علوم اجتماعية اختياري',
    'humanities elective': 'متطلب علوم إنسانية اختياري',
    'principles of cybersecurity': 'مبادئ الأمن السيبراني',
    'cryptography and network security': 'التشفير وأمن الشبكات',
    'ethical hacking and penetration testing': 'الاختراق الأخلاقي واختبار الاختراق',
    'digital forensics and incident response': 'التحقيق الجنائي الرقمي والاستجابة للحوادث',
    'secure software development': 'تطوير البرمجيات الآمنة',
    'cloud computing and security': 'الحوسبة السحابية وأمنها',
    'cybersecurity governance, risk and compliance': 'حوكمة الأمن السيبراني والمخاطر والامتثال',
    'cybersecurity capstone project i': 'مشروع تخرج الأمن السيبراني (١)',
    'cybersecurity capstone project ii': 'مشروع تخرج الأمن السيبراني (٢)',
    'cybersecurity elective i': 'مقرر أمن سيبراني اختياري (١)',
    'cybersecurity elective ii': 'مقرر أمن سيبراني اختياري (٢)',
    'introduction to data science': 'مقدمة في علم البيانات',
    'statistical methods for data science': 'الأساليب الإحصائية لعلم البيانات',
    'machine learning': 'تعلم الآلة',
    'data mining and warehousing': 'التنقيب في البيانات ومستودعاتها',
    'big data analytics': 'تحليلات البيانات الضخمة',
    'data visualization and storytelling': 'تصور البيانات وعرضها التفاعلي',
    'deep learning and neural networks': 'التعلم العميق والشبكات العصبية',
    'natural language processing': 'معالجة اللغات الطبيعية',
    'data science capstone project i': 'مشروع تخرج علم البيانات (١)',
    'data science capstone project ii': 'مشروع تخرج علم البيانات (٢)',
    'data science elective i': 'مقرر علم بيانات اختياري (١)',
    'data science elective ii': 'مقرر علم بيانات اختياري (٢)',
    'foundation english level 1': 'اللغة الإنجليزية التأسيسية - المستوى الأول',
    'foundation english level 2': 'اللغة الإنجليزية التأسيسية - المستوى الثاني',
    'foundation english level 3': 'اللغة الإنجليزية التأسيسية - المستوى الثالث',
    'foundation math': 'الرياضيات التأسيسية',
    'foundation it': 'تقنية المعلومات التأسيسية'
}

def localize_course_name(name_str, lang=None):
    """Localize course title to Arabic when lang == 'ar'."""
    if not name_str:
        return ''
    lang = lang or get_current_language()
    if lang != 'ar':
        return name_str
    clean = ' '.join(str(name_str).strip().split())
    lower = clean.lower()
    if lower in COURSE_NAMES_AR:
        return COURSE_NAMES_AR[lower]
    for en_k, ar_v in COURSE_NAMES_AR.items():
        if en_k == lower or (len(en_k) > 10 and en_k in lower):
            return ar_v
    # Word-level fallback for dynamic transcript course names
    fallback_terms = [
        (r'\bIntroduction to Technical Computing for the Sciences\b', 'مقدمة في الحوسبة التقنية للعلوم'),
        (r'\bIntroduction to\b', 'مقدمة في'),
        (r'\bBasic Academic English\b', 'اللغة الإنجليزية الأكاديمية الأساسية'),
        (r'\bAcademic Writing in Arabic\b', 'الكتابة الأكاديمية باللغة العربية'),
        (r'\bEnglish for Academic Purposes\b', 'اللغة الإنجليزية للأغراض الأكاديمية'),
        (r'\bComputer Organization with Assembly Language\b', 'تنظيم الحاسوب ولغة التجميع'),
        (r'\bComputer Programming\b', 'برمجة الحاسوب'),
        (r'\bProgramming Languages\b', 'لغات البرمجة'),
        (r'\bAdvanced Programming in Java\b', 'البرمجة المتقدمة بلغة جافا'),
        (r'\bProgramming\b', 'البرمجة'),
        (r'\bDigital System Design\b', 'تصميم الأنظمة الرقمية'),
        (r'\bData Structures\b', 'هياكل البيانات'),
        (r'\bAnalysis of Algorithms\b', 'تحليل الخوارزميات'),
        (r'\bComputer Networks\b', 'شبكات الحاسوب'),
        (r'\bGraphical User Interface\b', 'واجهات المستخدم الرسومية'),
        (r'\bOperating Systems\b', 'نظم التشغيل'),
        (r'\bDatabase Systems\b', 'نظم قواعد البيانات'),
        (r'\bSoftware Engineering\b', 'هندسة البرمجيات'),
        (r'\bArtificial Intelligence\b', 'الذكاء الاصطناعي'),
        (r'\bHuman Computer Interaction\b', 'التفاعل بين الإنسان والحاسوب'),
        (r'\bOmani Society\b', 'المجتمع العماني'),
        (r'\bIslamic Culture\b', 'الثقافة الإسلامية'),
        (r'\bEntrepreneurship\b', 'ريادة الأعمال'),
        (r'\bInnovation and Creativity\b', 'الابتكار والإبداع'),
        (r'\bCalculus\b', 'التفاضل والتكامل'),
        (r'\bLinear Algebra\b', 'الجبر الخطي'),
        (r'\bDiscrete Mathematics\b', 'الرياضيات المتقطعة'),
        (r'\bProbability and Statistics\b', 'الاحتمالات والإحصاء'),
        (r'\bGeneral Physics\b', 'الفيزياء العامة'),
        (r'\bGeneral Chemistry\b', 'الكيمياء العامة'),
        (r'\bGeneral Biology\b', 'الأحياء العامة'),
        (r'\bInternet Software Development\b', 'تطوير برمجيات الإنترنت'),
        (r'\bWeb Development\b', 'تطوير الويب'),
        (r'\bSystem Analysis and Design\b', 'تحليل وتصميم النظم'),
        (r'\bFinal Year Project\b', 'مشروع التخرج'),
        (r'\bDiploma Project\b', 'مشروع الدبلوم'),
        (r'\bInternship\b', 'التدريب الميداني'),
        (r'\bFoundation\b', 'تأسيسي'),
        (r'\bElective\b', 'مقرر اختياري')
    ]
    res = clean
    for pat, rep in fallback_terms:
        res = re.sub(pat, rep, res, flags=re.IGNORECASE)
    return res

def localize_category(cat_str, lang=None):
    """Localize curriculum requirement category."""
    if not cat_str:
        return ''
    lang = lang or get_current_language()
    if lang != 'ar':
        return cat_str
    mapping = {
        'University Requirement': 'متطلب جامعة إجباري',
        'University Elective': 'متطلب جامعة اختياري',
        'College Requirement': 'متطلب كلية إجباري',
        'College Elective': 'متطلب كلية اختياري',
        'Major Core': 'متطلب تخصص إجباري',
        'Major Requirement': 'متطلب تخصص إجباري',
        'Major Elective': 'متطلب تخصص اختياري',
        'Cybersecurity Core': 'متطلب تخصص أمن سيبراني',
        'Data Science Core': 'متطلب تخصص علم البيانات',
        'Department Requirement': 'متطلب قسم أكاديمي',
        'Foundation': 'البرنامج التأسيسي',
        'Elective / General': 'مقرر اختياري / عام',
        'General Guidance': 'إرشادات أكاديمية عامة',
        'Academic Regulations': 'اللوائح والأنظمة الأكاديمية',
        'Academic Probation & Standing': 'لوائح الملاحظة والوضع الأكاديمي',
        'Degree Requirements': 'متطلبات الدرجة العلمية',
        'Plan of Study': 'الخطة الدراسية المعتمدة',
        'Study Guides & Guidelines': 'أدلة الدراسة والإرشاد',
        'Registration & Add/Drop Bylaws': 'لوائح التسجيل والحذف والإضافة',
        'Grading & Examination Policy': 'سياسة التقييم والامتحانات'
    }
    return mapping.get(str(cat_str).strip(), cat_str)

def localize_days(days_str, lang=None):
    """Localize schedule days (SunTueThu, MonWed, etc.)."""
    if not days_str:
        return ''
    lang = lang or get_current_language()
    if lang != 'ar':
        return days_str
    mapping = {
        'SunTueThu': 'أحد - ثلاثاء - خميس',
        'MonWed': 'إثنين - أربعاء',
        'Sun': 'الأحد',
        'Mon': 'الإثنين',
        'Tue': 'الثلاثاء',
        'Wed': 'الأربعاء',
        'Thu': 'الخميس',
        'Daily (Field)': 'يومياً (تدريب ميداني)'
    }
    return mapping.get(str(days_str).strip(), days_str)

def localize_session_type(session_str, lang=None):
    """Localize Morning / Evening session."""
    if not session_str:
        return ''
    lang = lang or get_current_language()
    if lang != 'ar':
        return session_str
    mapping = {
        'Morning': 'صباحي',
        'Evening': 'مسائي'
    }
    return mapping.get(str(session_str).strip(), session_str)

def localize_language(lang_str, lang=None):
    """Localize language of instruction (English / Arabic)."""
    if not lang_str:
        return ''
    lang = lang or get_current_language()
    if lang != 'ar':
        return lang_str
    mapping = {
        'English': 'الإنجليزية',
        'Arabic': 'العربية'
    }
    return mapping.get(str(lang_str).strip(), lang_str)

def localize_instructor(inst_str, lang=None):
    """Localize instructor or faculty label."""
    if not inst_str:
        return ''
    lang = lang or get_current_language()
    if lang != 'ar':
        return inst_str
    mapping = {
        'Dr. Nasser Tabook': 'د. ناصر تبوك',
        'Nasser Tabook': 'د. ناصر تبوك',
        'CS Faculty': 'هيئة تدريس علوم الحاسوب',
        'Math Faculty': 'هيئة تدريس الرياضيات',
        'Physics Faculty': 'هيئة تدريس الفيزياء',
        'FP English Dept': 'قسم اللغة الإنجليزية',
        'General Studies Dept': 'قسم الدراسات العامة',
        'Management Dept': 'قسم الإدارة والأعمال'
    }
    return mapping.get(str(inst_str).strip(), inst_str)

def localize_remark(rem_str, lang=None):
    """Localize schedule remark or prerequisite string."""
    if not rem_str:
        return ''
    lang = lang or get_current_language()
    if lang != 'ar':
        return rem_str
    r = str(rem_str).strip()
    r = re.sub(r'\bLecture \+ Lab\b', 'محاضرة + مختبر عملي', r, flags=re.IGNORECASE)
    r = re.sub(r'\bUniversity Requirement\b', 'متطلب جامعة', r, flags=re.IGNORECASE)
    r = re.sub(r'\bDepartment Requirement\b', 'متطلب قسم', r, flags=re.IGNORECASE)
    r = re.sub(r'\bSenior Standing / Internship\b', 'مستوى التخرج / تدريب ميداني', r, flags=re.IGNORECASE)
    r = re.sub(r'\bPrereq:\s*', 'المتطلب السابق: ', r, flags=re.IGNORECASE)
    r = re.sub(r'\bCoreq:\s*', 'المتطلب المتزامن: ', r, flags=re.IGNORECASE)
    r = re.sub(r'\bDiploma Final Year\b', 'السنة النهائية للدبلوم', r, flags=re.IGNORECASE)
    r = re.sub(r'\bB\.Sc\. Final Year\b', 'السنة النهائية للبكالوريوس', r, flags=re.IGNORECASE)
    r = re.sub(r'\bCompleted (\d+) CH\b', r'إنجاز \1 ساعة معتمدة', r, flags=re.IGNORECASE)
    r = re.sub(r'\band\b', 'و', r, flags=re.IGNORECASE)
    return r

def localize_seat_status(status_str, lang=None):
    """Localize section seat status."""
    if not status_str:
        return ''
    lang = lang or get_current_language()
    if lang != 'ar':
        return status_str
    mapping = {
        'Open': 'متاح',
        'Full': 'مكتمل',
        'Closed': 'مغلق',
        'Not Offered': 'غير مطروح',
        'Not Offered in Current Term': 'غير مطروح في الفصل الحالي'
    }
    return mapping.get(str(status_str).strip(), status_str)

def localize_notice_category(cat_str, lang=None):
    """Localize sticky notice category."""
    if not cat_str:
        return ''
    lang = lang or get_current_language()
    if lang != 'ar':
        return cat_str
    mapping = {
        'Urgent Risk': 'خطر أكاديمي عاجل',
        'Follow-Up': 'متابعة إرشادية',
        'Registration': 'تسجيل المقررات',
        'Meeting': 'اجتماع إرشادي',
        'General': 'عام'
    }
    return mapping.get(str(cat_str).strip(), cat_str)

def localize_notice(note: dict, lang=None) -> dict:
    """Return a localized copy of a notice board note dictionary."""
    if not note:
        return note
    lang = lang or get_current_language()
    out = dict(note)
    prog_raw = out.get('program') or out.get('student_program') or ''
    if lang != 'ar':
        out['category_display'] = out.get('category', 'general')
        out['student_program_display'] = prog_raw
        return out

    cat_map = {
        'at_risk': 'حالات الملاحظة الحرجة',
        'meeting': 'اجتماع إرشادي',
        'registration': 'تسجيل المقررات',
        'follow_up': 'متابعة إرشادية',
        'general': 'عام',
        'Urgent Risk': 'خطر أكاديمي عاجل',
        'Follow-Up': 'متابعة إرشادية',
        'Registration': 'تسجيل المقررات',
        'Meeting': 'اجتماع إرشادي',
        'General': 'عام'
    }
    out['category_display'] = cat_map.get(str(out.get('category', 'general')).strip(), out.get('category', 'عام'))
    if prog_raw == 'All Programs':
        out['program'] = 'جميع التخصصات'
        out['student_program_display'] = 'جميع التخصصات'
    elif prog_raw == 'BSc Computer Science':
        out['program'] = 'بكالوريوس علوم الحاسوب'
        out['student_program_display'] = 'بكالوريوس علوم الحاسوب'
    else:
        loc_p = localize_program(prog_raw, lang='ar')
        out['program'] = loc_p
        out['student_program_display'] = loc_p

    title = str(out.get('title', ''))
    content = str(out.get('content', ''))

    seed_titles = {
        'Strict Probation Urgent Check-in': 'متابعة عاجلة لطلبة الملاحظة الأكاديمية الصارمة',
        'Spring 2026/2027 Advising Memo Prep': 'إعداد مذكرات الإرشاد الأكاديمي لفصل ربيع ٢٠٢٦/٢٠٢٧',
        'Book Office Hours Hub Sessions': 'حجز جلسات الساعات المكتبية والمقابلات الإرشادية',
        'Untitled Notice': 'ملاحظة بدون عنوان'
    }
    seed_contents = {
        'Follow up with advisees on Strict & 2nd Probation before Drop/Add deadline. Ensure Article 14 credit limits (max 12 credits) are enforced.':
            'متابعة الطلبة المدرجين تحت الملاحظة الأكاديمية الصارمة والثانية قبل انتهاء فترة الحذف والإضافة، والتأكد من تطبيق سقف الـ ١٢ ساعة معتمدة (المادة ١٤).',
        'Review students completing 60+ credit hours for major milestone requirements and elective prerequisites.':
            'مراجعة سجلات الطلبة الذين أتموا ٦٠ ساعة معتمدة فأكثر للتحقق من متطلبات التخصص المرحلية والمقررات الاختيارية.',
        'Schedule 15-minute 1-on-1 virtual check-ins with at-risk cohort in the Virtual Office Hours Hub.':
            'جدولة جلسات إرشادية افتراضية فردية (١٥ دقيقة) مع الطلبة تحت الملاحظة عبر مركز الساعات المكتبية الافتراضي.',
        'Review 12-credit hour cap and mandatory course repeats (Article 18) before add/drop closes.':
            'مراجعة الحد الأقصى الإلزامي للساعات (١٢ ساعة معتمدة) وإعادة المقررات المتعثرة (المادة ١٨) قبل إغلاق فترة الحذف والإضافة.',
        'Verify study plan progression and prerequisite chains for all CS & IT Diploma students.':
            'التحقق من تقدم الخطة الدراسية وسلاسل المتطلبات السابقة لكافة طلبة علوم الحاسوب ودبلوم تقنية المعلومات.',
        'Schedule 1-on-1 virtual or in-person consultations with First & Second Probation students.':
            'جدولة جلسات استشارية فردية (افتراضية أو حضورية) مع طلبة الملاحظة الأكاديمية الأولى والثانية.'
    }
    if title in seed_titles:
        title = seed_titles[title]
    elif title.startswith('Strict Probation Alert:'):
        student_part = title.replace('Strict Probation Alert:', '').strip()
        title = f'تنبيه ملاحظة أكاديمية صارمة: {student_part}'
    elif title.startswith('Academic Probation Alert:'):
        student_part = title.replace('Academic Probation Alert:', '').strip()
        title = f'تنبيه ملاحظة أكاديمية: {student_part}'
    elif title.startswith('Probation Follow-Up:'):
        student_part = title.replace('Probation Follow-Up:', '').strip()
        title = f'متابعة ملاحظة أكاديمية: {student_part}'

    if content in seed_contents:
        content = seed_contents[content]
    elif 'Standing:' in content:
        content = localize_standing_in_text(content)
        content = content.replace('Standing:', 'الوضع الأكاديمي:')
        content = content.replace('CGPA:', 'المعدل التراكمي:')
        content = content.replace('SGPA:', 'المعدل الفصلي:')
        content = content.replace(
            'Call for advising meeting. Max credit load: 12 cr. Review transcript for retakes.',
            'استدعاء لجلسة إرشادية عاجلة. الحد الأقصى للعبء الدراسي: ١٢ ساعة معتمدة. مراجعة السجل الأكاديمي لإعادة المقررات المتعثرة.'
        )
        content = content.replace(
            'Mandatory 12-credit cap & repeat failed/D courses (DU Art. 14 & 18). Schedule immediate advising session.',
            'الحد الأقصى الإلزامي ١٢ ساعة معتمدة مع إعادة المقررات الراسبة أو ذات التقدير المنخفض (المادتان ١٤ و١٨). يرجى جدولة جلسة إرشادية فورية.'
        )

    out['title'] = title
    out['content'] = content
    return out

def localize_standing_in_text(text: str) -> str:
    """Helper to replace English standing phrases inside composite text."""
    replacements = [
        ('Third/Strict Probation', 'الملاحظة الأكاديمية الصارمة / الثالثة'),
        ('Second Strict Probation', 'الملاحظة الأكاديمية الصارمة الثانية'),
        ('Strict Probation', 'الملاحظة الأكاديمية الصارمة'),
        ('Second Probation', 'الملاحظة الأكاديمية الثانية'),
        ('First Probation', 'الملاحظة الأكاديمية الأولى'),
        ('Academic Probation Removal', 'رفع الملاحظة الأكاديمية'),
        ('Normal / Good Standing', 'الوضع الأكاديمي السليم')
    ]
    res = text
    for en_s, ar_s in replacements:
        res = res.replace(en_s, ar_s)
    return res

def localize_policy_doc(policy_obj, lang=None):
    """Localize a PolicyReference object or dict for display in templates."""
    lang = lang or get_current_language()
    if lang != 'ar':
        return policy_obj
    import copy
    p = copy.copy(policy_obj)
    title_map = {
        'DU Undergraduate Academic Regulations': 'لوائح الدراسات الجامعية الأولى بجامعة ظفار',
        'DU Academic Advising Handbook': 'دليل الإرشاد الأكاديمي بجامعة ظفار',
        'Cybersecurity Plan Of Study': 'الخطة الدراسية لبكالوريوس الأمن السيبراني',
        'Cybersecurity Plan of Study': 'الخطة الدراسية لبكالوريوس الأمن السيبراني',
        'Data Science Plan Of Study': 'الخطة الدراسية لبكالوريوس علم البيانات',
        'Data Science Plan of Study': 'الخطة الدراسية لبكالوريوس علم البيانات',
        'Computer Science Plan Of Study': 'الخطة الدراسية لبكالوريوس علوم الحاسوب',
        'Computer Science Plan of Study': 'الخطة الدراسية لبكالوريوس علوم الحاسوب',
        'Requirements For Studying Computer Science Diploma': 'متطلبات دراسة دبلوم علوم الحاسوب والانتقال للبكالوريوس',
        'Requirements for Studying Computer Science Diploma': 'متطلبات دراسة دبلوم علوم الحاسوب والانتقال للبكالوريوس'
    }
    desc_map = {
        'Official Academic Regulations reference guide': 'الدليل المرجعي الرسمي للوائح والأنظمة الأكاديمية بجامعة ظفار',
        'Official Study Guides & Guidelines reference guide': 'الدليل الإرشادي المرجعي الرسمي للدراسة والتوجيه الأكاديمي',
        'Official Plan of Study reference guide': 'الدليل المرجعي الرسمي للخطة الدراسية المعتمدة وتوزيع المقررات',
        'Official Degree Requirements reference guide': 'الدليل المرجعي الرسمي لمتطلبات الدرجة العلمية وشروط التجسير'
    }
    t_val = getattr(p, 'title', '') if not isinstance(p, dict) else p.get('title', '')
    c_val = getattr(p, 'category', '') if not isinstance(p, dict) else p.get('category', '')
    d_val = getattr(p, 'description', '') if not isinstance(p, dict) else p.get('description', '')

    ar_t = title_map.get(t_val, t_val)
    ar_c = localize_category(c_val, lang='ar')
    ar_d = desc_map.get(d_val, d_val)
    if ar_d == d_val and d_val.startswith('Official ') and d_val.endswith(' reference guide'):
        ar_d = f'الدليل المرجعي الرسمي — {ar_c}'

    if isinstance(p, dict):
        p['title'] = ar_t
        p['category'] = ar_c
        p['description'] = ar_d
    else:
        p.title = ar_t
        p.category = ar_c
        p.description = ar_d
    return p

def localize_settings(settings: dict, lang=None) -> dict:
    """Return localized application settings dictionary when Arabic is active."""
    if not settings:
        return settings
    lang = lang or get_current_language()
    if lang != 'ar':
        return settings
    import copy
    s = copy.deepcopy(settings)
    b = s.get('branding', {})
    if b.get('app_title') == 'Dhofar University':
        b['app_title'] = 'جامعة ظفار'
    if b.get('app_badge') == 'ADVISING':
        b['app_badge'] = 'الإرشاد الأكاديمي'
    if 'Dhofar University' in b.get('browser_tab_title', ''):
        b['browser_tab_title'] = 'منصة الإرشاد الأكاديمي — جامعة ظفار'

    f = s.get('footer', {})
    if 'Dhofar University' in f.get('organization_line', ''):
        f['organization_line'] = 'جامعة ظفار — قسم علوم الحاسوب (وحدة الإرشاد الأكاديمي)'
    if 'Academic Advising' in f.get('tagline', ''):
        f['tagline'] = 'منصة الإرشاد الأكاديمي الذكي، تدقيق الخطط الدراسية، ومتابعة الطلبة'
    if 'educational and academic advising purposes' in f.get('disclaimer', ''):
        f['disclaimer'] = (
            'إخلاء مسؤولية مؤسسي وتعليمي: تم تطوير هذا النظام لأغراض الإرشاد الأكاديمي والمتابعة التعليمية في جامعة ظفار. '
            'ورغم مواءمة عمليات التدقيق الأكاديمي مع لوائح الجامعة، يظل نظام معلومات الطلبة الرسمي (SIS) ومكتب المسجل العام هما المرجع القانوني النهائي للسجلات الأكاديمية.'
        )
    if 'Dhofar University' in f.get('copyright', ''):
        f['copyright'] = '© ٢٠٢٦ جامعة ظفار — قسم علوم الحاسوب. جميع الحقوق محفوظة.'

    a = s.get('about', {})
    if 'Dhofar University' in a.get('app_name', ''):
        a['app_name'] = 'منصة الإرشاد الأكاديمي وإدارة الطلبة بجامعة ظفار'
    if 'Enterprise Academic' in a.get('release_name', ''):
        a['release_name'] = 'إصدار الذكاء الإرشادي الأكاديمي المتكامل'
    if 'March 2026' in a.get('release_date', ''):
        a['release_date'] = 'مارس ٢٠٢٦'
    if 'comprehensive academic advising' in a.get('purpose_statement', ''):
        a['purpose_statement'] = (
            'منصة إرشاد أكاديمي شاملة ومنظومة متكاملة لمتابعة الطلبة، مصممة خصيصاً لأعضاء الهيئة التدريسية والمرشدين الأكاديميين '
            'في قسم علوم الحاسوب بكلية الآداب والعلوم التطبيقية في جامعة ظفار. توحد المنصة تحليل السجلات الأكاديمية، وتدقيق الخطط الدراسية '
            'لبرامج الدبلوم والبكالوريوس، والتدخل المبكر لطلبة الملاحظة الأكاديمية، وغرف الاجتماعات المرئية التفاعلية.'
        )
    if 'support faculty advisors' in a.get('institutional_disclaimer', ''):
        a['institutional_disclaimer'] = (
            'تم تصميم هذه المنصة لدعم المرشدين الأكاديميين والطلبة خلال جلسات الإرشاد والتخطيط الفصلي. '
            'جميع التوصيات والمحاكاة استرشادية وتخضع للتحقق النهائي عبر بوابة التسجيل الرسمية بجامعة ظفار (web.du.edu.om) ولوائح الدراسات الجامعية الأولى.'
        )
    if a.get('advisor_name') in ('Dr. Nasser Tabook', 'Nasser Tabook'):
        a['advisor_name'] = 'د. ناصر تبوك'
    if 'Academic Advisor' in a.get('advisor_role', ''):
        a['advisor_role'] = 'المرشد الأكاديمي وأستاذ علوم الحاسوب المساعد'
    if 'College of Arts' in a.get('college', ''):
        a['college'] = 'كلية الآداب والعلوم التطبيقية (CAAS)'
    if 'Computer Science' in a.get('department', ''):
        a['department'] = 'قسم علوم الحاسوب'

    p = s.get('profile', {})
    if 'Nasser' in p.get('full_name', ''):
        p['full_name'] = 'د. ناصر طمطيم تبوك'
    if 'Assistant Professor' in p.get('title', ''):
        p['title'] = 'أستاذ مساعد في علوم الحاسوب ومرشد أكاديمي'
    if 'College of Arts' in p.get('college', ''):
        p['college'] = 'كلية الآداب والعلوم التطبيقية (CAAS)'
    if 'Computer Science' in p.get('department', ''):
        p['department'] = 'قسم علوم الحاسوب والرياضيات'
    if 'CAAS Building' in p.get('office_location', ''):
        p['office_location'] = 'مبنى كلية الآداب والعلوم التطبيقية — قسم علوم الحاسوب، جامعة ظفار، صلالة، سلطنة عُمان'
    if 'Sunday' in p.get('office_hours', ''):
        p['office_hours'] = 'الأحد، الثلاثاء، الخميس: ١٠:٠٠ صباحاً – ١:٠٠ ظهراً | الإثنين، الأربعاء: ١١:٠٠ صباحاً – ١٢:٣٠ ظهراً (أو عبر المكتب الافتراضي)'
    if 'faculty member and Academic Advisor' in p.get('bio', ''):
        p['bio'] = (
            'د. ناصر طمطيم تبوك عضو هيئة تدريس ومرشد أكاديمي في قسم علوم الحاسوب بكلية الآداب والعلوم التطبيقية في جامعة ظفار. '
            'يركز عمله الأكاديمي والإرشادي على تمكين طلبة البكالوريوس والدبلوم في تخصصات علوم الحاسوب، والأمن السيبراني، وعلم البيانات، '
            'ودعمهم لتحقيق التميز الأكاديمي، والتعافي المنظم من الملاحظة الأكاديمية، والجاهزية المهنية لسوق العمل.'
        )
    if 'Every student has the potential' in p.get('advising_mission', ''):
        p['advising_mission'] = (
            'كل طالب يمتلك القدرة على التفوق عندما يُسلَّح بخارطة طريق أكاديمية واضحة، وتدخل إرشادي مبكر، وتوجيه شخصي مستمر '
            'يربط بين متطلبات الخطة الدراسية وطموحاته المهنية المستقبلية.'
        )
    if 'Computer Science' in p.get('research_interests', ''):
        p['research_interests'] = 'علوم الحاسوب، الذكاء الاصطناعي، الأمن السيبراني، علم البيانات، التكنولوجيا التعليمية، ونظم الإرشاد الأكاديمي الذكية'

    adm = s.get('admin', {})
    if adm.get('display_name') in ('Dr. Nasser Tabook', 'Nasser Tabook'):
        adm['display_name'] = 'د. ناصر تبوك'
    if 'Academic Advisor' in adm.get('role_title', ''):
        adm['role_title'] = 'المرشد الأكاديمي ومشرف النظام'

    return s

