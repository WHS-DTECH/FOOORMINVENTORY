from flask import Blueprint, render_template, redirect, url_for, flash, request
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

@ingredients_bp.route('/ingredients/delete_all', methods=['POST'])
@require_role('Admin')
def delete_all_ingredients():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM ingredient_inventory')
        conn.commit()
    flash('All ingredients deleted.', 'success')
    return redirect(url_for('ingredients.ingredients_page'))
