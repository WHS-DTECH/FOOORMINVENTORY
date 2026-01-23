# API endpoint for stepwise serving size strategies
from flask import jsonify

@debug_parser_serving_bp.route('/run_serving_strategy/<int:test_recipe_id>', methods=['POST'])
def run_serving_strategy(test_recipe_id):
    # For demonstration, use the same sample HTML as in debug_serving_size
    sample_html = '''<html><body><label>Serving Size</label> 4 portions <label>Serves</label> 6</body></html>'''
    # In production, fetch the real raw_data for the test_recipe_id
    raw_data = sample_html
    # Get the current step from the POST body
    data = request.get_json(force=True)
    current_step = int(data.get('current_step', 0))
    # Define strategies as functions
    def extract_label_serve_number(html):
        soup = BeautifulSoup(html, 'html.parser')
        label_tags = soup.find_all('label')
        for label in label_tags:
            label_text = label.get_text(strip=True).lower()
            if re.search(r'serv\w*', label_text):
                next_siblings = label.next_siblings
                for sib in next_siblings:
                    if isinstance(sib, str):
                        match = re.search(r'(\d+)', sib)
                        if match:
                            return match.group(1)
                    else:
                        text = sib.get_text(strip=True) if hasattr(sib, 'get_text') else str(sib)
                        match = re.search(r'(\d+)', text)
                        if match:
                            return match.group(1)
        return None
    def look_for_serves_or_makes(html):
        # Simple regex for demonstration
        match = re.search(r'(serves|makes)\s*(\d+)', html, re.IGNORECASE)
        if match:
            return match.group(2)
        return None
    def find_numbers_near_serving_or_portion(html):
        match = re.search(r'(serving|portion)[^\d]*(\d+)', html, re.IGNORECASE)
        if match:
            return match.group(2)
        return None
    def check_numbers_in_title(html):
        # For demo, just look for a number in the first 100 chars
        match = re.search(r'(\d+)', html[:100])
        if match:
            return match.group(1)
        return None
    def fallback_any_number_first_10_lines(html):
        lines = html.splitlines()[:10]
        for line in lines:
            match = re.search(r'(\d+)', line)
            if match:
                return match.group(1)
        return None
    strategies = [
        extract_label_serve_number,
        look_for_serves_or_makes,
        find_numbers_near_serving_or_portion,
        check_numbers_in_title,
        fallback_any_number_first_10_lines
    ]
    if 0 <= current_step < len(strategies):
        result = strategies[current_step](raw_data)
        return jsonify({'result': result or '(No match found)'})
    elif current_step == len(strategies):
        return jsonify({'result': 'N/A'})
    else:
        return jsonify({'result': '(Invalid step)'})
# debug_parser_Serving.py
# Layout and logic based on Title DEBUG code

from flask import Blueprint, render_template, request
from bs4 import BeautifulSoup
import re

debug_parser_serving_bp = Blueprint('debug_parser_serving', __name__, template_folder='templates')

@debug_parser_serving_bp.route('/debug_serving_size/<int:test_recipe_id>', methods=['GET', 'POST'])
def debug_serving_size(test_recipe_id):
    # Example: fetch test_recipe from DB (replace with actual DB logic)
    # For demonstration, use a sample HTML for raw_data
    sample_html = '''<html><body><label>Serving Size</label> 4 portions <label>Serves</label> 6</body></html>'''
    test_recipe = {
        'id': test_recipe_id,
        'serving_size': 'N/A',
        'upload_source_detail': '',
        'confirmed': {},
        'strategies': [],
        'raw_data': sample_html,
    }

    # Stepwise strategies
    strategies = []

    # 1. Look for <label> with 'Serve' and get nearest number
    def extract_label_serve_number(html):
        soup = BeautifulSoup(html, 'html.parser')
        label_tags = soup.find_all('label')
        for label in label_tags:
            label_text = label.get_text(strip=True).lower()
            # Match any label containing 'serv' with any ending (wildcard)
            if re.search(r'serv\w*', label_text):
                # Find the nearest number after the label
                next_siblings = label.next_siblings
                for sib in next_siblings:
                    if isinstance(sib, str):
                        match = re.search(r'(\d+)', sib)
                        if match:
                            return match.group(1)
                    else:
                        text = sib.get_text(strip=True) if hasattr(sib, 'get_text') else str(sib)
                        match = re.search(r'(\d+)', text)
                        if match:
                            return match.group(1)
        return None

    label_serve_result = extract_label_serve_number(test_recipe['raw_data'])
    strategies.append({
        'name': "Look for <label> with 'serv*' (wildcard) and get nearest number",
        'applied': True,
        'result': label_serve_result or '—',
        'solved': bool(label_serve_result)
    })

    # 2. Look for 'serves' or 'makes' in text (placeholder logic)
    # ...existing or placeholder logic for other strategies...
    # For demonstration, add placeholder for other strategies
    strategies.append({
        'name': "Look for 'serves' or 'makes' in text",
        'applied': False,
        'result': '—',
        'solved': False
    })
    strategies.append({
        'name': "Find numbers near 'serving' or 'portion'",
        'applied': False,
        'result': '—',
        'solved': False
    })
    strategies.append({
        'name': "Check for numbers in title",
        'applied': False,
        'result': '—',
        'solved': False
    })
    strategies.append({
        'name': "Fallback: Any number in first 10 lines",
        'applied': False,
        'result': '—',
        'solved': False
    })
    strategies.append({
        'name': 'If none, returns "N/A"',
        'applied': False,
        'result': 'N/A',
        'solved': not any(s['solved'] for s in strategies)
    })

    # Set serving_size to first solved strategy
    serving_size = next((s['result'] for s in strategies if s['solved']), 'N/A')
    test_recipe['serving_size'] = serving_size
    test_recipe['strategies'] = strategies

    solution = None
    if request.method == 'POST':
        solution = request.form.get('solution')
        # Save solution logic here
    return render_template(
        'debug_serving_size.html',
        test_recipe=test_recipe,
        solution=solution,
        test_recipe_id=test_recipe_id
    )
