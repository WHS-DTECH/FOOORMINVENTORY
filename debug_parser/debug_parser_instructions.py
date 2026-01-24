from flask import Blueprint, render_template, request
from bs4 import BeautifulSoup
import re

debug_parser_instructions_bp = Blueprint('debug_parser_instructions', __name__, template_folder='templates')

@debug_parser_instructions_bp.route('/debug_instructions/<int:test_recipe_id>', methods=['GET', 'POST'])
def debug_instructions(test_recipe_id):
    # Example: fetch test_recipe from DB (replace with actual DB logic)
    sample_html = '''<html><body><div class="instructions">Step 1: Mix.<br>Step 2: Bake.</div></body></html>'''
    test_recipe = {
        'id': test_recipe_id,
        'instructions': 'N/A',
        'upload_source_detail': '',
        'confirmed': {},
        'raw_data': sample_html,
    }

    def extract_instructions(html):
        soup = BeautifulSoup(html, 'html.parser')
        instructions_div = soup.find('div', class_='instructions')
        if instructions_div:
            return instructions_div.get_text(separator='\n', strip=True)
        # Fallback: look for lines with 'Step' or numbered steps
        matches = re.findall(r'(Step \d+:.*)', html, re.IGNORECASE)
        if matches:
            return '\n'.join(matches)
        return None

    extracted_instructions = extract_instructions(test_recipe['raw_data'])
    test_recipe['instructions'] = extracted_instructions or 'N/A'

    if request.method == 'POST':
        # Save solution logic here
        pass

    return render_template(
        'debug_instructions.html',
        test_recipe=test_recipe,
        extracted_instructions=extracted_instructions
    )
