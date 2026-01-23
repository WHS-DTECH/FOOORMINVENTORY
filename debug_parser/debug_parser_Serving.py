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
            if 'serve' in label.get_text(strip=True).lower():
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
        'name': Look for <label> with \'Serve\' and get nearest number,
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
