from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user

upload_url_bp = Blueprint(
    'upload_url',
    __name__,
    template_folder='templates/upload_URL'
)

# Route: URL upload form
def get_url_upload():
    return render_template('upload_URL/url_upload.html')

upload_url_bp.add_url_rule('/url_upload', view_func=get_url_upload, methods=['GET'])

# Route: Handle URL upload POST
def post_upload_url():
    # Logic for handling URL upload POST
    # ...
    return render_template('upload_URL/upload_recipe_url.html')

upload_url_bp.add_url_rule('/upload_url', view_func=post_upload_url, methods=['POST'])

# Route: View raw upload
def view_raw_upload():
    # Logic for viewing raw upload
    # ...
    return render_template('upload_URL/view_raw_upload.html')

upload_url_bp.add_url_rule('/view_raw_upload', view_func=view_raw_upload, methods=['GET'])

# Route: Review extracted recipe from URL
def review_recipe_url():
    # Logic for reviewing extracted recipe
    # ...
    return render_template('upload_URL/review_recipe_url.html')

upload_url_bp.add_url_rule('/review_recipe_url', view_func=review_recipe_url, methods=['GET', 'POST'])

# Route: Recipe added confirmation
def url_recipe_added():
    # Logic for recipe added confirmation
    # ...
    return render_template('upload_URL/URL_recipe_added.html')

upload_url_bp.add_url_rule('/URL_recipe_added', view_func=url_recipe_added, methods=['GET'])
