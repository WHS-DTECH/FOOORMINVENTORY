


# =======================
# DONT PUT NEW CODE HERE - put it in the appropriate section below!!!
# =======================

# =======================
# Imports (Standard, Third-party, Local)
# =======================

import os
import requests
from bs4 import BeautifulSoup
import re
import datetime
import json
import csv
import io
try:
    import uuid
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session

# Import and register admin_task blueprint early
from admin_task import admin_task_bp


app = Flask(__name__)
# Ensure secret key is set from environment for session persistence
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.register_blueprint(admin_task_bp)

# Import the ShopList blueprint
from ShopList import shoplist_bp
from flask_login import LoginManager, login_user, logout_user, current_user
from google_auth_oauthlib.flow import Flow
import psycopg2
import psycopg2.extras
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None

from recipe_parser_pdf import parse_recipes_from_text
from auth import User, get_staff_code_from_email, require_login, require_role, get_db_connection
# Register debug_source_url blueprint
from debug_parser.debug_source_url_route import bp as debug_source_url_bp
from navigation_main.context_nav import nav_context_processor, nav_bp


from book_a_class.book_a_class import book_a_class_bp
from debug_parser.debug_parser_instructions import debug_parser_instructions_bp
from upload_URL import upload_url_bp
from recipe_book import recipe_book_bp
from debug_parser.utils import extract_raw_text_from_url
from auth.google_auth import google_auth_bp
from ingredients.ingredients import ingredients_bp


# =======================
# AnonymousUser Class for Flask-Login
# =======================
class AnonymousUser:
    is_authenticated = False
    def is_admin(self):
        return False
    def is_teacher(self):
        return False
    def is_staff(self):
        return False

        
# =======================
# Utility Functions
# =======================
def simple_similarity(a, b):
    """Return a similarity score between 0 and 1 based on Levenshtein distance (if available) or substring match."""
    try:
        import Levenshtein
        return Levenshtein.ratio(a.lower(), b.lower())
    except ImportError:
        # Fallback: substring match
        a, b = a.lower(), b.lower()

# =======================
# App Creation & Configuration
# =======================
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
# Register blueprint for debug source url
app.register_blueprint(debug_source_url_bp)

# Register navigation context processor and blueprint
app.context_processor(nav_context_processor)
app.register_blueprint(nav_bp)

# Register admin_task blueprint
from admin_task.admin_routes import admin_task_bp
app.register_blueprint(admin_task_bp)


# Register book_a_class blueprint
app.register_blueprint(book_a_class_bp)

# Register debug_parser_instructions blueprint
app.register_blueprint(debug_parser_instructions_bp)

# Register upload_url blueprint
app.register_blueprint(upload_url_bp)

# Register recipe_book blueprint
app.register_blueprint(recipe_book_bp)

# Register recipe_suggest blueprint
from recipe_suggest.recipe_suggest import recipe_suggest_bp
app.register_blueprint(recipe_suggest_bp)

# Register debug_parser blueprint
from debug_parser import debug_parser_bp
app.register_blueprint(debug_parser_bp)

# Register the google_auth blueprint so /auth/callback is handled.
app.register_blueprint(google_auth_bp)

# Register the ingredients blueprint
app.register_blueprint(ingredients_bp)

# Register the program_help blueprint
from program_help.program_help import program_help_bp
app.register_blueprint(program_help_bp)

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    """Render custom 404 error page."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Render custom 500 error page."""
    return "An internal error occurred. Please try again later.", 500

# =======================
# Jinja2 Filters
# =======================

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    if value is None:
        return ''
    try:
        return value.strftime(format)
    except Exception:
        return str(value)

# =======================
# Test Routes
@app.template_filter('format_nz_week')
def format_nz_week(label):
    """Format NZ week label from yyyy-mm-dd to dd-mm-yyyy."""
    if not label or not isinstance(label, str):
        return ""
    import re
    match = re.match(r"(\d{4})-(\d{2})-(\d{2}) to (\d{4})-(\d{2})-(\d{2})", label)
    if match:
        start = f"{match.group(3)}-{match.group(2)}-{match.group(1)}"
        end = f"{match.group(6)}-{match.group(5)}-{match.group(4)}"
        return f"{start} to {end}"
    return label

# =======================
# Features: Recipe Book Routes
# =======================

from recipe_setup.inventory_routes import inventory_bp
# Register blueprints
app.register_blueprint(inventory_bp)

# --- Upload Details Page ---
@app.route('/upload_details/<int:recipe_id>')
@require_role('Admin')
def upload_details(recipe_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM recipes WHERE id = %s', (recipe_id,))
        recipe = c.fetchone()
    if not recipe:
        flash('Recipe not found.', 'error')
        return redirect(url_for('recipe_book.recbk'))
    return render_template('recipe_setup/upload_details.html', recipe=recipe)

# =======================
# Catering Blueprint Registration
# =======================
from catering.catering import catering_bp
app.register_blueprint(catering_bp)
# --- Delete flagged/test recipe from parser_test_recipes ---
@app.route('/parser_test_recipe/<int:parser_debug_id>/delete', methods=['POST'])
@require_role('Admin')
def delete_parser_test_recipe(parser_debug_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM parser_test_recipes WHERE id = %s', (parser_debug_id,))
        conn.commit()
    flash('Flagged/test recipe deleted.', 'success')
    return redirect(url_for('admin_task.admin_recipe_book_setup'))


# --- Recipe Index Draft/Test View ---
@app.route('/recipe_index/<int:recipe_id>')
@require_role('Admin')
def recipe_index_view(recipe_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM recipes WHERE id = %s', (recipe_id,))
        recipe = c.fetchone()
    return render_template('recipe_index_view.html', recipe=recipe)

# --- Flag/Unflag Parser Issue ---
@app.route('/flag_parser_issue/<int:recipe_id>', methods=['POST'])
@require_role('Admin')
def flag_parser_issue(recipe_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('UPDATE recipes SET parser_issue_flag = NOT COALESCE(parser_issue_flag, FALSE) WHERE id = %s', (recipe_id,))
        conn.commit()
    return redirect(url_for('recipe_index_view', recipe_id=recipe_id))


# --- Recipe Source Page ---

    steps_applied = []

    log.append(f"Fetching URL: {url}")

# --- Alias for /load_recipe_url to support form submissions from templates ---
@app.route('/load_recipe_url', methods=['POST'])
@require_role('Admin')
def load_recipe_url():
    print("[DEBUG] /load_recipe_url called")
    url = request.form.get('url') or request.form.get('recipe_url')
    print(f"[DEBUG] URL received: {url}")
    ingredients = []
    instructions = []
    if not url:
        print("[DEBUG] No URL provided, aborting.")
        return jsonify({'error': 'No URL provided.'}), 400
    url = request.form.get('url') or request.form.get('recipe_url')
    print(f"[DEBUG] URL after re-fetch: {url}")
    ingredients = []
    instructions = []
    extraction_warning = None
    title = url or ''
    serving_size = None
    # Defensive: always try to render the review page, never return JSON
    if not url or not (url.startswith('http://') or url.startswith('https://')):
        print("[DEBUG] Invalid or missing URL format.")
        extraction_warning = 'No or invalid URL provided. Please check the URL and try again.'
        recipe_data = {
            'title': title,
            'ingredients': ingredients,
            'instructions': instructions,
            'source_url': url,
            'serving_size': serving_size
        }
        # Store error in a temp file instead of session
        import uuid
        tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        raw_data_filename = f"raw_data_{uuid.uuid4().hex}.txt"
        raw_data_path = os.path.join(tmp_dir, raw_data_filename)
        with open(raw_data_path, 'w', encoding='utf-8') as f:
            f.write(f'Invalid or missing URL: {url}')
        session['raw_data_file'] = raw_data_filename
        return render_template(
            "review_recipe_url.html",
            recipe_data=recipe_data,
            extraction_warning=extraction_warning
        )
    global requests, BeautifulSoup
    if requests is None or BeautifulSoup is None:
        print("[DEBUG] Required libraries not installed.")
        extraction_warning = 'Required libraries (requests, BeautifulSoup) not installed.'
        recipe_data = {
            'title': title,
            'ingredients': ingredients,
            'instructions': instructions,
            'source_url': url,
            'serving_size': serving_size
        }
        # Store error in a temp file instead of session
        import uuid
        tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        raw_data_filename = f"raw_data_{uuid.uuid4().hex}.txt"
        raw_data_path = os.path.join(tmp_dir, raw_data_filename)
        with open(raw_data_path, 'w', encoding='utf-8') as f:
            f.write('Required libraries (requests, BeautifulSoup) not installed.')
        session['raw_data_file'] = raw_data_filename
        return render_template(
            "review_recipe_url.html",
            recipe_data=recipe_data,
            extraction_warning=extraction_warning
        )
    try:
        print(f"[DEBUG] About to fetch URL: {url}")
        resp = requests.get(url, timeout=10)
        print(f"[DEBUG] Fetched URL, status: {resp.status_code}")
        if resp.status_code != 200:
            extraction_warning = f'URL returned status code {resp.status_code}. Could not fetch recipe.'
            recipe_data = {
                'title': title,
                'ingredients': ingredients,
                'instructions': instructions,
                'source_url': url,
                'serving_size': serving_size
            }
            # Store response text in a temp file instead of session
            import uuid
            tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
            raw_data_filename = f"raw_data_{uuid.uuid4().hex}.txt"
            raw_data_path = os.path.join(tmp_dir, raw_data_filename)
            with open(raw_data_path, 'w', encoding='utf-8') as f:
                f.write(resp.text)
            session['raw_data_file'] = raw_data_filename
            return render_template(
                "review_recipe_url.html",
                recipe_data=recipe_data,
                extraction_warning=extraction_warning
            )
        html = resp.text
        print(f"[DEBUG] Successfully fetched HTML, length: {len(html)}")
    except Exception as e:
        print(f"[DEBUG] Exception fetching URL: {e}")
        extraction_warning = f'Failed to fetch URL: {str(e)}'
        recipe_data = {
            'title': title,
            'ingredients': ingredients,
            'instructions': instructions,
            'source_url': url,
            'serving_size': serving_size
        }
        # Store error in a temp file instead of session
        import uuid
        tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        raw_data_filename = f"raw_data_{uuid.uuid4().hex}.txt"
        raw_data_path = os.path.join(tmp_dir, raw_data_filename)
        with open(raw_data_path, 'w', encoding='utf-8') as f:
            f.write(f'Exception fetching URL: {str(e)}')
        session['raw_data_file'] = raw_data_filename
        return render_template(
            "review_recipe_url.html",
            recipe_data=recipe_data,
            extraction_warning=extraction_warning
        )

    # ...existing extraction logic for ingredients, instructions, etc. goes here...

    # Defensive: ensure a valid response is always returned
    recipe_data = {
        'title': title,
        'ingredients': ingredients,
        'instructions': instructions,
        'source_url': url,
        'serving_size': serving_size
    }
    # Store HTML in a temp file instead of session
    import uuid
    tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    raw_data_filename = f"raw_data_{uuid.uuid4().hex}.txt"
    raw_data_path = os.path.join(tmp_dir, raw_data_filename)
    with open(raw_data_path, 'w', encoding='utf-8') as f:
        f.write(html)
    session['raw_data_file'] = raw_data_filename

    # Immediately add to parser_test_recipes for debug index
    import datetime as dt
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            # Insert into parser_test_recipes (existing behavior)
            c.execute('''
                INSERT INTO parser_test_recipes (upload_source_type, upload_source_detail, uploaded_by, upload_date, notes, recipe_id, raw_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                'url',
                url,
                getattr(current_user, 'email', 'unknown'),
                dt.datetime.now(),
                'Loaded from URL',
                None,
                html
            ))
            # Also insert into parser_debug for debug index
            c.execute('''
                INSERT INTO parser_debug (recipe_id, raw_data, extracted_title, strategies, solution, created_at, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                None,  # recipe_id unknown at this stage
                html,
                url,  # Use URL as extracted_title placeholder
                '[{"result": "Loaded from URL"}]',
                '',
                dt.datetime.utcnow(),
                getattr(current_user, 'id', None)
            ))
            conn.commit()
    except Exception as e:
        print(f"[DEBUG] Could not insert into parser_test_recipes or parser_debug: {e}")

    # Remove raw_data if present before passing to template
    recipe_data_no_raw = dict(recipe_data)
    recipe_data_no_raw.pop('raw_data', None)
    if 'recipe_data' in locals():
        # Fallback: minimal blank review page
        return render_template(
            "review_recipe_url.html",
            recipe_data=recipe_data_no_raw,
            extraction_warning=extraction_warning if 'extraction_warning' in locals() else 'Unknown error occurred.'
        )

# --- Review Recipe URL Action Route ---
@app.route('/review_recipe_url_action', methods=['POST'])
@require_role('Admin')
def review_recipe_url_action():
    import json
    recipe_json = request.form.get('recipe_json')
    action = request.form.get('action')
    error_message = None
    try:
        recipe_data = json.loads(recipe_json) if recipe_json else {}
    except Exception as e:
        recipe_data = None
        error_message = f'Error parsing recipe data: {e}'

    if error_message or not recipe_data:
        # Show error on the review page, do not redirect
        # Try to recover original data for display if possible
        # If recipe_json is not valid JSON, try to show as much as possible
        try:
            # Try to load as Python dict (if single quotes were used)
            import ast
            recipe_data = ast.literal_eval(recipe_json)
        except Exception:
            recipe_data = {}
        return render_template(
            "review_recipe_url.html",
            recipe_data=recipe_data or {},
            extraction_warning=error_message
        )

    if action == 'confirm':
        # After confirming, fetch the latest parser_debug_id for this recipe (if exists)
        parser_debug_id = None
        try:
            with get_db_connection() as conn:
                c = conn.cursor()
                # Try to find the most recent parser_debug record for this recipe
                source_url = recipe_data.get('source_url') or recipe_data.get('title') or ''
                c.execute('SELECT id FROM parser_test_recipes WHERE upload_source_detail = %s ORDER BY id DESC LIMIT 1', (source_url,))
                test_recipe_row = c.fetchone()
                if test_recipe_row:
                    test_recipe_id = test_recipe_row['id']
                    c.execute('SELECT id FROM parser_debug WHERE recipe_id = %s ORDER BY id DESC LIMIT 1', (test_recipe_id,))
                    debug_row = c.fetchone()
                    if debug_row:
                        parser_debug_id = debug_row['id']
        except Exception as e:
            parser_debug_id = None
        if parser_debug_id:
            return render_template(
                "review_recipe_url.html",
                recipe_data=recipe_data or {},
                extraction_warning='Recipe confirmed and debug record loaded.',
                show_debug_prompt=True,
                parser_debug_id=parser_debug_id
            )
        else:
            return render_template(
                "review_recipe_url.html",
                recipe_data=recipe_data or {},
                extraction_warning='Recipe confirmed, but no debug record found.',
                show_debug_prompt=False
            )
    elif action == 'flag':
        # Insert recipe into parser_test_recipes for URL uploads: always use session['raw_data_file']
        parser_debug_id = None
        try:
            import datetime as dt
            source_url = recipe_data.get('source_url') or recipe_data.get('title') or ''
            # Sanitize the URL: remove duplicate protocols, strip whitespace
            source_url = source_url.strip()
            if source_url.startswith('http://http://'):
                source_url = source_url.replace('http://http://', 'http://', 1)
            elif source_url.startswith('https://https://'):
                source_url = source_url.replace('https://https://', 'https://', 1)
            elif source_url.startswith('http://https://'):
                source_url = source_url.replace('http://https://', 'https://', 1)
            elif source_url.startswith('https://http://'):
                source_url = source_url.replace('https://http://', 'http://', 1)
            # Read raw_data from temp file
            raw_data = ''
            error = None
            raw_data_filename = session.get('raw_data_file')
            if raw_data_filename:
                tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
                raw_data_path = os.path.join(tmp_dir, raw_data_filename)
                try:
                    with open(raw_data_path, 'r', encoding='utf-8') as f:
                        raw_data = f.read()
                except Exception as e:
                    error = f'Could not read raw_data file: {e}'
            else:
                error = 'No raw_data file found in session.'
            if error:
                error_message = f'Error extracting raw data for parser testing: {error}'
                return render_template(
                    "review_recipe_url.html",
                    recipe_data=recipe_data or {},
                    extraction_warning=error_message,
                    show_debug_prompt=False
                )
            with get_db_connection() as conn:
                c = conn.cursor()
                # Insert into parser_test_recipes and get test_recipe_id
                c.execute('''
                    INSERT INTO parser_test_recipes (upload_source_type, upload_source_detail, uploaded_by, upload_date, notes, recipe_id, raw_data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                ''', (
                    'url',
                    source_url,
                    getattr(current_user, 'email', 'unknown'),
                    dt.datetime.now(),
                    'Flagged for parser testing',
                    None,
                    raw_data
                ))
                test_recipe_id = c.fetchone()['id']
                # Insert into parser_debug and get parser_debug_id
                c.execute('''
                    INSERT INTO parser_debug (recipe_id, user_id, created_at, notes, solution)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                ''', (
                    test_recipe_id,
                    getattr(current_user, 'id', None),
                    dt.datetime.now(),
                    'Flagged for parser testing',
                    None
                ))
                parser_debug_id = c.fetchone()['id']
                conn.commit()
        except Exception as e:
            error_message = f'Error saving flagged recipe for parser testing: {e}'
            return render_template(
                "review_recipe_url.html",
                recipe_data=recipe_data or {},
                extraction_warning=error_message,
                show_debug_prompt=False
            )
        return render_template(
            "review_recipe_url.html",
            recipe_data=recipe_data if recipe_data else {},
            extraction_warning='Recipe flagged for manual review and stored for parser testing.',
            show_debug_prompt=True,
            parser_debug_id=parser_debug_id
        )
    else:
        error_message = 'Unknown action.'
        return render_template(
            "review_recipe_url.html",
            recipe_data=recipe_data or {},
            extraction_warning=error_message
        )



# =======================
# Flask-Login Manager Setup
# =======================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.anonymous_user = AnonymousUser

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'https://WHS-DTECH.pythonanywhere.com/auth/callback')

# Debug: Print loaded OAuth environment variables (remove after troubleshooting)
print('GOOGLE_CLIENT_ID:', repr(GOOGLE_CLIENT_ID))
print('GOOGLE_CLIENT_SECRET:', repr(GOOGLE_CLIENT_SECRET))
print('GOOGLE_REDIRECT_URI:', repr(GOOGLE_REDIRECT_URI))

# =======================
# New Shopping List (Rebuilt) Route
# =======================


# Register the ShopList blueprint after app is created
app.register_blueprint(shoplist_bp)

SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]


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

# Initialize database
def init_db():
    # You must manually migrate your schema to PostgreSQL. This function is now a placeholder.
    pass

@app.route('/')
def index():
    """Main page shows recipe book for everyone."""
    return redirect(url_for('recipe_book.recbk'))


# ============== Authentication Routes ==============

@app.route('/login')
def login():
    """Render login page."""
    if current_user.is_authenticated:
        return redirect(url_for('class_ingredients'))
    return render_template('login.html')


@app.route('/auth/google')
def auth_google():
    """Initiate Google OAuth flow."""
    if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
        flash('Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.')
        return redirect(url_for('login'))
    
    # Use Flow.from_client_config for direct configuration instead of file
    client_config = {
        'web': {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://accounts.google.com/o/oauth2/token',
            'redirect_uris': [GOOGLE_REDIRECT_URI]
        }
    }
    
    # Use the full callback URL to avoid mismatches
    redirect_uri = GOOGLE_REDIRECT_URI  # Use the configured URI from .env
    
    flow = Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri=redirect_uri)
    
    # Generate the authorization URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='select_account'
    )
    
    session['oauth_state'] = state
    session['redirect_uri'] = redirect_uri
    return redirect(authorization_url)


@app.route('/auth/callback')
def auth_callback():
    """Handle Google OAuth callback."""
    # Verify state for security
    state = session.get('oauth_state')
    redirect_uri = session.get('redirect_uri', GOOGLE_REDIRECT_URI)  # Use configured URI
    
    if not state:
        flash('OAuth state mismatch. Please try logging in again.')
        return redirect(url_for('login'))
    
    try:
        # Use the stored client config
        client_config = {
            'web': {
                'client_id': GOOGLE_CLIENT_ID,
                'client_secret': GOOGLE_CLIENT_SECRET,
                'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                'token_uri': 'https://accounts.google.com/o/oauth2/token',
                'redirect_uris': [redirect_uri]
            }
        }
        
        flow = Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri=redirect_uri, state=state)
        
        # Get the authorization code from the callback
        authorization_response = request.url.replace('http://', 'http://')  # Ensure consistent scheme
        flow.fetch_token(authorization_response=authorization_response)
        
        # Get user info
        credentials = flow.credentials
        user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        import requests as req_lib
        headers = {'Authorization': f'Bearer {credentials.token}'}
        response = req_lib.get(user_info_url, headers=headers)
        user_info = response.json()
        
        # Extract user data
        google_id = user_info.get('id')
        email = user_info.get('email')
        name = user_info.get('name', email.split('@')[0])
        
        # Get staff code from email lookup
        staff_code = get_staff_code_from_email(email)
        
        # Create user and store in session
        user = User(google_id, email, name, staff_code)
        session['user'] = {
            'google_id': google_id,
            'email': email,
            'name': name,
            'staff_code': staff_code,
            'role': user.role
        }
        # Store Google OAuth credentials for calendar integration
        session['google_creds'] = {
            'token': credentials.token,
            'refresh_token': getattr(credentials, 'refresh_token', None),
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        login_user(user, remember=True)
        flash(f'Welcome, {name}!', 'success')
        return redirect(url_for('recipe_book.recbk'))
    
    except Exception as e:
        flash(f'Authentication error: {str(e)}')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    """Log out the current user."""
    logout_user()
    # Remove temp raw_data file if present
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


# ============== End Authentication Routes ==============


def categorize_ingredient(ingredient_name):
    """Categorize ingredient by store section."""
    name_lower = ingredient_name.lower()
    
    # Produce
    produce = ['apple', 'banana', 'orange', 'lemon', 'lime', 'tomato', 'potato', 'onion', 'garlic', 
               'carrot', 'lettuce', 'spinach', 'cabbage', 'broccoli', 'cauliflower', 'pepper', 'capsicum',
               'cucumber', 'zucchini', 'mushroom', 'avocado', 'celery', 'ginger', 'herbs', 'parsley',
               'cilantro', 'basil', 'mint', 'thyme', 'rosemary', 'kale', 'chard', 'beetroot', 'pumpkin']
    
    # Dairy
    dairy = ['milk', 'cream', 'butter', 'cheese', 'yogurt', 'yoghurt', 'sour cream', 'feta', 'mozzarella',
             'parmesan', 'cheddar', 'brie', 'cottage cheese', 'ricotta', 'halloumi']
    
    # Meat & Seafood
    meat = ['chicken', 'beef', 'pork', 'lamb', 'turkey', 'bacon', 'sausage', 'mince', 'steak',
            'fish', 'salmon', 'tuna', 'prawns', 'shrimp', 'mussels', 'seafood']
    
    # Pantry/Dry Goods
    pantry = ['flour', 'sugar', 'rice', 'pasta', 'bread', 'cereal', 'oats', 'quinoa', 'couscous',
              'lentils', 'beans', 'chickpeas', 'oil', 'vinegar', 'sauce', 'stock', 'broth',
              'honey', 'jam', 'peanut butter', 'nuts', 'almonds', 'cashews', 'seeds', 'spice',
              'salt', 'pepper', 'cumin', 'paprika', 'cinnamon', 'vanilla', 'cocoa', 'chocolate',
              'baking powder', 'baking soda', 'yeast', 'cornstarch', 'cornflour']
    
    # Frozen
    frozen = ['frozen', 'ice cream', 'peas', 'corn', 'berries mixed']
    
    # Beverages
    beverages = ['juice', 'soda', 'water', 'tea', 'coffee', 'wine', 'beer']
    
    # Check categories
    for item in produce:
        if item in name_lower:
            return 'Produce'
    for item in dairy:
        if item in name_lower:
            return 'Dairy'
    for item in meat:
        if item in name_lower:
            return 'Meat & Seafood'
    for item in pantry:
        if item in name_lower:
            return 'Pantry'
    for item in frozen:
        if item in name_lower:
            return 'Frozen'
    for item in beverages:
        if item in name_lower:
            return 'Beverages'
    
    return 'Other'


@app.route('/api/update-recipe-tags/<int:recipe_id>', methods=['POST'])
@require_role('Admin', 'Teacher')
def update_recipe_tags(recipe_id):
    """Quick API to update recipe dietary tags, cuisine, and difficulty."""
    data = request.get_json()
    
    dietary_tags = data.get('dietary_tags', '')  # comma-separated
    cuisine = data.get('cuisine', '')
    difficulty = data.get('difficulty', '')
    
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''UPDATE recipes 
                    SET dietary_tags = %s, cuisine = %s, difficulty = %s
                    WHERE id = %s''',
                 (dietary_tags, cuisine, difficulty, recipe_id))
        conn.commit()
    return jsonify({'success': True, 'message': 'Tags updated'})

# --- Redirect old /class_ingredients route to new /book_a_class route ---
@app.route('/class_ingredients', methods=['GET', 'POST'])
def redirect_class_ingredients():
    return redirect(url_for('book_a_class.book_a_class'), code=301)


