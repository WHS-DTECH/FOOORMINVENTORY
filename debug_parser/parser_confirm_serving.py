"""
Confirmation logic for the Serving Size field in the parser debug workflow.
"""

def confirm_serving(raw_serving, test_recipe_id):
    from app import get_db_connection  # Local import to avoid circular import
    # TODO: Add real serving size validation/cleaning logic if needed
    confirmed_serving = raw_serving
    with get_db_connection() as conn:
        c = conn.cursor()
        # Upsert logic: update if exists, else insert
        c.execute('''
            INSERT INTO confirmed_parser_fields (parser_debug_id, serving_size)
            VALUES (%s, %s)
            ON CONFLICT (parser_debug_id) DO UPDATE SET serving_size = EXCLUDED.serving_size
        ''', (test_recipe_id, confirmed_serving))
        conn.commit()
    return confirmed_serving
