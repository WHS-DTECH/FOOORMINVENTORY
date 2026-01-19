# This file contains all debug_parser-related routes and logic extracted from app.py for modularization.
# To be used as the Flask blueprint/module for debug_parser.

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import current_user
from auth import require_role, get_db_connection
import json

# Import debug helpers
from debug_parser.parser_confirm_URL import confirm_url
from debug_parser.parser_confirm_title import confirm_title
from debug_parser.parser_confirm_serving import confirm_serving
from debug_parser.parser_confirm_ingredients import confirm_ingredients
from debug_parser.parser_confirm_instructions import confirm_instructions
from debug_parser.debug_parser_title import debug_title

bp = Blueprint('debug_parser', __name__, template_folder='templates/debug_parser')

# --- API: Save solution as confirmed title ---
@bp.route('/api/save_title_solution/<int:test_recipe_id>', methods=['POST'])
def api_save_title_solution(test_recipe_id):
    # ...existing code from app.py...
    pass

# --- API: Run second title extraction strategy ---
@bp.route('/api/title_strategy/recipe_word/<int:test_recipe_id>', methods=['GET'])
def api_title_strategy_recipe_word(test_recipe_id):
    # ...existing code from app.py...
    pass

# --- API: Run first title extraction strategy ---
@bp.route('/api/title_strategy/url_match/<int:test_recipe_id>', methods=['GET'])
def api_title_strategy_url_match(test_recipe_id):
    # ...existing code from app.py...
    pass

# --- Confirm Field (modular, including Source URL) ---
@bp.route('/confirm_field', methods=['POST'])
@require_role('Admin')
def confirm_field():
    # ...existing code from app.py...
    pass

# --- Debug Title Page (modular) ---
@bp.route('/debug_title/<int:test_recipe_id>')
@require_role('Admin')
def debug_title_route(test_recipe_id):
    # ...existing code from app.py...
    pass

# Route to render the debug extract text form
@bp.route('/debug_extract_text_form', methods=['GET'])
@require_role('Admin')
def debug_extract_text_form():
    # ...existing code from app.py...
    pass

# --- Raw Data View for flagged/test recipe ---
@bp.route('/parser_debug_raw/<int:test_recipe_id>')
@require_role('Admin')
def parser_debug_raw(test_recipe_id):
    # ...existing code from app.py...
    pass

# --- Parser Debug Page for flagged/test recipes ---
@bp.route('/parser_debug/<int:test_recipe_id>')
@require_role('Admin')
def parser_debug(test_recipe_id):
    # ...existing code from app.py...
    pass

# --- Handle Yes/No debug prompt after flag ---
@bp.route('/parser_test_decision', methods=['POST'])
@require_role('Admin')
def parser_test_decision():
    # ...existing code from app.py...
    pass
