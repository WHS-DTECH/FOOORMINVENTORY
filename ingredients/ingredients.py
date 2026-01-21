from flask import Blueprint, render_template
from auth import require_role, get_db_connection

ingredients_bp = Blueprint('ingredients', __name__, template_folder='templates')

@ingredients_bp.route('/ingredients')
@require_role('Admin')
def ingredients_page():
    # For now, load recipeID 77's ingredients from a hardcoded list (as a demo)
    # Replace this with a DB query or dynamic logic as needed
    import json
    recipe_id = 77  # You can make this dynamic later
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT ingredients FROM recipes WHERE id = %s', (recipe_id,))
        row = c.fetchone()
        ingredients = []
        if row and row['ingredients']:
            try:
                # Try to parse as JSON list
                ingredients = json.loads(row['ingredients'])
                # If it's a list of strings, convert to dicts
                if ingredients and isinstance(ingredients[0], str):
                    def parse_ingredient_str(s):
                        return {"ingredient_name": s}
                    ingredients = [parse_ingredient_str(s) for s in ingredients]
            except Exception:
                ingredients = []
    return render_template('ingredients/ingredients.html', ingredients=ingredients)
