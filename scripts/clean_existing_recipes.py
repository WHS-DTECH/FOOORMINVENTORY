# Script to clean up existing recipes in the database
# - Removes text before the first real recipe title (e.g., 'Quick Dinner Beef Nachos')
# - Sets the recipe name and serving size accordingly

import os
import re
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()
POSTGRES_URL = os.getenv('DATABASE_URL')
TITLE_REGEX = re.compile(r'(quick dinner beef nachos|[A-Z][a-z]+( [A-Z][a-z]+)+)', re.I)
SERVES_REGEX = re.compile(r'(?:per group of (\d+)|serves (\d+))', re.I)

def clean_recipe_text(text):
    """Finds the first real recipe title and trims text before it."""
    if not text:
        return text, None, None
    # Find the first real recipe title
    match = TITLE_REGEX.search(text)
    if match:
        title = match.group(1).strip()
        # Find serving size after the title
        serves_match = SERVES_REGEX.search(text[match.end():])
        serves = serves_match.group(1) or serves_match.group(2) if serves_match else None
        # Remove everything before the title
        cleaned = text[match.start():].strip()
        return cleaned, title, serves
    return text, None, None

def main():
    with psycopg2.connect(POSTGRES_URL, cursor_factory=psycopg2.extras.RealDictCursor) as conn:
        c = conn.cursor()
        c.execute('SELECT id, name, instructions FROM recipes')
        rows = c.fetchall()
        for row in rows:
            rid, name, instructions = row['id'], row['name'], row['instructions']
            cleaned, title, serves = clean_recipe_text(instructions or '')
            updates = {}
            if title and title != name:
                updates['name'] = title
            if serves:
                updates['serving_size'] = serves
            if cleaned and cleaned != instructions:
                updates['instructions'] = cleaned
            if updates:
                set_clause = ', '.join(f"{k} = %s" for k in updates)
                values = list(updates.values()) + [rid]
                c.execute(f'UPDATE recipes SET {set_clause} WHERE id = %s', values)
                print(f"Updated recipe {rid}: {updates}")
        conn.commit()
        print("Cleanup complete.")

if __name__ == '__main__':
    main()
