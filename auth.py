"""
Authentication and authorization module for the Food Room Inventory system.
Handles Google OAuth 2.0 login and role-based access control.
"""

from flask_login import UserMixin
from functools import wraps
from flask import session, redirect, url_for, flash
import sqlite3
import os

# Role definitions based on staff codes
ROLE_PERMISSIONS = {
    'VP': {
        'name': 'Vice Principal',
        'routes': ['recipes', 'recbk', 'class_ingredients', 'booking', 'shoplist', 'admin', 'dashboard']
    },
    'DK': {
        'name': 'Teacher',
        'routes': ['recipes', 'recbk', 'class_ingredients', 'booking', 'shoplist']
    },
    'MU': {
        'name': 'Booking Staff',
        'routes': ['recipes', 'recbk', 'booking', 'shoplist']
    },
    'public': {
        'name': 'Public',
        'routes': ['recbk']
    }
}


class User(UserMixin):
    """User model for authenticated users."""
    
    def __init__(self, google_id, email, name, staff_code=None):
        self.id = google_id
        self.email = email
        self.name = name
        self.staff_code = staff_code
        self.role = self._get_role()
    
    def _get_role(self):
        """Determine user role based on staff code."""
        if self.staff_code in ROLE_PERMISSIONS:
            return self.staff_code
        # Default to public if staff code not recognized
        return 'public'
    
    def has_access(self, endpoint):
        """Check if user has access to the given endpoint."""
        role = self.role
        if role not in ROLE_PERMISSIONS:
            return False
        return endpoint in ROLE_PERMISSIONS[role]['routes']
    
    def is_admin(self):
        """Check if user is an admin (VP)."""
        return self.role == 'VP'
    
    def is_teacher(self):
        """Check if user is a teacher."""
        return self.role in ['VP', 'DK']
    
    def is_staff(self):
        """Check if user is staff."""
        return self.role in ['VP', 'DK', 'MU']


def get_user_by_google_id(google_id):
    """Retrieve or create a user based on Google ID."""
    # In a real application, you would store this in a database
    # For now, we'll store it in the session
    if 'user' in session and session['user'].get('google_id') == google_id:
        user_data = session['user']
        return User(
            user_data['google_id'],
            user_data['email'],
            user_data['name'],
            user_data.get('staff_code')
        )
    return None


def get_staff_code_from_email(email):
    """Look up staff code from teacher email in database."""
    try:
        # Use absolute path to database
        db_path = os.path.join(os.path.dirname(__file__), 'recipes.db')
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute('SELECT code FROM teachers WHERE email = ?', (email,))
            result = c.fetchone()
            return result[0] if result else None
    except Exception:
        return None


def require_login(f):
    """Decorator to require user to be logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in to access this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def require_role(*allowed_roles):
    """Decorator to require user to have specific role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                flash('Please log in to access this page.')
                return redirect(url_for('login'))
            
            user_data = session['user']
            user = User(
                user_data['google_id'],
                user_data['email'],
                user_data['name'],
                user_data.get('staff_code')
            )
            
            if user.role not in allowed_roles:
                flash(f'You do not have permission to access this page. Required role: {", ".join(allowed_roles)}')
                return redirect(url_for('recbk'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def public_with_auth(f):
    """Decorator for routes that are public but can be enhanced if logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # This route doesn't require login, but can access user data if logged in
        return f(*args, **kwargs)
    return decorated_function
