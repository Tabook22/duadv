"""Authentication helper utilities and decorators"""

from functools import wraps
from flask import session, redirect, url_for, flash, request

def admin_required(f):
    """Decorator to require authenticated admin access for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Please log in with administrator credentials to access this area.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
