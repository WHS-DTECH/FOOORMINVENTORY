
# ...existing code...

# Place the /get_original_recipes route after the blueprint definition

@shoplist_bp.route('/get_original_recipes', methods=['POST'])
def get_original_recipes():
    """Return original recipe details for selected bookings as JSON."""
    data = request.get_json()
    # Expecting a list of dicts: [{"recipe": "Perfect Pavlova Recipe"}, ...]
    recipe_names = [b.get('recipe') for b in data.get('bookings', []) if b.get('recipe')]
    if not recipe_names:
        return {"success": False, "recipes": []}
    # Remove duplicates
    recipe_names = list(set(recipe_names))
    recipes = []
    with get_db_connection() as conn:
        c = conn.cursor()
        for name in recipe_names:
            c.execute('SELECT name, serving_size, ingredients FROM recipes WHERE name = %s LIMIT 1', (name,))
            row = c.fetchone()
            if row:
                try:
                    ingredients = row['ingredients']
                    if isinstance(ingredients, str):
                        import json
                        ingredients = json.loads(ingredients)
                except Exception:
                    ingredients = []
                recipes.append({
                    'name': row['name'],
                    'serving_size': row['serving_size'],
                    'ingredients': ingredients
                })
    return {"success": True, "recipes": recipes}
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


    # Assign a color and pastel (light) color to each teacher
    teacher_colors = ['#1976d2', '#43a047', '#e53935', '#fbc02d', '#8e24aa', '#00838f', '#6d4c41', '#c62828', '#3949ab', '#f57c00']
    # Pastel (light) versions for grid backgrounds (manually chosen for readability)
    teacher_pastel_colors = ['#d6e6fa', '#d6f5d6', '#f9d6d6', '#fdf5d6', '#f3d6fa', '#d6f5f9', '#ede2d6', '#fad6d6', '#e0e6fa', '#fbeed6']
    teacher_color_map = {}
    teacher_pastel_map = {}
    teacher_idx = 0
    for b in selected_bookings:
        tkey = b['teacher_key']
        if tkey not in teacher_color_map:
            teacher_color_map[tkey] = teacher_colors[teacher_idx % len(teacher_colors)]
            teacher_pastel_map[tkey] = teacher_pastel_colors[teacher_idx % len(teacher_pastel_colors)]
            teacher_idx += 1
        b['color'] = teacher_color_map[tkey]
        b['light_color'] = teacher_pastel_map[tkey]

    # Attach color and pastel color to each scheduled booking (for grid)
    for b in scheduled_bookings:
        # Try to match teacher name as in selected_bookings
        teacher = b.get('staff', '').split(' - ', 1)[-1].strip().lower()
        color = teacher_color_map.get(teacher)
        pastel = teacher_pastel_map.get(teacher)
        if not color:
            # fallback: try staff_code
            color = teacher_color_map.get(b.get('staff', '').strip().lower())
            pastel = teacher_pastel_map.get(b.get('staff', '').strip().lower())
        b['color'] = color or '#888888'  # fallback gray
        b['light_color'] = pastel or '#f8fafc'  # fallback very light

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
