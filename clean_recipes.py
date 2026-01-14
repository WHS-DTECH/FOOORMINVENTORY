#!/usr/bin/env python3
"""Clean up recipe database - remove duplicates and non-recipes."""

import os
basedir = os.path.abspath(os.path.dirname(__file__))
import sqlite3
import json
import re
import argparse
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def get_args():
    """
    Parse command-line arguments for database path and config file.
    Returns:
        argparse.Namespace: Parsed arguments with db and config attributes.
    """
    parser = argparse.ArgumentParser(description='Clean up recipe database - remove duplicates and non-recipes.')
    parser.add_argument('--db', type=str, default=None, help='Path to the recipes database file')
    parser.add_argument('--config', type=str, default=None, help='Path to custom cleaning rules config file (JSON or TXT)')
    args, _ = parser.parse_known_args()
    return args

def get_database_path(args):
    """
    Determine the path to the recipes database file.
    Args:
        args (argparse.Namespace): Parsed command-line arguments.
    Returns:
        str: Path to the database file.
    """
    if args.db:
        return args.db
    basedir = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(basedir, 'recipes.db')

def load_patterns_from_config(config_path):
    """
    Load junk patterns from a config file (JSON or plain text).
    Args:
        config_path (str): Path to the config file.
    Returns:
        list or None: List of regex patterns, or None if not provided or error.
    """
    if not config_path:
        return None
    try:
        if config_path.endswith('.json'):
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'junk_patterns' in data:
                    return data['junk_patterns']
                elif isinstance(data, list):
                    return data
        else:
            # Assume plain text, one pattern per line, skip comments/empty lines
            with open(config_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    except Exception as e:
        logging.error(f"Failed to load config file {config_path}: {e}")
        return None

    """
    Remove recipes that are clearly not recipes (worksheet questions, etc.).
    Args:
        conn (sqlite3.Connection): Database connection.
        junk_patterns (list, optional): List of regex patterns to match junk recipes. If None, use defaults.
    Returns:
        list: Names of deleted recipes.
    """
    try:
        c = conn.cursor()
        # Fetch all recipes (id, name, instructions)
        c.execute('SELECT id, name, instructions FROM recipes')
        rows = c.fetchall()
    except Exception as e:
        logging.error(f"Error fetching recipes for junk removal: {e}")
        return []
    if junk_patterns is None:
        junk_patterns = [
            r'\bname \d+ different\b',
            r'\bworking towards\b',
            r'\btick the appropriate\b',
            r'\bcorrect all spellings\b',
            r'\bweek \d+.*knowledge check\b',
            r'\bgive \d+ example\b',
            r'\bwhat could happen\b',
            r'\bwhat does.*mean\b',
            r'\bhow many\b',
            r'\bspellings\b',
            r'^skills$',
            r'^review$',
            r'\bunknown recipe\b',
            r'^\d+\.\d+\s+\d+$',  # Just numbers
            r'\beatwell\b',
            r'\bhedonic scale\b',
            r'\bdesign your own\b',
            r'\brecipe writing sheet\b',
            r'●.*●.*●',  # Multiple bullet points (likely page headers)
            r'^year \d+.*food technology\s*$',  # Just year/food tech header
            r'^making activity\s*:?\s*$',  # Blank "Making Activity" with no name
            r'forfar bridies.*makes 2 bridies',  # Incomplete Forfar Bridies parse
            r'\bfood preparation\b',  # "Food preparation skills"
            r'\bused in the\b',  # Partial sentences
            r'^you\.$',  # Just "you."
            r'salad:$',  # Ends with "salad:"
            r'cous\.$',  # Just "Cous."
        ]
    to_delete = []
    deleted = []
    for row in rows:
        recipe_id, name, instructions = row
        name_lower = name.lower() if name else ''
        inst_lower = instructions.lower() if instructions else ''
        # Skip recipes with very short names (likely junk)
        if name and len(name.strip()) < 3:
            logging.info(f"Deleting recipe with too-short name: '{name}'")
            to_delete.append((recipe_id,))
            deleted.append(name)
            continue
        # Check if name or instructions match any junk pattern
        is_junk = False
        for pattern in junk_patterns:
            if re.search(pattern, name_lower) or re.search(pattern, inst_lower):
                is_junk = True
                break
        if is_junk:
            logging.info(f"Deleting junk recipe: {name}")
            to_delete.append((recipe_id,))
            deleted.append(name)
    # Batch delete all junk recipes
    if to_delete:
        c.executemany('DELETE FROM recipes WHERE id = ?', to_delete)
    conn.commit()
    return deleted


def remove_duplicate_recipes(conn):
    """
    Remove duplicate recipes based on normalized name (case-insensitive, whitespace-insensitive).
    Args:
        conn (sqlite3.Connection): Database connection.
    Returns:
        list: Names of deleted duplicate recipes.
    """
    try:
        c = conn.cursor()
        # Fetch all recipes (id, name) ordered by id
        c.execute('SELECT id, name FROM recipes ORDER BY id')
        rows = c.fetchall()
    except Exception as e:
        logging.error(f"Error fetching recipes for duplicate removal: {e}")
        return []
    
    def normalize(s):
        if not s:
            return ''
        s = s.lower()
        # Remove extra spaces
        s = re.sub(r'\s+', ' ', s)
        s = s.strip()
        return s
    
    seen = {}
    to_delete = []
    deleted = []
    for row in rows:
        recipe_id, name = row
        norm_name = normalize(name)
        # If normalized name already seen, mark as duplicate
        if norm_name in seen:
            logging.info(f"Deleting duplicate: {name} (keeping id {seen[norm_name]})")
            to_delete.append((recipe_id,))
            deleted.append(name)
        else:
            seen[norm_name] = recipe_id
    # Batch delete all duplicates
    if to_delete:
        c.executemany('DELETE FROM recipes WHERE id = ?', to_delete)
    conn.commit()
    return deleted


def fix_recipe_names(conn):
    """
    Fix recipe names with spacing issues and remove prefixes like 'Making Activity' or 'Year7 Food Technology'.
    Args:
        conn (sqlite3.Connection): Database connection.
    Returns:
        list: Names of recipes that were fixed or deleted due to duplication after fixing.
    """
    try:
        c = conn.cursor()
        # Fetch all recipes (id, name)
        c.execute('SELECT id, name FROM recipes')
        rows = c.fetchall()
    except Exception as e:
        logging.error(f"Error fetching recipes for name fixing: {e}")
        return []
    
    fixed = []
    for row in rows:
        recipe_id, name = row
        original_name = name
        # Remove prefixes like "Making Activity 1:", "Year7 Food Technology 43"
        name = re.sub(r'^Making Activity\s+\d+:\s*', '', name, flags=re.I)
        name = re.sub(r'^Year\s*\d+\s+Food Technology\s+\d+\s*', '', name, flags=re.I)
        # Fix spacing issues like "Chee se" -> "Cheese", "Mushr oom" -> "Mushroom"
        # But don't join common connector words (and, or, with, etc.)
        # Split into words and check each pair for possible joining
        words = name.split()
        fixed_words = []
        i = 0
        while i < len(words):
            if i < len(words) - 1:
                current = words[i]
                next_word = words[i + 1]
                # List of common connector words to avoid joining
                connectors = ['and', 'or', 'with', '&', 'in', 'on', 'de', 'a', 'the']
                # Only join if both are short and next is not a connector
                if next_word.lower() not in connectors and len(current) <= 6 and len(next_word) <= 4:
                    # Check if this looks like a broken word (both parts short)
                    if len(current) + len(next_word) <= 10:  # Reasonable word length
                        # Join them and skip next
                        fixed_words.append(current + next_word)
                        i += 2
                        continue
            fixed_words.append(words[i])
            i += 1
        name = ' '.join(fixed_words)
        # Clean up extra spaces
        name = re.sub(r'\s+', ' ', name).strip()
        # If name was changed, update or delete if duplicate
        if name != original_name:
            logging.info(f"Fixing name: '{original_name}' -> '{name}'")
            # Check if this name already exists (duplicate after cleaning)
            c.execute('SELECT id FROM recipes WHERE name = ? AND id != ?', (name, recipe_id))
            existing = c.fetchone()
            if existing:
                logging.info(f"  -> Would create duplicate, deleting this entry instead")
                c.execute('DELETE FROM recipes WHERE id = ?', (recipe_id,))
            else:
                c.execute('UPDATE recipes SET name = ? WHERE id = ?', (name, recipe_id))
            fixed.append(original_name)
    # Commit all changes
    conn.commit()
    return fixed


def main():
    """
    Main entry point for cleaning the recipe database. Handles argument parsing, config loading,
    and runs all cleaning steps with error handling and logging.
    """
    args = get_args()
    db_path = get_database_path(args)
    logging.info(f"Cleaning database: {db_path}")

    # Load custom patterns if provided
    custom_patterns = load_patterns_from_config(args.config)

    try:
        with sqlite3.connect(db_path) as conn:
            try:
                logging.info("\n1. Removing junk recipes...")
                junk = remove_junk_recipes(conn, junk_patterns=custom_patterns)
                logging.info(f"   Deleted {len(junk)} junk entries")
            except Exception as e:
                logging.error(f"Error during junk recipe removal: {e}")

            try:
                logging.info("\n2. Removing duplicates...")
                dupes = remove_duplicate_recipes(conn)
                logging.info(f"   Deleted {len(dupes)} duplicates")
            except Exception as e:
                logging.error(f"Error during duplicate removal: {e}")

            try:
                logging.info("\n3. Fixing recipe names...")
                fixed = fix_recipe_names(conn)
                logging.info(f"   Fixed {len(fixed)} names")
            except Exception as e:
                logging.error(f"Error during name fixing: {e}")

            try:
                logging.info("\n4. Final recipe count...")
                c = conn.cursor()
                c.execute('SELECT COUNT(*) FROM recipes')
                count = c.fetchone()[0]
                logging.info(f"   Total recipes: {count}")
            except Exception as e:
                logging.error(f"Error fetching final recipe count: {e}")

            try:
                logging.info("\n5. Recipe list:")
                c.execute('SELECT id, name FROM recipes ORDER BY name')
                for row in c.fetchall():
                    logging.info(f"   [{row[0]}] {row[1]}")
            except Exception as e:
                logging.error(f"Error fetching recipe list: {e}")

        logging.info("\nDone!")
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")


if __name__ == '__main__':
    main()
