# =======================
# DONT PUT NEW CODE HERE - put it in the appropriate section below!!!
# =======================

# =======================
# Imports (Standard, Third-party, Local)
# =======================

import os
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
from upload_URL import upload_url_bp
from recipe_book import recipe_book_bp


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

# Register upload_url blueprint
app.register_blueprint(upload_url_bp)

# Register recipe_book blueprint
app.register_blueprint(recipe_book_bp)

# Register recipe_suggest blueprint
from recipe_suggest.recipe_suggest import recipe_suggest_bp
app.register_blueprint(recipe_suggest_bp)

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
# Utility: Extract all visible text from a URL or PDF
# =======================
def extract_raw_text_from_url(url):
    global requests, BeautifulSoup, PyPDF2
    if requests is None:
        return None, 'Requests library not installed.'
    try:
        resp = requests.get(url, timeout=10)
    except Exception as e:
        return None, f'Failed to fetch URL: {e}'
    if resp.status_code != 200:
        return None, f'URL returned status code {resp.status_code}'
    content_type = resp.headers.get('Content-Type', '')
    if 'pdf' in content_type or url.lower().endswith('.pdf'):
        if not PyPDF2:
            return None, 'PyPDF2 not installed.'
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(resp.content))
            full_text = "\n".join([page.extract_text() or '' for page in pdf_reader.pages])
            return full_text, None
        except Exception as e:
            return None, f'PDF extraction failed: {e}'
    else:
        html = resp.text
        if BeautifulSoup is None:
            return html, None
        soup = BeautifulSoup(html, 'html.parser')
        texts = soup.stripped_strings
        visible_text = "\n".join(texts)
        return visible_text, None

# =======================
# Features: Recipe Book Routes
# =======================



# --- Delete flagged/test recipe from parser_test_recipes ---
@app.route('/parser_test_recipe/<int:test_recipe_id>/delete', methods=['POST'])
@require_role('Admin')
def delete_parser_test_recipe(test_recipe_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM parser_test_recipes WHERE id = %s', (test_recipe_id,))
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


# --- Title Extraction Strategies ---
def extract_title_candidates(raw_html):
    candidates = []
    best_guess = None
    import re
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        BeautifulSoup = None
    # 1. <title> tag
    title_tag = None
    if BeautifulSoup:
        soup = BeautifulSoup(raw_html, 'html.parser')
        title_tag = soup.title.string.strip() if soup.title and soup.title.string else None
    else:
        m = re.search(r'<title>(.*?)</title>', raw_html, re.I|re.S)
        title_tag = m.group(1).strip() if m else None
    candidates.append({'name': '<title> tag', 'value': title_tag or '', 'best': False})
    # 2. og:title meta
    og_title = None
    if BeautifulSoup and soup:
        og = soup.find('meta', property='og:title')
        og_title = og['content'].strip() if og and og.get('content') else None
    else:
        m = re.search(r'<meta[^>]+property=["\"]og:title["\"][^>]+content=["\"](.*?)["\"]', raw_html, re.I|re.S)
        og_title = m.group(1).strip() if m else None
    candidates.append({'name': 'og:title meta', 'value': og_title or '', 'best': False})
    # 3. First <h1>
    h1 = None
    if BeautifulSoup and soup:
        h1tag = soup.find('h1')
        h1 = h1tag.get_text(strip=True) if h1tag else None
    else:
        m = re.search(r'<h1[^>]*>(.*?)</h1>', raw_html, re.I|re.S)
        h1 = m.group(1).strip() if m else None
    candidates.append({'name': 'First <h1>', 'value': h1 or '', 'best': False})
    # 4. JSON-LD schema.org name
    jsonld_title = None
    if BeautifulSoup and soup:
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict) and 'name' in data:
                    jsonld_title = data['name']
                    break
                elif isinstance(data, list):
                    for entry in data:
                        if isinstance(entry, dict) and 'name' in entry:
                            jsonld_title = entry['name']
                            break
            except Exception:
                continue
    candidates.append({'name': 'schema.org/JSON-LD name', 'value': jsonld_title or '', 'best': False})
    # 5. Heuristic: First large/bold text (e.g., <b>, <strong>, <h2>)
    heuristic = None
    if BeautifulSoup and soup:
        for tag in soup.find_all(['h2', 'b', 'strong']):
            txt = tag.get_text(strip=True)
            if txt and len(txt) > 5:
                heuristic = txt
                break
    candidates.append({'name': 'Heuristic: first large/bold text', 'value': heuristic or '', 'best': False})
    # Pick best guess (first non-empty in priority order)
    for cand in candidates:
        if cand['value']:
            cand['best'] = True
            best_guess = cand['value']
            break
    return candidates, best_guess or ''



# --- Alias for /load_recipe_url to support form submissions from templates ---
@app.route('/load_recipe_url', methods=['POST'])
@require_role('Admin')
def load_recipe_url():
    url = request.form.get('url') or request.form.get('recipe_url')
    ingredients = []
    instructions = []
    if not url:
        return jsonify({'error': 'No URL provided.'}), 400
    url = request.form.get('url') or request.form.get('recipe_url')
    ingredients = []
    instructions = []
    extraction_warning = None
    title = url or ''
    serving_size = None
    # Defensive: always try to render the review page, never return JSON
    if not url or not (url.startswith('http://') or url.startswith('https://')):
        extraction_warning = 'No or invalid URL provided. Please check the URL and try again.'
        recipe_data = {
            'title': title,
            'ingredients': ingredients,
            'instructions': instructions,
            'source_url': url,
            'serving_size': serving_size
        }
        session['raw_data'] = f'Invalid or missing URL: {url}'
        return render_template(
            "review_recipe_url.html",
            recipe_data=recipe_data,
            extraction_warning=extraction_warning
        )
    global requests, BeautifulSoup
    if requests is None or BeautifulSoup is None:
        extraction_warning = 'Required libraries (requests, BeautifulSoup) not installed.'
        recipe_data = {
            'title': title,
            'ingredients': ingredients,
            'instructions': instructions,
            'source_url': url,
            'serving_size': serving_size
        }
        session['raw_data'] = 'Required libraries (requests, BeautifulSoup) not installed.'
        return render_template(
            "review_recipe_url.html",
            recipe_data=recipe_data,
            extraction_warning=extraction_warning
        )
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            extraction_warning = f'URL returned status code {resp.status_code}. Could not fetch recipe.'
            recipe_data = {
                'title': title,
                'ingredients': ingredients,
                'instructions': instructions,
                'source_url': url,
                'serving_size': serving_size
            }
            session['raw_data'] = resp.text
            return render_template(
                "review_recipe_url.html",
                recipe_data=recipe_data,
                extraction_warning=extraction_warning
            )
        html = resp.text
    except Exception as e:
        extraction_warning = f'Failed to fetch URL: {str(e)}'
        recipe_data = {
            'title': title,
            'ingredients': ingredients,
            'instructions': instructions,
            'source_url': url,
            'serving_size': serving_size
        }
        session['raw_data'] = f'Exception fetching URL: {str(e)}'
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
    session['raw_data'] = html
    # Remove raw_data if present before passing to template
    recipe_data_no_raw = dict(recipe_data)
    recipe_data_no_raw.pop('raw_data', None)
    if 'recipe_data' in locals():
        # Fallback: minimal blank review page
        return render_template(
            "review_recipe_url.html",
            recipe_data=recipe_data_no_raw,

            # --- Admin routes and logic have been moved to admin_task/routes.py ---
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
        # Here you would save the recipe to the database
        flash('Recipe confirmed and ready for saving (not yet implemented).', 'success')
        return redirect(url_for('admin_task.admin_recipe_book_setup'))
    elif action == 'flag':
        # Insert recipe into parser_test_recipes for URL uploads: always use session['raw_data']
        test_recipe_id = None
        try:
            import datetime as dt
            source_url = recipe_data.get('source_url') or recipe_data.get('title') or ''
            # Use the same extraction logic as debug_extract_text
            raw_data, error = extract_raw_text_from_url(source_url)
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
                conn.commit()
        except Exception as e:
            error_message = f'Error saving flagged recipe for parser testing: {e}'
            # Do NOT redirect, just show error on the review page and keep the user there
            return render_template(
                "review_recipe_url.html",
                recipe_data=recipe_data or {},
                extraction_warning=error_message,
                show_debug_prompt=False
            )
        # Always show Yes/No debug prompt and keep page open until user clicks a button
        return render_template(
            "review_recipe_url.html",
            recipe_data=recipe_data if recipe_data else {},
            extraction_warning='Recipe flagged for manual review and stored for parser testing.',
            show_debug_prompt=True,
            test_recipe_id=test_recipe_id
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
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('recipe_book.recbk'))


# ============== End Authentication Routes ==============





@app.route('/uploadclass', methods=['POST'])
@require_role('Admin')
def uploadclass():
    uploaded = request.files.get('csvfile')
    if not uploaded:
        flash('No class file uploaded')
        return redirect(url_for('admin'))

    # Normalize line endings
    file_content = uploaded.stream.read().decode('utf-8', errors='ignore')
    file_content = file_content.replace('\r\n', '\n').replace('\r', '\n')
    stream = io.StringIO(file_content)
    reader = csv.DictReader(stream)
    rows = []
    with get_db_connection() as conn:
        c = conn.cursor()
        for row in reader:
            # Map expected fields, allow flexible header names
            classcode = row.get('ClassCode') or row.get('classcode') or row.get('Class') or row.get('class')
            lineno = row.get('LineNo') or row.get('lineno') or row.get('Line')
            try:
                ln = int(lineno) if lineno not in (None, '') else None
            except ValueError:
                ln = None
            # Upsert for PostgreSQL: ON CONFLICT (ClassCode) DO UPDATE
            if not classcode or ln is None:
                skipped_rows = skipped_rows + 1 if 'skipped_rows' in locals() else 1
                continue
            c.execute('''
                INSERT INTO classes (ClassCode, LineNo, Misc1, RoomNo, CourseName, Misc2, Year, Dept, StaffCode, ClassSize, TotalSize, TimetableYear, Misc3)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (ClassCode, LineNo) DO UPDATE SET
                  Misc1=EXCLUDED.Misc1,
                  RoomNo=EXCLUDED.RoomNo,
                  CourseName=EXCLUDED.CourseName,
                  Misc2=EXCLUDED.Misc2,
                  Year=EXCLUDED.Year,
                  Dept=EXCLUDED.Dept,
                  StaffCode=EXCLUDED.StaffCode,
                  ClassSize=EXCLUDED.ClassSize,
                  TotalSize=EXCLUDED.TotalSize,
                  TimetableYear=EXCLUDED.TimetableYear,
                  Misc3=EXCLUDED.Misc3
            ''',
                (
                    classcode,
                    ln,
                    row.get('Misc1'),
                    row.get('RoomNo'),
                    row.get('CourseName'),
                    row.get('Misc2'),
                    row.get('Year'),
                    row.get('Dept'),
                    row.get('StaffCode'),
                    row.get('ClassSize'),
                    row.get('TotalSize'),
                    row.get('TimetableYear'),
                    row.get('Misc3'),
                ))
            rows.append(row)

    flash('Classes CSV processed')
    if 'skipped_rows' in locals():
        flash(f'Skipped {skipped_rows} row(s) with missing ClassCode or LineNo.')
    
    # Fetch suggestions for admin page
    suggestions = []
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT id, name, source, source_url, upload_method, uploaded_by, upload_date FROM recipes ORDER BY name')
            recipe_list = [dict(row) for row in c.fetchall()]
        return render_template('recipe_book_setup.html', recipe_list=recipe_list)
    except Exception:
        suggestions = []
    return render_template('admin.html', preview_data=rows, suggestions=suggestions)


@app.route('/upload', methods=['GET', 'POST'], endpoint='main_upload')
@require_role('Admin')
def upload():
    # GET request - show the upload form
    if request.method == 'GET':
        return render_template('upload_recipe.html')
    
    # POST request - handle form submission
    # Step 1: PDF upload, extract and show titles
    if 'pdfFile' in request.files:
        try:
            if not PyPDF2:
                return render_template('upload_result.html', recipes=[], pdf_filename=None, error='PyPDF2 not installed - cannot parse PDF files')
            pdf_file = request.files.get('pdfFile')
            if not pdf_file or pdf_file.filename == '':
                return render_template('upload_result.html', recipes=[], pdf_filename=None, error='No PDF file selected')
            # Save PDF to a temp file, store temp filename in session
            import uuid
            tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
            tmp_filename = f"pdf_{uuid.uuid4().hex}.pdf"
            tmp_path = os.path.join(tmp_dir, tmp_filename)
            pdf_bytes = pdf_file.read()
            with open(tmp_path, 'wb') as f:
                f.write(pdf_bytes)
            session['pdf_tmpfile'] = tmp_filename
            session['pdf_filename'] = pdf_file.filename
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            full_text = "\n".join([page.extract_text() or '' for page in pdf_reader.pages])
            # Extract titles only
            recipes_found = parse_recipes_from_text(full_text)
            titles = [r.get('name', '').strip() for r in recipes_found if isinstance(r, dict) and r.get('name')]
            session['detected_titles'] = titles
            return render_template('upload_result.html', recipes=[{'name': t} for t in titles], pdf_filename=pdf_file.filename, step='titles')
        except Exception as e:
            print(f"[ERROR] PDF upload failed: {e}")
            return render_template('upload_result.html', recipes=[], pdf_filename=None, error=f'PDF upload failed: {str(e)}')

    # Step 2: Confirmed titles, extract full details
    if request.form.get('step') == 'titles_confirmed':
        try:
            tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
            tmp_filename = session.get('pdf_tmpfile')
            pdf_filename = session.get('pdf_filename')
            selected_titles = request.form.getlist('selected_titles')
            if not tmp_filename or not selected_titles:
                return render_template('upload_result.html', recipes=[], pdf_filename=None, error='Session expired or no titles selected.')
            tmp_path = os.path.join(tmp_dir, tmp_filename)
            with open(tmp_path, 'rb') as f:
                pdf_bytes = f.read()
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            full_text = "\n".join([page.extract_text() or '' for page in pdf_reader.pages])
            # Extract all recipes, then filter for selected titles
            all_recipes = parse_recipes_from_text(full_text)
            recipes_to_show = []
            for r in all_recipes:
                if r.get('name') in selected_titles:
                    # Ensure all required keys exist for template safety
                    recipe = dict(r)
                    if 'method' not in recipe:
                        recipe['method'] = ''
                    if 'ingredients' not in recipe:
                        recipe['ingredients'] = []
                    if 'equipment' not in recipe:
                        recipe['equipment'] = []
                    if 'serving_size' not in recipe:
                        recipe['serving_size'] = ''
                    recipes_to_show.append(recipe)
            session['recipes_to_save'] = recipes_to_show
            return render_template('upload_result.html', recipes=recipes_to_show, pdf_filename=pdf_filename, step='details')
        except Exception as e:
            print(f"[ERROR] Full details extraction failed: {e}")
            return render_template('upload_result.html', recipes=[], pdf_filename=None, error=f'Full details extraction failed: {str(e)}')

    # Step 3: Confirmed full details, save to DB
    if request.form.get('step') == 'details_confirmed':
        recipes_to_save = session.get('recipes_to_save', [])
        pdf_filename = session.get('pdf_filename', 'manual_upload')
        tmp_filename = session.get('pdf_tmpfile')
        tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
        saved_count = 0
        skipped_count = 0
        error_details = []
        with get_db_connection() as conn:
            c = conn.cursor()
            try:
                c.execute("SELECT name FROM recipes")
                all_existing_names = [row['name'] for row in c.fetchall()]
                for recipe in recipes_to_save:
                    c.execute("SELECT id FROM recipes WHERE LOWER(name) = LOWER(%s)", (recipe['name'],))
                    existing = c.fetchone()
                    if existing:
                        skipped_count += 1
                        error_details.append(f'Duplicate: "{recipe["name"]}" already exists.')
                        continue
                    similar = []
                    for existing_name in all_existing_names:
                        if simple_similarity(recipe['name'], existing_name) >= 0.7:
                            similar.append(existing_name)
                    if similar:
                        error_details.append(f'Warning: "{recipe["name"]}" is similar to existing recipe(s): {", ".join(similar)}.')
                    try:
                        c.execute(
                            "INSERT INTO recipes (name, ingredients, instructions, serving_size, equipment) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                            (
                                recipe['name'],
                                json.dumps(recipe.get('ingredients', [])),
                                recipe.get('method', ''),
                                recipe.get('serving_size'),
                                json.dumps(recipe.get('equipment', []))
                            ),
                        )
                        recipe_id = c.fetchone()[0]
                        # Save raw extracted text to recipe_upload
                        c.execute(
                            "INSERT INTO recipe_upload (recipe_id, upload_source_type, upload_source_detail, uploaded_by, raw_text) VALUES (%s, %s, %s, %s)",
                            (recipe_id, 'pdf', pdf_filename, getattr(current_user, 'email', None), full_text)
                        )
                        saved_count += 1
                    except psycopg2.IntegrityError as e:
                        conn.rollback()
                        skipped_count += 1
                        error_details.append(f'DB IntegrityError for "{recipe["name"]}": {str(e)}')
            except Exception as e:
                conn.rollback()
                error_details.append(f'Bulk upload failed: {str(e)}')
                saved_count = 0
                skipped_count = len(recipes_to_save)
        # Clean up temp file and session
        if tmp_filename:
            tmp_path = os.path.join(tmp_dir, tmp_filename)
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception as e:
                print(f"[WARN] Could not remove temp PDF: {e}")
        session.pop('pdf_tmpfile', None)
        session.pop('pdf_filename', None)
        session.pop('detected_titles', None)
        session.pop('recipes_to_save', None)
        return render_template('upload_result.html', recipes=recipes_to_save, pdf_filename=pdf_filename, step='done', saved_count=saved_count, skipped_count=skipped_count, errors=error_details)

    # Step 1: If PDF file, parse and return detected recipes for preview/correction
    if 'pdfFile' in request.files:
        try:
            if not PyPDF2:
                return render_template('upload_result.html', recipes=[], pdf_filename=None, error='PyPDF2 not installed - cannot parse PDF files')
            pdf_file = request.files.get('pdfFile')
            if not pdf_file or pdf_file.filename == '':
                return render_template('upload_result.html', recipes=[], pdf_filename=None, error='No PDF file selected')
            # --- Page Range Support ---
            page_range_str = request.form.get('pageRange', '').strip()
            titles_only = request.form.get('titlesOnly', '').lower() == 'true'
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)
            def parse_page_range(page_range, max_page):
                if not page_range:
                    return list(range(max_page))
                pages = set()
                for part in page_range.split(','):
                    part = part.strip()
                    if '-' in part:
                        start, end = part.split('-')
                        try:
                            start = int(start) - 1
                            end = int(end) - 1
                        except ValueError:
                            continue
                        if start < 0 or end >= max_page or start > end:
                            continue
                        pages.update(range(start, end + 1))
                    else:
                        try:
                            idx = int(part) - 1
                        except ValueError:
                            continue
                        if 0 <= idx < max_page:
                            pages.add(idx)
                return sorted(pages)
            selected_pages = parse_page_range(page_range_str, total_pages)
            if not selected_pages:
                return render_template('upload_result.html', recipes=[], pdf_filename=pdf_file.filename, error='No valid pages selected. Please check your page range.')
            full_text = ""
            for i in selected_pages:
                page = pdf_reader.pages[i]
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    full_text += page_text + "\n"
                elif pytesseract and Image:
                    try:
                        xobj = page.get("/Resources", {}).get("/XObject")
                        if xobj:
                            for obj in xobj:
                                img_obj = xobj[obj]
                                if img_obj.get("/Subtype") == "/Image":
                                    data = img_obj.get_data()
                                    mode = "RGB" if img_obj.get("/ColorSpace") == "/DeviceRGB" else "L"
                                    img = Image.frombytes(mode, (img_obj["/Width"], img_obj["/Height"]), data)
                                    ocr_text = pytesseract.image_to_string(img)
                                    if ocr_text.strip():
                                        full_text += ocr_text + "\n"
                    except Exception as ocr_e:
                        print(f"[OCR ERROR] {ocr_e}")
            # --- Titles Only Mode ---
            if titles_only:
                try:
                    recipes_found = parse_recipes_from_text(full_text)
                    titles = [r.get('name', '').strip() for r in recipes_found if isinstance(r, dict) and r.get('name')]
                    return render_template('upload_result.html', recipes=[{'name': t} for t in titles], pdf_filename=pdf_file.filename, titles_only=True)
                except Exception as e:
                    print(f"[ERROR] Titles only extraction failed: {e}")
                    return render_template('upload_result.html', recipes=[], pdf_filename=pdf_file.filename, error=f'Titles only extraction failed: {str(e)}')
            # --- Full Extraction (default) ---
            try:
                recipes_found = parse_recipes_from_text(full_text)
                if not recipes_found:
                    # Log extraction failure
                    try:
                        analytics_path = os.path.join(os.path.dirname(__file__), 'extraction_analytics.log')
                        with open(analytics_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps({
                                'event': 'no_recipes_found',
                                'pdf_filename': pdf_file.filename,
                                'selected_pages': selected_pages,
                                'timestamp': datetime.datetime.utcnow().isoformat()
                            }) + '\n')
                    except Exception as log_e:
                        print(f'[ANALYTICS LOG ERROR] {log_e}')
                    return render_template('upload_result.html', recipes=[], pdf_filename=pdf_file.filename, error=f'No recipes found with Ingredients, Equipment, and Method sections in the selected PDF pages ({len(selected_pages)} pages scanned). Try using manual recipe upload instead.')
                # Log flagged recipes (e.g., those with warnings or similarity issues)
                try:
                    analytics_path = os.path.join(os.path.dirname(__file__), 'extraction_analytics.log')
                    for recipe in recipes_found:
                        if isinstance(recipe, dict) and (recipe.get('flagged', False) or recipe.get('warnings')):
                            with open(analytics_path, 'a', encoding='utf-8') as f:
                                f.write(json.dumps({
                                    'event': 'flagged_recipe',
                                    'pdf_filename': pdf_file.filename,
                                    'recipe': recipe,
                                    'timestamp': datetime.datetime.utcnow().isoformat()
                                }) + '\n')
                except Exception as log_e:
                    print(f'[ANALYTICS LOG ERROR] {log_e}')
                # Render confirmation page for preview/correction (do not save yet)
                return render_template('upload_result.html', recipes=recipes_found, pdf_filename=pdf_file.filename)
            except Exception as e:
                print(f"[ERROR] Full extraction failed: {e}")
                return render_template('upload_result.html', recipes=[], pdf_filename=pdf_file.filename, error=f'Full extraction failed: {str(e)}')
        except Exception as e:
            print(f"[ERROR] PDF upload failed: {e}")
            return render_template('upload_result.html', recipes=[], pdf_filename=None, error=f'PDF upload failed: {str(e)}')
    
    # Handle form data upload
    name = request.form.get('name', '').strip()
    instructions = request.form.get('instructions', '').strip()
    
    if not name or not instructions:
        flash('Recipe name and instructions required', 'error')
        return redirect(url_for('recipes_page'))

    # Validate serving_size
    serving_size_raw = request.form.get('serving_size', '').strip()
    try:
        serving_size = int(serving_size_raw) if serving_size_raw != '' else None
    except ValueError:
        flash('Invalid serving size', 'error')
        return redirect(url_for('recipes_page'))

    equipment_text = request.form.get('equipment', '')

    # Collect structured ingredients

    quantities = request.form.getlist('quantity[]')
    units = request.form.getlist('unit[]')
    ingredients_names = request.form.getlist('ingredient[]')

    # Check if ingredients were parsed
    if not quantities or len(quantities) == 0:
        flash('No ingredients found. Please click "Format Ingredients" button before saving.', 'error')
        return redirect(url_for('admin'))

    ingredients = []
    for q, u, ing in zip(quantities, units, ingredients_names):
        ingredients.append({"quantity": q, "unit": u, "ingredient": ing})

    # Convert equipment text into a list
    equipment_list = [item.strip() for item in equipment_text.split('\n') if item.strip()]

    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            
            # Check if recipe name already exists
            c.execute("SELECT id, name FROM recipes WHERE name = %s", (name,))
            existing = c.fetchone()
            if existing:
                flash(f'Recipe "{name}" already exists in the database. Please use a different name or edit the existing recipe.', 'warning')
                return redirect(url_for('admin'))
            
            c.execute(
                "INSERT INTO recipes (name, ingredients, instructions, serving_size, equipment) VALUES (%s, %s, %s, %s, %s)",
                (name, json.dumps(ingredients), instructions, serving_size, json.dumps(equipment_list)),
            )
            conn.commit()
            
        # Run cleaners after form insert
        flash(f'Recipe "{name}" saved successfully!', 'success')
    except psycopg2.IntegrityError as e:
        flash(f'Recipe "{name}" already exists in the database. Please use a different name.', 'error')
        return redirect(url_for('admin'))
    except Exception as e:
        flash(f'Error saving recipe: {str(e)}', 'error')
        return redirect(url_for('admin'))
        
    return redirect(url_for('recipes_page'))



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
@require_role('VP', 'DK')
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




@app.route('/booking/export/ical')
@require_role('Admin', 'Teacher', 'Technician')
def export_ical():
    """Export bookings as iCal format for Google Calendar import."""
    from datetime import datetime
    
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT 
                cb.date_required as date,
                cb.period,
                cb.staff_code,
                cb.class_code,
                r.name as recipe_name,
                cb.desired_servings as servings,
                t.first_name || ' ' || t.last_name as staff_name
            FROM class_bookings cb
            LEFT JOIN recipes r ON cb.recipe_id = r.id
            LEFT JOIN teachers t ON cb.staff_code = t.code
            ORDER BY cb.date_required, cb.period
        ''')
        bookings = c.fetchall()

    # Build iCal content
    ical = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//WHS Food Room//NONSGML v1.0//EN'
    ]
    for b in bookings:
        dt = b['date_required']
        summary = f"{b['class_code']} - {b['recipe_name']}"
        description = f"Servings: {b['servings']}"
        uid = str(uuid.uuid4())
        ical.append('BEGIN:VEVENT')
        ical.append(f"UID:{uid}")
        ical.append(f"DTSTAMP:{dt.strftime('%Y%m%dT000000Z')}")
        ical.append(f"DTSTART;VALUE=DATE:{dt.strftime('%Y%m%d')}")
        ical.append(f"DTEND;VALUE=DATE:{dt.strftime('%Y%m%d')}")
        ical.append(f"SUMMARY:{summary}")
        ical.append(f"DESCRIPTION:{description}")
        ical.append('END:VEVENT')
    ical.append('END:VCALENDAR')
    ical_str = '\r\n'.join(ical)
    response = app.response_class(
        ical_str,
        mimetype='text/calendar',
        headers={
            'Content-Disposition': 'attachment; filename=bookings.ics'
        }
    )
    return response




# --- API endpoint for scheduled bookings (for modal popup) ---
@app.route('/api/scheduled_bookings')
def api_scheduled_bookings():
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''
                SELECT cb.date_required, cb.period, cb.class_code, r.name as recipe_name, cb.desired_servings AS servings,
                       t.last_name, t.first_name, t.title, t.code as staff_code
                FROM class_bookings cb
                LEFT JOIN recipes r ON cb.recipe_id = r.id
                LEFT JOIN teachers t ON cb.staff_code = t.code
                ORDER BY cb.date_required, cb.period
            ''')
            bookings = []
            for row in c.fetchall():
                # Robust date handling
                date_val = row['date_required']
                if hasattr(date_val, 'strftime'):
                    date_str = date_val.strftime('%Y-%m-%d')
                elif isinstance(date_val, str):
                    date_str = date_val
                elif date_val is not None:
                    date_str = str(date_val)
                else:
                    date_str = ''
                staff_display = f"{row['staff_code']} - {row['last_name']}, {row['first_name']}"
                bookings.append({
                    'date_required': date_str,
                    'period': row['period'],
                    'class_code': row['class_code'],
                    'recipe_name': row['recipe_name'],
                    'servings': row['servings'],
                    'staff_display': staff_display
                })
        return jsonify({'success': True, 'bookings': bookings})
    except Exception as e:
        print('[ERROR] Failed to fetch scheduled bookings:', e)
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

# --- View Raw Upload Route ---


# --- Manual Instruction Editing Route ---
@app.route('/edit_instructions/<int:recipe_id>', methods=['GET', 'POST'])
@require_role(['Admin', 'Recipe Editor'])
def edit_instructions(recipe_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        if request.method == 'POST':
            new_instructions = request.form.get('instructions', '').strip()
            c.execute('UPDATE recipes SET instructions = %s WHERE id = %s', (new_instructions, recipe_id))
            conn.commit()
            flash('Instructions updated.', 'success')
            return redirect(url_for('recipe_details', recipe_id=recipe_id))
        # Robust recipe lookup: fallback to ILIKE if not found by id
        c.execute('SELECT * FROM recipes WHERE id = %s', (recipe_id,))
        recipe = c.fetchone()
        if not recipe:
            # Try partial/case-insensitive match by name if id lookup fails
            c.execute('SELECT * FROM recipes WHERE name ILIKE %s LIMIT 1', (f'%{recipe_id}%',))
            recipe = c.fetchone()
        if not recipe:
            flash('Recipe not found.', 'error')
            return redirect(url_for('recipe_book.recbk'))
        return render_template('edit_instructions.html', recipe=recipe)

# --- Redirect old /class_ingredients route to new /book_a_class route ---
@app.route('/class_ingredients', methods=['GET', 'POST'])
def redirect_class_ingredients():
    return redirect(url_for('book_a_class.book_a_class'), code=301)


