# Google authentication logic will be moved here.
# Example placeholder for Google OAuth functions.

def login():
    pass

from flask import Blueprint
google_auth_bp = Blueprint('google_auth', __name__)

@google_auth_bp.route('/auth/callback')
def callback():
    print("[DEBUG] /auth/callback route hit!")
    import os
    import psycopg2
    from flask import request, session, redirect, url_for
    print("[DEBUG] Google OAuth callback triggered.")
    user_info = session.get('google_user')
    print(f"[DEBUG] session['google_user']: {user_info}")
    if not user_info:
        print("[DEBUG] No user_info found in session. Redirecting to login.")
        return redirect(url_for('login'))
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
    # Continue with login flow (redirect to dashboard or home)
    return redirect(url_for('admin_task.admin'))

def logout():
    pass
