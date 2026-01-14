# Bulk update recipe sources for Year 8 Recipe Book recipes
# Sets the source to 'Year 8 Recipe Book.pdf (Pg X)' for each recipe in the list
# For recipes in both books, combines both sources

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()
POSTGRES_URL = os.getenv('DATABASE_URL')

# List of (recipe name, page number) tuples for Year 8
RECIPES_Y8 = [
    ("Mini Carrot Cakes", 8),
    ("Mushroom Risotto", 19),
    ("Fajitas", 23),
    ("Pizza", 27),
    ("Cauliflower Cheese", 33),
]
# Recipes in both books: (name, y7_page, y8_page)
RECIPES_BOTH = [
    ("Vietnamese Style Lettuce Cups", 26, 13),
    ("Vegetable Couscous", 43, 41),
    ("Beef Nachos", 53, 45),
]

def main():
    with psycopg2.connect(POSTGRES_URL, cursor_factory=psycopg2.extras.RealDictCursor) as conn:
        c = conn.cursor()
        # Update Year 8 only recipes
        for name, page in RECIPES_Y8:
            source = f"Year 8 Recipe Book.pdf (Pg {page})"
            c.execute('UPDATE recipes SET source = %s WHERE LOWER(name) = LOWER(%s)', (source, name))
            print(f"Updated '{name}' to source: {source}")
        # Update recipes in both books
        for name, y7_page, y8_page in RECIPES_BOTH:
            source = f"Year 7 Recipe Book.pdf (Pg {y7_page}); Year 8 Recipe Book.pdf (Pg {y8_page})"
            c.execute('UPDATE recipes SET source = %s WHERE LOWER(name) = LOWER(%s)', (source, name))
            print(f"Updated '{name}' to source: {source}")
        conn.commit()
        print("Bulk update for Year 8 complete.")

if __name__ == '__main__':
    main()
