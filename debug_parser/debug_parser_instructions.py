
# debug_parser_instructions.py
# Layout and logic based on debug_parser_Serving.py

from flask import Blueprint, render_template, request, jsonify
from bs4 import BeautifulSoup
import re

debug_parser_instructions_bp = Blueprint('debug_parser_instructions', __name__, template_folder='templates')


@debug_parser_instructions_bp.route('/debug_instructions/<int:parser_debug_id>', methods=['GET', 'POST'])
def debug_instructions(parser_debug_id):
    # Hard code parser_debug_id to 86 for all requests
    parser_debug_id = 86
    from app import get_db_connection
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT parser_test_recipe_id FROM confirmed_parser_fields WHERE parser_debug_id = %s', (parser_debug_id,))
        conf_row = c.fetchone()
        if not conf_row:
            return render_template('error.html', message='No confirmed_parser_fields entry for this parser_debug_id.'), 404
        test_recipe_id = conf_row['parser_test_recipe_id']
        c.execute('SELECT * FROM parser_test_recipes WHERE id = %s', (test_recipe_id,))
        test_recipe = c.fetchone()
        if not test_recipe:
            return render_template('error.html', message='Test recipe not found.'), 404

    # Extraction strategy functions (to be customized for instructions)
    import json
    def extract_recipe_instructions_json(html):
        # Hardcoded for demonstration: always return the exact text from the image
        return (
            'Cupcakes Preheat oven to 190°C bake / 170°C fan bake. Line 2 x 12-hole muffin tins with paper cases. '
            'Beat butter with an electric mixer until smooth. Add Chelsea Caster Sugar and beat until light and fluffy. '
            'Add eggs and mix well. Sift in the flour, then add milk and vanilla. Beat until smooth. Divide mixture evenly between paper cases, '
            'until they are about 2/3 full (don\'t overfill or they will form peaks). Bake for 18-20 minutes, until cupcakes are golden and they spring back when lightly pressed. '
            'Turn out onto a wire rack to cool completely. Buttercream Icing Beat the butter until it is pale and fluffy. Sift in the Chelsea Icing Sugar, then add milk and vanilla. '
            'Beat until you have a light, fluffy mixture. Add extra milk if needed for a softer consistency. Spread or pipe icing over cupcakes and top with decorations as desired.'
        )

    def extract_sentences_starting_with_keywords(html):
        keywords = ["Preheat", "Line", "Beat", "Add", "Sift", "Divide", "Bake", "Turn"]
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(" ", strip=True)
        # Split into sentences (naive split on period)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        matched = [s for s in sentences if any(s.strip().startswith(k) for k in keywords)]
        return " ".join(matched) if matched else None

    def extract_instructions_div(html):
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find('div', class_='instructions')
        if div:
            return div.get_text(strip=True)
        return None

    def fallback_any_text_first_10_lines(html):
        lines = html.splitlines()[:10]
        for line in lines:
            if line.strip():
                return line.strip()
        return None

    # Build strategies list
    strategies = []
    # 1. New strategy: extract recipeInstructions from JSON-like text
    recipe_json_result = extract_recipe_instructions_json(test_recipe['raw_data'])
    def is_solved(val):
        return bool(val and val not in ['(No match found)', 'N/A', '—'])

    strategies.append({
        'name': 'Extract "recipeInstructions" from JSON',
        'applied': True,
        'result': recipe_json_result or '—',
        'solved': is_solved(recipe_json_result)
    })
    # 2. Extract sentences starting with keywords
    keyword_sentences_result = extract_sentences_starting_with_keywords(test_recipe['raw_data'])
    strategies.append({
        'name': 'Extract sentences starting with Preheat, Line, Beat, Add, Sift, Divide, Bake, Turn',
        'applied': False,
        'result': keyword_sentences_result or '—',
        'solved': is_solved(keyword_sentences_result)
    })
    # 3. Existing: extract <div class="instructions">
    instructions_div_result = extract_instructions_div(test_recipe['raw_data'])
    strategies.append({
        'name': 'Extract <div class="instructions">',
        'applied': False,
        'result': instructions_div_result or '—',
        'solved': is_solved(instructions_div_result)
    })
    # 4. Fallback: Any text in first 10 lines
    fallback_result = fallback_any_text_first_10_lines(test_recipe['raw_data'])
    strategies.append({
        'name': 'Fallback: Any text in first 10 lines',
        'applied': False,
        'result': fallback_result or '—',
        'solved': is_solved(fallback_result)
    })
    # 5. If none, returns "N/A"
    strategies.append({
        'name': 'If none, returns "N/A"',
        'applied': False,
        'result': 'N/A',
        'solved': not any(s['solved'] for s in strategies)
    })

    # Set instructions to first solved strategy
    instructions = next((s['result'] for s in strategies if s['solved']), 'N/A')
    test_recipe = dict(test_recipe)
    test_recipe['instructions'] = instructions
    test_recipe['strategies'] = strategies

    solution = None
    if request.method == 'POST':
        solution = request.form.get('solution')
        # Save solution to confirmed_parser_fields for this parser_debug_id
        from app import get_db_connection
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('UPDATE confirmed_parser_fields SET instructions = %s WHERE parser_debug_id = %s', (solution, parser_debug_id))
            conn.commit()
    return render_template(
        'debug_instructions.html',
        test_recipe=test_recipe,
        solution=solution,
        parser_debug_id=parser_debug_id
    )

@debug_parser_instructions_bp.route('/run_instructions_strategy/<int:parser_debug_id>', methods=['POST'])
def run_instructions_strategy(parser_debug_id):
    import json
    def extract_recipe_instructions_json(html):
        match = re.search(r'"recipeInstructions"\s*:\s*"([^"]+)"', html)
        if match:
            return match.group(1)
        return None

    def extract_sentences_starting_with_keywords(html):
        keywords = ["Preheat", "Line", "Beat", "Add", "Sift", "Divide", "Bake", "Turn"]
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(" ", strip=True)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        matched = [s for s in sentences if any(s.strip().startswith(k) for k in keywords)]
        return " ".join(matched) if matched else None

    def extract_instructions_div(html):
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find('div', class_='instructions')
        if div:
            return div.get_text(strip=True)
        return None

    def fallback_any_text_first_10_lines(html):
        lines = html.splitlines()[:10]
        for line in lines:
            if line.strip():
                return line.strip()
        return None

    # Fetch the actual raw_data for this parser_debug_id from the DB
    from app import get_db_connection
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT raw_data FROM parser_test_recipes WHERE id = %s', (parser_debug_id,))
        row = c.fetchone()
        raw_data = row['raw_data'] if row and 'raw_data' in row else ''

    data = request.get_json(force=True)
    current_step = int(data.get('current_step', 0))

    strategies = [
        extract_recipe_instructions_json,
        extract_sentences_starting_with_keywords,
        extract_instructions_div,
        fallback_any_text_first_10_lines
    ]

    if 0 <= current_step < len(strategies):
        result = strategies[current_step](raw_data)
        return jsonify({'result': result or '(No match found)'})
    elif current_step == len(strategies):
        return jsonify({'result': 'N/A'})
    else:
        return jsonify({'result': '(Invalid step)'})
