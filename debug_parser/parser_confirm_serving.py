"""
Confirmation logic for the Serving Size field in the parser debug workflow.
"""

def confirm_serving(raw_serving, test_recipe_id):
    from app import get_db_connection  # Local import to avoid circular import
    confirmed_serving = raw_serving
    from flask_login import current_user
    with get_db_connection() as conn:
        c = conn.cursor()
        confirmed_by = getattr(current_user, 'id', 'admin')
        # Upsert logic: always upsert into the same row for parser_debug_id
        c.execute('''
            INSERT INTO confirmed_parser_fields (parser_debug_id, serving_size, confirmed_by, confirmed_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (parser_debug_id) DO UPDATE SET
                serving_size = EXCLUDED.serving_size,
                confirmed_by = EXCLUDED.confirmed_by,
                confirmed_at = EXCLUDED.confirmed_at
        ''', (test_recipe_id, confirmed_serving, confirmed_by))
        conn.commit()
    return confirmed_serving
