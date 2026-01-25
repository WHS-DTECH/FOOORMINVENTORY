from flask import Blueprint, render_template, request
from debug_parser.debug_parser_URL import confirm_source_url
from auth import get_db_connection

# Blueprint for debug source url
bp = Blueprint('debug_source_url', __name__)

@bp.route('/debug_source_url/<int:parser_debug_id>', methods=['GET'])
def debug_source_url(parser_debug_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM parser_test_recipes WHERE id = %s', (parser_debug_id,))
        test_recipe = c.fetchone()
    if not test_recipe:
        return render_template('error.html', message='Test recipe not found.'), 404
    raw_url = test_recipe['upload_source_detail']
    debug_result = confirm_source_url(raw_url)
    return render_template('debug_source_url.html', test_recipe=test_recipe, debug_result=debug_result, parser_debug_id=parser_debug_id)
