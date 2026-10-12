"""Internationalization (i18n) and Bilingual Engine for Dhofar University Advising Portal.
Supports English (LTR) and Arabic (RTL) with academic terminology tailored for DU advising bylaws.
"""

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
        'supervisor_dashboard': 'Supervisor Advising Dashboard',
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
        
        # Students at Risk View
        'at_risk_subtitle': 'Advisees requiring academic advising intervention due to probation status or GPA < 65%',
        'du_probation_policies': 'DU Probation Policies',
        'view_print_report': 'View / Print Report',
        'download_excel': 'Download Excel (.xlsx)',
        'download_report_pdf': 'Download Report PDF',
        'stage_1_strict': 'Stage 1: Strict Probation (Critical Risk)',
        'stage_2_second': 'Stage 2: Second Probation (Consecutive Warning)',
        'stage_3_first': 'Stage 3: First Probation (Initial Intervention)',
        'probation_advising_note': 'Students in this group are at immediate risk of academic dismissal. Mandatory maximum credit limit is 12 credit hours. Priority must be given to repeating failed and low-grade courses.',
        
        # Student Detail & Degree Audit
        'student_details_title': 'Student Academic Dossier',
        'academic_information': 'Academic Information',
        'degree_progress': 'Degree Progress & Audit',
        'academic_history': 'Academic History & Transcript',
        'recovery_plan': 'Action Plan & Recommended Courses',
        'meeting_notes': 'Meeting Notes & Interaction Log',
        'mandatory_repeats_required': 'Mandatory Course Repeats Required (Dhofar University Bylaws Article 18)',
        'mandatory_repeats_desc': 'The student has unresolved course attempt(s) that were not passed. These courses block downstream prerequisites and weigh down the cumulative GPA.',
        'course_code': 'Course Code',
        'course_title': 'Course Title',
        'credits': 'Credits',
        'attempted_term': 'Attempted Term',
        'recorded_grade': 'Recorded Grade',
        'prerequisites': 'Prerequisites',
        'earned_credits': 'Earned Credits',
        'remaining_credits': 'Remaining Credits',
        'current_cgpa': 'Current CGPA',
        'gpa_deficit': 'GPA Deficit',
        
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
        'notice': 'Notice'
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
        
        # Students at Risk View
        'at_risk_subtitle': 'الطلبة الخاضعون للملاحظة الأكاديمية أو الذين يقل معدلهم التراكمي عن ٦٥٪',
        'du_probation_policies': 'لوائح الملاحظة الأكاديمية بجامعة ظفار',
        'view_print_report': 'عرض / طباعة التقرير',
        'download_excel': 'تنزيل ملف إكسل (.xlsx)',
        'download_report_pdf': 'تنزيل تقرير الحالات (PDF)',
        'stage_1_strict': 'المرحلة الأولى: ملاحظة أكاديمية صارمة (حرج جداً)',
        'stage_2_second': 'المرحلة الثانية: ملاحظة أكاديمية ثانية (إنذار متتالٍ)',
        'stage_3_first': 'المرحلة الثالثة: ملاحظة أكاديمية أولى (تدخل مبكر)',
        'probation_advising_note': 'الطلبة في هذه الفئة معرضون للفصل الأكاديمي الفوري. الحد الأقصى للتسجيل هو ١٢ ساعة معتمدة إجبارياً، مع أولوية إعادة المقررات الراسب فيها لتحسين المعدل.',
        
        # Student Detail & Degree Audit
        'student_details_title': 'الملف الأكاديمي الشامل للطالب',
        'academic_information': 'البيانات الأكاديمية',
        'degree_progress': 'التدقيق الأكاديمي ونسبة الإنجاز',
        'academic_history': 'السجل والفصول الدراسية',
        'recovery_plan': 'خطة التعافي والمقررات المقترحة',
        'meeting_notes': 'سجل الجلسات وملاحظات الإرشاد',
        'mandatory_repeats_required': 'مقررات معادة إجبارية (المادة ١٨ من لوائح جامعة ظفار)',
        'mandatory_repeats_desc': 'لدى الطالب محاولات غير مجتازة لمقررات تؤثر سلباً على المعدل التراكمي وتعيق المتطلبات السابقة.',
        'course_code': 'رمز المقرر',
        'course_title': 'اسم المقرر',
        'credits': 'الساعات',
        'attempted_term': 'فصل المحاولة',
        'recorded_grade': 'الدرجة المسجلة',
        'prerequisites': 'المتطلبات السابقة',
        'earned_credits': 'الساعات المنجزة',
        'remaining_credits': 'الساعات المتبقية',
        'current_cgpa': 'المعدل التراكمي الحالي',
        'gpa_deficit': 'عجز النقاط عن ٦٥٪',
        
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
        'notice': 'ملاحظة'
    }
}

def get_current_language():
    """Retrieve active language from session, query param, or fallback to 'en'."""
    # Allow query parameter override like ?lang=ar
    if request and request.args and 'lang' in request.args:
        lang = request.args.get('lang', '').lower().strip()
        if lang in TRANSLATIONS:
            session['lang'] = lang
            return lang
            
    # Check session
    lang = session.get('lang')
    if lang in TRANSLATIONS:
        return lang
        
    return 'en'

def is_rtl():
    """Check if current active language uses right-to-left writing direction."""
    return get_current_language() == 'ar'

def translate(key, default=None, **kwargs):
    """Translate a dictionary key based on active language with fallback to English."""
    lang = get_current_language()
    val = TRANSLATIONS.get(lang, {}).get(key)
    if val is None:
        # Fallback to English
        val = TRANSLATIONS.get('en', {}).get(key)
    if val is None:
        val = default if default is not None else key
        
    if kwargs:
        try:
            return val.format(**kwargs)
        except Exception:
            return val
    return val

# Alias for concise template usage: t('key')
t = translate
