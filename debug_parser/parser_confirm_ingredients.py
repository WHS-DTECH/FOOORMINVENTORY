"""
Confirmation logic for the Ingredients field in the parser debug workflow.
"""

def confirm_ingredients(raw_ingredients, parser_debug_id):
    from app import get_db_connection  # Local import to avoid circular import
    # TODO: Add real ingredients validation/cleaning logic if needed
    confirmed_ingredients = raw_ingredients
    from flask_login import current_user
    with get_db_connection() as conn:
        c = conn.cursor()
        confirmed_by = getattr(current_user, 'id', 'admin')
        # Upsert logic: update if exists, else insert
        c.execute('''
            INSERT INTO confirmed_parser_fields (parser_debug_id, ingredients, confirmed_by, confirmed_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (parser_debug_id) DO UPDATE SET ingredients = EXCLUDED.ingredients, confirmed_by = EXCLUDED.confirmed_by, confirmed_at = EXCLUDED.confirmed_at
        ''', (parser_debug_id, confirmed_ingredients, confirmed_by))
        conn.commit()
    return confirmed_ingredients
