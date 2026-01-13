-- NEON/POSTGRESQL BATCH FOR TABLE: saved_shopping_lists
-- Drop table if exists (for re-runs)
DROP TABLE IF EXISTS saved_shopping_lists;

-- Create table (PostgreSQL syntax)
CREATE TABLE saved_shopping_lists (
    id SERIAL PRIMARY KEY,
    list_name TEXT NOT NULL,
    week_label TEXT,
    items TEXT NOT NULL,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert data
INSERT INTO saved_shopping_lists (id, list_name, week_label, items, created_by, created_at) VALUES
    (1, 'Shopping List 17/12/2025', 'Week of 15/12/25 to 19/12/25', '[{"name": "margarine", "quantity": 3600, "unit": "g", "category": "Other"}, {"name": "carrots", "quantity": 6000, "unit": "g", "category": "Produce"}, {"name": "sugar", "quantity": 4800, "unit": "g", "category": "Pantry"}, {"name": "eggs", "quantity": 48, "unit": "pcs", "category": "Other"}, {"name": "flour", "quantity": 7920, "unit": "g", "category": "Pantry"}, {"name": "cinnamon", "quantity": 120, "unit": "ml", "category": "Pantry"}, {"name": "baking powder", "quantity": 120, "unit": "g", "category": "Pantry"}, {"name": "sultanas", "quantity": 4200, "unit": "g", "category": "Other"}, {"name": "nuts", "quantity": 1200, "unit": "g", "category": "Pantry"}, {"name": "butter", "quantity": 2640, "unit": "g", "category": "Dairy"}, {"name": "oats", "quantity": 960, "unit": "g", "category": "Pantry"}, {"name": "brown", "quantity": 720, "unit": "g", "category": "Other"}, {"name": "apples", "quantity": 48, "unit": "pcs", "category": "Produce"}, {"name": "of cauliflower", "quantity": 24, "unit": "", "category": "Produce"}, {"name": "milk", "quantity": 12000, "unit": "ml", "category": "Dairy"}, {"name": "cheese", "quantity": 2400, "unit": "g", "category": "Dairy"}]', 'vanessapringle@westlandhigh.school.nz', '2025-12-16 22:05:37');

-- Note: SERIAL in PostgreSQL auto-increments id. If you want to continue auto-incrementing from the highest id, run:
-- SELECT setval('saved_shopping_lists_id_seq', (SELECT MAX(id) FROM saved_shopping_lists));
