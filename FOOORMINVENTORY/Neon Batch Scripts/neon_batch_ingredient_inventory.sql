-- PostgreSQL compatible schema for Neon
-- Batch: ingredient_inventory

CREATE TABLE ingredient_inventory (
    id SERIAL PRIMARY KEY,
    ingredient_name TEXT NOT NULL UNIQUE,
    quantity REAL DEFAULT 0,
    unit TEXT,
    category TEXT DEFAULT 'Other',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- No data INSERTs found in SQLite dump for ingredient_inventory
