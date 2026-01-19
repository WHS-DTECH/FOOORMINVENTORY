
from flask import Blueprint

admin_task_bp = Blueprint('admin_task', __name__)

# Import all admin routes and utilities here
from . import admin_routes

