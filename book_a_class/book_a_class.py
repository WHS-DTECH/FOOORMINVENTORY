from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user
from auth import require_role, get_db_connection
import json

book_a_class_bp = Blueprint('book_a_class', __name__, template_folder='templates/book_a_class')

@book_a_class_bp.route('/book_a_class', methods=['GET', 'POST'])
@require_role('Admin', 'Teacher')
def book_a_class():
    # ...existing code from class_ingredients.py...
    staff_code = request.form.get('staff_code') if request.method == 'POST' else None
    class_code = request.form.get('class_code') if request.method == 'POST' else None
    date_required = request.form.get('date_required') if request.method == 'POST' else None
    period = request.form.get('period') if request.method == 'POST' else None

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''SELECT staff_code, COUNT(*) as booking_count FROM class_bookings \
                    GROUP BY staff_code ORDER BY booking_count DESC LIMIT 5''')
        most_used_staff_codes = [r['staff_code'] for r in c.fetchall()]
        c.execute('SELECT code, last_name, first_name, title FROM teachers ORDER BY last_name, first_name')
        all_staff = [dict(r) for r in c.fetchall()]
        most_used_staff = [s for s in all_staff if s['code'] in most_used_staff_codes]
        other_staff = [s for s in all_staff if s['code'] not in most_used_staff_codes]
        most_used_staff.sort(key=lambda x: most_used_staff_codes.index(x['code']))
        staff = most_used_staff + other_staff
        if not staff_code and current_user.is_authenticated:
            user_name_parts = current_user.name.split()
            if len(user_name_parts) >= 2:
                user_first = user_name_parts[0]
                user_last = user_name_parts[-1]
                for s in staff:
                    if (s['first_name'].lower() == user_first.lower() and \
                        s['last_name'].lower() == user_last.lower()):
                        staff_code = s['code']
                        break
        c.execute('''SELECT class_code, COUNT(*) as booking_count FROM class_bookings \
                    GROUP BY class_code ORDER BY booking_count DESC LIMIT 5''')
        most_used_class_codes = [r['class_code'] for r in c.fetchall()]
        c.execute('SELECT DISTINCT ClassCode FROM classes ORDER BY ClassCode')
        all_classes = [r['classcode'] for r in c.fetchall() if r['classcode']]
        most_used_classes = [c for c in all_classes if c in most_used_class_codes]
        other_classes = [c for c in all_classes if c not in most_used_class_codes]
        most_used_classes.sort(key=lambda x: most_used_class_codes.index(x))
        classes = most_used_classes + other_classes
        c.execute('SELECT id, name, ingredients, serving_size FROM recipes ORDER BY LOWER(name)')
        rows = c.fetchall()
        booking_recipe_id = None
        booking_servings = None
        if request.method == 'POST' and staff_code and class_code and date_required and period:
            c.execute('''SELECT recipe_id, desired_servings FROM class_bookings \
                        WHERE staff_code = %s AND class_code = %s AND date_required = %s AND period = %s''',
                     (staff_code, class_code, date_required, period))
            booking = c.fetchone()
            if booking:
                booking_recipe_id = booking['recipe_id']
                booking_servings = booking['desired_servings']

    recipes = []
    for r in rows:
        try:
            ings = json.loads(r['ingredients'] or '[]')
        except Exception:
            ings = []
        recipes.append({'id': r['id'], 'name': r['name'], 'ingredients': ings, 'serving_size': r['serving_size']})

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT cb.id, cb.staff_code, cb.class_code, cb.date_required, cb.period, \
                   cb.recipe_id, cb.desired_servings, r.name as recipe_name,
                   t.first_name, t.last_name
            FROM class_bookings cb
            LEFT JOIN recipes r ON cb.recipe_id = r.id
            LEFT JOIN teachers t ON cb.staff_code = t.code
            ORDER BY cb.date_required DESC, cb.period ASC
        ''')
        bookings = [dict(row) for row in c.fetchall()]

    return render_template('book_a_class.html', staff=staff, classes=classes, recipes=recipes,
                          bookings=bookings,
                          most_used_staff_count=len(most_used_staff), most_used_classes_count=len(most_used_classes),
                          pre_staff_code=staff_code, pre_class_code=class_code, 
                          pre_date_required=date_required, pre_period=period,
                          pre_recipe_id=booking_recipe_id, pre_servings=booking_servings)
