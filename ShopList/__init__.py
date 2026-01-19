from flask import Blueprint, render_template, request
from . import shoppinglist

shoplist_bp = Blueprint('shoplist', __name__, template_folder='templates')

# Route for the new menu item 'Book the Shopping'
@shoplist_bp.route('/book_the_shopping')
def book_the_shopping():
    """Serve the new Shopping List UI for the Book the Shopping menu item with week navigation."""
    # Get week offset from query param, default to 0 (this week)
    week_offset = 0
    if 'week' in request.args:
        try:
            week_offset = int(request.args.get('week', 0))
        except ValueError:
            week_offset = 0
    week_dates = shoppinglist.get_week_dates(week_offset)
    week_label = shoppinglist.get_week_label(week_dates)
    grid = shoppinglist.get_dummy_grid(week_dates)
    # For demo, bookings and recipes are static; replace with real data as needed
    # Demo scheduled bookings for popup
    scheduled_bookings = [
        {'date': '2026-01-15', 'period': 3, 'staff': 'VP - Pringle, Vanessa', 'class': '100COMP', 'recipe': 'Apple and Sultana Crumble', 'servings': 24},
        {'date': '2026-01-16', 'period': 1, 'staff': 'Dk - Diplock, Maryke', 'class': 'MEET', 'recipe': 'Chocolate Chip Cookies', 'servings': 12},
        {'date': '2026-01-19', 'period': 1, 'staff': 'HM - McKee, Holly', 'class': 'WHANAU', 'recipe': 'Apple and Sultana Crumble', 'servings': 24},
        {'date': '2026-01-20', 'period': 3, 'staff': 'Rs - Reeves, Adrienne', 'class': 'VEHOME', 'recipe': 'Vegetable Couscous', 'servings': 24},
    ]
    return render_template(
        'shoplist_new.html',
        week_label=week_label,
        week_dates=week_dates,
        grid=grid,
        bookings=[],
        week_offset=week_offset,
        scheduled_bookings=scheduled_bookings
    )
