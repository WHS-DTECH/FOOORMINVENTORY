"""
Confirmation logic for the Title field in the parser debug workflow.
"""

def confirm_title(raw_title, test_recipe_id):
    from app import get_db_connection  # Local import to avoid circular import
    # TODO: Add real title validation/cleaning logic if needed
    confirmed_title = raw_title
    with get_db_connection() as conn:
        c = conn.cursor()
        # Upsert logic: update if exists, else insert
        c.execute('''
            INSERT INTO confirmed_parser_fields (parser_test_recipe_id, title)
            VALUES (%s, %s)
            ON CONFLICT (parser_test_recipe_id) DO UPDATE SET title = EXCLUDED.title
        ''', (test_recipe_id, confirmed_title))
        conn.commit()
    return confirmed_title
