from flask import Blueprint, request, jsonify, session, flash, redirect, url_for
from auth import require_role, get_db_connection

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/update-recipe-tags/<int:recipe_id>', methods=['POST'])
@require_role('Admin', 'Teacher')
def update_recipe_tags(recipe_id):
    """Quick API to update recipe dietary tags, cuisine, and difficulty."""
    data = request.get_json()
    dietary_tags = data.get('dietary_tags', '')  # comma-separated
    cuisine = data.get('cuisine', '')
    difficulty = data.get('difficulty', '')
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''UPDATE recipes \
                    SET dietary_tags = %s, cuisine = %s, difficulty = %s\
                    WHERE id = %s''',
                 (dietary_tags, cuisine, difficulty, recipe_id))
        conn.commit()
    return jsonify({'success': True, 'message': 'Tags updated'})
