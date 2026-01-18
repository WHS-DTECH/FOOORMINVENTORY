"""
Confirmation logic for the Instructions field in the parser debug workflow.
"""

def confirm_instructions(raw_instructions, test_recipe_id):
    from app import get_db_connection  # Local import to avoid circular import
    # TODO: Add real instructions validation/cleaning logic if needed
    confirmed_instructions = raw_instructions
    with get_db_connection() as conn:
        c = conn.cursor()
        # Upsert logic: update if exists, else insert
        c.execute('''
            INSERT INTO confirmed_parser_fields (parser_test_recipe_id, instructions)
            VALUES (%s, %s)
            ON CONFLICT (parser_test_recipe_id) DO UPDATE SET instructions = EXCLUDED.instructions
        ''', (test_recipe_id, confirmed_instructions))
        conn.commit()
    return confirmed_instructions
