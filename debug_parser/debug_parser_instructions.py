
# debug_parser_instructions.py
# Layout and logic based on debug_parser_Serving.py

from flask import Blueprint, render_template, request, jsonify
from bs4 import BeautifulSoup
import re

debug_parser_instructions_bp = Blueprint('debug_parser_instructions', __name__, template_folder='templates')


@debug_parser_instructions_bp.route('/debug_instructions/<int:test_recipe_id>', methods=['GET', 'POST'])
def debug_instructions(test_recipe_id):
    # Example: fetch test_recipe from DB (replace with actual DB logic)
    sample_html = '''<html><body><div class="instructions">Step 1: Mix. Step 2: Bake.</div></body></html>'''
    test_recipe = {
        'id': test_recipe_id,
        'instructions': 'N/A',
        'upload_source_detail': '',
        'confirmed': {},
        'strategies': [],
        'raw_data': sample_html,
    }

    # Extraction strategy functions (to be customized for instructions)
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
    instructions_div_result = extract_instructions_div(test_recipe['raw_data'])
    strategies.append({
        'name': 'Extract <div class="instructions">',
        'applied': True,
        'result': instructions_div_result or '—',
        'solved': bool(instructions_div_result)
    })
    fallback_result = fallback_any_text_first_10_lines(test_recipe['raw_data'])
    strategies.append({
        'name': 'Fallback: Any text in first 10 lines',
        'applied': False,
        'result': fallback_result or '—',
        'solved': bool(fallback_result)
    })
    strategies.append({
        'name': 'If none, returns "N/A"',
        'applied': False,
        'result': 'N/A',
        'solved': not any(s['solved'] for s in strategies)
    })

    # Set instructions to first solved strategy
    instructions = next((s['result'] for s in strategies if s['solved']), 'N/A')
    test_recipe['instructions'] = instructions
    test_recipe['strategies'] = strategies

    solution = None
    if request.method == 'POST':
        solution = request.form.get('solution')
        # Save solution logic here
    return render_template(
        'debug_instructions.html',
        test_recipe=test_recipe,
        solution=solution,
        test_recipe_id=test_recipe_id
    )

@debug_parser_instructions_bp.route('/run_instructions_strategy/<int:test_recipe_id>', methods=['POST'])
def run_instructions_strategy(test_recipe_id):
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

    sample_html = '''<html><body><div class="instructions">Step 1: Mix. Step 2: Bake.</div></body></html>'''
    raw_data = sample_html
    data = request.get_json(force=True)
    current_step = int(data.get('current_step', 0))

    strategies = [
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
