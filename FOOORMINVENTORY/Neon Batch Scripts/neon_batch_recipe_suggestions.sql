-- NEON/POSTGRESQL BATCH FOR TABLE: recipe_suggestions
-- Drop table if exists (for re-runs)
DROP TABLE IF EXISTS recipe_suggestions;

-- Create table (PostgreSQL syntax)
CREATE TABLE recipe_suggestions (
    id SERIAL PRIMARY KEY,
    recipe_name TEXT NOT NULL,
    recipe_url TEXT,
    reason TEXT,
    suggested_by_name TEXT NOT NULL,
    suggested_by_email TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending'
);

-- Insert data
INSERT INTO recipe_suggestions (id, recipe_name, recipe_url, reason, suggested_by_name, suggested_by_email, created_at, status) VALUES
    (1, 'Spag Bol', NULL, 'Tertiary Student Staple', 'Vanessa Pringle', 'vanessapringle@westlandhigh.school.nz', '2025-12-17 02:24:47', 'pending'),
    (2, 'Chicken Noodle Soup', NULL, 'When you are sick', 'Vanessa Pringle', 'vanessapringle@westlandhigh.school.nz', '2025-12-17 02:33:39', 'pending'),
    (3, 'Milo', NULL, 'NZ Staple', 'Vanessa Pringle', 'vanessapringle@westlandhigh.school.nz', '2025-12-17 02:47:23', 'pending'),
    (4, 'Onion Dip', NULL, 'NZ Staple', 'Vanessa Pringle', 'vanessapringle@westlandhigh.school.nz', '2025-12-17 03:41:50', 'pending'),
    (5, 'kiwi fruit', NULL, 'Roxs', 'Vanessa Pringle', 'vanessapringle@westlandhigh.school.nz', '2025-12-17 03:49:34', 'pending'),
    (6, 'chocolate cake', NULL, 'Ve''s B''Day', 'Vanessa Pringle', 'vanessapringle@westlandhigh.school.nz', '2025-12-17 03:58:07', 'pending'),
    (7, 'cheese block`', NULL, 'Fav', 'Vanessa Pringle', 'vanessapringle@westlandhigh.school.nz', '2025-12-18 21:36:27', 'pending'),
    (8, 'Pavlova', 'https://www.chelsea.co.nz/recipes/browse-recipes/pavlova', 'T4 - 300Hospo', 'Maryke Diplock', 'marykediplock@westlandhigh.school.nz', '2025-12-19 02:17:47', 'pending');

-- Note: SERIAL in PostgreSQL auto-increments id. If you want to continue auto-incrementing from the highest id, run:
-- SELECT setval('recipe_suggestions_id_seq', (SELECT MAX(id) FROM recipe_suggestions));
