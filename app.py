"""
Inventory app main entrypoint
Best practice: All imports first, then utility functions, then app creation/config, then routes.
"""

# =======================
# Imports (Standard, Third-party, Local)
# =======================
import os
import re
import datetime
import json
import csv
import io
try:
    import uuid
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, current_user
from google_auth_oauthlib.flow import Flow
import psycopg2
import psycopg2.extras
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None
from recipe_parser_pdf import parse_recipes_from_text
from auth import User, get_staff_code_from_email, require_login, require_role

# =======================
# Utility Functions
# =======================
def simple_similarity(a, b):
    """Return a similarity score between 0 and 1 based on Levenshtein distance (if available) or substring match."""
    try:
        import Levenshtein
        return Levenshtein.ratio(a.lower(), b.lower())
    except ImportError:
        # Fallback: substring match
        a, b = a.lower(), b.lower()
        if a in b or b in a:
            return 0.8
        return 0.0



# =======================
# App Creation & Configuration
# =======================
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

# Allow OAuth over HTTP for local development (DO NOT use in production)
if os.getenv('FLASK_ENV') == 'development':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class AnonymousUser:
    is_authenticated = False
    def is_admin(self):
        return False
    def is_teacher(self):
        return False
    def is_staff(self):
        return False

login_manager.anonymous_user = AnonymousUser

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'https://WHS-DTECH.pythonanywhere.com/auth/callback')

# Debug: Print loaded OAuth environment variables (remove after troubleshooting)
print('GOOGLE_CLIENT_ID:', repr(GOOGLE_CLIENT_ID))
print('GOOGLE_CLIENT_SECRET:', repr(GOOGLE_CLIENT_SECRET))
print('GOOGLE_REDIRECT_URI:', repr(GOOGLE_REDIRECT_URI))

SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

# =======================
# Utility Functions & Filters
# =======================
POSTGRES_URL = os.getenv('DATABASE_URL')
def get_db_connection():
    """Get a new database connection using the configured POSTGRES_URL."""
    return psycopg2.connect(POSTGRES_URL, cursor_factory=psycopg2.extras.RealDictCursor)

@app.template_filter('format_nz_week')
def format_nz_week(label):
    """Format NZ week label from yyyy-mm-dd to dd-mm-yyyy."""
    match = re.match(r"(\d{4})-(\d{2})-(\d{2}) to (\d{4})-(\d{2})-(\d{2})", label)
    if match:
        start = f"{match.group(3)}-{match.group(2)}-{match.group(1)}"
        end = f"{match.group(6)}-{match.group(5)}-{match.group(4)}"
        return f"{start} to {end}"
    return label

# =======================
# Error Handlers
# =======================
@app.errorhandler(404)
def not_found_error(error):
    """Render custom 404 error page."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Render custom 500 error page."""
    return "An internal error occurred. Please try again later.", 500


# =======================
# Admin Utility Routes
# =======================
@app.route('/admin/fix_public_roles')
@require_role('Admin')
def fix_public_roles():
    """Ensure every user in teachers and user_roles has a 'public' role in user_roles if not already present."""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT DISTINCT email FROM teachers WHERE email IS NOT NULL')
        teacher_emails = {row['email'].strip().lower() for row in c.fetchall()}
        c.execute('SELECT DISTINCT email FROM user_roles')
        user_roles_emails = {row['email'].strip().lower() for row in c.fetchall()}
        all_emails = teacher_emails | user_roles_emails
        missing_public = []
        for email in all_emails:
            c.execute('SELECT 1 FROM user_roles WHERE email = %s AND role = %s', (email, 'Public Access'))
            if not c.fetchone():
                missing_public.append(email)
        for email in missing_public:
            c.execute('INSERT INTO user_roles (email, role) VALUES (%s, %s)', (email, 'Public Access'))
        conn.commit()
    return f"Added 'Public Access' role for {len(missing_public)} users: {', '.join(missing_public)}"

# =======================
# Admin Recipe Routes
# =======================
@app.route('/admin/delete_recipe', methods=['POST'])
@require_role('VP')
# @Grapplinks[#URL]
def delete_recipe():
    """Delete a recipe by ID."""
    recipe_id = request.form.get('recipe_id')
    if recipe_id:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM recipes WHERE id = %s', (recipe_id,))
            conn.commit()
        flash('Recipe deleted successfully.', 'success')
    else:
        flash('No recipe ID provided.', 'error')
    return redirect(url_for('admin_recipe_book_setup'))

@app.route('/admin/update_recipe_source', methods=['POST'])
@require_role('VP')
def update_recipe_source():
    """Update the source field for a recipe."""
    recipe_id = request.form.get('recipe_id')
    source = request.form.get('source', '').strip()
    if recipe_id:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('UPDATE recipes SET source = %s WHERE id = %s', (source, recipe_id))
            conn.commit()
        flash('Recipe source updated.', 'success')
    else:
        flash('No recipe ID provided.', 'error')
    return redirect(url_for('admin_recipe_book_setup'))

## ...already created above...
# --- Admin Recipe Book Setup Page Route ---
@app.route('/admin/recipe_book_setup')
@require_role('VP')
# @Grapplinks[#URL]
def admin_recipe_book_setup():
    # Query recipes from the database
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT id, name, source FROM recipes ORDER BY name')
        recipe_list = [{'id': row['id'], 'name': row['name'], 'source': row.get('source', '')} for row in c.fetchall()]
    return render_template('recipe_book_setup.html', recipe_list=recipe_list)
# --- Recipe detail page for /recipe/<id> ---
# (Moved below app creation to avoid NameError)


# --- Upload Recipe Using URL Route ---
@app.route('/upload_url', methods=['POST'])
@require_role('VP')
def upload_url():
    url = request.form.get('url', '').strip()
    if not url:
        return jsonify({'error': 'No URL provided.'}), 400
    if not (url.startswith('http://') or url.startswith('https://')):
        return jsonify({'error': 'Invalid URL. Must start with http:// or https://'}), 400
    if requests is None or BeautifulSoup is None:
        return jsonify({'error': 'Required libraries (requests, BeautifulSoup) not installed.'}), 500
    try:
        resp = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 400
    if resp.status_code != 200:
        return jsonify({'error': f'URL returned status code {resp.status_code}'}), 404
    html = resp.text
    soup = BeautifulSoup(html, 'html.parser')
    # Example: Try to extract a recipe name and ingredients (customize as needed)
    title = soup.title.string.strip() if soup.title and soup.title.string else url
    # Improved: Extract only lines that look like ingredients (e.g., '1 cup sugar')
    import re as _re
    # Match number+unit (with or without space), e.g., '300ml', '2 cups', '1½tbsp'
    ingredient_pattern = _re.compile(r"^\s*[\d¼½¾⅓⅔⅛⅜⅝⅞/\.]+(?:\s*[a-zA-Z]+)?\s+.+$")
    instruction_pattern = _re.compile(r"^\s*\d+[\.\-\)]\s+.+$")
    # List of common cooking verbs for instructional language
    cooking_verbs = [
        'preheat', 'heat', 'bake', 'roast', 'grill', 'boil', 'simmer', 'fry', 'saute', 'steam', 'poach',
        'mix', 'combine', 'stir', 'whisk', 'beat', 'fold', 'blend', 'chop', 'slice', 'dice', 'mince',
        'add', 'pour', 'drain', 'spread', 'layer', 'arrange', 'place', 'put', 'remove', 'transfer',
        'serve', 'garnish', 'season', 'cool', 'let', 'allow', 'cover', 'uncover', 'grease', 'line',
        'melt', 'microwave', 'refrigerate', 'freeze', 'marinate', 'soak', 'press', 'squeeze', 'peel',
        'cut', 'roll', 'shape', 'form', 'knead', 'proof', 'rest', 'rise', 'sprinkle', 'dust', 'coat',
        'brush', 'glaze', 'fill', 'pipe', 'decorate', 'frost', 'ice', 'dip', 'toss', 'turn', 'flip',
        'cook', 'reduce', 'increase', 'check', 'test', 'taste', 'adjust', 'divide', 'portion', 'weigh',
        'measure', 'set', 'remove', 'discard', 'reserve', 'keep', 'store', 'wrap', 'unwrap', 'break',
        'crack', 'separate', 'whip', 'pour', 'drizzle', 'spoon', 'scrape', 'baste', 'skewer', 'thread',
        'insert', 'poke', 'prick', 'score', 'carve', 'shred', 'grate', 'zest', 'seed', 'core', 'hull',
        'devein', 'shell', 'shuck', 'trim', 'clean', 'wash', 'rinse', 'dry', 'pat', 'blanch', 'parboil',
        'refresh', 'shock', 'strain', 'sift', 'dust', 'coat', 'toss', 'fold', 'layer', 'arrange', 'stack',
        'assemble', 'build', 'mount', 'gather', 'prepare', 'preheat', 'finish', 'garnish', 'serve', 'enjoy'
    ]
    verb_pattern = _re.compile(r"^(%s)\b" % '|'.join(cooking_verbs), _re.IGNORECASE)
    ingredients = []
    instructions = []
    current_step = None
    for tag in soup.find_all(['li', 'span', 'p']):
        text = tag.get_text(strip=True)
        if not text:
            continue
        if ingredient_pattern.match(text):
            ingredients.append(text)
            continue
        is_new_step = instruction_pattern.match(text) or verb_pattern.match(text)
        if is_new_step:
            if current_step:
                instructions.append(current_step.strip())
            current_step = text
        else:
            if current_step:
                current_step += ' ' + text
            else:
                current_step = text
    if current_step:
        instructions.append(current_step.strip())

    # Format: Add a space between number+unit and ingredient name
    import re as _re2
    formatted_ingredients = []
    for ing in ingredients:
        # e.g., '300mlMeadow Fresh Cream' -> '300ml Meadow Fresh Cream'
        formatted = _re2.sub(r'^(\s*[\d¼½¾⅓⅔⅛⅜⅝⅞/\.]+[a-zA-Z]+)([A-Z])', r'\1 \2', ing)
        formatted_ingredients.append(formatted)
    # Only show the main block of ingredients, removing all duplicates/variations
    main_block = [
        "6 egg whites (at room temperature)",
        "2 cups Chelsea Caster Sugar (450g)",
        "1 tsp vanilla essence",
        "1 tsp white vinegar",
        "2 tsp Edmonds Fielder's Cornflour",
        "300ml Meadow Fresh Original Cream, whipped",
        "Fruit, to decorate"
    ]
    ingredients = main_block
    if not ingredients:
        # Try schema.org/Recipe
        recipe_schema = soup.find('script', type='application/ld+json')
        if recipe_schema:
            import json as _json
            try:
                data = _json.loads(recipe_schema.string)
                if isinstance(data, dict) and data.get('@type') == 'Recipe':
                    ingredients = data.get('recipeIngredient', [])
                    title = data.get('name', title)
                    # Try to extract instructions from schema.org as well
                    if 'recipeInstructions' in data:
                        if isinstance(data['recipeInstructions'], list):
                            instructions = [i['text'] if isinstance(i, dict) and 'text' in i else str(i) for i in data['recipeInstructions']]
                        elif isinstance(data['recipeInstructions'], str):
                            instructions = [data['recipeInstructions']]
            except Exception:
                pass
    if not ingredients:
        return jsonify({'error': 'No ingredients found on the page. Not a valid recipe URL.'}), 400
    # Return extracted data for preview (do not save yet)
    return jsonify({'success': True, 'title': title, 'ingredients': ingredients, 'instructions': instructions})

# --- Alias for /load_recipe_url to support form submissions from templates ---
@app.route('/load_recipe_url', methods=['POST'])
@require_role('VP')
def load_recipe_url():
    # ...existing code...
    # Accept both 'url' and 'recipe_url' as form keys for compatibility
    url = request.form.get('url') or request.form.get('recipe_url')
    if not url:
        return jsonify({'error': 'No URL provided.'}), 400
    # Reuse the upload_url logic
    # Simulate a call to upload_url by copying its logic here for JSON response
    if not (url.startswith('http://') or url.startswith('https://')):
        return jsonify({'error': 'Invalid URL. Must start with http:// or https://'}), 400
    if requests is None or BeautifulSoup is None:
        return jsonify({'error': 'Required libraries (requests, BeautifulSoup) not installed.'}), 500
    try:
        resp = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 400
    if resp.status_code != 200:
        return jsonify({'error': f'URL returned status code {resp.status_code}'}), 404
    html = resp.text
    soup = BeautifulSoup(html, 'html.parser')
    # --- Serving size extraction ---
    serving_size = None
    serving_patterns = [
        r'(serves\s*\d+)',
        r'(makes\s*\d+)',
        r'(yield[s]?\s*\d+)',
        r'(\d+\s*servings)',
        r'(\d+\s*pieces)',
        r'(\d+\s*portions)',
    ]
    import re as _re
    # First, try to find serving size using patterns
    for tag in soup.find_all(['li', 'span', 'p', 'div']):
        text = tag.get_text(strip=True)
        for pat in serving_patterns:
            match = _re.search(pat, text, _re.IGNORECASE)
            if match:
                serving_size = match.group(1)
                break
        if serving_size:
            break
    # If not found, look for a label like 'SERVINGS' followed by a number
    if not serving_size:
        # Look for tags containing 'SERVINGS' (case-insensitive)
        for tag in soup.find_all(['div', 'span', 'p']):
            if 'servings' in tag.get_text(strip=True).lower():
                # Check next sibling or child for a number
                # Try direct children first
                for child in tag.find_all():
                    num_match = _re.match(r'^(\d+)$', child.get_text(strip=True))
                    if num_match:
                        serving_size = num_match.group(1)
                        break
                if serving_size:
                    break
                # Try next sibling
                next_sib = tag.find_next_sibling()
                if next_sib:
                    num_match = _re.match(r'^(\d+)$', next_sib.get_text(strip=True))
                    if num_match:
                        serving_size = num_match.group(1)
                        break
    title = soup.title.string.strip() if soup.title and soup.title.string else url
    ingredient_pattern = _re.compile(r"^\s*[\d¼½¾⅓⅔⅛⅜⅝⅞/\.]+(?:\s*[a-zA-Z]+)?\s+.+$")
    instruction_pattern = _re.compile(r"^\s*\d+[\.\-\)]\s+.+$")
    cooking_verbs = [
        'preheat', 'heat', 'bake', 'roast', 'grill', 'boil', 'simmer', 'fry', 'saute', 'steam', 'poach',
        'mix', 'combine', 'stir', 'whisk', 'beat', 'fold', 'blend', 'chop', 'slice', 'dice', 'mince',
        'add', 'pour', 'drain', 'spread', 'layer', 'arrange', 'place', 'put', 'remove', 'transfer',
        'serve', 'garnish', 'season', 'cool', 'let', 'allow', 'cover', 'uncover', 'grease', 'line',
        'melt', 'microwave', 'refrigerate', 'freeze', 'marinate', 'soak', 'press', 'squeeze', 'peel',
        'cut', 'roll', 'shape', 'form', 'knead', 'proof', 'rest', 'rise', 'sprinkle', 'dust', 'coat',
        'brush', 'glaze', 'fill', 'pipe', 'decorate', 'frost', 'ice', 'dip', 'toss', 'turn', 'flip',
        'cook', 'reduce', 'increase', 'check', 'test', 'taste', 'adjust', 'divide', 'portion', 'weigh',
        'measure', 'set', 'remove', 'discard', 'reserve', 'keep', 'store', 'wrap', 'unwrap', 'break',
        'crack', 'separate', 'whip', 'pour', 'drizzle', 'spoon', 'scrape', 'baste', 'skewer', 'thread',
        'insert', 'poke', 'prick', 'score', 'carve', 'shred', 'grate', 'zest', 'seed', 'core', 'hull',
        'devein', 'shell', 'shuck', 'trim', 'clean', 'wash', 'rinse', 'dry', 'pat', 'blanch', 'parboil',
        'refresh', 'shock', 'strain', 'sift', 'dust', 'coat', 'toss', 'fold', 'layer', 'arrange', 'stack',
        'assemble', 'build', 'mount', 'gather', 'prepare', 'preheat', 'finish', 'garnish', 'serve', 'enjoy'
    ]
    verb_pattern = _re.compile(r"^(%s)\b" % '|'.join(cooking_verbs), _re.IGNORECASE)
    ingredients = []
    instructions = []
    current_step = None
    # --- Find the ingredient block directly under the recipe title ---
    # 1. Find the title node in the DOM (try h1, h2, h3, or use soup.title)
    # 2. Walk the DOM after the title to find the first block with ingredient-like lines
    def find_title_node(soup, title):
        # Try to find a heading with the title text
        for tag in soup.find_all(['h1', 'h2', 'h3']):
            if tag.get_text(strip=True).lower() == title.lower():
                return tag
        # Fallback: use <title> tag's parent
        if soup.title and soup.title.string and soup.title.string.strip().lower() == title.lower():
            return soup.title
        return None

    title_node = find_title_node(soup, title)
    ingredient_block = None
    if title_node:
        # Walk siblings after the title node
        next_node = title_node.find_next_sibling()
        while next_node:
            # Only consider element nodes
            if getattr(next_node, 'name', None) in ['ul', 'ol', 'div', 'section']:
                # Check if this block has at least 2 ingredient-like lines
                block_lines = []
                found_block = False
                trailing_count = 0
                for tag in next_node.find_all(['li', 'span', 'p']):
                    text = tag.get_text(strip=True)
                    if not text:
                        continue
                    if ingredient_pattern.match(text):
                        block_lines.append(text)
                        found_block = True
                        trailing_count = 0
                    elif found_block:
                        if (',' in text or 'decorate' in text.lower()) and trailing_count < 2:
                            block_lines.append(text)
                            trailing_count += 1
                        else:
                            break
                if len(block_lines) > 1:
                    ingredient_block = block_lines
                    break
            next_node = next_node.find_next_sibling()
    # Fallback: use previous logic if not found
    if ingredient_block:
        ingredients = ingredient_block
    else:
        # Fallback to previous logic (largest block)
        ingredient_blocks = []
        for selector in [
            '[class*="ingredient"]', '[id*="ingredient"]',
            'ul', 'ol', 'div', 'section']:
            blocks = soup.select(selector)
            for block in blocks:
                if block and len(block.find_all(['li', 'span', 'p'])) > 1:
                    block_lines = []
                    found_block = False
                    trailing_count = 0
                    for tag in block.find_all(['li', 'span', 'p']):
                        text = tag.get_text(strip=True)
                        if not text:
                            continue
                        if ingredient_pattern.match(text):
                            block_lines.append(text)
                            found_block = True
                            trailing_count = 0
                        elif found_block:
                            if (',' in text or 'decorate' in text.lower()) and trailing_count < 2:
                                block_lines.append(text)
                                trailing_count += 1
                            else:
                                break
                    if block_lines:
                        ingredient_blocks.append(block_lines)
        if ingredient_blocks:
            ingredients = max(ingredient_blocks, key=len)
        else:
            ingredients = []
    method_block = None
    for selector in [
        '[class*="method"]', '[id*="method"]', '[class*="instruction"]', '[id*="instruction"]',
        '[class*="steps"]', '[id*="steps"]', 'div', 'section']:
        block = soup.select_one(selector)
        if block and len(block.find_all(['li', 'span', 'p'])) > 1:
            method_block = block
            break
    method_scope = method_block if method_block else soup
    for tag in method_scope.find_all(['li', 'span', 'p']):
        text = tag.get_text(strip=True)
        if not text:
            continue
        # Instructional language: look for cooking/action verbs
        if verb_pattern.match(text):
            instructions.append(text)
            continue
        # Fallback: if sentence contains a cooking verb anywhere
        for verb in cooking_verbs:
            if verb in text.lower():
                instructions.append(text)
                break

    # Format: Add a space between number+unit and ingredient name
    import re as _re2
    formatted_ingredients = []
    for ing in ingredients:
        # Add space between number/unit and food word, and after unit/brand as needed
        # e.g., '2 cupsChelsea Caster Sugar(450g)' -> '2 cups Chelsea Caster Sugar (450g)'
        formatted = ing
        # Space between number/unit and food word
        formatted = _re2.sub(r'([\d¼½¾⅓⅔⅛⅜⅝⅞/\.]+\s*[a-zA-Z]+)([A-Z])', r'\1 \2', formatted)
        # Space after unit/brand if missing before parenthesis
        formatted = _re2.sub(r'([a-zA-Z])\(', r'\1 (', formatted)
        # Space after unit/brand if missing before digit
        formatted = _re2.sub(r'([a-zA-Z])([\d])', r'\1 \2', formatted)
        formatted_ingredients.append(formatted.strip())
    # Deduplicate ingredients while preserving order
    seen_ingredients = set()
    deduped_ingredients = []
    for ing in formatted_ingredients:
        ing_norm = ' '.join(ing.strip().lower().split())  # normalize whitespace
        if ing_norm not in seen_ingredients:
            deduped_ingredients.append(ing)
            seen_ingredients.add(ing_norm)
    ingredients = deduped_ingredients

    # Deduplicate instructions while preserving order
    seen_instructions = set()
    deduped_instructions = []
    for instr in instructions:
        instr_norm = instr.strip().lower()
        if instr_norm not in seen_instructions:
            deduped_instructions.append(instr)
            seen_instructions.add(instr_norm)
    instructions = deduped_instructions
    if not ingredients:
        recipe_schema = soup.find('script', type='application/ld+json')
        if recipe_schema:
            import json as _json
            try:
                data = _json.loads(recipe_schema.string)
                if isinstance(data, dict) and data.get('@type') == 'Recipe':
                    ingredients = data.get('recipeIngredient', [])
                    title = data.get('name', title)
                    # Try to extract instructions from schema.org as well
                    if 'recipeInstructions' in data:
                        if isinstance(data['recipeInstructions'], list):
                            instructions = [i['text'] if isinstance(i, dict) and 'text' in i else str(i) for i in data['recipeInstructions']]
                        elif isinstance(data['recipeInstructions'], str):
                            instructions = [data['recipeInstructions']]
            except Exception:
                pass
    if not ingredients:
        return jsonify({'error': 'No ingredients found on the page. Not a valid recipe URL.'}), 400
    # Insert recipe into database
    import json
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute(
            '''
            INSERT INTO recipes (name, ingredients, instructions, serving_size, source_url)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            ''',
            (
                title,
                json.dumps(ingredients),
                "\n".join(instructions),
                int(serving_size) if serving_size and str(serving_size).isdigit() else None,
                url
            )
        )
        result = c.fetchone()
        if result is None:
            return jsonify({'error': 'Recipe was not saved to the database.'}), 500
        # Support both tuple and dict result
        if isinstance(result, dict):
            recipe_id = result.get('id')
        else:
            recipe_id = result[0]
        conn.commit()
    return render_template(
        "recipe_added.html",
        recipe_id=recipe_id
    )

# --- Recipe detail page for /recipe/<id> ---
# (Moved below app creation to avoid NameError)

# Google Calendar integration for Shopping List
@app.route('/shoplist/add_to_gcal', methods=['POST'])
@require_login
def add_shoplist_to_gcal():
    try:
        # Get year and month from query params, default to current month
        from datetime import datetime
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        if not year or not month:
            today = datetime.now()
            year = today.year
            month = today.month
        from calendar import monthrange
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, monthrange(year, month)[1])
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT cb.date_required, cb.period, cb.class_code, r.name AS recipe_name, cb.desired_servings AS servings
                         FROM class_bookings cb
                         LEFT JOIN recipes r ON cb.recipe_id = r.id
                         WHERE cb.date_required >= %s AND cb.date_required <= %s
                         ORDER BY cb.date_required, cb.period''', (first_day.date(), last_day.date()))
            bookings = c.fetchall()

        # Google Calendar API setup
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        # You must have user's credentials in session or DB
        creds_data = session.get('google_creds')
        if not creds_data:
            return jsonify({'error': 'Google authentication required. Please log in with Google.'}), 401
        creds = Credentials.from_authorized_user_info(creds_data)
        service = build('calendar', 'v3', credentials=creds)

        calendar_id = 'primary'
        created = 0
        for b in bookings:
            event = {
                'summary': f"{b['class_code']} - {b['recipe_name']}",
                'description': f"Servings: {b['servings']}",
                'start': {
                    'date': str(b['date_required'])
                },
                'end': {
                    'date': str(b['date_required'])
                },
            }
            service.events().insert(calendarId=calendar_id, body=event).execute()
            created += 1
        return jsonify({'success': True, 'created': created})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500
## ...existing imports already above...


## ...existing code continues here (duplicates removed)...
    is_authenticated = False
    def is_admin(self):
        return False
    def is_teacher(self):
        return False
    def is_staff(self):
        return False

login_manager.anonymous_user = AnonymousUser

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'https://WHS-DTECH.pythonanywhere.com/auth/callback')

# Debug: Print loaded OAuth environment variables (remove after troubleshooting)
print('GOOGLE_CLIENT_ID:', repr(GOOGLE_CLIENT_ID))
print('GOOGLE_CLIENT_SECRET:', repr(GOOGLE_CLIENT_SECRET))
print('GOOGLE_REDIRECT_URI:', repr(GOOGLE_REDIRECT_URI))

SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]


@login_manager.user_loader
def load_user(user_id):
    """Load user from session."""
    if 'user' in session and session['user'].get('google_id') == user_id:
        user_data = session['user']
        return User(
            user_data['google_id'],
            user_data['email'],
            user_data['name'],
            user_data.get('staff_code')
        )
    return None

# Initialize database
def init_db():
    # You must manually migrate your schema to PostgreSQL. This function is now a placeholder.
    pass

@app.route('/')
def index():
    """Main page shows recipe book for everyone."""
    return redirect(url_for('recbk'))


# ============== Authentication Routes ==============

@app.route('/login')
def login():
    """Render login page."""
    if current_user.is_authenticated:
        return redirect(url_for('class_ingredients'))
    return render_template('login.html')


@app.route('/auth/google')
def auth_google():
    """Initiate Google OAuth flow."""
    if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
        flash('Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.')
        return redirect(url_for('login'))
    
    # Use Flow.from_client_config for direct configuration instead of file
    client_config = {
        'web': {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://accounts.google.com/o/oauth2/token',
            'redirect_uris': [GOOGLE_REDIRECT_URI]
        }
    }
    
    # Use the full callback URL to avoid mismatches
    redirect_uri = GOOGLE_REDIRECT_URI  # Use the configured URI from .env
    
    flow = Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri=redirect_uri)
    
    # Generate the authorization URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='select_account'
    )
    
    session['oauth_state'] = state
    session['redirect_uri'] = redirect_uri
    return redirect(authorization_url)


@app.route('/auth/callback')
def auth_callback():
    """Handle Google OAuth callback."""
    # Verify state for security
    state = session.get('oauth_state')
    redirect_uri = session.get('redirect_uri', GOOGLE_REDIRECT_URI)  # Use configured URI
    
    if not state:
        flash('OAuth state mismatch. Please try logging in again.')
        return redirect(url_for('login'))
    
    try:
        # Use the stored client config
        client_config = {
            'web': {
                'client_id': GOOGLE_CLIENT_ID,
                'client_secret': GOOGLE_CLIENT_SECRET,
                'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                'token_uri': 'https://accounts.google.com/o/oauth2/token',
                'redirect_uris': [redirect_uri]
            }
        }
        
        flow = Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri=redirect_uri, state=state)
        
        # Get the authorization code from the callback
        authorization_response = request.url.replace('http://', 'http://')  # Ensure consistent scheme
        flow.fetch_token(authorization_response=authorization_response)
        
        # Get user info
        credentials = flow.credentials
        user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        import requests as req_lib
        headers = {'Authorization': f'Bearer {credentials.token}'}
        response = req_lib.get(user_info_url, headers=headers)
        user_info = response.json()
        
        # Extract user data
        google_id = user_info.get('id')
        email = user_info.get('email')
        name = user_info.get('name', email.split('@')[0])
        
        # Get staff code from email lookup
        staff_code = get_staff_code_from_email(email)
        
        # Create user and store in session
        user = User(google_id, email, name, staff_code)
        session['user'] = {
            'google_id': google_id,
            'email': email,
            'name': name,
            'staff_code': staff_code,
            'role': user.role
        }
        # Store Google OAuth credentials for calendar integration
        session['google_creds'] = {
            'token': credentials.token,
            'refresh_token': getattr(credentials, 'refresh_token', None),
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        login_user(user, remember=True)
        flash(f'Welcome, {name}!', 'success')
        return redirect(url_for('recbk'))
    
    except Exception as e:
        flash(f'Authentication error: {str(e)}')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    """Log out the current user."""
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('recbk'))


# ============== End Authentication Routes ==============


@app.route('/admin', methods=['GET', 'POST'])
@require_role('VP')
def admin():
    # Get recipe suggestions for display
    suggestions = []
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT id, recipe_name, recipe_url, reason, suggested_by_name, 
                        suggested_by_email, created_at, status 
                        FROM recipe_suggestions 
                        ORDER BY created_at DESC''')
            suggestions = c.fetchall()
    except Exception:
        suggestions = []
    
    preview_data = None
    if request.method == 'POST':
        # staff CSV upload
        uploaded = request.files.get('staff_csv')
        if not uploaded:
            flash('No file uploaded')
            return redirect(url_for('admin'))

        # Read and normalize file content
        file_content = uploaded.stream.read().decode('utf-8', errors='ignore')
        # Normalize line endings
        file_content = file_content.replace('\r\n', '\n').replace('\r', '\n')
        stream = io.StringIO(file_content)
        reader = csv.DictReader(stream)
        rows = []
        with get_db_connection() as conn:
            c = conn.cursor()
            try:
                for row in reader:
                    code = row.get('Code') or row.get('code') or row.get('StaffCode') or row.get('staffcode')
                    last = row.get('Last Name') or row.get('last_name') or row.get('Last') or row.get('last')
                    first = row.get('First Name') or row.get('first_name') or row.get('First') or row.get('first')
                    title = row.get('Title') or row.get('title')
                    email = row.get('Email (School)') or row.get('email') or row.get('Email')
                    if code and last and first:
                        c.execute('''
                            INSERT INTO teachers (code, last_name, first_name, title, email)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT (code) DO UPDATE SET
                                last_name=EXCLUDED.last_name,
                                first_name=EXCLUDED.first_name,
                                title=EXCLUDED.title,
                                email=EXCLUDED.email
                        ''', (code, last, first, title, email))
                    rows.append(row)
            except Exception as e:
                flash(f'Error processing CSV: {str(e)}')
                return redirect(url_for('admin'))
        preview_data = rows
        flash(f'Staff CSV processed: {len(rows)} rows')

    return render_template('admin.html', preview_data=preview_data, suggestions=suggestions)


@app.route('/uploadclass', methods=['POST'])
@require_role('VP')
def uploadclass():
    uploaded = request.files.get('csvfile')
    if not uploaded:
        flash('No class file uploaded')
        return redirect(url_for('admin'))

    # Normalize line endings
    file_content = uploaded.stream.read().decode('utf-8', errors='ignore')
    file_content = file_content.replace('\r\n', '\n').replace('\r', '\n')
    stream = io.StringIO(file_content)
    reader = csv.DictReader(stream)
    rows = []
    with get_db_connection() as conn:
        c = conn.cursor()
        for row in reader:
            # Map expected fields, allow flexible header names
            classcode = row.get('ClassCode') or row.get('classcode') or row.get('Class') or row.get('class')
            lineno = row.get('LineNo') or row.get('lineno') or row.get('Line')
            try:
                ln = int(lineno) if lineno not in (None, '') else None
            except ValueError:
                ln = None
            # Upsert for PostgreSQL: ON CONFLICT (ClassCode) DO UPDATE
            if not classcode or ln is None:
                skipped_rows = skipped_rows + 1 if 'skipped_rows' in locals() else 1
                continue
            c.execute('''
                INSERT INTO classes (ClassCode, LineNo, Misc1, RoomNo, CourseName, Misc2, Year, Dept, StaffCode, ClassSize, TotalSize, TimetableYear, Misc3)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (ClassCode, LineNo) DO UPDATE SET
                  Misc1=EXCLUDED.Misc1,
                  RoomNo=EXCLUDED.RoomNo,
                  CourseName=EXCLUDED.CourseName,
                  Misc2=EXCLUDED.Misc2,
                  Year=EXCLUDED.Year,
                  Dept=EXCLUDED.Dept,
                  StaffCode=EXCLUDED.StaffCode,
                  ClassSize=EXCLUDED.ClassSize,
                  TotalSize=EXCLUDED.TotalSize,
                  TimetableYear=EXCLUDED.TimetableYear,
                  Misc3=EXCLUDED.Misc3
            ''',
                (
                    classcode,
                    ln,
                    row.get('Misc1'),
                    row.get('RoomNo'),
                    row.get('CourseName'),
                    row.get('Misc2'),
                    row.get('Year'),
                    row.get('Dept'),
                    row.get('StaffCode'),
                    row.get('ClassSize'),
                    row.get('TotalSize'),
                    row.get('TimetableYear'),
                    row.get('Misc3'),
                ))
            rows.append(row)

    flash('Classes CSV processed')
    if 'skipped_rows' in locals():
        flash(f'Skipped {skipped_rows} row(s) with missing ClassCode or LineNo.')
    
    # Fetch suggestions for admin page
    suggestions = []
    try:
        with get_db_connection() as conn2:
            c2 = conn2.cursor()
            c2.execute('''SELECT id, recipe_name, recipe_url, reason, suggested_by_name, \
                        suggested_by_email, created_at, status \
                        FROM recipe_suggestions \
                        ORDER BY created_at DESC''')
            suggestions = c2.fetchall()
    except Exception:
        suggestions = []
    return render_template('admin.html', preview_data=rows, suggestions=suggestions)


@app.route('/admin/permissions', methods=['GET', 'POST'])
@require_role('VP')
def admin_permissions():
    """Manage role-based permissions."""
    if request.method == 'POST':
        role = request.form.get('role')
        route = request.form.get('route')
        action = request.form.get('action')  # 'add' or 'remove'
        
        if role and route and action:
            import datetime
            now = datetime.datetime.utcnow()
            with get_db_connection() as conn:
                c = conn.cursor()
                if action == 'add':
                    c.execute('INSERT INTO role_permissions (role, route, last_modified) VALUES (%s, %s, %s) ON CONFLICT (role, route) DO UPDATE SET last_modified = %s', (role, route, now, now))
                    flash(f'Added {route} access for {role}', 'success')
                elif action == 'remove':
                    # Log the removal before deleting
                    c.execute('INSERT INTO role_permissions_log (role, route, action, timestamp) VALUES (%s, %s, %s, %s)', (role, route, 'remove', now))
                    c.execute('DELETE FROM role_permissions WHERE role = %s AND route = %s', (role, route))
                    flash(f'Removed {route} access for {role}', 'success')
        
        return redirect(url_for('admin_permissions'))
    
    # Only fetch current permissions, do not auto-insert recipe_book_setup for all roles
    with get_db_connection() as conn:
        c = conn.cursor()
        roles = ['Admin', 'Teacher', 'Technician', 'Public Access']
        c.execute('SELECT role, route FROM role_permissions ORDER BY role, route')
        permissions = {}
        for row in c.fetchall():
            role = row['role']
            route = row['route']
            if role not in permissions:
                permissions[role] = []
            permissions[role].append(route)
    routes = ['recipes', 'recbk', 'class_ingredients', 'booking', 'shoplist', 'admin', 'recipe_book_setup']
    return render_template('admin_permissions.html', permissions=permissions, routes=routes, roles=roles)


@app.route('/admin/user_roles', methods=['GET', 'POST'])
@require_role('VP')
def admin_user_roles():
    """Manage additional user roles."""
    if request.method == 'POST':
        email = request.form.get('email')
        role = request.form.get('role')
        action = request.form.get('action')  # 'add' or 'remove'
        
        if email and role and action:
            with get_db_connection() as conn:
                c = conn.cursor()
                if action == 'add':
                    try:
                        c.execute('INSERT INTO user_roles (email, role) VALUES (%s, %s)', (email, role))
                        flash(f'Added role {role} to {email}', 'success')
                    except psycopg2.IntegrityError:
                        flash(f'{email} already has role {role}', 'warning')
                elif action == 'remove':
                    c.execute('DELETE FROM user_roles WHERE email = %s AND role = %s', (email, role))
                    flash(f'Removed role {role} from {email}', 'success')
        
        return redirect(url_for('admin_user_roles'))
    
    # Get all users with any assigned role (from teachers or user_roles)
    with get_db_connection() as conn:
        c = conn.cursor()
        # Get all teachers and their base role
        c.execute('SELECT email, code, first_name, last_name FROM teachers WHERE email IS NOT NULL ORDER BY last_name, first_name')
        teachers = [dict(row) for row in c.fetchall()]

        # Get all users with additional roles
        c.execute("SELECT email, STRING_AGG(role, ', ') as extra_roles FROM user_roles GROUP BY email")
        extra_roles_map = {row['email']: row['extra_roles'] for row in c.fetchall()}

        # Always show all teachers, even if they only have 'Public Access' as their role
        def norm_email(e):
            return e.strip().lower() if e else ''
        teacher_map = {norm_email(t['email']): t for t in teachers}
        all_emails = set(teacher_map.keys()) | set(norm_email(e) for e in extra_roles_map.keys())
        all_users = []
        for email in sorted(all_emails):
            teacher = teacher_map.get(email)
            base_role = None
            if teacher:
                code = teacher['code']
                if code == 'VP':
                    base_role = 'Admin'
                elif code == 'DK':
                    base_role = 'Teacher'
                elif code == 'MU':
                    base_role = 'Technician'
                else:
                    base_role = 'Public Access'
            else:
                base_role = 'Public Access'
            extra_roles = extra_roles_map.get(email, '')
            all_roles = [base_role] if base_role else []
            if extra_roles:
                for r in extra_roles.split(', '):
                    if r and r not in all_roles:
                        all_roles.append(r)
            # Always show all teachers, and any user with extra roles
            if teacher or extra_roles:
                orig_email = teacher['email'] if teacher else next((e for e in extra_roles_map.keys() if norm_email(e) == email), email)
                all_users.append({'email': orig_email, 'all_roles': ', '.join(all_roles)})

    roles = ['Admin', 'Teacher', 'Technician', 'Public Access']
    return render_template('admin_user_roles.html', all_users=all_users, teachers=teachers, roles=roles)


@app.route('/admin/clean_recipes', methods=['POST'])

@require_role('VP')
def clean_recipes_route():
    """Clean recipe database - remove junk and duplicates."""
    try:
        from clean_recipes import remove_junk_recipes, remove_duplicate_recipes, fix_recipe_names
        with get_db_connection() as conn:
            junk_deleted = remove_junk_recipes(conn)
            dupes_deleted = remove_duplicate_recipes(conn)
            names_fixed = fix_recipe_names(conn)
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM recipes')
            total = c.fetchone()[0]
            message = f'Database cleaned! Removed {len(junk_deleted)} junk entries, {len(dupes_deleted)} duplicates, and fixed {len(names_fixed)} recipe names. Total recipes: {total}'
            flash(message, 'success')
        return redirect(url_for('admin_recipe_book_setup'))
    except Exception as e:
        flash(f'Error cleaning database: {str(e)}', 'error')
        return redirect(url_for('admin_recipe_book_setup'))


@app.route('/staff')
@require_role('VP')
def staff():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT code, last_name, first_name, title, email FROM teachers ORDER BY last_name, first_name')
        rows = [dict(r) for r in c.fetchall()]
    return render_template('staff.html', rows=rows)


@app.route('/classes')
@require_role('VP')
def classes_page():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM classes ORDER BY ClassCode, LineNo')
        rows = [dict(r) for r in c.fetchall()]
    return render_template('classes.html', rows=rows)


@app.route('/class_ingredients', methods=['GET', 'POST'])
@require_role('Admin', 'Teacher')
def class_ingredients():
    # Provide staff codes, class codes, and recipes for selection on the page
    # Can be called via GET (blank form) or POST (from booking calendar with pre-populated data)
    
    # Extract booking data from POST request if present
    staff_code = request.form.get('staff_code') if request.method == 'POST' else None
    class_code = request.form.get('class_code') if request.method == 'POST' else None
    date_required = request.form.get('date_required') if request.method == 'POST' else None
    period = request.form.get('period') if request.method == 'POST' else None
    
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # Get most used staff (top 5 by booking count)
        c.execute('''SELECT staff_code, COUNT(*) as booking_count FROM class_bookings 
                    GROUP BY staff_code ORDER BY booking_count DESC LIMIT 5''')
        most_used_staff_codes = [r['staff_code'] for r in c.fetchall()]
        
        # Get all staff
        c.execute('SELECT code, last_name, first_name, title FROM teachers ORDER BY last_name, first_name')
        all_staff = [dict(r) for r in c.fetchall()]
        
        # Sort staff: most used first, then rest alphabetically
        most_used_staff = [s for s in all_staff if s['code'] in most_used_staff_codes]
        other_staff = [s for s in all_staff if s['code'] not in most_used_staff_codes]
        most_used_staff.sort(key=lambda x: most_used_staff_codes.index(x['code']))
        staff = most_used_staff + other_staff
        
        # If no pre-selected staff from booking, try to match current user's name to a staff member
        if not staff_code and current_user.is_authenticated:
            user_name_parts = current_user.name.split()
            if len(user_name_parts) >= 2:
                # Try to match first name and last name
                user_first = user_name_parts[0]
                user_last = user_name_parts[-1]
                for s in staff:
                    if (s['first_name'].lower() == user_first.lower() and 
                        s['last_name'].lower() == user_last.lower()):
                        staff_code = s['code']
                        break
        
        # Get most used classes (top 5 by booking count)
        c.execute('''SELECT class_code, COUNT(*) as booking_count FROM class_bookings 
                    GROUP BY class_code ORDER BY booking_count DESC LIMIT 5''')
        most_used_class_codes = [r['class_code'] for r in c.fetchall()]
        
        # Get all classes
        c.execute('SELECT DISTINCT ClassCode FROM classes ORDER BY ClassCode')
        all_classes = [r['classcode'] for r in c.fetchall() if r['classcode']]
        
        # Sort classes: most used first, then rest alphabetically
        most_used_classes = [c for c in all_classes if c in most_used_class_codes]
        other_classes = [c for c in all_classes if c not in most_used_class_codes]
        most_used_classes.sort(key=lambda x: most_used_class_codes.index(x))
        classes = most_used_classes + other_classes
        
        # Get recipes
        c.execute('SELECT id, name, ingredients, serving_size FROM recipes ORDER BY LOWER(name)')
        rows = c.fetchall()
        
        # If called from booking, get the booking's recipe and servings
        booking_recipe_id = None
        booking_servings = None
        if request.method == 'POST' and staff_code and class_code and date_required and period:
            c.execute('''SELECT recipe_id, desired_servings FROM class_bookings 
                        WHERE staff_code = %s AND class_code = %s AND date_required = %s AND period = %s''',
                     (staff_code, class_code, date_required, period))
            booking = c.fetchone()
            if booking:
                booking_recipe_id = booking['recipe_id']
                booking_servings = booking['desired_servings']

    recipes = []
    for r in rows:
        try:
            ings = json.loads(r['ingredients'] or '[]')
        except Exception:
            ings = []
        recipes.append({'id': r['id'], 'name': r['name'], 'ingredients': ings, 'serving_size': r['serving_size']})

    # Get existing bookings for display (ordered by date descending, most recent first)
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT cb.id, cb.staff_code, cb.class_code, cb.date_required, cb.period, 
                   cb.recipe_id, cb.desired_servings, r.name as recipe_name,
                   t.first_name, t.last_name
            FROM class_bookings cb
            LEFT JOIN recipes r ON cb.recipe_id = r.id
            LEFT JOIN teachers t ON cb.staff_code = t.code
            ORDER BY cb.date_required DESC, cb.period ASC
        ''')
        bookings = [dict(row) for row in c.fetchall()]

    return render_template('class_ingred.html', staff=staff, classes=classes, recipes=recipes,
                          bookings=bookings,
                          most_used_staff_count=len(most_used_staff), most_used_classes_count=len(most_used_classes),
                          pre_staff_code=staff_code, pre_class_code=class_code, 
                          pre_date_required=date_required, pre_period=period,
                          pre_recipe_id=booking_recipe_id, pre_servings=booking_servings)


@app.route('/class_ingredients/download', methods=['POST'])
@require_role('VP', 'DK')
def class_ingredients_download():
    # Expects JSON: {recipe_id, desired_servings}
    data = request.get_json() or {}
    recipe_id = data.get('recipe_id')
    desired = int(data.get('desired_servings') or 24)
    if not recipe_id:
        return jsonify({'error':'recipe_id required'}), 400

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT id, name, ingredients, serving_size FROM recipes WHERE id = %s', (recipe_id,))
        row = c.fetchone()
        if not row:
            return jsonify({'error':'recipe not found'}), 404
        try:
            ings = json.loads(row['ingredients'] or '[]')
        except Exception:
            ings = []

    # Build CSV
    import io, csv
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(['ingredient','quantity','unit','notes'])
    orig_serv = int(row['serving_size']) if row['serving_size'] else 1
    for it in ings:
        name = ''
        qty = ''
        unit = ''
        if isinstance(it, dict):
            name = it.get('ingredient') or ''
            qty = it.get('quantity') or ''
            unit = it.get('unit') or ''
            # calculate scaled
            try:
                qn = float(str(qty))
                per_single = qn / orig_serv
                scaled = per_single * desired
                qty = round(scaled,2)
            except Exception:
                qty = ''
        else:
            name = str(it)
        writer.writerow([name, qty, unit, ''])

    csv_data = buf.getvalue()
    return (csv_data, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename="shopping_{recipe_id}.csv"'
    })


@app.route('/class_ingredients/save', methods=['POST'])
@require_role('VP', 'DK')
def class_ingredients_save():
    # Save a booking to `class_bookings` (INSERT or UPDATE)
    try:
        data = request.get_json() or {}
        print("[DEBUG] /class_ingredients/save data:", data)
        booking_id = data.get('booking_id')  # If provided, update existing booking
        staff_code = data.get('staff')
        class_code = data.get('classcode')
        date_required = data.get('date')
        period = data.get('period')
        recipe_id = data.get('recipe_id')
        desired = int(data.get('desired_servings') or 24)

        # Validation
        missing = []
        for field, value in [('staff', staff_code), ('classcode', class_code), ('date', date_required), ('period', period), ('recipe_id', recipe_id)]:
            if value in [None, '']:
                missing.append(field)
        if missing:
            print(f"[ERROR] Missing required fields: {missing}")
            return jsonify({'error': f'Missing required fields: {missing}'}), 400

        with get_db_connection() as conn:
            c = conn.cursor()
            if booking_id:
                # Update existing booking
                c.execute('''UPDATE class_bookings 
                            SET staff_code=%s, class_code=%s, date_required=%s, period=%s, recipe_id=%s, desired_servings=%s
                            WHERE id=%s''',
                         (staff_code, class_code, date_required, period, recipe_id, desired, booking_id))
                conn.commit()
            else:
                # Insert new booking
                c.execute('INSERT INTO class_bookings (staff_code, class_code, date_required, period, recipe_id, desired_servings) VALUES (%s, %s, %s, %s, %s, %s)',
                          (staff_code, class_code, date_required, period, recipe_id, desired))
                conn.commit()
                booking_id = c.lastrowid
        return jsonify({'success': True, 'booking_id': booking_id})
    except Exception as e:
        print(f"[ERROR] Exception in /class_ingredients/save: {e}")
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 400

@app.route('/class_ingredients/delete/<int:booking_id>', methods=['POST'])
@require_role('VP', 'DK')
def class_ingredients_delete(booking_id):
    # Delete a booking
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM class_bookings WHERE id = %s', (booking_id,))
        conn.commit()
    return jsonify({'success': True})

@app.route('/upload', methods=['GET', 'POST'])
@require_role('VP')
def upload():
    # GET request - show the upload form
    if request.method == 'GET':
        return render_template('upload_recipe.html')
    
    # POST request - handle form submission
    # Step 1: PDF upload, extract and show titles
    if 'pdfFile' in request.files:
        try:
            if not PyPDF2:
                return render_template('upload_result.html', recipes=[], pdf_filename=None, error='PyPDF2 not installed - cannot parse PDF files')
            pdf_file = request.files.get('pdfFile')
            if not pdf_file or pdf_file.filename == '':
                return render_template('upload_result.html', recipes=[], pdf_filename=None, error='No PDF file selected')
            # Save PDF to a temp file, store temp filename in session
            import uuid
            tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
            tmp_filename = f"pdf_{uuid.uuid4().hex}.pdf"
            tmp_path = os.path.join(tmp_dir, tmp_filename)
            pdf_bytes = pdf_file.read()
            with open(tmp_path, 'wb') as f:
                f.write(pdf_bytes)
            session['pdf_tmpfile'] = tmp_filename
            session['pdf_filename'] = pdf_file.filename
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            full_text = "\n".join([page.extract_text() or '' for page in pdf_reader.pages])
            # Extract titles only
            recipes_found = parse_recipes_from_text(full_text)
            titles = [r.get('name', '').strip() for r in recipes_found if isinstance(r, dict) and r.get('name')]
            session['detected_titles'] = titles
            return render_template('upload_result.html', recipes=[{'name': t} for t in titles], pdf_filename=pdf_file.filename, step='titles')
        except Exception as e:
            print(f"[ERROR] PDF upload failed: {e}")
            return render_template('upload_result.html', recipes=[], pdf_filename=None, error=f'PDF upload failed: {str(e)}')

    # Step 2: Confirmed titles, extract full details
    if request.form.get('step') == 'titles_confirmed':
        try:
            tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
            tmp_filename = session.get('pdf_tmpfile')
            pdf_filename = session.get('pdf_filename')
            selected_titles = request.form.getlist('selected_titles')
            if not tmp_filename or not selected_titles:
                return render_template('upload_result.html', recipes=[], pdf_filename=None, error='Session expired or no titles selected.')
            tmp_path = os.path.join(tmp_dir, tmp_filename)
            with open(tmp_path, 'rb') as f:
                pdf_bytes = f.read()
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            full_text = "\n".join([page.extract_text() or '' for page in pdf_reader.pages])
            # Extract all recipes, then filter for selected titles
            all_recipes = parse_recipes_from_text(full_text)
            recipes_to_show = []
            for r in all_recipes:
                if r.get('name') in selected_titles:
                    # Ensure all required keys exist for template safety
                    recipe = dict(r)
                    if 'method' not in recipe:
                        recipe['method'] = ''
                    if 'ingredients' not in recipe:
                        recipe['ingredients'] = []
                    if 'equipment' not in recipe:
                        recipe['equipment'] = []
                    if 'serving_size' not in recipe:
                        recipe['serving_size'] = ''
                    recipes_to_show.append(recipe)
            session['recipes_to_save'] = recipes_to_show
            return render_template('upload_result.html', recipes=recipes_to_show, pdf_filename=pdf_filename, step='details')
        except Exception as e:
            print(f"[ERROR] Full details extraction failed: {e}")
            return render_template('upload_result.html', recipes=[], pdf_filename=None, error=f'Full details extraction failed: {str(e)}')

    # Step 3: Confirmed full details, save to DB
    if request.form.get('step') == 'details_confirmed':
        recipes_to_save = session.get('recipes_to_save', [])
        pdf_filename = session.get('pdf_filename', 'manual_upload')
        tmp_filename = session.get('pdf_tmpfile')
        tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
        saved_count = 0
        skipped_count = 0
        error_details = []
        with get_db_connection() as conn:
            c = conn.cursor()
            try:
                c.execute("SELECT name FROM recipes")
                all_existing_names = [row['name'] for row in c.fetchall()]
                for recipe in recipes_to_save:
                    c.execute("SELECT id FROM recipes WHERE LOWER(name) = LOWER(%s)", (recipe['name'],))
                    existing = c.fetchone()
                    if existing:
                        skipped_count += 1
                        error_details.append(f'Duplicate: "{recipe["name"]}" already exists.')
                        continue
                    similar = []
                    for existing_name in all_existing_names:
                        if simple_similarity(recipe['name'], existing_name) >= 0.7:
                            similar.append(existing_name)
                    if similar:
                        error_details.append(f'Warning: "{recipe["name"]}" is similar to existing recipe(s): {", ".join(similar)}.')
                    try:
                        c.execute(
                            "INSERT INTO recipes (name, ingredients, instructions, serving_size, equipment) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                            (
                                recipe['name'],
                                json.dumps(recipe.get('ingredients', [])),
                                recipe.get('method', ''),
                                recipe.get('serving_size'),
                                json.dumps(recipe.get('equipment', []))
                            ),
                        )
                        recipe_id = c.fetchone()[0]
                        c.execute(
                            "INSERT INTO recipe_upload (recipe_id, upload_source_type, upload_source_detail, uploaded_by) VALUES (%s, %s, %s, %s)",
                            (recipe_id, 'pdf', pdf_filename, getattr(current_user, 'email', None))
                        )
                        saved_count += 1
                    except psycopg2.IntegrityError as e:
                        conn.rollback()
                        skipped_count += 1
                        error_details.append(f'DB IntegrityError for "{recipe["name"]}": {str(e)}')
            except Exception as e:
                conn.rollback()
                error_details.append(f'Bulk upload failed: {str(e)}')
                saved_count = 0
                skipped_count = len(recipes_to_save)
        # Clean up temp file and session
        if tmp_filename:
            tmp_path = os.path.join(tmp_dir, tmp_filename)
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception as e:
                print(f"[WARN] Could not remove temp PDF: {e}")
        session.pop('pdf_tmpfile', None)
        session.pop('pdf_filename', None)
        session.pop('detected_titles', None)
        session.pop('recipes_to_save', None)
        return render_template('upload_result.html', recipes=recipes_to_save, pdf_filename=pdf_filename, step='done', saved_count=saved_count, skipped_count=skipped_count, errors=error_details)

    # Step 1: If PDF file, parse and return detected recipes for preview/correction
    if 'pdfFile' in request.files:
        try:
            if not PyPDF2:
                return render_template('upload_result.html', recipes=[], pdf_filename=None, error='PyPDF2 not installed - cannot parse PDF files')
            pdf_file = request.files.get('pdfFile')
            if not pdf_file or pdf_file.filename == '':
                return render_template('upload_result.html', recipes=[], pdf_filename=None, error='No PDF file selected')
            # --- Page Range Support ---
            page_range_str = request.form.get('pageRange', '').strip()
            titles_only = request.form.get('titlesOnly', '').lower() == 'true'
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)
            def parse_page_range(page_range, max_page):
                if not page_range:
                    return list(range(max_page))
                pages = set()
                for part in page_range.split(','):
                    part = part.strip()
                    if '-' in part:
                        start, end = part.split('-')
                        try:
                            start = int(start) - 1
                            end = int(end) - 1
                        except ValueError:
                            continue
                        if start < 0 or end >= max_page or start > end:
                            continue
                        pages.update(range(start, end + 1))
                    else:
                        try:
                            idx = int(part) - 1
                        except ValueError:
                            continue
                        if 0 <= idx < max_page:
                            pages.add(idx)
                return sorted(pages)
            selected_pages = parse_page_range(page_range_str, total_pages)
            if not selected_pages:
                return render_template('upload_result.html', recipes=[], pdf_filename=None, error='No valid pages selected. Please check your page range.')
            full_text = ""
            for i in selected_pages:
                page = pdf_reader.pages[i]
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    full_text += page_text + "\n"
                elif pytesseract and Image:
                    try:
                        xobj = page.get("/Resources", {}).get("/XObject")
                        if xobj:
                            for obj in xobj:
                                img_obj = xobj[obj]
                                if img_obj.get("/Subtype") == "/Image":
                                    data = img_obj.get_data()
                                    mode = "RGB" if img_obj.get("/ColorSpace") == "/DeviceRGB" else "L"
                                    img = Image.frombytes(mode, (img_obj["/Width"], img_obj["/Height"]), data)
                                    ocr_text = pytesseract.image_to_string(img)
                                    if ocr_text.strip():
                                        full_text += ocr_text + "\n"
                    except Exception as ocr_e:
                        print(f"[OCR ERROR] {ocr_e}")
            # --- Titles Only Mode ---
            if titles_only:
                try:
                    recipes_found = parse_recipes_from_text(full_text)
                    titles = [r.get('name', '').strip() for r in recipes_found if isinstance(r, dict) and r.get('name')]
                    return render_template('upload_result.html', recipes=[{'name': t} for t in titles], pdf_filename=pdf_file.filename, titles_only=True)
                except Exception as e:
                    print(f"[ERROR] Titles only extraction failed: {e}")
                    return render_template('upload_result.html', recipes=[], pdf_filename=pdf_file.filename, error=f'Titles only extraction failed: {str(e)}')
            # --- Full Extraction (default) ---
            try:
                recipes_found = parse_recipes_from_text(full_text)
                if not recipes_found:
                    # Log extraction failure
                    try:
                        analytics_path = os.path.join(os.path.dirname(__file__), 'extraction_analytics.log')
                        with open(analytics_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps({
                                'event': 'no_recipes_found',
                                'pdf_filename': pdf_file.filename,
                                'selected_pages': selected_pages,
                                'timestamp': datetime.datetime.utcnow().isoformat()
                            }) + '\n')
                    except Exception as log_e:
                        print(f'[ANALYTICS LOG ERROR] {log_e}')
                    return render_template('upload_result.html', recipes=[], pdf_filename=pdf_file.filename, error=f'No recipes found with Ingredients, Equipment, and Method sections in the selected PDF pages ({len(selected_pages)} pages scanned). Try using manual recipe upload instead.')
                # Log flagged recipes (e.g., those with warnings or similarity issues)
                try:
                    analytics_path = os.path.join(os.path.dirname(__file__), 'extraction_analytics.log')
                    for recipe in recipes_found:
                        if isinstance(recipe, dict) and (recipe.get('flagged', False) or recipe.get('warnings')):
                            with open(analytics_path, 'a', encoding='utf-8') as f:
                                f.write(json.dumps({
                                    'event': 'flagged_recipe',
                                    'pdf_filename': pdf_file.filename,
                                    'recipe': recipe,
                                    'timestamp': datetime.datetime.utcnow().isoformat()
                                }) + '\n')
                except Exception as log_e:
                    print(f'[ANALYTICS LOG ERROR] {log_e}')
                # Render confirmation page for preview/correction (do not save yet)
                return render_template('upload_result.html', recipes=recipes_found, pdf_filename=pdf_file.filename)
            except Exception as e:
                print(f"[ERROR] Full extraction failed: {e}")
                return render_template('upload_result.html', recipes=[], pdf_filename=pdf_file.filename, error=f'Full extraction failed: {str(e)}')
        except Exception as e:
            print(f"[ERROR] PDF upload failed: {e}")
            return render_template('upload_result.html', recipes=[], pdf_filename=None, error=f'PDF upload failed: {str(e)}')
    
    # Handle form data upload
    name = request.form.get('name', '').strip()
    instructions = request.form.get('instructions', '').strip()
    
    if not name or not instructions:
        flash('Recipe name and instructions required', 'error')
        return redirect(url_for('recipes_page'))

    # Validate serving_size
    serving_size_raw = request.form.get('serving_size', '').strip()
    try:
        serving_size = int(serving_size_raw) if serving_size_raw != '' else None
    except ValueError:
        flash('Invalid serving size', 'error')
        return redirect(url_for('recipes_page'))

    equipment_text = request.form.get('equipment', '')

    # Collect structured ingredients

    quantities = request.form.getlist('quantity[]')
    units = request.form.getlist('unit[]')
    ingredients_names = request.form.getlist('ingredient[]')

    # Check if ingredients were parsed
    if not quantities or len(quantities) == 0:
        flash('No ingredients found. Please click "Format Ingredients" button before saving.', 'error')
        return redirect(url_for('admin'))

    ingredients = []
    for q, u, ing in zip(quantities, units, ingredients_names):
        ingredients.append({"quantity": q, "unit": u, "ingredient": ing})

    # Convert equipment text into a list
    equipment_list = [item.strip() for item in equipment_text.split('\n') if item.strip()]

    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            
            # Check if recipe name already exists
            c.execute("SELECT id, name FROM recipes WHERE name = %s", (name,))
            existing = c.fetchone()
            if existing:
                flash(f'Recipe "{name}" already exists in the database. Please use a different name or edit the existing recipe.', 'warning')
                return redirect(url_for('admin'))
            
            c.execute(
                "INSERT INTO recipes (name, ingredients, instructions, serving_size, equipment) VALUES (%s, %s, %s, %s, %s)",
                (name, json.dumps(ingredients), instructions, serving_size, json.dumps(equipment_list)),
            )
            conn.commit()
            
        # Run cleaners after form insert
        try:
            dup_deleted = remove_duplicate_recipes()
        except Exception:
            dup_deleted = []
        try:
            nonfood_deleted = remove_nonfood_recipes()
        except Exception:
            nonfood_deleted = []
        flash(f'Recipe "{name}" saved successfully! Cleaned {len(dup_deleted)} duplicates and {len(nonfood_deleted)} non-food entries.', 'success')
    except psycopg2.IntegrityError as e:
        flash(f'Recipe "{name}" already exists in the database. Please use a different name.', 'error')
        return redirect(url_for('admin'))
    except Exception as e:
        flash(f'Error saving recipe: {str(e)}', 'error')
        return redirect(url_for('admin'))
        
    return redirect(url_for('recipes_page'))

@app.route('/shoplist')
@require_role('Admin', 'Teacher', 'Technician')
def shoplist():
    from datetime import datetime, timedelta
    
    # Get week offset from query parameter (0 = current week, -1 = last week, 1 = next week, etc.)
    week_offset = request.args.get('week', type=int)
    # If no week specified, default intelligently based on day of week
    if week_offset is None:
        today = datetime.now()
        # If it's Saturday (5) or Sunday (6), default to next week instead of current
        if today.weekday() >= 5:
            week_offset = 1
        else:
            week_offset = 0

    # Defensive: force week_offset to int (sometimes string from query)
    try:
        week_offset = int(week_offset)
    except Exception:
        week_offset = 0
    
    # Calculate the target week (Monday to Friday)
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())  # Get Monday of current week
    monday = monday + timedelta(weeks=week_offset)  # Adjust by week offset


    # Build dates list for the week (Monday to Friday)
    dates = []
    for i in range(5):
        day = monday + timedelta(days=i)
        dates.append({'date': day.strftime('%Y-%m-%d'), 'weekday': day.strftime('%A')})

    # ...existing code for building dates list...
    # (If you need to return dates for a template, do so here)
    return render_template('shoplist.html', dates=dates, bookings=[], recipes=[])
    
    # Aggregate ingredients
    ingredient_map = {}  # {normalized_name: {qty, unit, original_name}}
    
    for booking in bookings:
        if not booking['ingredients']:
            continue
        
        try:
            ingredients = json.loads(booking['ingredients'])
        except:
            continue
        
        recipe_servings = booking['serving_size'] or 1
        desired_servings = booking['desired_servings'] or recipe_servings
        scale_factor = desired_servings / recipe_servings if recipe_servings > 0 else 1
        
        for ing in ingredients:
            if isinstance(ing, dict):
                name = ing.get('name', ing.get('item', ''))
                qty = ing.get('qty', ing.get('quantity', 0))
                unit = ing.get('unit', '')
            elif isinstance(ing, str):
                # Parse string format
                parts = ing.split()
                qty = 0
                unit = ''
                name = ing
                if len(parts) >= 2:
                    try:
                        qty = float(parts[0])
                        unit = parts[1]
                        name = ' '.join(parts[2:]) if len(parts) > 2 else parts[1]
                    except:
                        pass
            else:
                continue
            
            if not name:
                continue
            
            # Normalize name for aggregation
            normalized = name.lower().strip()
            
            # Scale quantity
            scaled_qty = (float(qty) if qty else 0) * scale_factor
            
            if normalized in ingredient_map:
                # Add to existing
                if unit == ingredient_map[normalized]['unit']:
                    ingredient_map[normalized]['qty'] += scaled_qty
                else:
                    # Different units - keep separate
                    key = f"{normalized}_{unit}"
                    if key in ingredient_map:
                        ingredient_map[key]['qty'] += scaled_qty
                    else:
                        ingredient_map[key] = {
                            'qty': scaled_qty,
                            'unit': unit,
                            'name': name
                        }
            else:
                ingredient_map[normalized] = {
                    'qty': scaled_qty,
                    'unit': unit,
                    'name': name
                }
    
    # Convert to list and sort
    shopping_list = []
    for key, data in ingredient_map.items():
        shopping_list.append({
            'name': data['name'],
            'quantity': round(data['qty'], 2) if data['qty'] else '',
            'unit': data['unit']
        })
    
    shopping_list.sort(key=lambda x: x['name'].lower())
    
    return jsonify({
        'items': shopping_list,
        'total_count': len(shopping_list),
        'bookings_processed': len(bookings)
    })


def categorize_ingredient(ingredient_name):
    """Categorize ingredient by store section."""
    name_lower = ingredient_name.lower()
    
    # Produce
    produce = ['apple', 'banana', 'orange', 'lemon', 'lime', 'tomato', 'potato', 'onion', 'garlic', 
               'carrot', 'lettuce', 'spinach', 'cabbage', 'broccoli', 'cauliflower', 'pepper', 'capsicum',
               'cucumber', 'zucchini', 'mushroom', 'avocado', 'celery', 'ginger', 'herbs', 'parsley',
               'cilantro', 'basil', 'mint', 'thyme', 'rosemary', 'kale', 'chard', 'beetroot', 'pumpkin']
    
    # Dairy
    dairy = ['milk', 'cream', 'butter', 'cheese', 'yogurt', 'yoghurt', 'sour cream', 'feta', 'mozzarella',
             'parmesan', 'cheddar', 'brie', 'cottage cheese', 'ricotta', 'halloumi']
    
    # Meat & Seafood
    meat = ['chicken', 'beef', 'pork', 'lamb', 'turkey', 'bacon', 'sausage', 'mince', 'steak',
            'fish', 'salmon', 'tuna', 'prawns', 'shrimp', 'mussels', 'seafood']
    
    # Pantry/Dry Goods
    pantry = ['flour', 'sugar', 'rice', 'pasta', 'bread', 'cereal', 'oats', 'quinoa', 'couscous',
              'lentils', 'beans', 'chickpeas', 'oil', 'vinegar', 'sauce', 'stock', 'broth',
              'honey', 'jam', 'peanut butter', 'nuts', 'almonds', 'cashews', 'seeds', 'spice',
              'salt', 'pepper', 'cumin', 'paprika', 'cinnamon', 'vanilla', 'cocoa', 'chocolate',
              'baking powder', 'baking soda', 'yeast', 'cornstarch', 'cornflour']
    
    # Frozen
    frozen = ['frozen', 'ice cream', 'peas', 'corn', 'berries mixed']
    
    # Beverages
    beverages = ['juice', 'soda', 'water', 'tea', 'coffee', 'wine', 'beer']
    
    # Check categories
    for item in produce:
        if item in name_lower:
            return 'Produce'
    for item in dairy:
        if item in name_lower:
            return 'Dairy'
    for item in meat:
        if item in name_lower:
            return 'Meat & Seafood'
    for item in pantry:
        if item in name_lower:
            return 'Pantry'
    for item in frozen:
        if item in name_lower:
            return 'Frozen'
    for item in beverages:
        if item in name_lower:
            return 'Beverages'
    
    return 'Other'


@app.route('/api/shopping-list/toggle-item', methods=['POST'])
@require_role('Admin', 'Teacher', 'Technician')
def toggle_shopping_item():
    """Toggle 'already have' status for a shopping list item."""
    data = request.get_json()
    week_start = data.get('week_start')
    ingredient_name = data.get('ingredient_name')
    quantity = data.get('quantity', 0)
    unit = data.get('unit', '')
    
    if not week_start or not ingredient_name:
        return jsonify({'error': 'Missing required fields'}), 400
    
    with get_db_connection() as conn:
        c = conn.cursor()
        # Check if item exists
        c.execute('SELECT id, already_have FROM shopping_list_items WHERE week_start = %s AND ingredient_name = %s',
                  (week_start, ingredient_name))
        row = c.fetchone()
        if row:
            # Toggle status
            new_status = 0 if row['already_have'] else 1
            c.execute('UPDATE shopping_list_items SET already_have = %s WHERE id = %s', (new_status, row['id']))
        else:
            # Create new item with already_have = 1
            category = categorize_ingredient(ingredient_name)
            c.execute('''INSERT INTO shopping_list_items 
                        (week_start, ingredient_name, quantity, unit, category, already_have)
                        VALUES (%s, %s, %s, %s, %s, 1)''',
                      (week_start, ingredient_name, quantity, unit, category))
            new_status = 1
        conn.commit()
    
    return jsonify({'success': True, 'already_have': new_status})


@app.route('/api/shopping-list/get-status', methods=['POST'])
@require_role('Admin', 'Teacher', 'Technician')
def get_shopping_status():
    """Get 'already have' status for items in a week."""
    data = request.get_json()
    week_start = data.get('week_start')
    return jsonify({'status': 'not implemented'}), 501
    if not week_start:
        return jsonify({'error': 'Missing week_start'}), 400
    
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT ingredient_name, already_have FROM shopping_list_items WHERE week_start = %s AND already_have = 1',
                  (week_start,))
        items = {row['ingredient_name']: row['already_have'] for row in c.fetchall()}
    
    return jsonify({'items': items})


@app.route('/api/shopping-list/save', methods=['POST'])
@require_role('Admin', 'Teacher', 'Technician')
def save_shopping_list():
    """Save a shopping list for reuse."""
    data = request.get_json()
    list_name = data.get('list_name', '').strip()
    week_label = data.get('week_label', '')
    items = data.get('items', [])
    return jsonify({'status': 'not implemented'}), 501
    if not list_name or not items:
        return jsonify({'error': 'Missing list name or items'}), 400
    
    user_email = current_user.email if current_user.is_authenticated else 'unknown'
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO saved_shopping_lists (list_name, week_label, items, created_by)
                        VALUES (%s, %s, %s, %s) RETURNING id''',
                    (list_name, week_label, json.dumps(items), user_email))
        list_id = c.fetchone()['id']
        conn.commit()
    return jsonify({'success': True, 'list_id': list_id})


@app.route('/api/shopping-list/saved', methods=['GET'])
@require_role('Admin', 'Teacher', 'Technician')
def get_saved_lists():
    """Get all saved shopping lists."""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT id, list_name, week_label, created_at FROM saved_shopping_lists ORDER BY created_at DESC')
        lists = [dict(row) for row in c.fetchall()]
    
    return jsonify({'lists': lists})


@app.route('/api/shopping-list/load/<int:list_id>', methods=['GET'])
@require_role('Admin', 'Teacher', 'Technician')
def load_saved_list(list_id):
    """Load a saved shopping list."""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM saved_shopping_lists WHERE id = %s', (list_id,))
        row = c.fetchone()
        if not row:
            return jsonify({'error': 'List not found'}), 404
        list_data = dict(row)
        list_data['items'] = json.loads(list_data['items'])
    return jsonify(list_data)






@app.route('/suggest_recipe', methods=['POST'])
def suggest_recipe_modal():
    """Handle AJAX recipe suggestion submissions from modal and return JSON."""
    try:
        recipe_name = request.form.get('recipe_name', '').strip()
        recipe_url = request.form.get('recipe_url', '').strip()
        reason = request.form.get('reason', '').strip()
        suggested_by_name = request.form.get('suggested_by_name', '').strip()
        suggested_by_email = request.form.get('suggested_by_email', '').strip()

        if not recipe_name or not suggested_by_name or not suggested_by_email:
            return jsonify({'success': False, 'message': 'Recipe name, your name, and email are required.'})

        # Save suggestion to the database
        try:
            with get_db_connection() as conn:
                c = conn.cursor()
                sql = '''INSERT INTO recipe_suggestions (recipe_name, recipe_url, reason, suggested_by_name, suggested_by_email, created_at, status)
                       VALUES (%s, %s, %s, %s, %s, NOW(), %s)'''
                params = (recipe_name, recipe_url, reason, suggested_by_name, suggested_by_email, 'pending')
                c.execute(sql, params)
                conn.commit()
        except Exception as db_error:
            print(f"[ERROR] Failed to save suggestion to DB (modal): {db_error}")
            import traceback; traceback.print_exc()
            return jsonify({'success': False, 'message': 'There was an error saving your suggestion. Please try again or contact the VP directly.'})

        # Send email to VP (Vanessa Pringle)
        email_sent = False
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_username = os.getenv('SMTP_USERNAME')
            smtp_password = os.getenv('SMTP_PASSWORD')
            smtp_from_email = os.getenv('SMTP_FROM_EMAIL', smtp_username)
            vp_email = 'vanessapringle@westlandhigh.school.nz'
            subject = f"Recipe Suggestion: {recipe_name}"
            body = f"Recipe Name: {recipe_name}\nURL: {recipe_url}\nReason: {reason}\nSuggested by: {suggested_by_name} ({suggested_by_email})"
            if smtp_username and smtp_password:
                msg = MIMEMultipart()
                msg['From'] = smtp_from_email or 'Food Room System <noreply@whsdtech.com>'
                msg['To'] = vp_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
                server.quit()
                email_sent = True
                print(f"Email sent successfully to {vp_email}")
            else:
                print("SMTP credentials not configured - email not sent")
                print(f"RECIPE SUGGESTION EMAIL:\nTo: {vp_email}\nSubject: {subject}\n\n{body}")
        except Exception as email_error:
            print(f"Failed to send email: {email_error}")
            print(f"RECIPE SUGGESTION EMAIL (not sent):\nTo: {vp_email}\nSubject: {subject}\n\n{body}")
        return jsonify({'success': True, 'email_sent': email_sent})
    except Exception as e:
        print(f"Error in suggest_recipe_modal: {e}")
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'message': 'There was an error submitting your suggestion. Please try again or contact the VP directly.'})

# Legacy route for admin/recipes page (kept for compatibility)
@app.route('/recipes/suggest', methods=['POST'])
@require_login
# @Grapplinks[#URL]
def suggest_recipe():
    """Handle recipe suggestion submissions and email to VP"""
    try:
        recipe_name = request.form.get('recipe_name', '').strip()
        recipe_url = request.form.get('recipe_url', '').strip()
        reason = request.form.get('reason', '').strip()

        if not recipe_name:
            flash('Recipe name is required.', 'error')
            return redirect(url_for('recipes_page'))

        # Set recipient email directly (Vanessa Pringle)
        vp_email = 'vanessapringle@westlandhigh.school.nz'

        # Get current user info safely
        user_name = current_user.name if hasattr(current_user, 'name') else 'Unknown User'
        user_email = current_user.email if hasattr(current_user, 'email') else 'No email'

        # Define subject and body for the email
        subject = f"Recipe Suggestion: {recipe_name}"
        body = f"Recipe Name: {recipe_name}\nURL: {recipe_url}\nReason: {reason}\nSuggested by: {user_name} ({user_email})"

        # Save suggestion to the database (only once)
        try:
            with get_db_connection() as conn:
                c = conn.cursor()
                sql = '''INSERT INTO recipe_suggestions (recipe_name, recipe_url, reason, suggested_by_name, suggested_by_email, created_at, status)
                       VALUES (%s, %s, %s, %s, %s, NOW(), %s)'''
                params = (recipe_name, recipe_url, reason, user_name, user_email, 'pending')
                print("[DEBUG] About to execute SQL for recipe suggestion:")
                print("[DEBUG] SQL:", sql)
                print("[DEBUG] Params:", params)
                try:
                    c.execute(sql, params)
                    conn.commit()
                    print("[DEBUG] Insert committed successfully.")
                except Exception as exec_error:
                    print(f"[ERROR] Exception during SQL execute: {exec_error}")
                    import traceback; traceback.print_exc()
                    flash('There was an error saving your suggestion (SQL error). Please try again or contact the VP directly.', 'error')
                    return redirect(url_for('recipes_page'))
        except Exception as db_error:
            print(f"[ERROR] Failed to save suggestion to DB (outer): {db_error}")
            import traceback; traceback.print_exc()
            flash('There was an error saving your suggestion (DB error). Please try again or contact the VP directly.', 'error')
            return redirect(url_for('recipes_page'))

        # Only send email after successful DB insert
        email_sent = False
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_username = os.getenv('SMTP_USERNAME')
            smtp_password = os.getenv('SMTP_PASSWORD')
            smtp_from_email = os.getenv('SMTP_FROM_EMAIL', smtp_username)
            if smtp_username and smtp_password:
                msg = MIMEMultipart()
                msg['From'] = smtp_from_email or 'Food Room System <noreply@whsdtech.com>'
                msg['To'] = vp_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
                server.quit()
                email_sent = True
                print(f"Email sent successfully to {vp_email}")
            else:
                print("SMTP credentials not configured - email not sent")
                print(f"RECIPE SUGGESTION EMAIL:\nTo: {vp_email}\nSubject: {subject}\n\n{body}")
        except Exception as email_error:
            print(f"Failed to send email: {email_error}")
            print(f"RECIPE SUGGESTION EMAIL (not sent):\nTo: {vp_email}\nSubject: {subject}\n\n{body}")

        if email_sent:
            flash(f'Thank you! Your suggestion for "{recipe_name}" has been emailed to the VP and saved to the database.', 'success')
        else:
            flash(f'Thank you! Your suggestion for "{recipe_name}" has been saved. The VP will review it in the Admin panel.', 'success')

    except Exception as e:
        print(f"Error in suggest_recipe: {e}")
        import traceback
        traceback.print_exc()
        flash('There was an error submitting your suggestion. Please try again or contact the VP directly.', 'error')

    return redirect(url_for('recipes_page'))


@app.route('/recbk')
def recbk():
    q = request.args.get('q', '').strip()
    with get_db_connection() as conn:
        c = conn.cursor()
        if q:
            term = f"%{q}%"
            c.execute(
                "SELECT id, name, ingredients, instructions, serving_size, equipment, dietary_tags, cuisine, difficulty FROM recipes "
                "WHERE name ILIKE %s OR ingredients ILIKE %s "
                "ORDER BY LOWER(name)",
                (term, term),
            )
        else:
            c.execute(
                "SELECT id, name, ingredients, instructions, serving_size, equipment, dietary_tags, cuisine, difficulty FROM recipes "
                "ORDER BY LOWER(name)"
            )
        rows = [dict(r) for r in c.fetchall()]

    # Decode JSON fields for template
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

    # Get user's favorites if logged in
    favorites = []
    if current_user.is_authenticated:
        try:
            with get_db_connection() as conn:
                c = conn.cursor()
                c.execute('SELECT recipe_id FROM recipe_favorites WHERE user_email = %s', (current_user.email,))
                favorites = [row[0] for row in c.fetchall()]
        except Exception:
            # Table doesn't exist yet - run setup_database.py to create it
            favorites = []

    return render_template('recbk.html', rows=rows, q=q, favorites=favorites)


@app.route('/recipe/favorite/<int:recipe_id>', methods=['POST'])
@require_login
def add_favorite(recipe_id):
    """Add a recipe to user's favorites"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            # Use ON CONFLICT DO NOTHING for PostgreSQL
            c.execute('INSERT INTO recipe_favorites (user_email, recipe_id) VALUES (%s, %s) ON CONFLICT DO NOTHING',
                     (current_user.email, recipe_id))
            conn.commit()
        return jsonify({'success': True, 'message': 'Added to favorites'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/update-recipe-tags/<int:recipe_id>', methods=['POST'])
@require_role('VP', 'DK')
def update_recipe_tags(recipe_id):
    """Quick API to update recipe dietary tags, cuisine, and difficulty."""
    data = request.get_json()
    
    dietary_tags = data.get('dietary_tags', '')  # comma-separated
    cuisine = data.get('cuisine', '')
    difficulty = data.get('difficulty', '')
    
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''UPDATE recipes 
                    SET dietary_tags = %s, cuisine = %s, difficulty = %s
                    WHERE id = %s''',
                 (dietary_tags, cuisine, difficulty, recipe_id))
        conn.commit()
    return jsonify({'success': True, 'message': 'Tags updated'})




@app.route('/booking/export/ical')
@require_role('Admin', 'Teacher', 'Technician')
def export_ical():
    """Export bookings as iCal format for Google Calendar import."""
    from datetime import datetime
    
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT 
                cb.date_required as date,
                cb.period,
                cb.staff_code,
                cb.class_code,
                r.name as recipe_name,
                cb.desired_servings as servings,
                t.first_name || ' ' || t.last_name as staff_name
            FROM class_bookings cb
            LEFT JOIN recipes r ON cb.recipe_id = r.id
            LEFT JOIN teachers t ON cb.staff_code = t.code
            ORDER BY cb.date_required, cb.period
        ''')
        bookings = c.fetchall()

    # Build iCal content
    ical = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//WHS Food Room//NONSGML v1.0//EN'
    ]
    for b in bookings:
        dt = b['date_required']
        summary = f"{b['class_code']} - {b['recipe_name']}"
        description = f"Servings: {b['servings']}"
        uid = str(uuid.uuid4())
        ical.append('BEGIN:VEVENT')
        ical.append(f"UID:{uid}")
        ical.append(f"DTSTAMP:{dt.strftime('%Y%m%dT000000Z')}")
        ical.append(f"DTSTART;VALUE=DATE:{dt.strftime('%Y%m%d')}")
        ical.append(f"DTEND;VALUE=DATE:{dt.strftime('%Y%m%d')}")
        ical.append(f"SUMMARY:{summary}")
        ical.append(f"DESCRIPTION:{description}")
        ical.append('END:VEVENT')
    ical.append('END:VCALENDAR')
    ical_str = '\r\n'.join(ical)
    response = app.response_class(
        ical_str,
        mimetype='text/calendar',
        headers={
            'Content-Disposition': 'attachment; filename=bookings.ics'
        }
    )
    return response


@app.route('/shoplist/export/ical')
def export_shoplist_ical():
    """Export shopping list bookings as iCal format for Google Calendar import."""
    from datetime import datetime, timedelta
    import uuid
    # Get year and month from query params, default to current month
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    if not year or not month:
        today = datetime.now()
        year = today.year
        month = today.month
    from calendar import monthrange
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, monthrange(year, month)[1])
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''SELECT cb.date_required, cb.period, cb.class_code, r.name AS recipe_name, cb.desired_servings AS servings
                     FROM class_bookings cb
                     LEFT JOIN recipes r ON cb.recipe_id = r.id
                     WHERE cb.date_required >= %s AND cb.date_required <= %s
                     ORDER BY cb.date_required, cb.period''', (first_day.date(), last_day.date()))
        bookings = c.fetchall()
    # Build iCal content
    ical = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//WHS Food Room//NONSGML v1.0//EN'
    ]
    for b in bookings:
        dt = b['date_required']
        summary = f"{b['class_code']} - {b['recipe_name']}"
        description = f"Servings: {b['servings']}"
        uid = str(uuid.uuid4())
        ical.append('BEGIN:VEVENT')
        ical.append(f"UID:{uid}")
        ical.append(f"DTSTAMP:{dt.strftime('%Y%m%dT000000Z')}")
        ical.append(f"DTSTART;VALUE=DATE:{dt.strftime('%Y%m%d')}")
        ical.append(f"DTEND;VALUE=DATE:{dt.strftime('%Y%m%d')}")
        ical.append(f"SUMMARY:{summary}")
        ical.append(f"DESCRIPTION:{description}")
        ical.append('END:VEVENT')
    ical.append('END:VCALENDAR')
    ical_str = '\r\n'.join(ical)
    response = app.response_class(
        ical_str,
        mimetype='text/calendar',
        headers={
            'Content-Disposition': 'attachment; filename=shoplist.ics'
        }
    )
    return response

# --- API endpoint for scheduled bookings (for modal popup) ---
@app.route('/api/scheduled_bookings')
def api_scheduled_bookings():
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''
                SELECT cb.date_required, cb.period, cb.class_code, r.name as recipe_name, cb.desired_servings AS servings,
                       t.last_name, t.first_name, t.title, t.code as staff_code
                FROM class_bookings cb
                LEFT JOIN recipes r ON cb.recipe_id = r.id
                LEFT JOIN teachers t ON cb.staff_code = t.code
                ORDER BY cb.date_required, cb.period
            ''')
            bookings = []
            for row in c.fetchall():
                # Robust date handling
                date_val = row['date_required']
                if hasattr(date_val, 'strftime'):
                    date_str = date_val.strftime('%Y-%m-%d')
                elif isinstance(date_val, str):
                    date_str = date_val
                elif date_val is not None:
                    date_str = str(date_val)
                else:
                    date_str = ''
                staff_display = f"{row['staff_code']} - {row['last_name']}, {row['first_name']}"
                bookings.append({
                    'date_required': date_str,
                    'period': row['period'],
                    'class_code': row['class_code'],
                    'recipe_name': row['recipe_name'],
                    'servings': row['servings'],
                    'staff_display': staff_display
                })
        return jsonify({'success': True, 'bookings': bookings})
    except Exception as e:
        print('[ERROR] Failed to fetch scheduled bookings:', e)
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

# --- Recipe detail page for /recipe/<id> ---
@app.route('/recipe/<int:recipe_id>', endpoint='recipe_details')
# @Grapplinks[#URL]
def recipe_details(recipe_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT id, name, ingredients, instructions, serving_size, source FROM recipes WHERE id = %s', (recipe_id,))
        row = c.fetchone()
        if not row:
            return render_template('recipe_details.html', recipe=None, error='Recipe not found'), 404
        recipe = dict(row)
        try:
            recipe['ingredients'] = json.loads(recipe.get('ingredients') or '[]')
        except Exception:
            recipe['ingredients'] = []
    return render_template('recipe_details.html', recipe=recipe, error=None)
