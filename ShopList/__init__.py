from flask import Blueprint, render_template

shoplist_bp = Blueprint('shoplist', __name__, template_folder='templates')

@shoplist_bp.route('/shoplist')
def shoplist():
    """Serve the rebuilt Shopping List page (now default)."""
    # Pass dummy data to prevent template errors
    bookings = []
    recipes = []
    dates = []
    return render_template('shoplist.html', bookings=bookings, recipes=recipes, dates=dates)
