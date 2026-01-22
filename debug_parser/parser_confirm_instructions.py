"""
Confirmation logic for the Instructions field in the parser debug workflow.
"""

def confirm_instructions(raw_instructions, test_recipe_id):
    from app import get_db_connection  # Local import to avoid circular import
    # TODO: Add real instructions validation/cleaning logic if needed
    confirmed_instructions = raw_instructions
    from flask_login import current_user
    with get_db_connection() as conn:
        c = conn.cursor()
        confirmed_by = getattr(current_user, 'id', 'admin')
        # Upsert logic: update if exists, else insert
        c.execute('''
            INSERT INTO confirmed_parser_fields (parser_debug_id, instructions, confirmed_by, confirmed_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (parser_debug_id) DO UPDATE SET instructions = EXCLUDED.instructions, confirmed_by = EXCLUDED.confirmed_by, confirmed_at = EXCLUDED.confirmed_at
        ''', (test_recipe_id, confirmed_instructions, confirmed_by))
        conn.commit()
    return confirmed_instructions
