
# =======================
# Imports
# =======================
import os
from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
from flask_login import LoginManager, current_user, login_user, logout_user
from dotenv import load_dotenv

# App-specific imports
from utils import simple_similarity, categorize_ingredient
from jinja_filters import datetimeformat, format_nz_week
from auth import require_role, get_db_connection, User
from book_a_class.book_a_class import book_a_class_bp
from catering.catering import catering_bp
from debug_parser.debug_parser_instructions import debug_parser_instructions_bp
from upload_URL import upload_url_bp
from recipe_book import recipe_book_bp
from debug_parser.utils import extract_raw_text_from_url
from auth.google_auth import google_auth_bp
from ingredients.ingredients import ingredients_bp
from program_help.program_help import program_help_bp
from recipe_setup import recipe_book_setup
from admin_task.utils import get_staff_code_from_email
# ...other imports as needed...

# =======================
# App Creation & Configuration
# =======================
load_dotenv()
app = Flask(__name__)
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['format_nz_week'] = format_nz_week
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

# =======================
# Context Processors
# =======================
@app.context_processor
def inject_current_user():
    return dict(current_user=current_user)

# =======================
# Flask-Login Setup
# =======================
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    """Load user from session."""
    if 'user' in session and session['user'].get('google_id') == user_id:
        user_data = session['user']
        return User(
            user_data['google_id'],
            user_data['email'],
            user_data['name'],
            user_data.get('staff_code')
        )
    return None

# =======================
# Register Blueprints
# =======================
from auth.routes import auth_bp
from ShopList import shoplist_bp
from api.routes import api_bp
app.register_blueprint(auth_bp)
app.register_blueprint(shoplist_bp)
app.register_blueprint(api_bp)
# Register book_a_class, catering, ingredients, and program_help blueprints for navigation
app.register_blueprint(book_a_class_bp)
app.register_blueprint(catering_bp)
app.register_blueprint(ingredients_bp)
app.register_blueprint(program_help_bp)
app.register_blueprint(recipe_book_bp)
# ...register other blueprints as needed...

# =======================
# Register Error Handlers
# =======================
from error_handlers import not_found_error, internal_error
app.register_error_handler(404, not_found_error)
app.register_error_handler(500, internal_error)

# =======================
# Routes
# =======================
@app.route("/")
def index():
    return redirect(url_for('recipe_book.recbk'))

# =======================
# Other Config/Constants
# =======================
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]