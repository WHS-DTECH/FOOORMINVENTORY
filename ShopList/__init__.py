from flask import Blueprint, render_template

shoplist_bp = Blueprint('shoplist', __name__, template_folder='templates')


# Route for the new menu item 'Book the Shopping'
@shoplist_bp.route('/book_the_shopping')
def book_the_shopping():
    """Serve the new Shopping List UI for the Book the Shopping menu item."""
    bookings = []
    recipes = []
    dates = []
    return render_template('shoplist_new.html', bookings=bookings, recipes=recipes, dates=dates)
