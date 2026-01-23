from flask import Blueprint, render_template
from auth import require_role, get_db_connection

inventory_bp = Blueprint('inventory', __name__, template_folder='templates')

@inventory_bp.route('/inventory')
@require_role('Admin')
def inventory_page():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT id, ingredient_name, quantity, unit, category, last_updated, recipe_id, found_ingredient FROM ingredient_inventory ORDER BY LOWER(ingredient_name)')
        ingredients = [dict(row) for row in c.fetchall()]
    return render_template('recipe_setup/inventory.html', ingredients=ingredients)
