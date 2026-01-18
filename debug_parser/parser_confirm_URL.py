# parser_confirm_URL.py
"""
Confirmation logic for the Source URL field in the parser debug workflow.
"""

from app import get_db_connection

def confirm_url(raw_url, test_recipe_id):
    """
    Validate and store the confirmed source URL in the confirmed_parser_fields table.
    Returns the confirmed value.
    """
    # TODO: Add real URL validation/cleaning logic if needed
    confirmed_url = raw_url
    with get_db_connection() as conn:
        c = conn.cursor()
        # Upsert logic: update if exists, else insert
        c.execute('''
            INSERT INTO confirmed_parser_fields (parser_test_recipe_id, source_url)
            VALUES (%s, %s)
            ON CONFLICT (parser_test_recipe_id) DO UPDATE SET source_url = EXCLUDED.source_url
        ''', (test_recipe_id, confirmed_url))
        conn.commit()
    return confirmed_url
