import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from auth import require_login, require_role, get_db_connection

recipe_book_bp = Blueprint(
    'recipe_book',
    __name__,
    template_folder='templates/recipe_book'
)

@recipe_book_bp.route('/recbk')
def recbk():
    q = request.args.get('q', '').strip()
    with get_db_connection() as conn:
        c = conn.cursor()
        if q:
            term = f"%{q}%"
            c.execute(
                "SELECT id, name, ingredients, instructions, serving_size, equipment, dietary_tags, cuisine, difficulty, source_url FROM recipes "
                "WHERE name ILIKE %s OR ingredients ILIKE %s "
                "ORDER BY LOWER(name)",
                (term, term),
            )
        else:
            c.execute(
                "SELECT id, name, ingredients, instructions, serving_size, equipment, dietary_tags, cuisine, difficulty, source_url FROM recipes "
                "ORDER BY LOWER(name)"
            )
        rows = [dict(r) for r in c.fetchall()]

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

    favorites = []
    if current_user.is_authenticated:
        try:
            with get_db_connection() as conn:
                c = conn.cursor()
                c.execute('SELECT recipe_id FROM recipe_favorites WHERE user_email = %s', (current_user.email,))
                favorites = [row[0] for row in c.fetchall()]
        except Exception:
            favorites = []

    return render_template('recbk.html', rows=rows, q=q, favorites=favorites)

@recipe_book_bp.route('/recipe_index/<int:recipe_id>')
@require_role('Admin')
def recipe_index_view(recipe_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM recipes WHERE id = %s', (recipe_id,))
        recipe = c.fetchone()
    return render_template('recipe_index_view.html', recipe=recipe)

@recipe_book_bp.route('/recipe/<int:recipe_id>')
@require_login
def recipe_details(recipe_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM recipes WHERE id = %s', (recipe_id,))
        recipe = c.fetchone()
        if not recipe:
            flash('Recipe not found.', 'error')
            return redirect(url_for('recipe_book.recbk'))
        try:
            if isinstance(recipe['ingredients'], str):
                recipe['ingredients'] = json.loads(recipe['ingredients'])
        except Exception:
            pass
        return render_template('recipe_details.html', recipe=recipe)

@recipe_book_bp.route('/edit_instructions/<int:recipe_id>', methods=['GET', 'POST'])
@require_role(['Admin', 'Recipe Editor'])
def edit_instructions(recipe_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        if request.method == 'POST':
            new_instructions = request.form.get('instructions', '').strip()
            c.execute('UPDATE recipes SET instructions = %s WHERE id = %s', (new_instructions, recipe_id))
            conn.commit()
            flash('Instructions updated.', 'success')
            return redirect(url_for('recipe_book.recipe_details', recipe_id=recipe_id))
        c.execute('SELECT * FROM recipes WHERE id = %s', (recipe_id,))
        recipe = c.fetchone()
        if not recipe:
            flash('Recipe not found.', 'error')
            return redirect(url_for('recipe_book.recbk'))
        return render_template('edit_instructions.html', recipe=recipe)

@recipe_book_bp.route('/recipe_book_setup')
def recipe_book_setup():
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT id, name, source, source_url, upload_method, uploaded_by, upload_date FROM recipes ORDER BY name')
            recipe_list = [dict(row) for row in c.fetchall()]
        return render_template('recipe_book_setup.html', recipe_list=recipe_list)
    except Exception:
        return render_template('recipe_book_setup.html', recipe_list=[])
