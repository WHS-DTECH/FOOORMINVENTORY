# Google authentication logic will be moved here.
# Example placeholder for Google OAuth functions.

def login():
    pass

from flask import Blueprint
google_auth_bp = Blueprint('google_auth', __name__)


import requests
from flask import current_app, request, session, redirect, url_for
import os
import psycopg2

@google_auth_bp.route('/auth/callback')
def callback():

    print("[DEBUG] /auth/callback route hit!")
    code = request.args.get('code')
    if not code:
        print("[DEBUG] No code in request.args. Redirecting to login.")
        return redirect(url_for('login'))

    # Exchange code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": os.getenv('GOOGLE_CLIENT_ID', current_app.config.get('GOOGLE_CLIENT_ID')),
        "client_secret": os.getenv('GOOGLE_CLIENT_SECRET', current_app.config.get('GOOGLE_CLIENT_SECRET')),
        "redirect_uri": os.getenv('GOOGLE_REDIRECT_URI', current_app.config.get('GOOGLE_REDIRECT_URI')),
        "grant_type": "authorization_code"
    }
    token_resp = requests.post(token_url, data=data)
    if not token_resp.ok:
        print(f"[DEBUG] Token exchange failed: {token_resp.text}")
        return redirect(url_for('login'))
    tokens = token_resp.json()
    access_token = tokens.get("access_token")

    # Fetch user info
    userinfo_resp = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    if not userinfo_resp.ok:
        print(f"[DEBUG] Userinfo fetch failed: {userinfo_resp.text}")
        return redirect(url_for('login'))
    user_info = userinfo_resp.json()
    print(f"[DEBUG] Google user info: {user_info}")


    # Save user info in session for both keys (compatibility)
    session['google_user'] = user_info
    session['user'] = {
        'google_id': user_info.get('id'),
        'email': user_info.get('email'),
        'name': user_info.get('name'),
        'picture': user_info.get('picture'),
        'hd': user_info.get('hd'),
    }

    email = user_info.get('email')
    name = user_info.get('name')
    google_id = user_info.get('id')
    print(f"[DEBUG] Extracted user: email={email}, name={name}, google_id={google_id}")
    # Insert or update USERS table
    db_url = os.getenv('DATABASE_URL', 'postgresql://neondb_owner:npg_7EDJk4mGarQC@ep-holy-tooth-aff8oa6n-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require')
    try:
        conn = psycopg2.connect(db_url)
        c = conn.cursor()
        c.execute('''INSERT INTO users (email, name, google_id, last_login) VALUES (%s, %s, %s, NOW()) ON CONFLICT (email) DO UPDATE SET name=EXCLUDED.name, google_id=EXCLUDED.google_id, last_login=NOW()''', (email, name, google_id))
        conn.commit()
        conn.close()
        print(f"[DEBUG] User {email} inserted/updated in USERS table.")
    except Exception as e:
        print(f"[DEBUG] Error inserting/updating user in USERS table: {e}")

    # Grant admin access to Vanessa Pringle (for development/owner)
    if user_info.get('email', '').lower() == 'vanessapringle@westlandhigh.school.nz':
        try:
            with psycopg2.connect(db_url) as conn:
                c = conn.cursor()
                c.execute('INSERT INTO user_roles (email, role) VALUES (%s, %s) ON CONFLICT DO NOTHING', (email, 'Admin'))
                conn.commit()
                print('[DEBUG] Admin role (Admin) granted to Vanessa Pringle.')
        except Exception as e:
            print(f'[DEBUG] Error granting admin role: {e}')
        # Force reload of user roles in session after admin grant
        session['user']['staff_code'] = 'Admin'

    # Continue with login flow (redirect to dashboard or home)
    return redirect(url_for('admin_task.admin'))

def logout():
    pass
