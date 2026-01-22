"""
Confirmation logic for the Title field in the parser debug workflow.
"""

def confirm_title(raw_title, test_recipe_id):
    from app import get_db_connection  # Local import to avoid circular import
    # TODO: Add real title validation/cleaning logic if needed
    confirmed_title = raw_title
    from flask_login import current_user
    with get_db_connection() as conn:
        c = conn.cursor()
        confirmed_by = getattr(current_user, 'id', 'admin')
        # Upsert logic: update if exists, else insert
        c.execute('''
            INSERT INTO confirmed_parser_fields (parser_debug_id, title, confirmed_by, confirmed_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (parser_debug_id) DO UPDATE SET title = EXCLUDED.title, confirmed_by = EXCLUDED.confirmed_by, confirmed_at = EXCLUDED.confirmed_at
        ''', (test_recipe_id, confirmed_title, confirmed_by))
        conn.commit()
    return confirmed_title
