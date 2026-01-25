# --- Review Recipe URL Action Route ---
from flask import render_template, request, redirect, session
import os, ast, json, datetime as dt
from flask_login import current_user
from auth import require_role, get_db_connection

from flask import Blueprint
recipe_review_bp = Blueprint('recipe_review', __name__)

@recipe_review_bp.route('/review_recipe_url_action', methods=['POST'])
@require_role('Admin')
def review_recipe_url_action():
    recipe_json = request.form.get('recipe_json')
    action = request.form.get('action')
    error_message = None
    try:
        recipe_data = json.loads(recipe_json) if recipe_json else {}
    except Exception as e:
        recipe_data = None
        error_message = f'Error parsing recipe data: {e}'

    if error_message or not recipe_data:
        try:
            recipe_data = ast.literal_eval(recipe_json)
        except Exception:
            recipe_data = {}
        return render_template(
            "review_recipe_url.html",
            recipe_data=recipe_data or {},
            extraction_warning=error_message
        )

    if action == 'confirm':
        parser_debug_id = None
        try:
            with get_db_connection() as conn:
                c = conn.cursor()
                source_url = recipe_data.get('source_url') or recipe_data.get('title') or ''
                c.execute('SELECT id FROM parser_test_recipes WHERE upload_source_detail = %s ORDER BY id DESC LIMIT 1', (source_url,))
                test_recipe_row = c.fetchone()
                if test_recipe_row:
                    test_recipe_id = test_recipe_row['id']
                    c.execute('SELECT id FROM parser_debug WHERE recipe_id = %s ORDER BY id DESC LIMIT 1', (test_recipe_id,))
                    debug_row = c.fetchone()
                    if debug_row:
                        parser_debug_id = debug_row['id']
                    else:
                        c.execute('INSERT INTO parser_debug (recipe_id) VALUES (%s) RETURNING id', (test_recipe_id,))
                        parser_debug_id = c.fetchone()['id']
                        conn.commit()
        except Exception as e:
            parser_debug_id = None
        if parser_debug_id:
            return redirect(f"/debug_title/{parser_debug_id}")
        else:
            return render_template(
                "review_recipe_url.html",
                recipe_data=recipe_data or {},
                extraction_warning='Recipe confirmed, but no debug record found.',
                show_debug_prompt=False
            )
    elif action == 'flag':
        parser_debug_id = None
        try:
            source_url = recipe_data.get('source_url') or recipe_data.get('title') or ''
            source_url = source_url.strip()
            if source_url.startswith('http://http://'):
                source_url = source_url.replace('http://http://', 'http://', 1)
            elif source_url.startswith('https://https://'):
                source_url = source_url.replace('https://https://', 'https://', 1)
            elif source_url.startswith('http://https://'):
                source_url = source_url.replace('http://https://', 'https://', 1)
            elif source_url.startswith('https://http://'):
                source_url = source_url.replace('https://http://', 'http://', 1)
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
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user
from auth import require_role, get_db_connection
import datetime as dt
import json

recipe_book_routes_bp = Blueprint('recipe_book_routes', __name__)

# --- Recipe Extraction/Review/Flagging Routes ---

@recipe_book_routes_bp.route('/extract_url/<int:recipe_id>', methods=['POST'])
@require_role('Admin')
def extract_url(recipe_id):
    # Extraction logic for URL
    flash('URL extracted for recipe.', 'success')
    return redirect(url_for('upload_details', recipe_id=recipe_id))

@recipe_book_routes_bp.route('/extract_title/<int:test_recipe_id>', methods=['POST'])
@require_role('Admin')
def extract_title(test_recipe_id):
    # Extraction logic for title
    flash('Title extracted for recipe.', 'success')
    return redirect(url_for('upload_details', recipe_id=test_recipe_id))

@recipe_book_routes_bp.route('/extract_serving/<int:test_recipe_id>', methods=['POST'])
@require_role('Admin')
def extract_serving(test_recipe_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT raw_data FROM parser_test_recipes WHERE id = %s', (test_recipe_id,))
        row = c.fetchone()
        if not row:
            flash('Test recipe not found.', 'error')
            return redirect('/')
        raw_data = row['raw_data']
        # Placeholder for actual serving extraction logic
        serving_size = 'N/A'
        c.execute('UPDATE parser_test_recipes SET serving_size = %s WHERE id = %s', (serving_size, test_recipe_id))
        c.execute('SELECT id FROM parser_debug WHERE recipe_id = %s ORDER BY id DESC LIMIT 1', (test_recipe_id,))
        debug_row = c.fetchone()
        parser_debug_id = debug_row['id'] if debug_row else None
        conn.commit()
    flash(f'Serving size extracted: {serving_size}', 'success')
    if parser_debug_id:
        return redirect(url_for('debug_parser.parser_debug', parser_debug_id=parser_debug_id))
    else:
        return redirect('/')

@recipe_book_routes_bp.route('/extract_ingredients/<int:test_recipe_id>', methods=['POST'])
@require_role('Admin')
def extract_ingredients(test_recipe_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT raw_data FROM parser_test_recipes WHERE id = %s', (test_recipe_id,))
        row = c.fetchone()
        if not row:
            flash('Test recipe not found.', 'error')
            return redirect('/')
        raw_data = row['raw_data']
        # Placeholder for actual ingredient extraction logic
        ingredients = 'N/A'
        c.execute('UPDATE parser_test_recipes SET ingredients = %s WHERE id = %s', (ingredients, test_recipe_id))
        c.execute('SELECT id FROM parser_debug WHERE recipe_id = %s ORDER BY id DESC LIMIT 1', (test_recipe_id,))
        debug_row = c.fetchone()
        parser_debug_id = debug_row['id'] if debug_row else None
        conn.commit()
    flash('Ingredients extracted.', 'success')
    if parser_debug_id:
        return redirect(url_for('debug_parser.parser_debug', parser_debug_id=parser_debug_id))
    else:
        return redirect('/')

@recipe_book_routes_bp.route('/extract_instructions/<int:test_recipe_id>', methods=['POST'])
@require_role('Admin')
def extract_instructions(test_recipe_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT raw_data FROM parser_test_recipes WHERE id = %s', (test_recipe_id,))
        row = c.fetchone()
        if not row:
            flash('Test recipe not found.', 'error')
            return redirect('/')
        raw_data = row['raw_data']
        # Placeholder for actual instructions extraction logic
        instructions = 'N/A'
        c.execute('UPDATE parser_test_recipes SET instructions = %s WHERE id = %s', (instructions, test_recipe_id))
        c.execute('SELECT id FROM parser_debug WHERE recipe_id = %s ORDER BY id DESC LIMIT 1', (test_recipe_id,))
        debug_row = c.fetchone()
        parser_debug_id = debug_row['id'] if debug_row else None
        conn.commit()
    flash('Instructions extracted.', 'success')
    if parser_debug_id:
        return redirect(url_for('debug_parser.parser_debug', parser_debug_id=parser_debug_id))
    else:
        return redirect('/')

@recipe_book_routes_bp.route('/review_recipe_url_action', methods=['POST'])
@require_role('Admin')
def review_recipe_url_action():
    recipe_json = request.form.get('recipe_json')
    action = request.form.get('action')
    error_message = None
    try:
        recipe_data = json.loads(recipe_json) if recipe_json else {}
    except Exception as e:
        recipe_data = None
        error_message = f'Error parsing recipe data: {e}'
    if error_message or not recipe_data:
        try:
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
        parser_debug_id = None
        try:
            with get_db_connection() as conn:
                c = conn.cursor()
                c.execute('INSERT INTO parser_debug (recipe_id) VALUES (%s) RETURNING id', (None,))
                parser_debug_id = c.fetchone()['id']
                conn.commit()
        except Exception as e:
            parser_debug_id = None
        if parser_debug_id:
            return redirect(f"/debug_title/{parser_debug_id}")
        else:
            return render_template(
                "review_recipe_url.html",
                recipe_data=recipe_data or {},
                extraction_warning='Recipe confirmed, but no debug record found.',
                show_debug_prompt=False
            )
    elif action == 'flag':
        parser_debug_id = None
        try:
            source_url = recipe_data.get('source_url') or recipe_data.get('title') or ''
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
