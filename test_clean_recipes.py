import unittest
import sqlite3
from clean_recipes import remove_junk_recipes, remove_duplicate_recipes, fix_recipe_names

class TestCleanRecipes(unittest.TestCase):
    def test_remove_junk_recipes_with_missing_table(self):
        # Test error handling when the recipes table is missing
        # Use a fresh in-memory DB with no table
        conn = sqlite3.connect(':memory:')
        # Should not raise, should log error and return []
        result = remove_junk_recipes(conn)
        self.assertEqual(result, [])
        conn.close()

    def test_remove_junk_recipes_with_custom_patterns(self):
        # Custom pattern to match "Chocolate Cake" as junk
        custom_patterns = [r'chocolate cake']
        self.conn.execute("INSERT INTO recipes (name, instructions) VALUES (?, ?)", ("Chocolate Cake", "Bake it"))
        self.conn.execute("INSERT INTO recipes (name, instructions) VALUES (?, ?)", ("Skills", "irrelevant"))
        self.conn.commit()
        deleted = remove_junk_recipes(self.conn, junk_patterns=custom_patterns)
        self.assertIn("Chocolate Cake", deleted)
        c = self.conn.cursor()
        c.execute("SELECT name FROM recipes")
        names = [row[0] for row in c.fetchall()]
        self.assertNotIn("Chocolate Cake", names)
        # "Skills" should remain since not in custom pattern
        self.assertIn("Skills", names)
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.execute('''CREATE TABLE recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            instructions TEXT
        )''')

    def tearDown(self):
        self.conn.close()

    def test_remove_junk_recipes(self):
        self.conn.execute("INSERT INTO recipes (name, instructions) VALUES (?, ?)", ("Skills", "irrelevant"))
        self.conn.execute("INSERT INTO recipes (name, instructions) VALUES (?, ?)", ("Chocolate Cake", "Bake it"))
        self.conn.commit()
        deleted = remove_junk_recipes(self.conn)
        self.assertIn("Skills", deleted)
        c = self.conn.cursor()
        c.execute("SELECT name FROM recipes")
        names = [row[0] for row in c.fetchall()]
        self.assertIn("Chocolate Cake", names)
        self.assertNotIn("Skills", names)

    def test_remove_duplicate_recipes(self):
        self.conn.execute("INSERT INTO recipes (name, instructions) VALUES (?, ?)", ("Pancakes", "Mix and fry"))
        self.conn.execute("INSERT INTO recipes (name, instructions) VALUES (?, ?)", ("pancakes", "Mix and fry"))
        self.conn.commit()
        deleted = remove_duplicate_recipes(self.conn)
        self.assertIn("pancakes", deleted)
        c = self.conn.cursor()
        c.execute("SELECT name FROM recipes")
        names = [row[0] for row in c.fetchall()]
        self.assertIn("Pancakes", names)
        self.assertNotIn("pancakes", names)

    def test_fix_recipe_names(self):
        self.conn.execute("INSERT INTO recipes (name, instructions) VALUES (?, ?)", ("Making Activity 1: Chee se", "Do it"))
        self.conn.execute("INSERT INTO recipes (name, instructions) VALUES (?, ?)", ("Year7 Food Technology 43 Mushr oom", "Do it"))
        self.conn.commit()
        fixed = fix_recipe_names(self.conn)
        c = self.conn.cursor()
        c.execute("SELECT name FROM recipes")
        names = [row[0] for row in c.fetchall()]
        self.assertIn("Cheese", names)
        self.assertIn("Mushroom", names)
        self.assertIn("Making Activity 1: Chee se", fixed)
        self.assertIn("Year7 Food Technology 43 Mushr oom", fixed)

if __name__ == '__main__':
    unittest.main()
