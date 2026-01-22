
# =======================
# Debug Parser - Title Section
# =======================


# --- API: Save solution as confirmed title ---
from flask import request

@app.route('/api/save_title_solution/<int:test_recipe_id>', methods=['POST'])

def api_save_title_solution(test_recipe_id):
    data = request.get_json()
    solution = (data or {}).get('solution', '').strip()
    raw_data = (data or {}).get('raw_data', '').strip()
    extracted_title = (data or {}).get('extracted_title', '').strip()
    strategies = data.get('strategies') if data else None
    user_id = getattr(current_user, 'id', None)
    if not solution:
        return jsonify({'error': 'No solution provided.'}), 400
    # Save to confirmed_parser_fields table using parser_debug_id
    from debug_parser.parser_confirm_title import confirm_title
    parser_debug_id = test_recipe_id  # Now using parser_debug_id as the main reference
    confirm_title(solution, parser_debug_id)
    # Save debug state to parser_debug table (upsert)
    with get_db_connection() as conn:
        c = conn.cursor()
        # Try update first
        c.execute('''
            UPDATE parser_debug SET raw_data=%s, extracted_title=%s, strategies=%s, solution=%s, user_id=%s, created_at=NOW()
            WHERE id=%s
        ''', (raw_data, extracted_title, json.dumps(strategies) if strategies else None, solution, user_id, parser_debug_id))
        if c.rowcount == 0:
            # Insert if not exists
            c.execute('''
                INSERT INTO parser_debug (id, raw_data, extracted_title, strategies, solution, user_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            ''', (parser_debug_id, raw_data, extracted_title, json.dumps(strategies) if strategies else None, solution, user_id))
        conn.commit()
    return jsonify({'success': True, 'title': solution})



# --- API: Run second title extraction strategy ---
@app.route('/api/title_strategy/recipe_word/<int:test_recipe_id>', methods=['GET'])
def api_title_strategy_recipe_word(test_recipe_id):
    # Fetch test recipe
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM parser_test_recipes WHERE id = %s', (test_recipe_id,))
        test_recipe = c.fetchone()
    if not test_recipe:
        return jsonify({'error': 'Test recipe not found.'}), 404
    raw_data = test_recipe.get('raw_data') or ''
    lines = [line.strip() for line in raw_data.split('\n') if line.strip()]
    matches = []
    for line in lines:
        words = line.split()
        if not words:
            continue
        if words[0].lower() == 'recipe' or words[-1].lower() == 'recipe':
            matches.append(line)
    result = {
        'strategy': 'Is there a set of words that start with the word or end with the word "Recipe"?',
        'matches': matches,
        'match': bool(matches),
        'raw_data_length': len(raw_data)
    }
    return jsonify(result)


# --- API: Run first title extraction strategy ---
from flask import jsonify

@app.route('/api/title_strategy/url_match/<int:test_recipe_id>', methods=['GET'])
def api_title_strategy_url_match(test_recipe_id):
    # Fetch test recipe
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM parser_test_recipes WHERE id = %s', (test_recipe_id,))
        test_recipe = c.fetchone()
    if not test_recipe:
        return jsonify({'error': 'Test recipe not found.'}), 404
    url = test_recipe['upload_source_detail'] or ''
    raw_data = test_recipe.get('raw_data') or ''
    # Extract words from URL (split by - or /, ignore short/common words)
    import re
    url_words = re.split(r'[-/]', url)
    url_words = [w.lower() for w in url_words if len(w) > 2 and w.isalpha()]
    # Check if any url words appear in raw_data (case-insensitive)
    found = []
    for word in url_words:
        if word in raw_data.lower():
            found.append(word)
    result = {
        'strategy': 'Is there matching words from the URL in the Raw Data?',
        'url_words': url_words,
        'found': found,
        'match': bool(found),
        'raw_data_length': len(raw_data)
    }
    return jsonify(result)

from debug_parser.parser_confirm_URL import confirm_url
from debug_parser.parser_confirm_title import confirm_title
from debug_parser.parser_confirm_serving import confirm_serving
from debug_parser.parser_confirm_ingredients import confirm_ingredients
from debug_parser.parser_confirm_instructions import confirm_instructions
from debug_parser.debug_parser_title import debug_title
# --- Confirm Field (modular, including Source URL) ---
@app.route('/confirm_field', methods=['POST'])
@require_role('Admin')
def confirm_field():
    field = request.form.get('field')
    test_recipe_id = request.form.get('test_recipe_id')
    if not test_recipe_id or not field:
        return render_template('error.html', message='Missing field or test_recipe_id.'), 400
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM parser_test_recipes WHERE id = %s', (test_recipe_id,))
        test_recipe = c.fetchone()
    if not test_recipe:
        return render_template('error.html', message='Test recipe not found.'), 404
    confirmed = {}
    # Modular confirmation logic
    if field == 'source_url':
        raw_url = test_recipe['upload_source_detail']
        confirm_url(raw_url, test_recipe_id)
            # Also update parser_debug table
            with get_db_connection() as conn:
                c = conn.cursor()
                c.execute('''
                    UPDATE parser_debug SET source_url=%s WHERE recipe_id=%s
                ''', (raw_url, test_recipe_id))
                conn.commit()
    elif field == 'title':
        raw_title = test_recipe['upload_source_detail']
        confirm_title(raw_title, test_recipe_id)
            with get_db_connection() as conn:
                c = conn.cursor()
                c.execute('''
                    UPDATE parser_debug SET title=%s WHERE recipe_id=%s
                ''', (raw_title, test_recipe_id))
                conn.commit()
    elif field == 'serving_size':
        raw_serving = test_recipe['serving_size']
        confirm_serving(raw_serving, test_recipe_id)
            # Ensure integer for DB
            serving_int = None
            try:
                serving_int = int(raw_serving)
            except (TypeError, ValueError):
                serving_int = None
            with get_db_connection() as conn:
                c = conn.cursor()
                c.execute('''
                    UPDATE parser_debug SET serving_size=%s WHERE recipe_id=%s
                ''', (serving_int, test_recipe_id))
                conn.commit()
    elif field == 'ingredients':
        raw_ingredients = test_recipe['ingredients']
        confirm_ingredients(raw_ingredients, test_recipe_id)
            with get_db_connection() as conn:
                c = conn.cursor()
                c.execute('''
                    UPDATE parser_debug SET ingredients=%s WHERE recipe_id=%s
                ''', (raw_ingredients, test_recipe_id))
                conn.commit()
    elif field == 'instructions':
        raw_instructions = test_recipe['instructions']
        confirm_instructions(raw_instructions, test_recipe_id)
            with get_db_connection() as conn:
                c = conn.cursor()
                c.execute('''
                    UPDATE parser_debug SET instructions=%s WHERE recipe_id=%s
                ''', (raw_instructions, test_recipe_id))
                conn.commit()
    # TODO: Add logic for other fields as needed
    # Fetch all confirmed fields for this test_recipe_id (always)
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM confirmed_parser_fields WHERE parser_test_recipe_id = %s', (test_recipe_id,))
        row = c.fetchone()
        if row:
            confirmed = dict(row)
    # Fetch parser_debug record for this test_recipe, if any
    parser_debug = None
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM parser_debug WHERE recipe_id = %s', (test_recipe_id,))
        debug_row = c.fetchone()
        if debug_row:
            parser_debug = dict(debug_row)
    return render_template('parser_debug.html', test_recipe=test_recipe, confirmed=confirmed, parser_debug=parser_debug)

# --- Debug Title Page (modular) ---
@app.route('/debug_title/<int:test_recipe_id>')
@require_role('Admin')
def debug_title_route(test_recipe_id):
    @app.route('/debug_title2/<int:parser_debug_id>')
    @require_role('Admin')
    def debug_title2_route(parser_debug_id):
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM parser_debug WHERE id = %s', (parser_debug_id,))
            debug_row = c.fetchone()
            if not debug_row:
                return render_template('error.html', message='Parser debug entry not found.'), 404
            debug_row = dict(debug_row)
            recipe_id = debug_row['recipe_id']
            c.execute('SELECT * FROM parser_test_recipes WHERE id = %s', (recipe_id,))
            test_recipe = c.fetchone()
        if not test_recipe:
            return render_template('error.html', message='Test recipe not found.'), 404
        raw_title = test_recipe['upload_source_detail']
        raw_data = test_recipe.get('raw_data') or ''
        debugged_title = debug_title(raw_title, recipe_id)
        debug_state = debug_row
        if debug_state.get('strategies'):
            try:
                debug_state['strategies'] = json.loads(debug_state['strategies'])
            except Exception:
                pass
        return render_template(
            'debug_parser/debug_title.html',
            raw_title=raw_title,
            raw_data=raw_data,
            debugged_title=debugged_title,
            test_recipe_id=recipe_id,
            debug_state=debug_state
        )
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM parser_test_recipes WHERE id = %s', (test_recipe_id,))
        test_recipe = c.fetchone()
        # Try to load parser_debug state for this test_recipe_id
        c.execute('SELECT * FROM parser_debug WHERE recipe_id = %s', (test_recipe_id,))
        debug_row = c.fetchone()
    if not test_recipe:
        return render_template('error.html', message='Test recipe not found.'), 404
    raw_title = test_recipe['upload_source_detail']
    raw_data = test_recipe.get('raw_data') or ''
    debugged_title = debug_title(raw_title, test_recipe_id)
    # If parser_debug state exists, use it to pre-populate UI
    debug_state = None
    if debug_row:
        debug_state = dict(debug_row)
        # Parse strategies JSON if present
        if debug_state.get('strategies'):
            try:
                debug_state['strategies'] = json.loads(debug_state['strategies'])
            except Exception:
                pass
    return render_template(
        'debug_parser/debug_title.html',
        raw_title=raw_title,
        raw_data=raw_data,
        debugged_title=debugged_title,
        test_recipe_id=test_recipe_id,
        debug_state=debug_state
    )

# Route to render the debug extract text form
@app.route('/debug_extract_text_form', methods=['GET'])
@require_role('Admin')
def debug_extract_text_form():
    return render_template('debug_extract_text_form.html')

# --- Raw Data View for flagged/test recipe ---
@app.route('/parser_debug_raw/<int:test_recipe_id>')
@require_role('Admin')
def parser_debug_raw(test_recipe_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM parser_test_recipes WHERE id = %s', (test_recipe_id,))
        test_recipe = c.fetchone()
    if not test_recipe:
        return render_template('error.html', message='Test recipe not found.'), 404
    # Show all raw fields in a simple preformatted block
    return render_template('parser_debug_raw.html', test_recipe=test_recipe)


# --- Parser Debug Page for flagged/test recipes ---

@app.route('/parser_debug/<int:test_recipe_id>')
@require_role('Admin')
def parser_debug(test_recipe_id):
        print("[DEBUG] confirmed_list:", confirmed_list)
    # Fetch the flagged/test recipe from parser_test_recipes
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM parser_test_recipes WHERE id = %s', (test_recipe_id,))
        test_recipe = c.fetchone()
        if not test_recipe:
            return render_template('error.html', message='Test recipe not found.'), 404
        # Fetch all confirmed fields (all records, now using parser_debug_id)
        c.execute('SELECT * FROM confirmed_parser_fields ORDER BY id')
        all_rows = c.fetchall()
        all_confirmed_parser_fields = [dict(row) for row in all_rows] if all_rows else []
        # Fetch confirmed fields for this parser_debug_id only
        confirmed_list = [dict(row) for row in all_rows if row.get('parser_debug_id') == test_recipe_id] if all_rows else []
        confirmed = confirmed_list[0] if confirmed_list else {}
        # Fetch parser_debug info for this parser_debug_id
        c.execute('SELECT * FROM parser_debug WHERE id = %s', (test_recipe_id,))
        parser_debug = c.fetchone()
    return render_template('parser_debug.html', test_recipe=test_recipe, confirmed=confirmed, confirmed_list=confirmed_list, parser_debug=parser_debug, all_confirmed_parser_fields=all_confirmed_parser_fields)

@app.route('/delete_confirmed_parser_field', methods=['POST'])
@require_role('Admin')
def delete_confirmed_parser_field():
    field_id = request.form.get('id')
    if not field_id:
        flash('No field id provided.', 'error')
        return redirect(request.referrer or url_for('admin_task.admin_recipe_book_setup'))
    with get_db_connection() as conn:
        c = conn.cursor()
        # Get the parser_test_recipe_id before deleting for redirect
        c.execute('SELECT parser_test_recipe_id FROM confirmed_parser_fields WHERE id = %s', (field_id,))
        row = c.fetchone()
        if not row:
            flash('Confirmed field not found.', 'error')
            return redirect(request.referrer or url_for('admin_task.admin_recipe_book_setup'))
        test_recipe_id = row['parser_test_recipe_id']
        c.execute('DELETE FROM confirmed_parser_fields WHERE id = %s', (field_id,))
        conn.commit()
    flash('Confirmed parser field deleted.', 'success')
    return redirect(url_for('parser_debug', test_recipe_id=test_recipe_id))
@app.route('/parser_test_decision', methods=['POST'])
@require_role('Admin')
def parser_test_decision():
    test_recipe_id = request.form.get('test_recipe_id')
    debug_now = request.form.get('debug_now')
    # Optionally fetch recipe_data for display
    if debug_now == 'yes' and test_recipe_id:
        # Redirect to parser debug page for this test recipe
        return redirect(url_for('parser_debug', test_recipe_id=test_recipe_id))
    else:
        # Show confirmation message on the draft page
        return render_template(
            "review_recipe_url.html",
            extraction_warning='Recipe stored in parser testing table as a test sample for future improvements.',
            show_debug_prompt=False)

