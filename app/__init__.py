"""Flask application factory"""

from flask import Flask
from config import config
import logging
import os

def create_app(config_name=None):
    """Create Flask application"""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(project_root, 'templates')
    static_dir = os.path.join(project_root, 'static')
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config[config_name])
    
    # Enable reverse proxy support (SCRIPT_NAME prefix, proto, host)
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Initialize logging
    setup_logging(app)
    
    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Context processor for global application settings and admin session state
    @app.context_processor
    def inject_app_context():
        from flask import session
        from app.settings_manager import get_settings
        return {
            'app_settings': get_settings(),
            'is_admin_logged_in': session.get('is_admin', False),
            'admin_username': session.get('admin_username', '')
        }
    
    # Optional global login enforcement if admin configured require_login_for_portal
    @app.before_request
    def check_portal_access():
        from flask import session, request, redirect, url_for
        from app.settings_manager import get_settings
        settings = get_settings()
        if settings.get('admin', {}).get('require_login_for_portal', False):
            if not session.get('is_admin'):
                endpoint = request.endpoint or ''
                if (endpoint.startswith('static') or 
                    request.blueprint == 'auth' or 
                    endpoint == 'main.about_page' or 
                    'meeting' in endpoint):
                    return None
                return redirect(url_for('auth.login', next=request.url))
    
    return app

def setup_logging(app):
    """Setup application logging"""
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Dhofar University Student Management System startup')
