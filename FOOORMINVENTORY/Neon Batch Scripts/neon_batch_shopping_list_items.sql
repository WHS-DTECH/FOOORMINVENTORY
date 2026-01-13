-- NEON/POSTGRESQL BATCH FOR TABLE: shopping_list_items
-- Drop table if exists (for re-runs)
DROP TABLE IF EXISTS shopping_list_items;

-- Create table (PostgreSQL syntax)
CREATE TABLE shopping_list_items (
    id SERIAL PRIMARY KEY,
    week_start TEXT NOT NULL,
    ingredient_name TEXT NOT NULL,
    quantity REAL,
    unit TEXT,
    category TEXT DEFAULT 'Other',
    already_have INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(week_start, ingredient_name)
);

-- No data to insert (no INSERTs found in SQLite dump)

-- Note: SERIAL in PostgreSQL auto-increments id. If you want to continue auto-incrementing from the highest id, run:
-- SELECT setval('shopping_list_items_id_seq', (SELECT MAX(id) FROM shopping_list_items));
