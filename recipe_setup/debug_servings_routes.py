from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user
from auth import require_role, get_db_connection
import re

bp = Blueprint('debug_servings', __name__, template_folder='templates')

@bp.route('/debug_servings/<int:parser_debug_id>')
@require_role('Admin')
def debug_servings_route(parser_debug_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM parser_test_recipes WHERE id = %s', (parser_debug_id,))
        test_recipe = c.fetchone()
    if not test_recipe:
        return render_template('error.html', message='Test recipe not found.'), 404
    raw_data = test_recipe.get('raw_data', '')
    # Simple best guess: look for 'serves' or 'makes' in first 10 lines
    best_guess = '(No serving size found)'
    for line in raw_data.split('\n')[:10]:
        match = re.search(r'(serves|makes)\s*(\d+)', line, re.I)
        if match:
            best_guess = match.group(0)
            break
    return render_template(
        'debug_servings.html',
        parser_debug_id=parser_debug_id,
        raw_data=raw_data,
        best_guess=best_guess
    )

@bp.route('/run_serving_strategy/<int:parser_debug_id>', methods=['POST'])
@require_role('Admin')
def run_serving_strategy(parser_debug_id):
    data = request.get_json(force=True)
    current_step = data.get('current_step', 0)
    action = data.get('action', 'continue')
    STRATEGIES = [
        "Look for 'serves' or 'makes' in text",
        "Find numbers near 'serving' or 'portion'",
        "Check for numbers in title",
        "Fallback: Any number in first 10 lines",
        'If none, returns "N/A"'
    ]
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
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT raw_data FROM parser_test_recipes WHERE id = %s', (parser_debug_id,))
        row = c.fetchone()
        if not row:
            return jsonify({'error': 'Test recipe not found'}), 404
        raw_data = row['raw_data']
    lines = (raw_data or '').split('\n')
    result = ''
    if strategy == "Look for 'serves' or 'makes' in text":
        for line in lines:
            match = re.search(r'(serves|makes)\s*(\d+)', line, re.I)
            if match:
                result = match.group(0)
                break
        else:
            result = '(No match found)'
    elif strategy == "Find numbers near 'serving' or 'portion'":
        for line in lines:
            match = re.search(r'(serving|portion)\D*(\d+)', line, re.I)
            if match:
                result = match.group(0)
                break
        else:
            result = '(No match found)'
    elif strategy == "Check for numbers in title":
        title_line = lines[0] if lines else ''
        match = re.search(r'\d+', title_line)
        result = match.group(0) if match else '(No number in title)'
    elif strategy == "Fallback: Any number in first 10 lines":
        for line in lines[:10]:
            match = re.search(r'\d+', line)
            if match:
                result = match.group(0)
                break
        else:
            result = '(No number found)'
    elif strategy == 'If none, returns "N/A"':
        result = 'N/A'
    else:
        result = f'(No logic implemented for strategy: {strategy})'
    return jsonify({
        'done': False,
        'solved': False,
        'current_step': current_step,
        'strategy': strategy,
        'result': result,
        'continue_enabled': current_step < len(STRATEGIES) - 1,
        'solved_enabled': True
    })

@bp.route('/api/save_serving_solution/<int:parser_debug_id>', methods=['POST'])
@require_role('Admin')
def api_save_serving_solution(parser_debug_id):
    data = request.get_json(force=True)
    solution = data.get('solution', '').strip()
    if not solution:
        return jsonify({'success': False, 'error': 'No solution provided.'}), 400
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            # Check if row exists for this parser_debug_id
            c.execute('SELECT id FROM confirmed_parser_fields WHERE parser_debug_id = %s', (parser_debug_id,))
            row = c.fetchone()
            if row:
                c.execute('UPDATE confirmed_parser_fields SET serving_size = %s WHERE id = %s', (solution, row['id']))
            else:
                c.execute('INSERT INTO confirmed_parser_fields (parser_debug_id, serving_size) VALUES (%s, %s)', (parser_debug_id, solution))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
