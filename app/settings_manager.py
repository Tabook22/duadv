"""Application Settings and Configuration Manager

Manages persistent configuration for:
- Branding (App Title, Logo Icon/Image, Badge, Browser Tab Title)
- Footer text (Organization, Tagline, Institutional Disclaimer, Copyright)
- About information (App Name, Version, Release, Mission, Advisor Profile)
- Access Control & Permissions (Who can enter meetings, send messages, edit notes)
- Admin Security (Username, Password Hash, Session Requirements)
"""

import os
import json
import logging
from threading import Lock
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)

DEFAULT_SETTINGS = {
    "admin": {
        "username": "admin",
        "password_hash": generate_password_hash("admin123"),
        "display_name": "Dr. Nasser Tabook",
        "role_title": "Academic Advisor & Supervisor",
        "avatar_initials": "NT",
        "require_login_for_portal": False
    },
    "branding": {
        "app_title": "Dhofar University",
        "app_badge": "ADVISING",
        "logo_icon": "fa-graduation-cap",
        "logo_image_url": "",
        "browser_tab_title": "Dhofar University - Student Management System",
        "theme_color": "#2563eb"
    },
    "footer": {
        "organization_line": "Dhofar University • College of Arts & Applied Sciences",
        "tagline": "Student Management System • Advisee Analytics & WebRTC Hub",
        "disclaimer": "This independent advising management platform is developed solely for educational mentoring and advisory workflow facilitation. It is not an official system of any educational institution and is maintained by the advisor for direct student supervision.",
        "copyright": "© 2026 Academic Advising Hub. All rights reserved."
    },
    "about": {
        "app_name": "DU Advisee & Academic Advisory Suite",
        "version": "v2.5.0",
        "release_name": "Academic Nexus Edition",
        "release_date": "October 2026",
        "purpose_statement": "A dedicated, professional academic advising and analytics suite built for academic advisors to track student degree progress, monitor academic standing, automate transcript auditing, and facilitate secure virtual office consultations.",
        "institutional_disclaimer": "Notice: This application is an independent educational tool designed solely for the benefit of the advisor to know the situation and status of his advisees at any given time. It does not belong to any educational institute.",
        "advisor_name": "Dr. Nasser Tabook",
        "advisor_role": "Assistant Professor & Academic Advisor",
        "college": "College of Arts & Applied Sciences",
        "department": "Computer Science & Mathematics"
    },
    "permissions": {
        "require_advisor_admission": True,
        "allow_guest_chat": True,
        "allow_guest_notes_edit": False,
        "allow_guest_video": True,
        "allow_guest_audio": True,
        "meeting_passcode": ""
    }
}

_lock = Lock()
_cached_settings = None

def _get_settings_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, 'settings.json')

def load_settings():
    """Load settings from JSON file, creating with defaults if absent."""
    global _cached_settings
    with _lock:
        path = _get_settings_path()
        if not os.path.exists(path):
            _cached_settings = json.loads(json.dumps(DEFAULT_SETTINGS))
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(_cached_settings, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.error(f"Error initializing default settings file: {e}")
            return _cached_settings

        try:
            with open(path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            
            # Deep merge with defaults so new keys are always present
            merged = json.loads(json.dumps(DEFAULT_SETTINGS))
            for section, values in loaded.items():
                if section in merged and isinstance(values, dict):
                    merged[section].update(values)
                else:
                    merged[section] = values
            
            _cached_settings = merged
            return _cached_settings
        except Exception as e:
            logger.error(f"Error loading settings from {path}: {e}")
            if _cached_settings:
                return _cached_settings
            return json.loads(json.dumps(DEFAULT_SETTINGS))

def get_settings():
    """Retrieve current cached settings (loading if not yet cached)."""
    global _cached_settings
    if _cached_settings is None:
        return load_settings()
    return _cached_settings

def save_settings(new_settings):
    """Save full settings dictionary to disk and update cache."""
    global _cached_settings
    with _lock:
        path = _get_settings_path()
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(new_settings, f, indent=2, ensure_ascii=False)
            _cached_settings = new_settings
            return True, "Settings saved successfully."
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False, f"Failed to save settings: {str(e)}"

def verify_admin_credentials(username, password):
    """Verify admin login credentials against stored settings."""
    settings = get_settings()
    admin_cfg = settings.get('admin', {})
    stored_username = admin_cfg.get('username', 'admin')
    stored_hash = admin_cfg.get('password_hash', '')

    if username.strip().lower() != stored_username.strip().lower():
        return False

    return check_password_hash(stored_hash, password)

def update_admin_security(new_username, new_password=None, display_name=None, role_title=None, initials=None, require_login=None):
    """Update admin username, password, display details and login policy."""
    settings = json.loads(json.dumps(get_settings()))
    admin_cfg = settings.setdefault('admin', {})

    if new_username and new_username.strip():
        admin_cfg['username'] = new_username.strip()
    
    if new_password and len(new_password) >= 4:
        admin_cfg['password_hash'] = generate_password_hash(new_password)
    
    if display_name is not None:
        admin_cfg['display_name'] = display_name.strip()
        
    if role_title is not None:
        admin_cfg['role_title'] = role_title.strip()
        
    if initials is not None:
        admin_cfg['avatar_initials'] = initials.strip()
        
    if require_login is not None:
        admin_cfg['require_login_for_portal'] = bool(require_login)

    return save_settings(settings)

def update_branding(app_title=None, app_badge=None, logo_icon=None, logo_image_url=None, browser_tab_title=None, theme_color=None):
    """Update application branding settings."""
    settings = json.loads(json.dumps(get_settings()))
    branding = settings.setdefault('branding', {})

    if app_title is not None:
        branding['app_title'] = app_title.strip()
    if app_badge is not None:
        branding['app_badge'] = app_badge.strip()
    if logo_icon is not None:
        branding['logo_icon'] = logo_icon.strip()
    if logo_image_url is not None:
        branding['logo_image_url'] = logo_image_url.strip()
    if browser_tab_title is not None:
        branding['browser_tab_title'] = browser_tab_title.strip()
    if theme_color is not None:
        branding['theme_color'] = theme_color.strip()

    return save_settings(settings)

def update_footer(organization_line=None, tagline=None, disclaimer=None, copyright=None):
    """Update footer content and disclaimers."""
    settings = json.loads(json.dumps(get_settings()))
    footer = settings.setdefault('footer', {})

    if organization_line is not None:
        footer['organization_line'] = organization_line.strip()
    if tagline is not None:
        footer['tagline'] = tagline.strip()
    if disclaimer is not None:
        footer['disclaimer'] = disclaimer.strip()
    if copyright is not None:
        footer['copyright'] = copyright.strip()

    return save_settings(settings)

def update_about(app_name=None, version=None, release_name=None, release_date=None, purpose_statement=None, institutional_disclaimer=None, advisor_name=None, advisor_role=None, college=None, department=None):
    """Update 'About Application' description, release info, and disclaimers."""
    settings = json.loads(json.dumps(get_settings()))
    about = settings.setdefault('about', {})

    if app_name is not None:
        about['app_name'] = app_name.strip()
    if version is not None:
        about['version'] = version.strip()
    if release_name is not None:
        about['release_name'] = release_name.strip()
    if release_date is not None:
        about['release_date'] = release_date.strip()
    if purpose_statement is not None:
        about['purpose_statement'] = purpose_statement.strip()
    if institutional_disclaimer is not None:
        about['institutional_disclaimer'] = institutional_disclaimer.strip()
    if advisor_name is not None:
        about['advisor_name'] = advisor_name.strip()
    if advisor_role is not None:
        about['advisor_role'] = advisor_role.strip()
    if college is not None:
        about['college'] = college.strip()
    if department is not None:
        about['department'] = department.strip()

    return save_settings(settings)

def update_permissions(require_advisor_admission=None, allow_guest_chat=None, allow_guest_notes_edit=None, allow_guest_video=None, allow_guest_audio=None, meeting_passcode=None):
    """Update permissions controlling who can enter, write, and send messages."""
    settings = json.loads(json.dumps(get_settings()))
    perms = settings.setdefault('permissions', {})

    if require_advisor_admission is not None:
        perms['require_advisor_admission'] = bool(require_advisor_admission)
    if allow_guest_chat is not None:
        perms['allow_guest_chat'] = bool(allow_guest_chat)
    if allow_guest_notes_edit is not None:
        perms['allow_guest_notes_edit'] = bool(allow_guest_notes_edit)
    if allow_guest_video is not None:
        perms['allow_guest_video'] = bool(allow_guest_video)
    if allow_guest_audio is not None:
        perms['allow_guest_audio'] = bool(allow_guest_audio)
    if meeting_passcode is not None:
        perms['meeting_passcode'] = meeting_passcode.strip()

    return save_settings(settings)
