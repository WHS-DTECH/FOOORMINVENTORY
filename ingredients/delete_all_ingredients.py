from flask import Blueprint, redirect, url_for
from app import get_db_connection

ingredients_bp = Blueprint('ingredients_bp', __name__)

@ingredients_bp.route('/delete_all_ingredients', methods=['POST'])
def delete_all_ingredients():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM ingredient_inventory')
        conn.commit()
    return redirect(url_for('ingredients.ingredients_inventory'))
