import sqlite3
import json


def setup_database():
    # Use a context manager so the connection is committed/closed automatically
    with sqlite3.connect('recipes.db') as conn:
        c = conn.cursor()

        # Create teachers table with requested fields
        c.execute(
            '''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            title TEXT,
            email TEXT
        )
    '''
        )

        # Create classes table
        c.execute(
            '''
        CREATE TABLE IF NOT EXISTS classes (
            ClassCode TEXT NOT NULL,
            LineNo INTEGER,
            Misc1 TEXT,
            RoomNo TEXT,
            CourseName TEXT,
            Misc2 TEXT,
            Year INTEGER,
            Dept TEXT,
            StaffCode TEXT,
            ClassSize INTEGER,
            TotalSize INTEGER,
            TimetableYear INTEGER,
            Misc3 TEXT,
            PRIMARY KEY (ClassCode, LineNo)
        )
    '''
        )

        # Create recipes table (store ingredients as JSON string)
        c.execute(
            '''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            ingredients TEXT NOT NULL,
            instructions TEXT,
            serving_size INTEGER
        )
    '''
        )

        # Insert example teachers (optional) using INSERT OR IGNORE to avoid duplicates
        example_teachers = [
            ('VP', 'Pringle', 'Vanessa', 'Ms', 'vanessa.pringle@school.edu'),
            ('JD', 'Doe', 'John', 'Mr', 'john.doe@school.edu'),
            ('AS', 'Smith', 'Alice', 'Mrs', 'alice.smith@school.edu')
        ]
        for code, last_name, first_name, title, email in example_teachers:
            c.execute(
                'INSERT OR IGNORE INTO teachers (code, last_name, first_name, title, email) VALUES (?, ?, ?, ?, ?)',
                (code, last_name, first_name, title, email),
            )

        # Insert example recipe (optional) using INSERT OR IGNORE
        example_ingredients = [
            {"quantity": 100.0, "unit": "g", "ingredient": "Quality Mark lamb mince"},
            {"quantity": 0.25, "unit": "Tbsp", "ingredient": "olive oil"},
            {"quantity": 0.25, "unit": "tsp", "ingredient": "ground cumin"},
            {"quantity": 0.25, "unit": "tsp", "ingredient": "smoked paprika"},
            {"quantity": 0.25, "unit": "tsp", "ingredient": "honey, pepper, to taste"},
            {"quantity": 0.5, "unit": "whole", "ingredient": "telegraph cucumbers, cut into chunks"},
            {"quantity": 62.5, "unit": "g", "ingredient": "cherry tomatoes, halved, ½ red onion, finely sliced, ½ cup fresh herbs, chopped, ½ cup olives, pitted and roughly chopped"},
            {"quantity": 37.5, "unit": "g", "ingredient": "feta cheese, ½ cup Greek style yoghurt"},
            {"quantity": 0.25, "unit": "Tbsp", "ingredient": "lemon juice"},
            {"quantity": 0.25, "unit": "Tbsp", "ingredient": "olive oil, Hot honey"},
            {"quantity": 1.0, "unit": "whole", "ingredient": "pita pockets, cut into triangles"}
        ]
        c.execute(
            'INSERT OR IGNORE INTO recipes (name, ingredients, instructions, serving_size) VALUES (?, ?, ?, ?)',
            ('Lamb Salad', json.dumps(example_ingredients), 'Mix ingredients and serve.', 1),
        )

    print("Database setup complete.")

if __name__ == '__main__':
    setup_database()