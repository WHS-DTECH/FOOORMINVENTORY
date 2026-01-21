from flask import Blueprint, render_template
from auth import require_role, get_db_connection

ingredients_bp = Blueprint('ingredients', __name__, template_folder='templates')

@ingredients_bp.route('/ingredients')
@require_role('Admin')
def ingredients_page():
    # For now, load recipeID 77's ingredients from a hardcoded list (as a demo)
    # Replace this with a DB query or dynamic logic as needed
    ingredients = [
        {"ingredient_name": "170.0 water, boiling", "quantity": "170.0", "unit": "water,", "category": "", "last_updated": ""},
        {"ingredient_name": "1.0 vegetable stock cube", "quantity": "1.0", "unit": "vegetable", "category": "", "last_updated": ""},
        {"ingredient_name": "100.0 couscous", "quantity": "100.0", "unit": "couscous", "category": "", "last_updated": ""},
        {"ingredient_name": "1.0 medium tomato", "quantity": "1.0", "unit": "medium", "category": "", "last_updated": ""},
        {"ingredient_name": "1.0 spring onion", "quantity": "1.0", "unit": "spring", "category": "", "last_updated": ""},
        {"ingredient_name": "¼ cucumber", "quantity": "", "unit": "", "category": "", "last_updated": ""},
        {"ingredient_name": "½ yellow pepper", "quantity": "", "unit": "", "category": "", "last_updated": ""},
        {"ingredient_name": "4.0 dried apricots", "quantity": "4.0", "unit": "dried", "category": "", "last_updated": ""},
        {"ingredient_name": "1.0 15ml spoon parsley", "quantity": "1.0", "unit": "", "category": "", "last_updated": ""},
        {"ingredient_name": "2.0 15ml spoons low fat dressing", "quantity": "2.0", "unit": "", "category": "", "last_updated": ""},
    ]
    return render_template('ingredients/ingredients.html', ingredients=ingredients)
