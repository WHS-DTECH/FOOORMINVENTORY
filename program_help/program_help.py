from flask import Blueprint, render_template

program_help_bp = Blueprint('program_help', __name__, template_folder='templates')

@program_help_bp.route('/program_help')
def help_home():
    return render_template('program_help/help_home.html')
