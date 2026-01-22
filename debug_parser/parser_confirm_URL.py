"""
Confirmation logic for the Source URL field in the parser debug workflow.
"""

def confirm_url(raw_url, test_recipe_id):
    from app import get_db_connection  # Local import to avoid circular import
    # TODO: Add real URL validation/cleaning logic if needed
    confirmed_url = raw_url
    from flask_login import current_user
    with get_db_connection() as conn:
        c = conn.cursor()
        # Ensure parser_debug record exists for this test_recipe_id
        c.execute('SELECT id FROM parser_debug WHERE id = %s', (test_recipe_id,))
        if not c.fetchone():
            c.execute('INSERT INTO parser_debug (id, created_at) VALUES (%s, NOW())', (test_recipe_id,))
            conn.commit()
        confirmed_by = getattr(current_user, 'id', 'admin')
        # Upsert logic: update if exists, else insert
        c.execute('''
            INSERT INTO confirmed_parser_fields (parser_debug_id, source_url, confirmed_by, confirmed_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (parser_debug_id) DO UPDATE SET source_url = EXCLUDED.source_url, confirmed_by = EXCLUDED.confirmed_by, confirmed_at = EXCLUDED.confirmed_at
        ''', (test_recipe_id, confirmed_url, confirmed_by))
        conn.commit()
    return confirmed_url
