# navigation_main/context_nav.py
from flask import Blueprint

def nav_context_processor():
    # Add any variables you want available in all templates (e.g., nav links)
    return {
        'main_nav_links': [
            {'name': 'Food Room', 'endpoint': 'index'},
            {'name': 'Recipe Book', 'endpoint': 'recbk'},
            {'name': 'Class Ingredients', 'endpoint': 'class_ingredients'},
            {'name': 'Shopping List', 'endpoint': 'book_the_shopping'},
            {'name': 'Admin', 'endpoint': 'admin'},
        ]
    }

# Optionally, you can create a blueprint for navigation if you want to add nav-specific routes later
nav_bp = Blueprint('navigation_main', __name__, template_folder='templates')
