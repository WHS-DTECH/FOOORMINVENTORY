from flask import Blueprint, render_template
from auth import require_role, get_db_connection

ingredients_bp = Blueprint('ingredients', __name__, template_folder='templates')

@ingredients_bp.route('/ingredients')
@require_role('Admin')
def ingredients_page():
    # Show all rows from ingredient_inventory table
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM ingredient_inventory ORDER BY ingredient_name ASC')
        ingredients = c.fetchall()
    return render_template('ingredients/ingredients.html', ingredients=ingredients)
