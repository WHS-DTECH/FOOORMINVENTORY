# admin_task/__init__.py

from flask import Blueprint

admin_task_bp = Blueprint('admin_task', __name__)

# Import all admin routes and utilities here
from . import routes
from flask import Blueprint, render_template, request
from auth import get_db_connection
import datetime

# --- Admin Recipe Suggestions Page ---
@app.route('/admin/recipe_suggestions')
@require_role('Admin')
def recipe_suggestions():
    # Placeholder: Render a simple template for now
    return render_template('admin_recipe_suggestions.html')


@app.route('/admin/update_recipe_source', methods=['POST'])
@require_role('Admin')
def update_recipe_source():
    """Update the source field for a recipe."""
    recipe_id = request.form.get('recipe_id')
    source = request.form.get('source', '').strip()
    if recipe_id:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('UPDATE recipes SET source = %s WHERE id = %s', (source, recipe_id))
            conn.commit()
        flash('Recipe source updated.', 'success')
    else:
        flash('No recipe ID provided.', 'error')
    return redirect(url_for('admin_recipe_book_setup'))


# --- Admin Recipe Book Setup Page Route ---
@app.route('/admin/recipe_book_setup')
@require_role('Admin')
def admin_recipe_book_setup():
    # Query recipes from the database
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT id, name, source, source_url, upload_method, uploaded_by, upload_date, serving_size FROM recipes ORDER BY name')
        recipe_list = [dict(row) for row in c.fetchall()]
        # Query flagged/test recipes for parser debug index
        c.execute('SELECT id, upload_source_detail, uploaded_by, upload_date, notes FROM parser_test_recipes ORDER BY upload_date DESC')
        parser_test_list = [dict(row) for row in c.fetchall()]
    return render_template('recipe_book_setup.html', recipe_list=recipe_list, parser_test_list=parser_test_list)
# --- Recipe detail page for /recipe/<id> ---
# (Moved below app creation to avoid NameError)

@app.route('/admin', methods=['GET', 'POST'])
@require_role('Admin')
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
                        c.execute('''
                            INSERT INTO teachers (code, last_name, first_name, title, email)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT (code) DO UPDATE SET
                                last_name=EXCLUDED.last_name,
                                first_name=EXCLUDED.first_name,
                                title=EXCLUDED.title,
                                email=EXCLUDED.email
                        ''', (code, last, first, title, email))
                    rows.append(row)
            except Exception as e:
                flash(f'Error processing CSV: {str(e)}')
                return redirect(url_for('admin'))
        preview_data = rows
        flash(f'Staff CSV processed: {len(rows)} rows')

    return render_template('admin.html', preview_data=preview_data, suggestions=suggestions)

@app.route('/admin/permissions', methods=['GET', 'POST'])
@require_role('Admin')
def admin_permissions():
    """Manage role-based permissions."""
    if request.method == 'POST':
        role = request.form.get('role')
        route = request.form.get('route')
        action = request.form.get('action')  # 'add' or 'remove'
        
        if role and route and action:
            import datetime
            now = datetime.datetime.utcnow()
            with get_db_connection() as conn:
                c = conn.cursor()
                if action == 'add':
                    c.execute('INSERT INTO role_permissions (role, route, last_modified) VALUES (%s, %s, %s) ON CONFLICT (role, route) DO UPDATE SET last_modified = %s', (role, route, now, now))
                    flash(f'Added {route} access for {role}', 'success')
                elif action == 'remove':
                    # Log the removal before deleting
                    c.execute('INSERT INTO role_permissions_log (role, route, action, timestamp) VALUES (%s, %s, %s, %s)', (role, route, 'remove', now))
                    c.execute('DELETE FROM role_permissions WHERE role = %s AND route = %s', (role, route))
                    flash(f'Removed {route} access for {role}', 'success')
        
        return redirect(url_for('admin_permissions'))
    
    @app.route('/admin/user_roles', methods=['GET', 'POST'])
@require_role('Admin')
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
    
    # Get all users with any assigned role (from teachers or user_roles)
    with get_db_connection() as conn:
        c = conn.cursor()
        # Get all teachers and their base role
        c.execute('SELECT email, code, first_name, last_name FROM teachers WHERE email IS NOT NULL ORDER BY last_name, first_name')
        teachers = [dict(row) for row in c.fetchall()]

        # Get all users with additional roles
        c.execute("SELECT email, STRING_AGG(role, ', ') as extra_roles FROM user_roles GROUP BY email")
        extra_roles_map = {row['email']: row['extra_roles'] for row in c.fetchall()}

        # Always show all teachers, even if they only have 'Public Access' as their role
        def norm_email(e):
            return e.strip().lower() if e else ''
        teacher_map = {norm_email(t['email']): t for t in teachers}
        all_emails = set(teacher_map.keys()) | set(norm_email(e) for e in extra_roles_map.keys())
        all_users = []
        for email in sorted(all_emails):
            teacher = teacher_map.get(email)
            base_role = None
            if teacher:
                code = teacher['code']
                if code == 'VP':
                    base_role = 'Admin'
                elif code == 'DK':
                    base_role = 'Teacher'
                elif code == 'MU':
                    base_role = 'Technician'
                else:
                    base_role = 'Public Access'
            else:
                base_role = 'Public Access'
            extra_roles = extra_roles_map.get(email, '')
            all_roles = [base_role] if base_role else []
            if extra_roles:
                for r in extra_roles.split(', '):
                    if r and r not in all_roles:
                        all_roles.append(r)
            # Always show all teachers, and any user with extra roles
            if teacher or extra_roles:
                orig_email = teacher['email'] if teacher else next((e for e in extra_roles_map.keys() if norm_email(e) == email), email)
                all_users.append({'email': orig_email, 'all_roles': ', '.join(all_roles)})

    roles = ['Admin', 'Teacher', 'Technician', 'Public Access']
    return render_template('admin_user_roles.html', all_users=all_users, teachers=teachers, roles=roles)

    @app.route('/admin/clean_recipes', methods=['POST'])

@require_role('Admin')
def clean_recipes_route():
    """Clean recipe database - remove junk and duplicates."""
    try:
        from clean_recipes import remove_junk_recipes, remove_duplicate_recipes, fix_recipe_names
        with get_db_connection() as conn:
            junk_deleted = remove_junk_recipes(conn)
            dupes_deleted = remove_duplicate_recipes(conn)
            names_fixed = fix_recipe_names(conn)
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM recipes')
            total = c.fetchone()[0]
            message = f'Database cleaned! Removed {len(junk_deleted)} junk entries, {len(dupes_deleted)} duplicates, and fixed {len(names_fixed)} recipe names. Total recipes: {total}'
            flash(message, 'success')
        return redirect(url_for('admin_recipe_book_setup'))
    except Exception as e:
        flash(f'Error cleaning database: {str(e)}', 'error')
        return redirect(url_for('admin_recipe_book_setup'))

@app.route('/staff')
@require_role('Admin')
def staff():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT code, last_name, first_name, title, email FROM teachers ORDER BY last_name, first_name')
        rows = [dict(r) for r in c.fetchall()]
    return render_template('staff.html', rows=rows)


@app.route('/classes')
@require_role('Admin')
def classes_page():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM classes ORDER BY ClassCode, LineNo')
        rows = [dict(r) for r in c.fetchall()]
    return render_template('classes.html', rows=rows)

