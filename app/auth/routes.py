"""Authentication routes for Administrator and Academic Advisor"""

from flask import render_template, redirect, url_for, flash, request, session
from app.auth import bp
from app.settings_manager import verify_admin_credentials, get_settings

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Administrator / Advisor login page"""
    if session.get('is_admin'):
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please enter both username and password.', 'warning')
            return render_template('auth/login.html')
            
        if verify_admin_credentials(username, password):
            session['is_admin'] = True
            session['admin_username'] = username
            settings = get_settings()
            advisor_name = settings.get('admin', {}).get('display_name', 'Advisor')
            flash(f'Signed in successfully as {advisor_name}. Full administrative access granted.', 'success')
            
            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(url_for('main.admin_settings'))
        else:
            flash('Invalid username or password. Please check your credentials and try again.', 'danger')

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    """Sign out current administrator"""
    session.pop('is_admin', None)
    session.pop('admin_username', None)
    flash('You have been signed out successfully.', 'info')
    return redirect(url_for('main.index'))
