
# admin_task/routes.py
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from auth import require_role, get_db_connection
from flask_login import current_user
import os, csv, datetime, json, io
from . import admin_task_bp

# --- Admin Permissions Page ---
@admin_task_bp.route('/admin/permissions', methods=['GET', 'POST'])
@require_role('Admin')
def admin_permissions():
    roles = ['Admin', 'Teacher', 'Technician', 'Public Access']
    routes = ['recipes', 'recbk', 'class_ingredients', 'booking', 'shoplist', 'admin', 'recipe_book_setup', 'recipe_editor']
    permissions = {role: {route: False for route in routes} for role in roles}
    if request.method == 'POST':
        # Handle new role creation
        if request.form.get('add_role') == '1':
            new_role = request.form.get('new_role', '').strip()
            if new_role and new_role not in roles:
                roles.append(new_role)
                with get_db_connection() as conn:
                    c = conn.cursor()
                    for route in routes:
                        # Default: no access
                        c.execute('INSERT INTO role_permissions (role, route, has_access) VALUES (%s, %s, %s)', (new_role, route, False))
                    conn.commit()
                flash(f'Role "{new_role}" added successfully.')
            else:
                flash('Role name is empty or already exists.', 'error')
        else:
            # Build new permissions from form data
            new_permissions = {role: {route: False for route in routes} for role in roles}
            for role in roles:
                for route in routes:
                    key = f'perm_{role}_{route}'
                    if request.form.get(key) == '1':
                        new_permissions[role][route] = True
            # Update DB
            with get_db_connection() as conn:
                c = conn.cursor()
                for role in roles:
                    for route in routes:
                        c.execute('UPDATE role_permissions SET has_access = %s WHERE role = %s AND route = %s', (new_permissions[role][route], role, route))
                conn.commit()
            flash('Permissions updated successfully.')
            permissions = new_permissions
    else:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT role, route, has_access FROM role_permissions')
            for row in c.fetchall():
                role = row['role']
                route = row['route']
                has_access = row['has_access']
                if role in permissions and route in permissions[role]:
                    permissions[role][route] = has_access
    return render_template('admin_task/admin_permissions.html', permissions=permissions, routes=routes, roles=roles)

# --- Admin User Roles Page ---
@admin_task_bp.route('/admin/user_roles')
@require_role('Admin')
def admin_user_roles():
    users = []
    with get_db_connection() as conn:
        c = conn.cursor()
        # Get all staff emails from teachers table
        c.execute('SELECT email FROM teachers WHERE email IS NOT NULL')
        staff_emails = [row['email'].strip().lower() for row in c.fetchall()]
        # Get all user roles
        c.execute('SELECT email, role FROM user_roles')
        user_roles = {}
        for row in c.fetchall():
            email = row['email'].strip().lower()
            role = row['role']
            if email not in user_roles:
                user_roles[email] = []
            user_roles[email].append(role)
        # Build user list for template
        for email in staff_emails:
            roles = user_roles.get(email, ['Public Access'])
            users.append({'email': email, 'roles': roles})
    return render_template('admin_task/admin_user_roles.html', users=users)

# --- Recipe Book Setup Page ---
@admin_task_bp.route('/admin/recipe_book_setup')
@require_role('Admin')
def admin_recipe_book_setup():
    recipe_list = []
    parser_debugs = []
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            # Fetch recipes for Recipe Index
            c.execute('SELECT id, name, source, source_url, upload_method, uploaded_by, upload_date, serving_size FROM recipes ORDER BY name')
            recipe_list = [dict(row) for row in c.fetchall()]
            # Fetch parser debug/index data (match actual columns)
            c.execute('SELECT id, recipe_id, raw_data, extracted_title, strategies, solution FROM parser_debug ORDER BY id DESC')
            parser_debugs = [dict(row) for row in c.fetchall()]
    except Exception as e:
        print(f"Error fetching data for recipe_book_setup: {e}")
    return render_template('recipe_setup/recipe_book_setup.html', recipe_list=recipe_list, parser_debugs=parser_debugs)

# --- Admin Utility: Fix Public Roles ---
@admin_task_bp.route('/admin/fix_public_roles')
@require_role('Admin')
def fix_public_roles():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT DISTINCT email FROM teachers WHERE email IS NOT NULL')
        teacher_emails = {row['email'].strip().lower() for row in c.fetchall()}
        c.execute('SELECT DISTINCT email FROM user_roles')
        user_roles_emails = {row['email'].strip().lower() for row in c.fetchall()}
        all_emails = teacher_emails | user_roles_emails
        missing_public = []
        for email in all_emails:
            c.execute('SELECT 1 FROM user_roles WHERE email = %s AND role = %s', (email, 'Public Access'))
            if not c.fetchone():
                missing_public.append(email)
        for email in missing_public:
            c.execute('INSERT INTO user_roles (email, role) VALUES (%s, %s)', (email, 'Public Access'))
        conn.commit()
    return f"Added 'Public Access' role for {len(missing_public)} users: {', '.join(missing_public)}"

# --- Admin Main Page ---
@admin_task_bp.route('/admin', methods=['GET', 'POST'])
@require_role('Admin')
def admin():
    suggestions = []
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT id, recipe_name, recipe_url, reason, suggested_by_name, suggested_by_email, created_at, status FROM recipe_suggestions ORDER BY created_at DESC''')
            suggestions = c.fetchall()
    except Exception:
        suggestions = []
    preview_data = None
    if request.method == 'POST':
        uploaded = request.files.get('staff_csv')
        if not uploaded:
            flash('No file uploaded')
            return redirect(url_for('admin_task.admin'))
        file_content = uploaded.stream.read().decode('utf-8', errors='ignore')
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
                        c.execute('''INSERT INTO teachers (code, last_name, first_name, title, email) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (code) DO UPDATE SET last_name=EXCLUDED.last_name, first_name=EXCLUDED.first_name, title=EXCLUDED.title, email=EXCLUDED.email''', (code, last, first, title, email))
                    rows.append(row)
            except Exception as e:
                flash(f'Error processing CSV: {str(e)}')
                return redirect(url_for('admin_task.admin'))
        preview_data = rows
        flash(f'Staff CSV processed: {len(rows)} rows')
    return render_template('admin_task/admin.html', preview_data=preview_data, suggestions=suggestions)

# --- Upload Class CSV ---
@admin_task_bp.route('/uploadclass', methods=['POST'])
@require_role('Admin')
def uploadclass():
    uploaded = request.files.get('csvfile')
    if not uploaded:
        flash('No class file uploaded')
        return redirect(url_for('admin_task.admin'))
    file_content = uploaded.stream.read().decode('utf-8', errors='ignore')
    file_content = file_content.replace('\r\n', '\n').replace('\r', '\n')
    stream = io.StringIO(file_content)
    reader = csv.DictReader(stream)
    rows = []
    with get_db_connection() as conn:
        c = conn.cursor()
        for row in reader:
            classcode = row.get('ClassCode') or row.get('classcode') or row.get('Class') or row.get('class')
            lineno = row.get('LineNo') or row.get('lineno') or row.get('Line')
            try:
                ln = int(lineno) if lineno not in (None, '') else None
            except ValueError:
                ln = None
            if not classcode or ln is None:
                skipped_rows = skipped_rows + 1 if 'skipped_rows' in locals() else 1
                continue
            c.execute('''INSERT INTO classes (ClassCode, LineNo, Misc1, RoomNo, CourseName, Misc2, Year, Dept, StaffCode, ClassSize, TotalSize, TimetableYear, Misc3) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (ClassCode, LineNo) DO UPDATE SET Misc1=EXCLUDED.Misc1, RoomNo=EXCLUDED.RoomNo, CourseName=EXCLUDED.CourseName, Misc2=EXCLUDED.Misc2, Year=EXCLUDED.Year, Dept=EXCLUDED.Dept, StaffCode=EXCLUDED.StaffCode, ClassSize=EXCLUDED.ClassSize, TotalSize=EXCLUDED.TotalSize, TimetableYear=EXCLUDED.TimetableYear, Misc3=EXCLUDED.Misc3''', (classcode, ln, row.get('Misc1'), row.get('RoomNo'), row.get('CourseName'), row.get('Misc2'), row.get('Year'), row.get('Dept'), row.get('StaffCode'), row.get('ClassSize'), row.get('TotalSize'), row.get('TimetableYear'), row.get('Misc3')))
            rows.append(row)
    flash('Classes CSV processed')
    if 'skipped_rows' in locals():
        flash(f'Skipped {skipped_rows} row(s) with missing ClassCode or LineNo.')
    suggestions = []
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT id, name, source, source_url, upload_method, uploaded_by, upload_date FROM recipes ORDER BY name')
            recipe_list = [dict(row) for row in c.fetchall()]
        return render_template('recipe_setup/recipe_book_setup.html', recipe_list=recipe_list)
    except Exception:
        suggestions = []
    return render_template('admin_task/admin.html', preview_data=rows, suggestions=suggestions)

# --- Staff List ---
@admin_task_bp.route('/staff')
@require_role('Admin')
def staff():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT code, last_name, first_name, title, email FROM teachers ORDER BY last_name, first_name')
        rows = [dict(r) for r in c.fetchall()]
    return render_template('admin_task/staff.html', rows=rows)

# --- Classes List ---
@admin_task_bp.route('/classes')
@require_role('Admin')
def classes_page():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM classes ORDER BY ClassCode, LineNo')
        rows = [dict(r) for r in c.fetchall()]
    return render_template('admin_task/classes.html', rows=rows)

# --- Add more admin routes as needed (permissions, user_roles, clean_recipes, etc.) ---
