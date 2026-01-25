from flask import Blueprint, redirect, url_for, session, flash
import os
from flask_login import logout_user

navigation_bp = Blueprint('navigation', __name__)

@navigation_bp.route('/logout')
def logout():
    """Log out the current user."""
    logout_user()
    raw_data_filename = session.get('raw_data_file')
    if raw_data_filename:
        tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
        raw_data_path = os.path.join(tmp_dir, raw_data_filename)
        try:
            if os.path.exists(raw_data_path):
                os.remove(raw_data_path)
        except Exception:
            pass
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('recipe_book.recbk'))
