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
from debug_parser.utils import extract_raw_text_from_url
from auth.google_auth import google_auth_bp
from ingredients.ingredients import ingredients_bp
from flask_login import current_user, login_user, logout_user
from recipe_setup import recipe_book_setup
from google_auth_oauthlib.flow import Flow


from admin_task.utils import get_staff_code_from_email

# Import AnonymousUser from auth.anonymous_user






# =======================
# App Creation & Configuration
# =======================
load_dotenv()

app = Flask(__name__)
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['format_nz_week'] = format_nz_week
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

# Register blueprints after app is created

# Register blueprints after app is created
from auth.routes import auth_bp
from ShopList import shoplist_bp
from api.routes import api_bp
app.register_blueprint(auth_bp)
app.register_blueprint(shoplist_bp)
app.register_blueprint(api_bp)
app.register_blueprint(recipe_book_bp)

# Register error handlers
from error_handlers import not_found_error, internal_error
app.register_error_handler(404, not_found_error)
app.register_error_handler(500, internal_error)

SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]



# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

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



# Google OAuth routes are now handled in auth.routes (auth_bp)



# Google OAuth callback is now handled in auth.routes (auth_bp)



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
# ...existing code...

# --- Redirect old /class_ingredients route to new /book_a_class route ---
@app.route('/class_ingredients', methods=['GET', 'POST'])
def redirect_class_ingredients():
    return redirect(url_for('book_a_class.book_a_class'), code=301)


