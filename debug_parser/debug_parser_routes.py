# --- API: Run title extraction strategies ---
from flask import jsonify
from debug_parser.debug_parser_title import is_likely_title


from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import current_user
from auth import require_role, get_db_connection
import json
import re

# Import debug helpers
from debug_parser.parser_confirm_URL import confirm_url
from debug_parser.parser_confirm_title import confirm_title
from debug_parser.parser_confirm_serving import confirm_serving
from debug_parser.parser_confirm_ingredients import confirm_ingredients
from debug_parser.parser_confirm_instructions import confirm_instructions
from debug_parser.debug_parser_title import debug_title

bp = Blueprint('debug_parser', __name__, template_folder='templates')

@bp.route('/api/run_title_strategies/<int:test_recipe_id>', methods=['POST'])
@require_role('Admin')
def api_run_title_strategies(test_recipe_id):
    # Fetch raw_data for the test_recipe
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT raw_data FROM parser_test_recipes WHERE id = %s', (test_recipe_id,))
        row = c.fetchone()
        if not row:
            return jsonify({'error': 'Test recipe not found'}), 404
        raw_data = row['raw_data']
    # Example: split lines and run is_likely_title on each
    lines = (raw_data or '').split('\n')
    results = []
    for i, line in enumerate(lines):
        result = {
            'line': line,
            'is_likely_title': is_likely_title(line)
        }
        results.append(result)
    # Return all lines and which are likely titles
    return jsonify({'lines': results})

# --- Delete confirmed_parser_field entry ---
@bp.route('/delete_confirmed_parser_field/<int:field_id>', methods=['POST'])
@require_role('Admin')
def delete_confirmed_parser_field(field_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        # Optionally fetch parser_test_recipe_id for redirect
        c.execute('SELECT parser_test_recipe_id FROM confirmed_parser_fields WHERE id = %s', (field_id,))
        row = c.fetchone()
        parser_test_recipe_id = row['parser_test_recipe_id'] if row and 'parser_test_recipe_id' in row else None
        c.execute('DELETE FROM confirmed_parser_fields WHERE id = %s', (field_id,))
        conn.commit()
    flash('Confirmed parser field record deleted.', 'success')
    # Redirect to the parser_debug page for the related test recipe if possible, else to admin_task
    if parser_test_recipe_id:
        return redirect(url_for('debug_parser.parser_debug', test_recipe_id=parser_test_recipe_id))
    return redirect(url_for('admin_task.admin_recipe_book_setup'))
# This file contains all debug_parser-related routes and logic extracted from app.py for modularization.
# To be used as the Flask blueprint/module for debug_parser.

# --- Delete parser_debug entry ---
@bp.route('/delete_debug/<int:debug_id>', methods=['POST'])
@require_role('Admin')
def delete_debug(debug_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM parser_debug WHERE id = %s', (debug_id,))
        conn.commit()
    flash('Parser debug entry deleted.', 'success')
    return redirect(url_for('admin_task.admin_recipe_book_setup'))



# --- API: Save solution as confirmed title ---
@bp.route('/api/save_title_solution/<int:test_recipe_id>', methods=['POST'])
def api_save_title_solution(test_recipe_id):
    # ...existing code from app.py...
    pass

# --- API: Run second title extraction strategy ---
@bp.route('/api/title_strategy/recipe_word/<int:test_recipe_id>', methods=['GET'])
def api_title_strategy_recipe_word(test_recipe_id):
    # ...existing code from app.py...
    pass

# --- API: Run first title extraction strategy ---
@bp.route('/api/title_strategy/url_match/<int:test_recipe_id>', methods=['GET'])
def api_title_strategy_url_match(test_recipe_id):
    # ...existing code from app.py...
    pass

# --- Confirm Field (modular, including Source URL) ---
@bp.route('/confirm_field', methods=['POST'])
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
    # Modular confirmation logic for all fields
    if field == 'source_url':
        value = test_recipe.get('upload_source_detail')
        confirm_url(value, test_recipe_id)
    elif field == 'title':
        value = test_recipe.get('upload_source_detail')
        confirm_title(value, test_recipe_id)
    elif field == 'serving_size':
        value = test_recipe.get('serving_size')
        confirm_serving(value, test_recipe_id)
    elif field == 'ingredients':
        value = test_recipe.get('ingredients')
        confirm_ingredients(value, test_recipe_id)
    elif field == 'instructions':
        value = test_recipe.get('instructions')
        confirm_instructions(value, test_recipe_id)
    # Add more fields as needed
    # Fetch all confirmed fields for this test_recipe_id (always)
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM confirmed_parser_fields WHERE parser_test_recipe_id = %s', (test_recipe_id,))
        row = c.fetchone()
        if row:
            confirmed = dict(row)
        # Fetch all confirmed_parser_fields for the table (for debug block and table)
        c.execute('SELECT * FROM confirmed_parser_fields')
        all_confirmed_parser_fields = c.fetchall() or []
    return render_template(
        'parser_debug.html',
        test_recipe=test_recipe,
        confirmed=confirmed,
        parser_debug=None,
        all_confirmed_parser_fields=all_confirmed_parser_fields
    )

# --- Debug Title Page (modular) ---
@bp.route('/debug_title/<int:test_recipe_id>')
@require_role('Admin')
def debug_title_route(test_recipe_id):
    # Minimal implementation: fetch raw title from parser_test_recipes and debug it
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM parser_test_recipes WHERE id = %s', (test_recipe_id,))
        test_recipe = c.fetchone()
    if not test_recipe:
        flash('Test recipe not found.', 'danger')
        return redirect(url_for('admin_task.admin_recipe_book_setup'))
    raw_data = test_recipe.get('raw_data', '')
    # For now, use the first non-empty line as a best guess (placeholder for real strategy logic)
    best_guess = next((line for line in raw_data.split('\n') if line.strip()), '(No title found)')
    return render_template(
        'debug_title.html',
        test_recipe_id=test_recipe_id,
        raw_data=raw_data,
        best_guess=best_guess
    )

# Route to render the debug extract text form
@bp.route('/debug_extract_text_form', methods=['GET'])
@require_role('Admin')
def debug_extract_text_form():
    # ...existing code from app.py...
    pass

# --- Raw Data View for flagged/test recipe ---
@bp.route('/parser_debug_raw/<int:test_recipe_id>')
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
@bp.route('/parser_debug/<int:test_recipe_id>')
@require_role('Admin')
def parser_debug(test_recipe_id):
    # Fetch the flagged/test recipe from parser_test_recipes
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM parser_test_recipes WHERE id = %s', (test_recipe_id,))
        test_recipe = c.fetchone()
        # Always fetch all confirmed_parser_fields for debug table
        c.execute('SELECT * FROM confirmed_parser_fields')
        all_confirmed_parser_fields = c.fetchall() or []
        if test_recipe:
            c.execute('SELECT * FROM confirmed_parser_fields WHERE parser_test_recipe_id = %s', (test_recipe_id,))
            row = c.fetchone()
            confirmed = dict(row) if row else {}
            return render_template(
                'parser_debug.html',
                test_recipe=test_recipe,
                confirmed=confirmed,
                parser_debug=None,
                all_confirmed_parser_fields=all_confirmed_parser_fields
            )
        # If not found, try parser_debug table
        c.execute('SELECT * FROM parser_debug WHERE id = %s', (test_recipe_id,))
        debug_entry = c.fetchone()
        if debug_entry:
            return render_template(
                'parser_debug.html',
                test_recipe=None,
                confirmed={},
                parser_debug=debug_entry,
                all_confirmed_parser_fields=all_confirmed_parser_fields
            )
        return render_template('error.html', message='Test recipe not found.'), 404

# --- Handle Yes/No debug prompt after flag ---
@bp.route('/parser_test_decision', methods=['POST'])
@require_role('Admin')
def parser_test_decision():
    test_recipe_id = request.form.get('test_recipe_id')
    debug_now = request.form.get('debug_now')
    # Optionally fetch recipe_data for display
    if debug_now == 'yes' and test_recipe_id:
        # Redirect to parser debug page for this test recipe (use correct blueprint endpoint)
        return redirect(url_for('debug_parser.parser_debug', test_recipe_id=test_recipe_id))
    else:
        # Show confirmation message on the draft page
        return render_template(
            "review_recipe_url.html",
            extraction_warning='Recipe stored in parser testing table as a test sample for future improvements.',
            show_debug_prompt=False,
            recipe_data={})


# Backend-driven stepwise runner: accept current_step, return next step, button state
@bp.route('/run_strategy/<int:test_recipe_id>', methods=['POST'])
@require_role('Admin')
def run_strategy(test_recipe_id):
    data = request.get_json(force=True)
    current_step = data.get('current_step', 0)
    action = data.get('action', 'continue')  # 'continue' or 'solved'
    STRATEGIES = [
        'URL: What is between the <title></title> tag.',
        'Is there matching words from the URL in the Raw Data?',
        'Not a section header',
        'Not all lowercase',
        'Not too short (≥4 chars)',
        'Not only digits/symbols',
        'Prefers larger/bold lines',
        'NLP noun phrase/WORK_OF_ART',
        'Fallback: Uppercase start, not junk word',
        'Up to 5 lines above first ingredient',
        'Prefers food words from ingredient block',
        'Closest non-empty line above ingredient block',
        'If none, returns "Unknown Recipe"'
    ]
    # If solved, just return solved state
    if action == 'solved':
        return jsonify({
            'solved': True,
            'current_step': current_step,
            'strategy': STRATEGIES[current_step] if current_step < len(STRATEGIES) else None,
            'result': data.get('result', ''),
            'continue_enabled': False,
            'solved_enabled': False,
            'done': True
        })
    # Otherwise, run the strategy for current_step
    if current_step >= len(STRATEGIES):
        return jsonify({
            'done': True,
            'solved': False,
            'current_step': current_step,
            'strategy': None,
            'result': '',
            'continue_enabled': False,
            'solved_enabled': False
        })
    strategy = STRATEGIES[current_step]
    # Fetch raw_data for the test_recipe
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT raw_data FROM parser_test_recipes WHERE id = %s', (test_recipe_id,))
        row = c.fetchone()
        if not row:
            return jsonify({'error': 'Test recipe not found'}), 404
        raw_data = row['raw_data']
    lines = (raw_data or '').split('\n')
    result = ''
    # --- Strategy logic (same as before) ---
    if strategy == 'URL: What is between the <title></title> tag.':
        match = re.search(r'<title>(.*?)</title>', raw_data, re.IGNORECASE | re.DOTALL)
        result = match.group(1).strip() if match else '(No <title> tag found)'
    elif strategy == 'Is there matching words from the URL in the Raw Data?':
        url_match = re.search(r'(https?://\S+)', raw_data)
        if url_match:
            url = url_match.group(1)
            url_words = re.findall(r'[a-zA-Z]+', url)
            found = []
            for word in url_words:
                for line in lines:
                    if word.lower() in line.lower():
                        found.append(word)
                        break
            result = f"Words from URL found in raw data: {', '.join(found)}" if found else 'No URL words found in raw data.'
        else:
            result = 'No URL found in raw data.'
    elif strategy == 'Not a section header':
        def dummy_detect_section(line):
            return bool(re.match(r'^(ingredients|instructions|method|directions)[:\s]*$', line.strip(), re.I))
        candidates = [line for line in lines if line.strip() and not dummy_detect_section(line)]
        result = candidates[0] if candidates else 'No non-section-header line found.'
    elif strategy == 'Not all lowercase':
        candidates = [line for line in lines if line.strip() and not line.islower()]
        result = candidates[0] if candidates else 'No line found that is not all lowercase.'
    elif strategy == 'Not too short (≥4 chars)':
        candidates = [line for line in lines if len(line.strip()) >= 4]
        result = candidates[0] if candidates else 'No line found with ≥4 chars.'
    elif strategy == 'Not only digits/symbols':
        candidates = [line for line in lines if not re.match(r'^[\d\W]+$', line.strip())]
        result = candidates[0] if candidates else 'No line found that is not only digits/symbols.'
    elif strategy == 'Prefers larger/bold lines':
        candidates = sorted([line for line in lines if line.strip()], key=lambda l: -len(l))
        result = candidates[0] if candidates else 'No non-empty lines.'
    elif strategy == 'NLP noun phrase/WORK_OF_ART':
        from debug_parser.debug_parser_title import nlp
        if nlp:
            for line in lines:
                doc = nlp(line)
                if any(ent.label_ == 'WORK_OF_ART' for ent in doc.ents):
                    result = line
                    break
            else:
                result = 'No WORK_OF_ART found.'
        else:
            result = 'spaCy NLP not available.'
    elif strategy == 'Fallback: Uppercase start, not junk word':
        junk_words = ['skills', 'worksheet', 'target', 'tick', 'review', 'technology', 'assessment', 'evaluation', 'scenario', 'brief', 'attributes', 'learning objective']
        for line in lines:
            if line and line[0].isupper() and not any(x in line.lower() for x in junk_words):
                result = line
                break
        else:
            result = 'No suitable fallback line found.'
    elif strategy == 'Up to 5 lines above first ingredient':
        idx = next((i for i, line in enumerate(lines) if re.search(r'ingredient', line, re.I)), None)
        if idx is not None:
            from debug_parser.debug_parser_title import infer_title_above
            ingredient_block = [l for l in lines if re.search(r'\d', l)]
            result = infer_title_above(lines, idx, ingredient_block)
        else:
            result = 'No ingredient block found.'
    elif strategy == 'Prefers food words from ingredient block':
        food_words = ['chicken', 'beef', 'pasta', 'salad', 'soup', 'cake', 'bread']
        for line in lines:
            if any(word in line.lower() for word in food_words):
                result = line
                break
        else:
            result = 'No food word found.'
    elif strategy == 'Closest non-empty line above ingredient block':
        idx = next((i for i, line in enumerate(lines) if re.search(r'ingredient', line, re.I)), None)
        if idx is not None:
            for j in range(1, 6):
                above = idx - j
                if above < 0:
                    break
                candidate = lines[above].strip()
                if candidate:
                    result = candidate
                    break
            else:
                result = 'No non-empty line found above ingredient block.'
        else:
            result = 'No ingredient block found.'
    elif strategy == 'If none, returns "Unknown Recipe"':
        result = 'Unknown Recipe'
    else:
        result = f'(No logic implemented for strategy: {strategy})'
    # Return backend-driven state
    return jsonify({
        'done': False,
        'solved': False,
        'current_step': current_step,
        'strategy': strategy,
        'result': result,
        'continue_enabled': current_step < len(STRATEGIES) - 1,
        'solved_enabled': True
    })
