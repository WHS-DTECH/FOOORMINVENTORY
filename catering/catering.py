from flask import Blueprint, render_template
from auth import get_db_connection
import datetime

catering_bp = Blueprint('catering', __name__)

@catering_bp.route('/catering')
def catering():
    # Query real class_bookings, teachers, and recipes data
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT cb.id, cb.class_code, cb.period, cb.date_required, cb.recipe_id, cb.class_size, cb.desired_serving,
                   r.name as recipe_name, r.serving_size, t.first_name, t.last_name, t.title
            FROM class_bookings cb
            LEFT JOIN recipes r ON cb.recipe_id = r.id
            LEFT JOIN teachers t ON cb.staff_code = t.code
            ORDER BY cb.date_required DESC, cb.period ASC
        ''')
        bookings = []
        for row in c.fetchall():
            # Map day from date_required
            date_obj = row['date_required']
            if isinstance(date_obj, str):
                try:
                    date_obj = datetime.datetime.strptime(date_obj, '%Y-%m-%d')
                except Exception:
                    date_obj = None
            day = date_obj.strftime('%A') if date_obj else ''
            teacher = f"{row['first_name']} {row['last_name']}" if row['first_name'] and row['last_name'] else ''
            bookings.append({
                'id': row['id'],
                'class': row['class_code'],
                'recipe': row['recipe_name'],
                'recipe_id': row['recipe_id'],
                'servings': row['serving_size'],
                'day': day,
                'period': row['period'],
                'teacher': teacher,
                'class_size': row['class_size'],
                'desired_serving': row['desired_serving'],
            })
        # Also pass all recipes for lookup if needed (with ingredients)
        c.execute('SELECT id, name, ingredients, serving_size FROM recipes ORDER BY LOWER(name)')
        recipes = []
        for r in c.fetchall():
            try:
                ings = json.loads(r['ingredients'] or '[]')
            except Exception:
                ings = []
            recipes.append({'id': r['id'], 'name': r['name'], 'ingredients': ings, 'serving_size': r['serving_size']})
    return render_template('catering.html', bookings=bookings, recipes=recipes)
