
# ...existing code...

# --- Recipe detail page for /recipe/<id> ---
# (Moved below app creation to avoid NameError)

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import os
import re
# ...existing imports...

# Create Flask app and set secret key
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

# Register Jinja2 filter after app creation and all imports
@app.template_filter('format_nz_week')
def format_nz_week(label):
    # Expects label in format yyyy-mm-dd to yyyy-mm-dd
    match = re.match(r"(\d{4})-(\d{2})-(\d{2}) to (\d{4})-(\d{2})-(\d{2})", label)
    if match:
        start = f"{match.group(3)}-{match.group(2)}-{match.group(1)}"
        end = f"{match.group(6)}-{match.group(5)}-{match.group(4)}"
        return f"{start} to {end}"
    return label
from flask_login import LoginManager, login_user, logout_user, current_user
from google_auth_oauthlib.flow import Flow
import psycopg2
import psycopg2.extras
import json
import csv
import io
import re
import os
import datetime
from dotenv import load_dotenv
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
from recipe_parser import parse_recipes_from_text, format_recipe, parse_ingredient_line
from auth import User, get_staff_code_from_email, require_login, require_role, public_with_auth


# PostgreSQL connection string from environment variable
POSTGRES_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(POSTGRES_URL, cursor_factory=psycopg2.extras.RealDictCursor)


# Load environment variables
load_dotenv()

# Allow OAuth over HTTP for local development (DO NOT use in production)
# Only enable in development, not production
if os.getenv('FLASK_ENV') == 'development':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

## ...already created above...

# Google Calendar integration for Shopping List
@app.route('/shoplist/add_to_gcal', methods=['POST'])
@require_login
def add_shoplist_to_gcal():
    try:
        # Get current week's bookings (reuse logic from shoplist route)
        from datetime import datetime, timedelta
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        friday = monday + timedelta(days=4)
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT date_required, period, class_code, recipe_name, servings FROM class_bookings cb
                         LEFT JOIN recipes r ON cb.recipe_id = r.id
                         WHERE date_required >= %s AND date_required <= %s
                         ORDER BY date_required, period''', (monday.date(), friday.date()))
            bookings = c.fetchall()

        # Google Calendar API setup
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        # You must have user's credentials in session or DB
        creds_data = session.get('google_creds')
        if not creds_data:
            return jsonify({'error': 'Google authentication required. Please log in with Google.'}), 401
        creds = Credentials.from_authorized_user_info(creds_data)
        service = build('calendar', 'v3', credentials=creds)

        calendar_id = 'primary'
        created = 0
        for b in bookings:
            event = {
                'summary': f"{b['class_code']} - {b['recipe_name']}",
                'description': f"Servings: {b['servings']}",
                'start': {
                    'date': str(b['date_required'])
                },
                'end': {
                    'date': str(b['date_required'])
                },
            }
            service.events().insert(calendarId=calendar_id, body=event).execute()
            created += 1
        return jsonify({'success': True, 'created': created})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500
## ...existing imports already above...


# PostgreSQL connection string from environment variable
POSTGRES_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(POSTGRES_URL, cursor_factory=psycopg2.extras.RealDictCursor)


# Load environment variables
load_dotenv()

# Allow OAuth over HTTP for local development (DO NOT use in production)
# Only enable in development, not production
if os.getenv('FLASK_ENV') == 'development':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

## ...already created above...

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.anonymous_user = lambda: type('AnonymousUser', (), {'is_authenticated': False})()

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'https://WHS-DTECH.pythonanywhere.com/auth/callback')

# Debug: Print loaded OAuth environment variables (remove after troubleshooting)
print('GOOGLE_CLIENT_ID:', repr(GOOGLE_CLIENT_ID))
print('GOOGLE_CLIENT_SECRET:', repr(GOOGLE_CLIENT_SECRET))
print('GOOGLE_REDIRECT_URI:', repr(GOOGLE_REDIRECT_URI))

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
    return redirect(url_for('recbk'))


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
        
        login_user(user, remember=True)
        flash(f'Welcome, {name}!', 'success')
        
        return redirect(url_for('recbk'))
    
    except Exception as e:
        flash(f'Authentication error: {str(e)}')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    """Log out the current user."""
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('recbk'))


# ============== End Authentication Routes ==============


@app.route('/admin', methods=['GET', 'POST'])
@require_role('VP')
def admin():
    # Get recipe suggestions for display
    suggestions = []
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT id, recipe_name, recipe_url, reason, suggested_by_name, 
                        suggested_by_email, created_at, status 
                        FROM recipe_suggestions 
                        ORDER BY created_at DESC''')
            suggestions = c.fetchall()
    except Exception:
        suggestions = []
    
    preview_data = None
    if request.method == 'POST':
        # staff CSV upload
        uploaded = request.files.get('staff_csv')
        if not uploaded:
            flash('No file uploaded')
            return redirect(url_for('admin'))

        # Read and normalize file content
        file_content = uploaded.stream.read().decode('utf-8', errors='ignore')
        # Normalize line endings
        file_content = file_content.replace('\r\n', '\n').replace('\r', '\n')
        stream = io.StringIO(file_content)
        reader = csv.DictReader(stream)
        rows = []
        with get_db_connection() as conn:
            c = conn.cursor()
            try:
                for row in reader:
                    code = row.get('Code') or row.get('code') or row.get('StaffCode') or row.get('staffcode')
                    last = row.get('Last Name') or row.get('last_name') or row.get('Last') or row.get('last')
                    first = row.get('First Name') or row.get('first_name') or row.get('First') or row.get('first')
                    title = row.get('Title') or row.get('title')
                    email = row.get('Email (School)') or row.get('email') or row.get('Email')
                    if code and last and first:
                        c.execute('INSERT OR IGNORE INTO teachers (code, last_name, first_name, title, email) VALUES (?, ?, ?, ?, ?)',
                                  (code, last, first, title, email))
                    rows.append(row)
            except Exception as e:
                flash(f'Error processing CSV: {str(e)}')
                return redirect(url_for('admin'))
        preview_data = rows
        flash(f'Staff CSV processed: {len(rows)} rows')

    return render_template('admin.html', preview_data=preview_data, suggestions=suggestions)


@app.route('/uploadclass', methods=['POST'])
@require_role('VP')
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
            # Insert or replace to update existing
            c.execute('INSERT OR REPLACE INTO classes (ClassCode, LineNo, Misc1, RoomNo, CourseName, Misc2, Year, Dept, StaffCode, ClassSize, TotalSize, TimetableYear, Misc3) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
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
    
    return render_template('admin.html', preview_data=rows, suggestions=suggestions)


@app.route('/admin/permissions', methods=['GET', 'POST'])
@require_role('VP')
def admin_permissions():
    """Manage role-based permissions."""
    if request.method == 'POST':
        role = request.form.get('role')
        route = request.form.get('route')
        action = request.form.get('action')  # 'add' or 'remove'
        
        if role and route and action:
            with get_db_connection() as conn:
                c = conn.cursor()
                if action == 'add':
                    c.execute('INSERT OR IGNORE INTO role_permissions (role, route) VALUES (?, ?)', (role, route))
                    flash(f'Added {route} access for {role}', 'success')
                elif action == 'remove':
                    c.execute('DELETE FROM role_permissions WHERE role = ? AND route = ?', (role, route))
                    flash(f'Removed {route} access for {role}', 'success')
        
        return redirect(url_for('admin_permissions'))
    
    # Get current permissions
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT role, route FROM role_permissions ORDER BY role, route')
        permissions = {}
        for row in c.fetchall():
            role = row['role']
            route = row['route']
            if role not in permissions:
                permissions[role] = []
            permissions[role].append(route)
    
    # Available routes
    routes = ['recipes', 'recbk', 'class_ingredients', 'booking', 'shoplist', 'admin']
    roles = ['VP', 'DK', 'MU', 'public']
    
    return render_template('admin_permissions.html', permissions=permissions, routes=routes, roles=roles)


@app.route('/admin/user_roles', methods=['GET', 'POST'])
@require_role('VP')
def admin_user_roles():
    """Manage additional user roles."""
    if request.method == 'POST':
        email = request.form.get('email')
        role = request.form.get('role')
        action = request.form.get('action')  # 'add' or 'remove'
        
        if email and role and action:
            with get_db_connection() as conn:
                c = conn.cursor()
                if action == 'add':
                    try:
                        c.execute('INSERT INTO user_roles (email, role) VALUES (%s, %s)', (email, role))
                        flash(f'Added role {role} to {email}', 'success')
                    except psycopg2.IntegrityError:
                        flash(f'{email} already has role {role}', 'warning')
                elif action == 'remove':
                    c.execute('DELETE FROM user_roles WHERE email = %s AND role = %s', (email, role))
                    flash(f'Removed role {role} from {email}', 'success')
        
        return redirect(url_for('admin_user_roles'))
    
    # Get all users with additional roles
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT email, STRING_AGG(role, ', ') as roles
            FROM user_roles
            GROUP BY email
            ORDER BY email
        ''')
        users_with_roles = [dict(row) for row in c.fetchall()]
        
        # Get all teachers for the dropdown
        c.execute('SELECT email, code, first_name, last_name FROM teachers WHERE email IS NOT NULL ORDER BY last_name, first_name')
        teachers = [dict(row) for row in c.fetchall()]
    
    roles = ['VP', 'DK', 'MU', 'public']
    
    return render_template('admin_user_roles.html', users_with_roles=users_with_roles, teachers=teachers, roles=roles)


@app.route('/admin/clean_recipes', methods=['POST'])

@require_role('VP')
def clean_recipes_route():
    """Clean recipe database - remove junk and duplicates."""
    try:
        from clean_recipes import remove_junk_recipes, remove_duplicate_recipes, fix_recipe_names
        
        with get_db_connection() as conn:
            # Run all cleaning operations
            junk_deleted = remove_junk_recipes(conn)
            dupes_deleted = remove_duplicate_recipes(conn)
            names_fixed = fix_recipe_names(conn)
            
            # Get final count
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM recipes')
            total = c.fetchone()[0]
            
            message = f'Database cleaned! Removed {len(junk_deleted)} junk entries, {len(dupes_deleted)} duplicates, and fixed {len(names_fixed)} recipe names. Total recipes: {total}'
            flash(message, 'success')
    except Exception as e:
        flash(f'Error cleaning database: {str(e)}', 'error')
    
    return redirect(url_for('admin'))


@app.route('/staff')
@require_role('VP')
def staff():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT code, last_name, first_name, title, email FROM teachers ORDER BY last_name, first_name')
        rows = [dict(r) for r in c.fetchall()]
    return render_template('staff.html', rows=rows)


@app.route('/classes')
@require_role('VP')
def classes_page():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM classes ORDER BY ClassCode, LineNo')
        rows = [dict(r) for r in c.fetchall()]
    return render_template('classes.html', rows=rows)


@app.route('/class_ingredients', methods=['GET', 'POST'])
@require_role('VP', 'DK')
def class_ingredients():
    # Provide staff codes, class codes, and recipes for selection on the page
    # Can be called via GET (blank form) or POST (from booking calendar with pre-populated data)
    
    # Extract booking data from POST request if present
    staff_code = request.form.get('staff_code') if request.method == 'POST' else None
    class_code = request.form.get('class_code') if request.method == 'POST' else None
    date_required = request.form.get('date_required') if request.method == 'POST' else None
    period = request.form.get('period') if request.method == 'POST' else None
    
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # Get most used staff (top 5 by booking count)
        c.execute('''SELECT staff_code, COUNT(*) as booking_count FROM class_bookings 
                    GROUP BY staff_code ORDER BY booking_count DESC LIMIT 5''')
        most_used_staff_codes = [r['staff_code'] for r in c.fetchall()]
        
        # Get all staff
        c.execute('SELECT code, last_name, first_name, title FROM teachers ORDER BY last_name, first_name')
        all_staff = [dict(r) for r in c.fetchall()]
        
        # Sort staff: most used first, then rest alphabetically
        most_used_staff = [s for s in all_staff if s['code'] in most_used_staff_codes]
        other_staff = [s for s in all_staff if s['code'] not in most_used_staff_codes]
        most_used_staff.sort(key=lambda x: most_used_staff_codes.index(x['code']))
        staff = most_used_staff + other_staff
        
        # If no pre-selected staff from booking, try to match current user's name to a staff member
        if not staff_code and current_user.is_authenticated:
            user_name_parts = current_user.name.split()
            if len(user_name_parts) >= 2:
                # Try to match first name and last name
                user_first = user_name_parts[0]
                user_last = user_name_parts[-1]
                for s in staff:
                    if (s['first_name'].lower() == user_first.lower() and 
                        s['last_name'].lower() == user_last.lower()):
                        staff_code = s['code']
                        break
        
        # Get most used classes (top 5 by booking count)
        c.execute('''SELECT class_code, COUNT(*) as booking_count FROM class_bookings 
                    GROUP BY class_code ORDER BY booking_count DESC LIMIT 5''')
        most_used_class_codes = [r['class_code'] for r in c.fetchall()]
        
        # Get all classes
        c.execute('SELECT DISTINCT ClassCode FROM classes ORDER BY ClassCode')
        all_classes = [r['classcode'] for r in c.fetchall() if r['classcode']]
        
        # Sort classes: most used first, then rest alphabetically
        most_used_classes = [c for c in all_classes if c in most_used_class_codes]
        other_classes = [c for c in all_classes if c not in most_used_class_codes]
        most_used_classes.sort(key=lambda x: most_used_class_codes.index(x))
        classes = most_used_classes + other_classes
        
        # Get recipes
        c.execute('SELECT id, name, ingredients, serving_size FROM recipes ORDER BY LOWER(name)')
        rows = c.fetchall()
        
        # If called from booking, get the booking's recipe and servings
        booking_recipe_id = None
        booking_servings = None
        if request.method == 'POST' and staff_code and class_code and date_required and period:
            c.execute('''SELECT recipe_id, desired_servings FROM class_bookings 
                        WHERE staff_code = %s AND class_code = %s AND date_required = %s AND period = %s''',
                     (staff_code, class_code, date_required, period))
            booking = c.fetchone()
            if booking:
                booking_recipe_id = booking['recipe_id']
                booking_servings = booking['desired_servings']

    recipes = []
    for r in rows:
        try:
            ings = json.loads(r['ingredients'] or '[]')
        except Exception:
            ings = []
        recipes.append({'id': r['id'], 'name': r['name'], 'ingredients': ings, 'serving_size': r['serving_size']})

    # Get existing bookings for display (ordered by date descending, most recent first)
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT cb.id, cb.staff_code, cb.class_code, cb.date_required, cb.period, 
                   cb.recipe_id, cb.desired_servings, r.name as recipe_name,
                   t.first_name, t.last_name
            FROM class_bookings cb
            LEFT JOIN recipes r ON cb.recipe_id = r.id
            LEFT JOIN teachers t ON cb.staff_code = t.code
            ORDER BY cb.date_required DESC, cb.period ASC
        ''')
        bookings = [dict(row) for row in c.fetchall()]

    return render_template('class_ingred.html', staff=staff, classes=classes, recipes=recipes,
                          bookings=bookings,
                          most_used_staff_count=len(most_used_staff), most_used_classes_count=len(most_used_classes),
                          pre_staff_code=staff_code, pre_class_code=class_code, 
                          pre_date_required=date_required, pre_period=period,
                          pre_recipe_id=booking_recipe_id, pre_servings=booking_servings)


@app.route('/class_ingredients/download', methods=['POST'])
@require_role('VP', 'DK')
def class_ingredients_download():
    # Expects JSON: {recipe_id, desired_servings}
    data = request.get_json() or {}
    recipe_id = data.get('recipe_id')
    desired = int(data.get('desired_servings') or 24)
    if not recipe_id:
        return jsonify({'error':'recipe_id required'}), 400

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT id, name, ingredients, serving_size FROM recipes WHERE id = %s', (recipe_id,))
        row = c.fetchone()
        if not row:
            return jsonify({'error':'recipe not found'}), 404
        try:
            ings = json.loads(row['ingredients'] or '[]')
        except Exception:
            ings = []

    # Build CSV
    import io, csv
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(['ingredient','quantity','unit','notes'])
    orig_serv = int(row['serving_size']) if row['serving_size'] else 1
    for it in ings:
        name = ''
        qty = ''
        unit = ''
        if isinstance(it, dict):
            name = it.get('ingredient') or ''
            qty = it.get('quantity') or ''
            unit = it.get('unit') or ''
            # calculate scaled
            try:
                qn = float(str(qty))
                per_single = qn / orig_serv
                scaled = per_single * desired
                qty = round(scaled,2)
            except Exception:
                qty = ''
        else:
            name = str(it)
        writer.writerow([name, qty, unit, ''])

    csv_data = buf.getvalue()
    return (csv_data, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename="shopping_{recipe_id}.csv"'
    })


@app.route('/class_ingredients/save', methods=['POST'])
@require_role('VP', 'DK')
def class_ingredients_save():
    # Save a booking to `class_bookings` (INSERT or UPDATE)
    try:
        data = request.get_json() or {}
        print("[DEBUG] /class_ingredients/save data:", data)
        booking_id = data.get('booking_id')  # If provided, update existing booking
        staff_code = data.get('staff')
        class_code = data.get('classcode')
        date_required = data.get('date')
        period = data.get('period')
        recipe_id = data.get('recipe_id')
        desired = int(data.get('desired_servings') or 24)

        # Validation
        missing = []
        for field, value in [('staff', staff_code), ('classcode', class_code), ('date', date_required), ('period', period), ('recipe_id', recipe_id)]:
            if value in [None, '']:
                missing.append(field)
        if missing:
            print(f"[ERROR] Missing required fields: {missing}")
            return jsonify({'error': f'Missing required fields: {missing}'}), 400

        with get_db_connection() as conn:
            c = conn.cursor()
            if booking_id:
                # Update existing booking
                c.execute('''UPDATE class_bookings 
                            SET staff_code=%s, class_code=%s, date_required=%s, period=%s, recipe_id=%s, desired_servings=%s
                            WHERE id=%s''',
                         (staff_code, class_code, date_required, period, recipe_id, desired, booking_id))
                conn.commit()
            else:
                # Insert new booking
                c.execute('INSERT INTO class_bookings (staff_code, class_code, date_required, period, recipe_id, desired_servings) VALUES (%s, %s, %s, %s, %s, %s)',
                          (staff_code, class_code, date_required, period, recipe_id, desired))
                conn.commit()
                booking_id = c.lastrowid
        return jsonify({'success': True, 'booking_id': booking_id})
    except Exception as e:
        print(f"[ERROR] Exception in /class_ingredients/save: {e}")
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 400

@app.route('/class_ingredients/delete/<int:booking_id>', methods=['POST'])
@require_role('VP', 'DK')
def class_ingredients_delete(booking_id):
    # Delete a booking
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM class_bookings WHERE id = %s', (booking_id,))
        conn.commit()
    return jsonify({'success': True})

@app.route('/upload', methods=['GET', 'POST'])
@require_role('VP')
def upload():
    # GET request - show the upload form
    if request.method == 'GET':
        return render_template('upload_recipe.html')
    
    # POST request - handle form submission
    # Check if PDF file is being uploaded
    if 'pdfFile' in request.files:
        if not PyPDF2:
            flash('PyPDF2 not installed - cannot parse PDF files', 'error')
            return redirect(url_for('recipes_page'))
        
        pdf_file = request.files.get('pdfFile')
        if not pdf_file or pdf_file.filename == '':
            flash('No PDF file selected', 'error')
            return redirect(url_for('recipes_page'))
        
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            # Extract ALL text from entire PDF first (recipes span multiple pages)
            print(f"DEBUG: PDF has {len(pdf_reader.pages)} pages")  # Debug
            full_text = ""
            for page in pdf_reader.pages:
                full_text += page.extract_text() + "\n"

            # Parse the complete text for recipes
            recipes_found = parse_recipes_from_text(full_text)
            print(f"DEBUG: Total recipes found: {len(recipes_found)}")  # Debug
            if not recipes_found:
                flash(f'No recipes found with Ingredients, Equipment, and Method sections in the PDF ({len(pdf_reader.pages)} pages scanned). Try using manual recipe upload instead.', 'warning')
                return redirect(url_for('recipes_page'))

            # Save recipes to database (skip duplicates)
            saved_count = 0
            skipped_count = 0
            with get_db_connection() as conn:
                c = conn.cursor()
                for recipe in recipes_found:
                    try:
                        c.execute(
                            "INSERT INTO recipes (name, ingredients, instructions, serving_size, equipment) VALUES (%s, %s, %s, %s, %s)",
                            (
                                recipe['name'],
                                json.dumps(recipe.get('ingredients', [])),
                                recipe.get('method', ''),
                                recipe.get('serving_size'),
                                json.dumps(recipe.get('equipment', []))
                            ),
                        )
                        saved_count += 1
                    except psycopg2.IntegrityError:
                        conn.rollback()  # Rollback the failed insert
                        skipped_count += 1
                # Commit after all inserts
                conn.commit()

            # Run cleaners after insert (temporarily disabled for debugging)
            # dup_deleted = remove_duplicate_recipes()
            # nonfood_deleted = remove_nonfood_recipes()
            dup_deleted = []
            nonfood_deleted = []

            message = f'Saved {saved_count} new recipe(s).'
            if skipped_count > 0:
                message += f' Skipped {skipped_count} duplicate(s).'
            # if len(dup_deleted) > 0 or len(nonfood_deleted) > 0:
            #     message += f' Cleaned {len(dup_deleted)} duplicates and {len(nonfood_deleted)} non-food entries.'

            flash(message, 'success')
            return redirect(url_for('recipes_page'))
        except Exception as e:
            # Rollback if a transaction is open
            try:
                if 'conn' in locals():
                    conn.rollback()
            except Exception:
                pass
            flash(f'Error uploading PDF: {str(e)}', 'error')
            return redirect(url_for('recipes_page'))
    
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
            c.execute("SELECT id, name FROM recipes WHERE name = ?", (name,))
            existing = c.fetchone()
            if existing:
                flash(f'Recipe "{name}" already exists in the database. Please use a different name or edit the existing recipe.', 'warning')
                return redirect(url_for('admin'))
            
            c.execute(
                "INSERT INTO recipes (name, ingredients, instructions, serving_size, equipment) VALUES (?, ?, ?, ?, ?)",
                (name, json.dumps(ingredients), instructions, serving_size, json.dumps(equipment_list)),
            )
            conn.commit()
            
        # Run cleaners after form insert
        dup_deleted = remove_duplicate_recipes()
        nonfood_deleted = remove_nonfood_recipes()

        flash(f'Recipe "{name}" saved successfully! Cleaned {len(dup_deleted)} duplicates and {len(nonfood_deleted)} non-food entries.', 'success')
    except psycopg2.IntegrityError as e:
        flash(f'Recipe "{name}" already exists in the database. Please use a different name.', 'error')
        return redirect(url_for('admin'))
    except Exception as e:
        flash(f'Error saving recipe: {str(e)}', 'error')
        return redirect(url_for('admin'))
        
    return redirect(url_for('recipes_page'))

@app.route('/shoplist')
@require_role('VP', 'DK', 'MU')
def shoplist():
    from datetime import datetime, timedelta
    
    # Get week offset from query parameter (0 = current week, -1 = last week, 1 = next week, etc.)
    week_offset = request.args.get('week', type=int)
    
    # If no week specified, default intelligently based on day of week
    if week_offset is None:
        today = datetime.now()
        # If it's Saturday (5) or Sunday (6), default to next week instead of current
        if today.weekday() >= 5:
            week_offset = 1
        else:
            week_offset = 0
    
    # Calculate the target week (Monday to Friday)
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())  # Get Monday of current week
    monday = monday + timedelta(weeks=week_offset)  # Adjust by week offset

    # Build dates list for the week (Monday to Friday)
    dates = []
    for i in range(5):
        day = monday + timedelta(days=i)
        dates.append({
            'date': day.strftime('%Y-%m-%d'),
            'label': day.strftime('%A %d %b'),
            'day_name': day.strftime('%A'),
            'nz_date': day.strftime('%d/%m/%Y')
        })

    with get_db_connection() as conn:
        c = conn.cursor()
        # Get all bookings for this week
        week_start = dates[0]['date']
        week_end = dates[4]['date']
        c.execute('''SELECT cb.id, cb.staff_code, cb.class_code, cb.date_required, cb.period, 
                           cb.recipe_id, cb.desired_servings, r.name as recipe_name, t.last_name, t.first_name
                    FROM class_bookings cb
                    LEFT JOIN recipes r ON cb.recipe_id = r.id
                    LEFT JOIN teachers t ON cb.staff_code = t.code
                    WHERE cb.date_required BETWEEN %s AND %s
                    ORDER BY cb.date_required, cb.period''',
                   (week_start, week_end))
        bookings_list = [dict(r) for r in c.fetchall()]
        # Get all recipes for ingredient lookup
        c.execute('SELECT id, name, ingredients, serving_size FROM recipes ORDER BY name')
        all_recipes = {}
        for r in c.fetchall():
            try:
                ings = json.loads(r['ingredients'] or '[]')
            except Exception:
                ings = []
            all_recipes[r['id']] = {'name': r['name'], 'ingredients': ings, 'serving_size': r['serving_size']}

    # Organize bookings into a grid structure
    grid = {}
    for date_obj in dates:
        for period in range(1, 6):
            grid[f"{date_obj['date']}_P{period}"] = None

    for booking in bookings_list:
        # Ensure date_required is a string in YYYY-MM-DD format
        date_str = str(booking['date_required'])
        if hasattr(booking['date_required'], 'strftime'):
            date_str = booking['date_required'].strftime('%Y-%m-%d')
        key = f"{date_str}_P{booking['period']}"
        if key in grid:
            grid[key] = booking

    # Calculate previous and next week offsets and week label
    prev_week = week_offset - 1 if week_offset is not None else -1
    next_week = week_offset + 1 if week_offset is not None else 1
    week_label = f"{dates[0]['date']} to {dates[-1]['date']}"

    return render_template('shoplist.html', dates=dates, grid=grid, bookings=bookings_list, recipes=all_recipes, 
                          week_offset=week_offset, prev_week=prev_week, next_week=next_week, week_label=week_label)


@app.route('/api/generate-shopping-list', methods=['POST'])
@require_role('VP', 'DK', 'MU')
def generate_shopping_list():
    """Auto-generate shopping list from selected booking IDs."""
    data = request.get_json()
    booking_ids = data.get('booking_ids', [])
    
    if not booking_ids:
        return jsonify({'error': 'No bookings selected'}), 400
    
    with get_db_connection() as conn:
        c = conn.cursor()
        # Get all bookings with their recipes
        placeholders = ','.join(['%s'] * len(booking_ids))
        c.execute(f'''
            SELECT 
                cb.id,
                cb.recipe_id,
                cb.desired_servings,
                cb.date_required,
                cb.period,
                cb.class_code,
                r.name as recipe_name,
                r.ingredients,
                r.serving_size,
                t.first_name || ' ' || t.last_name as teacher_name
            FROM class_bookings cb
            LEFT JOIN recipes r ON cb.recipe_id = r.id
            LEFT JOIN teachers t ON cb.staff_code = t.code
            WHERE cb.id IN ({placeholders})
        ''', booking_ids)
        bookings = [dict(row) for row in c.fetchall()]
    
    # Aggregate ingredients
    ingredient_map = {}  # {normalized_name: {qty, unit, original_name}}
    
    for booking in bookings:
        if not booking['ingredients']:
            continue
        
        try:
            ingredients = json.loads(booking['ingredients'])
        except:
            continue
        
        recipe_servings = booking['serving_size'] or 1
        desired_servings = booking['desired_servings'] or recipe_servings
        scale_factor = desired_servings / recipe_servings if recipe_servings > 0 else 1
        
        for ing in ingredients:
            if isinstance(ing, dict):
                name = ing.get('name', ing.get('item', ''))
                qty = ing.get('qty', ing.get('quantity', 0))
                unit = ing.get('unit', '')
            elif isinstance(ing, str):
                # Parse string format
                parts = ing.split()
                qty = 0
                unit = ''
                name = ing
                if len(parts) >= 2:
                    try:
                        qty = float(parts[0])
                        unit = parts[1]
                        name = ' '.join(parts[2:]) if len(parts) > 2 else parts[1]
                    except:
                        pass
            else:
                continue
            
            if not name:
                continue
            
            # Normalize name for aggregation
            normalized = name.lower().strip()
            
            # Scale quantity
            scaled_qty = (float(qty) if qty else 0) * scale_factor
            
            if normalized in ingredient_map:
                # Add to existing
                if unit == ingredient_map[normalized]['unit']:
                    ingredient_map[normalized]['qty'] += scaled_qty
                else:
                    # Different units - keep separate
                    key = f"{normalized}_{unit}"
                    if key in ingredient_map:
                        ingredient_map[key]['qty'] += scaled_qty
                    else:
                        ingredient_map[key] = {
                            'qty': scaled_qty,
                            'unit': unit,
                            'name': name
                        }
            else:
                ingredient_map[normalized] = {
                    'qty': scaled_qty,
                    'unit': unit,
                    'name': name
                }
    
    # Convert to list and sort
    shopping_list = []
    for key, data in ingredient_map.items():
        shopping_list.append({
            'name': data['name'],
            'quantity': round(data['qty'], 2) if data['qty'] else '',
            'unit': data['unit']
        })
    
    shopping_list.sort(key=lambda x: x['name'].lower())
    
    return jsonify({
        'items': shopping_list,
        'total_count': len(shopping_list),
        'bookings_processed': len(bookings)
    })


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


@app.route('/api/shopping-list/toggle-item', methods=['POST'])
@require_role('VP', 'DK', 'MU')
def toggle_shopping_item():
    """Toggle 'already have' status for a shopping list item."""
    data = request.get_json()
    week_start = data.get('week_start')
    ingredient_name = data.get('ingredient_name')
    quantity = data.get('quantity', 0)
    unit = data.get('unit', '')
    
    if not week_start or not ingredient_name:
        return jsonify({'error': 'Missing required fields'}), 400
    
    with get_db_connection() as conn:
        c = conn.cursor()
        # Check if item exists
        c.execute('SELECT id, already_have FROM shopping_list_items WHERE week_start = %s AND ingredient_name = %s',
                  (week_start, ingredient_name))
        row = c.fetchone()
        if row:
            # Toggle status
            new_status = 0 if row['already_have'] else 1
            c.execute('UPDATE shopping_list_items SET already_have = %s WHERE id = %s', (new_status, row['id']))
        else:
            # Create new item with already_have = 1
            category = categorize_ingredient(ingredient_name)
            c.execute('''INSERT INTO shopping_list_items 
                        (week_start, ingredient_name, quantity, unit, category, already_have)
                        VALUES (%s, %s, %s, %s, %s, 1)''',
                      (week_start, ingredient_name, quantity, unit, category))
            new_status = 1
        conn.commit()
    
    return jsonify({'success': True, 'already_have': new_status})


@app.route('/api/shopping-list/get-status', methods=['POST'])
@require_role('VP', 'DK', 'MU')
def get_shopping_status():
    """Get 'already have' status for items in a week."""
    data = request.get_json()
    week_start = data.get('week_start')
    
    if not week_start:
        return jsonify({'error': 'Missing week_start'}), 400
    
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT ingredient_name, already_have FROM shopping_list_items WHERE week_start = %s AND already_have = 1',
                  (week_start,))
        items = {row['ingredient_name']: row['already_have'] for row in c.fetchall()}
    
    return jsonify({'items': items})


@app.route('/api/shopping-list/save', methods=['POST'])
@require_role('VP', 'DK', 'MU')
def save_shopping_list():
    """Save a shopping list for reuse."""
    data = request.get_json()
    list_name = data.get('list_name', '').strip()
    week_label = data.get('week_label', '')
    items = data.get('items', [])
    
    if not list_name or not items:
        return jsonify({'error': 'Missing list name or items'}), 400
    
    user_email = current_user.email if current_user.is_authenticated else 'unknown'
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO saved_shopping_lists (list_name, week_label, items, created_by)
                        VALUES (%s, %s, %s, %s) RETURNING id''',
                    (list_name, week_label, json.dumps(items), user_email))
        list_id = c.fetchone()['id']
        conn.commit()
    return jsonify({'success': True, 'list_id': list_id})


@app.route('/api/shopping-list/saved', methods=['GET'])
@require_role('VP', 'DK', 'MU')
def get_saved_lists():
    """Get all saved shopping lists."""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT id, list_name, week_label, created_at FROM saved_shopping_lists ORDER BY created_at DESC')
        lists = [dict(row) for row in c.fetchall()]
    
    return jsonify({'lists': lists})


@app.route('/api/shopping-list/load/<int:list_id>', methods=['GET'])
@require_role('VP', 'DK', 'MU')
def load_saved_list(list_id):
    """Load a saved shopping list."""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM saved_shopping_lists WHERE id = %s', (list_id,))
        row = c.fetchone()
        if not row:
            return jsonify({'error': 'List not found'}), 404
        list_data = dict(row)
        list_data['items'] = json.loads(list_data['items'])
    return jsonify(list_data)






@app.route('/suggest_recipe', methods=['POST'])
def suggest_recipe_modal():
    """Handle AJAX recipe suggestion submissions from modal and return JSON."""
    try:
        recipe_name = request.form.get('recipe_name', '').strip()
        recipe_url = request.form.get('recipe_url', '').strip()
        reason = request.form.get('reason', '').strip()
        suggested_by_name = request.form.get('suggested_by_name', '').strip()
        suggested_by_email = request.form.get('suggested_by_email', '').strip()

        if not recipe_name or not suggested_by_name or not suggested_by_email:
            return jsonify({'success': False, 'message': 'Recipe name, your name, and email are required.'})

        # Save suggestion to the database
        try:
            with get_db_connection() as conn:
                c = conn.cursor()
                sql = '''INSERT INTO recipe_suggestions (recipe_name, recipe_url, reason, suggested_by_name, suggested_by_email, created_at, status)
                       VALUES (%s, %s, %s, %s, %s, NOW(), %s)'''
                params = (recipe_name, recipe_url, reason, suggested_by_name, suggested_by_email, 'pending')
                c.execute(sql, params)
                conn.commit()
        except Exception as db_error:
            print(f"[ERROR] Failed to save suggestion to DB (modal): {db_error}")
            import traceback; traceback.print_exc()
            return jsonify({'success': False, 'message': 'There was an error saving your suggestion. Please try again or contact the VP directly.'})

        # Optionally send email (can be added here if needed)
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error in suggest_recipe_modal: {e}")
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'message': 'There was an error submitting your suggestion. Please try again or contact the VP directly.'})

# Legacy route for admin/recipes page (kept for compatibility)
@app.route('/recipes/suggest', methods=['POST'])
@require_login
def suggest_recipe():
    """Handle recipe suggestion submissions and email to VP"""
    try:
        recipe_name = request.form.get('recipe_name', '').strip()
        recipe_url = request.form.get('recipe_url', '').strip()
        reason = request.form.get('reason', '').strip()

        if not recipe_name:
            flash('Recipe name is required.', 'error')
            return redirect(url_for('recipes_page'))

        # Set recipient email directly (Vanessa Pringle)
        vp_email = 'vanessapringle@westlandhigh.school.nz'

        # Get current user info safely
        user_name = current_user.name if hasattr(current_user, 'name') else 'Unknown User'
        user_email = current_user.email if hasattr(current_user, 'email') else 'No email'

        # Define subject and body for the email
        subject = f"Recipe Suggestion: {recipe_name}"
        body = f"Recipe Name: {recipe_name}\nURL: {recipe_url}\nReason: {reason}\nSuggested by: {user_name} ({user_email})"

        # Save suggestion to the database (only once)
        try:
            with get_db_connection() as conn:
                c = conn.cursor()
                sql = '''INSERT INTO recipe_suggestions (recipe_name, recipe_url, reason, suggested_by_name, suggested_by_email, created_at, status)
                       VALUES (%s, %s, %s, %s, %s, NOW(), %s)'''
                params = (recipe_name, recipe_url, reason, user_name, user_email, 'pending')
                print("[DEBUG] About to execute SQL for recipe suggestion:")
                print("[DEBUG] SQL:", sql)
                print("[DEBUG] Params:", params)
                try:
                    c.execute(sql, params)
                    conn.commit()
                    print("[DEBUG] Insert committed successfully.")
                except Exception as exec_error:
                    print(f"[ERROR] Exception during SQL execute: {exec_error}")
                    import traceback; traceback.print_exc()
                    flash('There was an error saving your suggestion (SQL error). Please try again or contact the VP directly.', 'error')
                    return redirect(url_for('recipes_page'))
        except Exception as db_error:
            print(f"[ERROR] Failed to save suggestion to DB (outer): {db_error}")
            import traceback; traceback.print_exc()
            flash('There was an error saving your suggestion (DB error). Please try again or contact the VP directly.', 'error')
            return redirect(url_for('recipes_page'))

        # Only send email after successful DB insert
        email_sent = False
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_username = os.getenv('SMTP_USERNAME')
            smtp_password = os.getenv('SMTP_PASSWORD')
            smtp_from_email = os.getenv('SMTP_FROM_EMAIL', smtp_username)
            if smtp_username and smtp_password:
                msg = MIMEMultipart()
                msg['From'] = smtp_from_email or 'Food Room System <noreply@whsdtech.com>'
                msg['To'] = vp_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
                server.quit()
                email_sent = True
                print(f"Email sent successfully to {vp_email}")
            else:
                print("SMTP credentials not configured - email not sent")
                print(f"RECIPE SUGGESTION EMAIL:\nTo: {vp_email}\nSubject: {subject}\n\n{body}")
        except Exception as email_error:
            print(f"Failed to send email: {email_error}")
            print(f"RECIPE SUGGESTION EMAIL (not sent):\nTo: {vp_email}\nSubject: {subject}\n\n{body}")

        if email_sent:
            flash(f'Thank you! Your suggestion for "{recipe_name}" has been emailed to the VP and saved to the database.', 'success')
        else:
            flash(f'Thank you! Your suggestion for "{recipe_name}" has been saved. The VP will review it in the Admin panel.', 'success')

    except Exception as e:
        print(f"Error in suggest_recipe: {e}")
        import traceback
        traceback.print_exc()
        flash('There was an error submitting your suggestion. Please try again or contact the VP directly.', 'error')

    return redirect(url_for('recipes_page'))


@app.route('/recbk')
def recbk():
    q = request.args.get('q', '').strip()
    with get_db_connection() as conn:
        c = conn.cursor()
        if q:
            term = f"%{q}%"
            c.execute(
                "SELECT id, name, ingredients, instructions, serving_size, equipment, dietary_tags, cuisine, difficulty FROM recipes "
                "WHERE name ILIKE %s OR ingredients ILIKE %s "
                "ORDER BY LOWER(name)",
                (term, term),
            )
        else:
            c.execute(
                "SELECT id, name, ingredients, instructions, serving_size, equipment, dietary_tags, cuisine, difficulty FROM recipes "
                "ORDER BY LOWER(name)"
            )
        rows = [dict(r) for r in c.fetchall()]

    # Decode JSON fields for template
    for r in rows:
        try:
            r['ingredients'] = json.loads(r.get('ingredients') or '[]')
        except Exception:
            r['ingredients'] = []
        try:
            r['equipment'] = json.loads(r.get('equipment') or '[]')
        except Exception:
            r['equipment'] = []
        try:
            r['dietary_tags_list'] = json.loads(r.get('dietary_tags') or '[]')
        except Exception:
            r['dietary_tags_list'] = []

    # Get user's favorites if logged in
    favorites = []
    if current_user.is_authenticated:
        try:
            with get_db_connection() as conn:
                c = conn.cursor()
                c.execute('SELECT recipe_id FROM recipe_favorites WHERE user_email = %s', (current_user.email,))
                favorites = [row[0] for row in c.fetchall()]
        except Exception:
            # Table doesn't exist yet - run setup_database.py to create it
            favorites = []

    return render_template('recbk.html', rows=rows, q=q, favorites=favorites)


@app.route('/recipe/favorite/<int:recipe_id>', methods=['POST'])
@require_login
def add_favorite(recipe_id):
    """Add a recipe to user's favorites"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            # Use ON CONFLICT DO NOTHING for PostgreSQL
            c.execute('INSERT INTO recipe_favorites (user_email, recipe_id) VALUES (%s, %s) ON CONFLICT DO NOTHING',
                     (current_user.email, recipe_id))
            conn.commit()
        return jsonify({'success': True, 'message': 'Added to favorites'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


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
@require_role('VP', 'DK', 'MU')
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


@app.route('/shoplist/export/ical')
def export_shoplist_ical():
    """Export shopping list bookings as iCal format for Google Calendar import."""
    from datetime import datetime, timedelta
    import uuid
    # Get current week's bookings
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    friday = monday + timedelta(days=4)
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''SELECT date_required, period, class_code, recipe_name, servings FROM class_bookings cb
                     LEFT JOIN recipes r ON cb.recipe_id = r.id
                     WHERE date_required >= %s AND date_required <= %s
                     ORDER BY date_required, period''', (monday.date(), friday.date()))
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
            'Content-Disposition': 'attachment; filename=shoplist.ics'
        }
    )
    return response
