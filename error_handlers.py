from flask import render_template

def not_found_error(error):
    """Render custom 404 error page."""
    return render_template('404.html'), 404

def internal_error(error):
    """Render custom 500 error page."""
    return render_template('500.html'), 500
from flask import render_template

def not_found_error(error):
    """Render custom 404 error page."""
    return render_template('404.html'), 404

def internal_error(error):
    """Render custom 500 error page."""
    return "An internal error occurred. Please try again later.", 500
