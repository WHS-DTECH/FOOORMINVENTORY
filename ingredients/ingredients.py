from flask import Blueprint, render_template
from auth import require_role, get_db_connection

ingredients_bp = Blueprint('ingredients', __name__, template_folder='templates')

@ingredients_bp.route('/ingredients')
@require_role('Admin')
def ingredients_page():
    # For now, load recipeID 77's ingredients from a hardcoded list (as a demo)
    # Replace this with a DB query or dynamic logic as needed
    import json
    import re
    recipe_id = 77  # You can make this dynamic later
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT ingredients FROM recipes WHERE id = %s', (recipe_id,))
        row = c.fetchone()
        ingredients = []
        if row and row['ingredients']:
            try:
                raw_ingredients = json.loads(row['ingredients'])
                # If it's a list of strings, convert to dicts
                if raw_ingredients and isinstance(raw_ingredients[0], str):
                    for s in raw_ingredients:
                        # Insert raw string into found_ingredient
                        # Process to extract a normalized ingredient name
                        # Example: remove brand names, keep main food word
                        # This is a simple demo, you can improve the logic
                        # Remove common brand words
                        processed = re.sub(r'Chelsea|Edmonds|Meadow Fresh|Quality Mark|Fielder\'s', '', s, flags=re.IGNORECASE)
                        # Remove extra details in parentheses
                        processed = re.sub(r'\(.*?\)', '', processed)
                        # Remove extra whitespace and units
                        processed = processed.strip()
                        # Remove leading numbers/units
                        processed = re.sub(r'^\d+\s*([a-zA-Z]+)?\s*', '', processed)
                        # Remove trailing commas
                        processed = processed.rstrip(',')
                        # Insert into DB (demo: not checking for duplicates)
                        c.execute('''
                            INSERT INTO ingredient_inventory (found_ingredient, ingredient_name, recipe_id)
                            VALUES (%s, %s, %s)
                        ''', (s, processed, recipe_id))
                        ingredients.append({"found_ingredient": s, "ingredient_name": processed})
                else:
                    # If already dicts, just use as is
                    ingredients = raw_ingredients
                conn.commit()
            except Exception:
                ingredients = []
    return render_template('ingredients/ingredients.html', ingredients=ingredients)
