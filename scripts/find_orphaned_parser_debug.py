# Script to check for orphaned parser_debug rows (where recipe_id does not exist in parser_test_recipes)
# and optionally repair or report them.


import sys
import os
# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import get_db_connection

def find_orphaned_parser_debug():
    with get_db_connection() as conn:
        c = conn.cursor()
        # Find all parser_debug rows where recipe_id does not exist in parser_test_recipes
        c.execute('''
            SELECT pd.id AS parser_debug_id, pd.recipe_id
            FROM parser_debug pd
            LEFT JOIN parser_test_recipes ptr ON pd.recipe_id = ptr.id
            WHERE ptr.id IS NULL
        ''')
        orphans = c.fetchall()
        if not orphans:
            print('No orphaned parser_debug rows found!')
        else:
            print('Orphaned parser_debug rows:')
            for row in orphans:
                print(f"parser_debug.id={row['parser_debug_id']} points to missing recipe_id={row['recipe_id']}")
        return orphans

if __name__ == '__main__':
    find_orphaned_parser_debug()
