# navigation_main/context_nav.py
from flask import Blueprint

def nav_context_processor():
    # No longer need to provide main_nav_links; navigation is hardcoded in nav.html
    return {}

# Optionally, you can create a blueprint for navigation if you want to add nav-specific routes later
nav_bp = Blueprint('navigation_main', __name__, template_folder='templates')
