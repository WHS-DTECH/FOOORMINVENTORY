from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import current_user
from auth import require_role, get_db_connection
import json

book_a_class_bp = Blueprint('book_a_class', __name__, template_folder='templates/book_a_class')

@book_a_class_bp.route('/book_a_class', methods=['GET', 'POST'])
@require_role('Admin', 'Teacher')
def book_a_class():
    # ...existing code from app.py class_ingredients()...

    # Support editBooking via GET param
    edit_booking_id = request.args.get('edit_booking_id')
    staff_code = request.form.get('staff') if request.method == 'POST' else None
    class_code = request.form.get('classcode') if request.method == 'POST' else None
    date_required = request.form.get('date') if request.method == 'POST' else None
    period = request.form.get('period') if request.method == 'POST' else None
    recipe_id = request.form.get('recipe') if request.method == 'POST' else None
    class_size = request.form.get('class_size') if request.method == 'POST' else None

    # If editing, pre-fill form fields from booking
    if edit_booking_id:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM class_bookings WHERE id = %s', (edit_booking_id,))
            booking = c.fetchone()
            if booking:
                staff_code = booking['staff_code']
                class_code = booking['class_code']
                date_required = booking['date_required']
                period = str(booking['period']) if booking['period'] is not None else ''
                recipe_id = booking['recipe_id']
                class_size = booking['desired_servings']

    # Standard form POST handling: insert or update booking
    if request.method == 'POST' and staff_code and class_code and date_required and period and recipe_id:
        edit_booking_id = request.form.get('edit_booking_id')
        with get_db_connection() as conn:
            c = conn.cursor()
            if edit_booking_id:
                # Update existing booking
                c.execute('''UPDATE class_bookings SET staff_code=%s, class_code=%s, date_required=%s, period=%s, recipe_id=%s, desired_servings=%s WHERE id=%s''',
                          (staff_code, class_code, date_required, period, recipe_id, class_size or 24, edit_booking_id))
                conn.commit()
                flash('Booking updated successfully.', 'success')
                return redirect(url_for('book_a_class.book_a_class'))
            else:
                # Insert new booking
                c.execute('''INSERT INTO class_bookings (staff_code, class_code, date_required, period, recipe_id, desired_servings)
                             VALUES (%s, %s, %s, %s, %s, %s)''',
                          (staff_code, class_code, date_required, period, recipe_id, class_size or 24))
                conn.commit()

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
        c.execute('SELECT ClassCode, COALESCE(class_size, 24) as class_size FROM classes ORDER BY ClassCode')
        all_classes = [{'classcode': r['classcode'], 'class_size': r['class_size']} for r in c.fetchall() if r['classcode']]
        most_used_classes = [c for c in all_classes if c['classcode'] in most_used_class_codes]
        other_classes = [c for c in all_classes if c['classcode'] not in most_used_class_codes]
        most_used_classes.sort(key=lambda x: most_used_class_codes.index(x['classcode']))
        classes = most_used_classes + other_classes
        c.execute('SELECT id, name, ingredients, serving_size FROM recipes ORDER BY LOWER(name)')
        rows = c.fetchall()

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
                          pre_recipe_id=recipe_id, pre_class_size=class_size or 24)

@book_a_class_bp.route('/class_ingredients/download', methods=['POST'])
@require_role('VP', 'DK')
def class_ingredients_download():
    # ...existing code from app.py class_ingredients_download()...
    data = request.get_json() or {}
    recipe_id = data.get('recipe_id')
    desired = int(data.get('desired_servings') or 24)
    if not recipe_id:
        return jsonify({'error':'recipe_id required'}), 400

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT id, name, ingredients, serving_size FROM recipes WHERE id = %s', (recipe_id,))
        row = c.fetchone()
        if not row:
            return jsonify({'error':'recipe not found'}), 404
        try:
            ings = json.loads(row['ingredients'] or '[]')
        except Exception:
            ings = []

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(['ingredient','quantity','unit','notes'])
    orig_serv = int(row['serving_size']) if row['serving_size'] else 1
    for it in ings:
        name = ''
        qty = ''
        unit = ''
        if isinstance(it, dict):
            name = it.get('ingredient') or ''
            qty = it.get('quantity') or ''
            unit = it.get('unit') or ''
            try:
                qn = float(str(qty))
                per_single = qn / orig_serv
                scaled = per_single * desired
                qty = round(scaled,2)
            except Exception:
                qty = ''
        else:
            name = str(it)
        writer.writerow([name, qty, unit, ''])

    csv_data = buf.getvalue()
    return (csv_data, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename="shopping_{recipe_id}.csv"'
    })


# --- API endpoint for scheduled bookings (for modal popup) ---
@book_a_class_bp.route('/api/scheduled_bookings')
def api_scheduled_bookings():
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''
                SELECT cb.date_required, cb.period, cb.class_code, r.name as recipe_name, cb.desired_servings AS servings,
                       t.last_name, t.first_name, t.title, t.code as staff_code
                FROM class_bookings cb
                LEFT JOIN recipes r ON cb.recipe_id = r.id
                LEFT JOIN teachers t ON cb.staff_code = t.code
                ORDER BY cb.date_required, cb.period
            ''')
            bookings = []
            for row in c.fetchall():
                # Robust date handling
                date_val = row['date_required']
                if hasattr(date_val, 'strftime'):
                    date_str = date_val.strftime('%Y-%m-%d')
                elif isinstance(date_val, str):
                    date_str = date_val
                elif date_val is not None:
                    date_str = str(date_val)
                else:
                    date_str = ''
                staff_display = f"{row['staff_code']} - {row['last_name']}, {row['first_name']}"
                bookings.append({
                    'date_required': date_str,
                    'period': row['period'],
                    'class_code': row['class_code'],
                    'recipe_name': row['recipe_name'],
                    'servings': row['servings'],
                    'staff_display': staff_display
                })
        return jsonify({'success': True, 'bookings': bookings})
    except Exception as e:
        print('[ERROR] Failed to fetch scheduled bookings:', e)
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@book_a_class_bp.route('/class_ingredients/save', methods=['POST'])
@require_role('VP', 'DK')
def class_ingredients_save():
    # ...existing code from app.py class_ingredients_save()...
    try:
        data = request.get_json() or {}
        booking_id = data.get('booking_id')
        staff_code = data.get('staff')
        class_code = data.get('classcode')
        date_required = data.get('date')
        period = data.get('period')
        recipe_id = data.get('recipe_id')
        desired = int(data.get('desired_servings') or 24)
        missing = []
        for field, value in [('staff', staff_code), ('classcode', class_code), ('date', date_required), ('period', period), ('recipe_id', recipe_id)]:
            if value in [None, '']:
                missing.append(field)
        if missing:
            return jsonify({'error': f'Missing required fields: {missing}'}), 400
        with get_db_connection() as conn:
            c = conn.cursor()
            if booking_id:
                c.execute('''UPDATE class_bookings \
                            SET staff_code=%s, class_code=%s, date_required=%s, period=%s, recipe_id=%s, desired_servings=%s
                            WHERE id=%s''',
                         (staff_code, class_code, date_required, period, recipe_id, desired, booking_id))
                conn.commit()
            else:
                c.execute('INSERT INTO class_bookings (staff_code, class_code, date_required, period, recipe_id, desired_servings) VALUES (%s, %s, %s, %s, %s, %s)',
                          (staff_code, class_code, date_required, period, recipe_id, desired))
                conn.commit()
                booking_id = c.lastrowid
        return jsonify({'success': True, 'booking_id': booking_id})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 400

@book_a_class_bp.route('/class_ingredients/delete/<int:booking_id>', methods=['POST'])
@require_role('Admin', 'Teacher')

def class_ingredients_delete(booking_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM class_bookings WHERE id = %s', (booking_id,))
        conn.commit()
    flash('Booking deleted successfully.', 'success')
    return redirect(url_for('book_a_class.book_a_class'))



