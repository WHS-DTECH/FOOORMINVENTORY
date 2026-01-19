
from flask import Blueprint, render_template, request
from . import shoppinglist
from auth import get_db_connection
import datetime

shoplist_bp = Blueprint('shoplist', __name__, template_folder='templates')

# Route for the new menu item 'Book the Shopping'

@shoplist_bp.route('/book_the_shopping')
def book_the_shopping():
    """Serve the new Shopping List UI for the Book the Shopping menu item with week navigation."""
    week_offset = 0
    if 'week' in request.args:
        try:
            week_offset = int(request.args.get('week', 0))
        except ValueError:
            week_offset = 0
    week_dates = shoppinglist.get_week_dates(week_offset)
    week_label = shoppinglist.get_week_label(week_dates)
    grid = shoppinglist.get_dummy_grid(week_dates)

    # Fetch all scheduled bookings for the week from the database
    scheduled_bookings = []
    selected_bookings = []
    start_date = week_dates[0]
    end_date = week_dates[-1]
    with get_db_connection() as conn:
        c = conn.cursor()
        # Scheduled bookings for the week (for grid and modal)
        c.execute('''
            SELECT cb.date_required, cb.period, cb.class_code, cb.staff_code, r.name AS recipe, cb.desired_servings AS servings, t.first_name, t.last_name
            FROM class_bookings cb
            LEFT JOIN recipes r ON cb.recipe_id = r.id
            LEFT JOIN teachers t ON cb.staff_code = t.code
            WHERE cb.date_required >= %s AND cb.date_required <= %s
            ORDER BY cb.date_required, cb.period
        ''', (start_date, end_date))
        for row in c.fetchall():
            teacher = f"{row['last_name']}, {row['first_name']}" if row['first_name'] and row['last_name'] else row['staff_code']
            scheduled_bookings.append({
                'date': row['date_required'].strftime('%Y-%m-%d'),
                'period': row['period'],
                'staff': f"{row['staff_code']} - {teacher}",
                'class': row['class_code'],
                'recipe': row['recipe'],
                'servings': row['servings']
            })

        # Selected bookings (grouped by teacher, for sidebar)
        c.execute('''
            SELECT cb.staff_code, t.first_name, t.last_name, cb.date_required, cb.class_code, r.name AS recipe
            FROM class_bookings cb
            LEFT JOIN teachers t ON cb.staff_code = t.code
            LEFT JOIN recipes r ON cb.recipe_id = r.id
            WHERE cb.date_required >= %s AND cb.date_required <= %s
            ORDER BY t.last_name, t.first_name, cb.date_required, cb.class_code, r.name
        ''', (start_date, end_date))
        for row in c.fetchall():
            teacher = f"{row['last_name']}, {row['first_name']}" if row['first_name'] and row['last_name'] else row['staff_code']
            selected_bookings.append({
                'teacher': teacher,
                'staff_code': row['staff_code'],
                'date': row['date_required'].strftime('%Y-%m-%d'),
                'class': row['class_code'],
                'recipe': row['recipe'],
            })

    # Normalize teacher+staff_code for grouping (case-insensitive, strip whitespace)
    for b in selected_bookings:
        b['teacher_key'] = b['teacher'].strip().lower()
    selected_bookings = sorted(selected_bookings, key=lambda b: (b['teacher_key'], b['date'], b['class'], b['recipe']))

    # Assign a color to each teacher
    teacher_colors = ['#1976d2', '#43a047', '#e53935', '#fbc02d', '#8e24aa', '#00838f', '#6d4c41', '#c62828', '#3949ab', '#f57c00']
    teacher_color_map = {}
    if selected_bookings:
        teacher_idx = 0
        for b in selected_bookings:
            tkey = b['teacher_key']
            if tkey not in teacher_color_map:
                teacher_color_map[tkey] = teacher_colors[teacher_idx % len(teacher_colors)]
                teacher_idx += 1

    # Populate grid with bookings
    for b in scheduled_bookings:
        date_obj = datetime.datetime.strptime(b['date'], '%Y-%m-%d').date()
        b['date_display'] = date_obj.strftime('%d/%m/%Y')
        key = (b['period'], date_obj)
        grid[key] = b

    return render_template(
        'shoplist_new.html',
        week_label=week_label,
        week_dates=week_dates,
        grid=grid,
        bookings=scheduled_bookings,
        week_offset=week_offset,
        scheduled_bookings=scheduled_bookings,
        selected_bookings=selected_bookings,
        teacher_color_map=teacher_color_map
    )
