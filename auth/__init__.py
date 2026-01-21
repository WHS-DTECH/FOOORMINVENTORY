"""
Authentication and authorization module for the Food Room Inventory system.
Handles Google OAuth 2.0 login and role-based access control.
"""

from flask_login import UserMixin
from functools import wraps
from flask import session, redirect, url_for, flash
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Role mapping between display names and legacy codes
ROLE_NAME_TO_CODE = {
    'Admin': 'Admin',
    'Admin': 'Admin',
    'Teacher': 'Teacher',
    'Technician': 'MU',
    'Public Access': 'public',
    'Teacher': 'Teacher',
    'MU': 'MU',
    'public': 'public',
}
ROLE_CODE_TO_NAME = {v: k for k, v in ROLE_NAME_TO_CODE.items()}

# Legacy fallback - now permissions are stored in database
ROLE_PERMISSIONS = {
    'Admin': {
        'name': 'Admin',
        'routes': ['recipes', 'recbk', 'class_ingredients', 'booking', 'shoplist', 'admin', 'dashboard']
    },
    'Teacher': {
        'name': 'Teacher',
        'routes': ['recipes', 'recbk', 'class_ingredients', 'booking', 'shoplist']
    },
    'MU': {
        'name': 'Technician',
        'routes': ['recipes', 'recbk', 'booking', 'shoplist']
    },
    'public': {
        'name': 'Public Access',
        'routes': ['recbk']
    }
}

def get_db_connection():
    """Get a PostgreSQL database connection using psycopg2."""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise RuntimeError('DATABASE_URL environment variable not set')
    return psycopg2.connect(db_url, cursor_factory=RealDictCursor)

def get_role_permissions_from_db(role):
    """Get list of routes a role has access to from database."""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT route FROM role_permissions WHERE role = %s', (role,))
            routes = [row['route'] for row in c.fetchall()]
            return routes
    except Exception as e:
        # Fallback to hardcoded permissions if database read fails
        print(f"Error reading permissions from database: {e}")
        if role in ROLE_PERMISSIONS:
            return ROLE_PERMISSIONS[role]['routes']
        return []

class User(UserMixin):
    """User model for authenticated users."""
    def __init__(self, google_id, email, name, staff_code=None):
        self.id = google_id
        self.email = email
        self.name = name
        self.staff_code = staff_code
        self.role = self._get_role()
        self.additional_roles = self._get_additional_roles()
    def _get_role(self):
        """Determine user role based on staff code."""
        # Accept both legacy code and new display name
        if self.staff_code in ROLE_PERMISSIONS:
            return self.staff_code
        if self.staff_code in ROLE_NAME_TO_CODE:
            return ROLE_NAME_TO_CODE[self.staff_code]
        # Default to public if staff code not recognized
        return 'public'
    def _get_additional_roles(self):
        """Get additional roles assigned to this user from the database."""
        try:
            with get_db_connection() as conn:
                c = conn.cursor()
                c.execute('SELECT role FROM user_roles WHERE email = %s', (self.email,))
                return [row['role'] for row in c.fetchall()]
        except Exception:
            return []
    def get_all_roles(self):
        """Get all roles for this user (primary + additional), normalized to both code and display name."""
        roles = [self.role]
        roles.extend(self.additional_roles)
        # Normalize: include both code and display name for each role
        normalized = set()
        for r in roles:
            code = ROLE_NAME_TO_CODE.get(r, r)
            name = ROLE_CODE_TO_NAME.get(code, code)
            normalized.add(code)
            normalized.add(name)
        return list(normalized)
    def has_access(self, endpoint):
        """Check if user has access to the given endpoint."""
        # Check all roles (primary + additional)
        all_roles = self.get_all_roles()
        for role in all_roles:
            allowed_routes = get_role_permissions_from_db(role)
            if endpoint in allowed_routes:
                return True
        return False
    def is_admin(self):
        """Check if user is an admin (Admin)."""
        return 'Admin' in self.get_all_roles()
    def is_teacher(self):
        """Check if user is a teacher."""
        all_roles = self.get_all_roles()
        return any(role in ['Admin', 'Teacher'] for role in all_roles)
    def is_staff(self):
        """Check if user is staff."""
        all_roles = self.get_all_roles()
        return any(role in ['Admin', 'Teacher', 'MU'] for role in all_roles)

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
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT code FROM teachers WHERE email = %s', (email,))
            result = c.fetchone()
            return result['code'] if result else None
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

            # Normalize allowed_roles to include both code and display name
            allowed = set()
            for r in allowed_roles:
                code = ROLE_NAME_TO_CODE.get(r, r)
                name = ROLE_CODE_TO_NAME.get(code, code)
                allowed.add(code)
                allowed.add(name)

            user_roles = set(user.get_all_roles())
            if not user_roles & allowed:
                flash(f'You do not have permission to access this page. Required role: {", ".join(allowed_roles)}')
                return redirect(url_for('recipe_book.recbk'))

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
