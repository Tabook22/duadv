"""Authentication routes"""

from flask import render_template, redirect, url_for, flash, request
from app.auth import bp

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Supervisor login page"""
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    """Logout supervisor"""
    return redirect(url_for('main.index'))
