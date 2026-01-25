from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import os
import ast
import json
import datetime as dt
from flask_login import current_user, login_user, logout_user
from auth import require_role, get_db_connection, User
from admin_task.utils import get_staff_code_from_email
from google_auth_oauthlib.flow import Flow

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('class_ingredients'))
    return render_template('login.html')

@auth_bp.route('/auth/google')
def auth_google():
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'https://WHS-DTECH.pythonanywhere.com/auth/callback')
    if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
        flash('Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.')
        return redirect(url_for('login'))
    client_config = {
        'web': {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://accounts.google.com/o/oauth2/token',
            'redirect_uris': [GOOGLE_REDIRECT_URI]
        }
    }
    redirect_uri = GOOGLE_REDIRECT_URI
    flow = Flow.from_client_config(client_config, scopes=[
        'openid',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ], redirect_uri=redirect_uri)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='select_account'
    )
    session['oauth_state'] = state
    session['redirect_uri'] = redirect_uri
    return redirect(authorization_url)

@auth_bp.route('/auth/callback')
def auth_callback():
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'https://WHS-DTECH.pythonanywhere.com/auth/callback')
    state = session.get('oauth_state')
    redirect_uri = session.get('redirect_uri', GOOGLE_REDIRECT_URI)
    if not state:
        flash('OAuth state mismatch. Please try logging in again.')
        return redirect(url_for('login'))
    try:
        client_config = {
            'web': {
                'client_id': GOOGLE_CLIENT_ID,
                'client_secret': GOOGLE_CLIENT_SECRET,
                'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                'token_uri': 'https://accounts.google.com/o/oauth2/token',
                'redirect_uris': [redirect_uri]
            }
        }
        flow = Flow.from_client_config(client_config, scopes=[
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ], redirect_uri=redirect_uri, state=state)
        authorization_response = request.url.replace('http://', 'http://')
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        import requests as req_lib
        headers = {'Authorization': f'Bearer {credentials.token}'}
        response = req_lib.get(user_info_url, headers=headers)
        user_info = response.json()
        google_id = user_info.get('id')
        email = user_info.get('email')
        name = user_info.get('name', email.split('@')[0])
        staff_code = get_staff_code_from_email(email)
        user = User(google_id, email, name, staff_code)
        session['user'] = {
            'google_id': google_id,
            'email': email,
            'name': name,
            'staff_code': staff_code,
            'role': user.role
        }
        session['google_creds'] = {
            'token': credentials.token,
            'refresh_token': getattr(credentials, 'refresh_token', None),
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        login_user(user, remember=True)
        flash(f'Welcome, {name}!', 'success')
        return redirect(url_for('recipe_book.recbk'))
    except Exception as e:
        flash(f'Authentication error: {str(e)}')
        return redirect(url_for('login'))

@auth_bp.route('/logout')
def logout():
    logout_user()
    raw_data_filename = session.get('raw_data_file')
    if raw_data_filename:
        tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
        raw_data_path = os.path.join(tmp_dir, raw_data_filename)
        try:
            if os.path.exists(raw_data_path):
                os.remove(raw_data_path)
        except Exception:
            pass
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('recipe_book.recbk'))
