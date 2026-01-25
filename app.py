from debug_parser.debug_parser_instructions import debug_instructions
import os
from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
from flask_login import LoginManager
from dotenv import load_dotenv
from recipe_parser_pdf import parse_recipes_from_text
from debug_parser.debug_parser_Serving import debug_serving
from debug_parser.debug_parser_title import debug_title




from utils import simple_similarity, categorize_ingredient
from jinja_filters import datetimeformat, format_nz_week
from auth import require_role, get_db_connection, User

from book_a_class.book_a_class import book_a_class_bp
from debug_parser.debug_parser_instructions import debug_parser_instructions_bp
from upload_URL import upload_url_bp
from recipe_book import recipe_book_bp
from recipe_book.routes import recipe_book_routes_bp, recipe_review_bp
from debug_parser.utils import extract_raw_text_from_url
from auth.google_auth import google_auth_bp
from ingredients.ingredients import ingredients_bp
from flask_login import current_user, login_user, logout_user
from recipe_setup import recipe_book_setup
from google_auth_oauthlib.flow import Flow


from admin_task.utils import get_staff_code_from_email

# Import AnonymousUser from auth.anonymous_user





# After app is created and configured, register blueprints
from auth.routes import auth_bp
app.register_blueprint(auth_bp)
app.register_blueprint(shoplist_bp)

# Register error handlers
from error_handlers import not_found_error, internal_error
app.register_error_handler(404, not_found_error)
app.register_error_handler(500, internal_error)

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
    return redirect(url_for('recipe_book.recbk'))


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
        return redirect(url_for('recipe_book.recbk'))
    
    except Exception as e:
        flash(f'Authentication error: {str(e)}')
        return redirect(url_for('login'))



# Register navigation blueprint for redirects and miscellaneous routes
from navigation_main.routes import navigation_bp
app.register_blueprint(navigation_bp)


# ============== End Authentication Routes ==============


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


@app.route('/api/update-recipe-tags/<int:recipe_id>', methods=['POST'])
@require_role('Admin', 'Teacher')
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

# --- Redirect old /class_ingredients route to new /book_a_class route ---
@app.route('/class_ingredients', methods=['GET', 'POST'])
def redirect_class_ingredients():
    return redirect(url_for('book_a_class.book_a_class'), code=301)


