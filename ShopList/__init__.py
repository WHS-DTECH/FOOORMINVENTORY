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
    # Remove scheduled bookings for now
    return render_template(
        'shoplist_new.html',
        week_label=week_label,
        week_dates=week_dates,
        grid=grid,
        bookings=[],
        week_offset=week_offset
    )
