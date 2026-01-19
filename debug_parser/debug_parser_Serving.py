# debug_parser_Serving.py
# Layout and logic based on Title DEBUG code

from flask import Blueprint, render_template, request

debug_parser_serving_bp = Blueprint('debug_parser_serving', __name__, template_folder='templates')

@debug_parser_serving_bp.route('/debug_serving_size/<int:test_recipe_id>', methods=['GET', 'POST'])
def debug_serving_size(test_recipe_id):
    # Example: fetch test_recipe from DB (replace with actual DB logic)
    test_recipe = {
        'id': test_recipe_id,
        'serving_size': 'N/A',
        'upload_source_detail': '',
        'confirmed': {},
        'strategies': [],
        'raw_data': '',
    }
    solution = None
    if request.method == 'POST':
        solution = request.form.get('solution')
        # Save solution logic here
    return render_template(
        'debug_serving_size.html',
        test_recipe=test_recipe,
        solution=solution
    )
