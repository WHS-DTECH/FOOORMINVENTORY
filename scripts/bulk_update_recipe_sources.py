# Bulk update recipe sources for specific recipes
# Sets the source to 'Year 7 Recipe Book.pdf (Pg X)' for each recipe in the list

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()
POSTGRES_URL = os.getenv('DATABASE_URL')

# List of (recipe name, page number) tuples
RECIPES_TO_UPDATE = [
    ("Fruit Smoothie", 16),
    ("Vietnamese Style Lettuce Cups", 26),
    ("Courgette and Cheese Muffins", 32),
    ("Banana & Chocolate chip Muffins", 36),
    ("Vegetable Couscous", 43),
    ("Apple and Sultana Crumble", 45),
    ("Forfar Bridies", 49),
    ("Beef Nachos", 53),
    ("S'more cake in a mug", 55),
]

SOURCE_TEMPLATE = "Year 7 Recipe Book.pdf (Pg {page})"

def main():
    with psycopg2.connect(POSTGRES_URL, cursor_factory=psycopg2.extras.RealDictCursor) as conn:
        c = conn.cursor()
        for name, page in RECIPES_TO_UPDATE:
            source = SOURCE_TEMPLATE.format(page=page)
            c.execute('UPDATE recipes SET source = %s WHERE LOWER(name) = LOWER(%s)', (source, name))
            print(f"Updated '{name}' to source: {source}")
        conn.commit()
        print("Bulk update complete.")

if __name__ == '__main__':
    main()
