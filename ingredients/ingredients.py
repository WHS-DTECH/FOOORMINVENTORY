from flask import Blueprint, render_template
from auth import require_role, get_db_connection

ingredients_bp = Blueprint('ingredients', __name__, template_folder='templates')

@ingredients_bp.route('/ingredients')
@require_role('Admin')
def ingredients_page():
    # For now, load recipeID 77's ingredients from a hardcoded list (as a demo)
    # Replace this with a DB query or dynamic logic as needed
    recipe_id = 77  # You can make this dynamic later
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM ingredient_inventory WHERE recipe_id = %s ORDER BY ingredient_name', (recipe_id,))
        ingredients = c.fetchall()
    return render_template('ingredients/ingredients.html', ingredients=ingredients)
