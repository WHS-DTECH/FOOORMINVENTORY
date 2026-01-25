# Ensure current_user is always available in templates
from flask_login import current_user

@app.context_processor
def inject_current_user():
    return dict(current_user=current_user)
from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
import os

from debug_parser.debug_parser_instructions import debug_instructions
import os
from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
from flask_login import LoginManager
from dotenv import load_dotenv
from recipe_parser_pdf import parse_recipes_from_text
from debug_parser.debug_parser_Serving import debug_serving
from debug_parser.debug_parser_title import debug_title

from utils import simple_similarity, categorize_ingredient
from jinja_filters import datetimeformat, format_nz_week
from auth import require_role, get_db_connection, User

from book_a_class.book_a_class import book_a_class_bp
from debug_parser.debug_parser_instructions import debug_parser_instructions_bp
from upload_URL import upload_url_bp
from recipe_book import recipe_book_bp
from debug_parser.utils import extract_raw_text_from_url
from auth.google_auth import google_auth_bp
from ingredients.ingredients import ingredients_bp
from flask_login import current_user, login_user, logout_user
from recipe_setup import recipe_book_setup
from google_auth_oauthlib.flow import Flow

from admin_task.utils import get_staff_code_from_email

# ...existing code...
app = Flask(__name__)
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['format_nz_week'] = format_nz_week
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

# Redirect root URL to recipe book
@app.route("/")
def index():
    return redirect(url_for('recipe_book.recbk'))
# ...existing code...

# Import AnonymousUser from auth.anonymous_user

# =======================
# App Creation & Configuration
# =======================

load_dotenv()

app = Flask(__name__)
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['format_nz_week'] = format_nz_week
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

# Register blueprints after app is created

# Register blueprints after app is created
from auth.routes import auth_bp
from ShopList import shoplist_bp
from api.routes import api_bp
app.register_blueprint(auth_bp)
app.register_blueprint(shoplist_bp)
app.register_blueprint(api_bp)
app.register_blueprint(recipe_book_bp)

# Register error handlers
from error_handlers import not_found_error, internal_error
app.register_error_handler(404, not_found_error)
app.register_error_handler(500, internal_error)

SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]


# Initialize Flask-Login
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