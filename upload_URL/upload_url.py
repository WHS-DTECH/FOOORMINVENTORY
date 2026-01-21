
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from auth import get_db_connection
import datetime

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
    # Get the submitted URL from the form
    url = request.form.get('url')
    if not url:
        flash('No URL provided.', 'danger')
        return redirect(url_for('upload_url.get_url_upload'))
    # Redirect to the extraction/review route with the URL as a query parameter
    return redirect(f"/load_recipe_url?url={url}")

upload_url_bp.add_url_rule('/upload_url', view_func=post_upload_url, methods=['POST'])

# Route: View raw upload
def view_raw_upload():
    # Logic for viewing raw upload
    # ...
    return render_template('upload_URL/view_raw_upload.html')

upload_url_bp.add_url_rule('/view_raw_upload', view_func=view_raw_upload, methods=['GET'])

# Route: Review extracted recipe from URL
def review_recipe_url():
    # Simulate extraction (replace with real extraction logic)
    url = request.args.get('url')
    extracted_title = url or ''
    raw_data = f"Extracted from: {url}"
    solution = ''
    strategies = '[{"result": "Match: recipe title from URL"}]'
    created_at = datetime.datetime.utcnow()
    user_id = current_user.get_id() if current_user.is_authenticated else None

    # Insert into parser_debug table
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO parser_debug (recipe_id, raw_data, extracted_title, strategies, solution, created_at, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (None, raw_data, extracted_title, strategies, solution, created_at, user_id))
        conn.commit()

    return render_template('upload_URL/review_recipe_url.html', extracted_title=extracted_title)

upload_url_bp.add_url_rule('/review_recipe_url', view_func=review_recipe_url, methods=['GET', 'POST'])

# Route: Recipe added confirmation
def url_recipe_added():
    # Logic for recipe added confirmation
    # ...
    return render_template('upload_URL/URL_recipe_added.html')

upload_url_bp.add_url_rule('/URL_recipe_added', view_func=url_recipe_added, methods=['GET'])
