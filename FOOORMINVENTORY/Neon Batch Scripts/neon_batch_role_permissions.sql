-- NEON/POSTGRESQL BATCH FOR TABLE: role_permissions
-- Drop table if exists (for re-runs)
DROP TABLE IF EXISTS role_permissions;

-- Create table (PostgreSQL syntax)
CREATE TABLE role_permissions (
    id SERIAL PRIMARY KEY,
    role TEXT NOT NULL,
    route TEXT NOT NULL,
    UNIQUE(role, route)
);

-- Insert data
INSERT INTO role_permissions (id, role, route) VALUES
    (1, 'VP', 'recipes'),
    (2, 'VP', 'recbk'),
    (3, 'VP', 'class_ingredients'),
    (4, 'VP', 'booking'),
    (5, 'VP', 'shoplist'),
    (6, 'VP', 'admin'),
    (7, 'DK', 'recipes'),
    (8, 'DK', 'recbk'),
    (9, 'DK', 'class_ingredients'),
    (10, 'DK', 'booking'),
    (11, 'DK', 'shoplist'),
    (12, 'MU', 'recipes'),
    (13, 'MU', 'recbk'),
    (14, 'MU', 'booking'),
    (15, 'MU', 'shoplist'),
    (16, 'public', 'recbk'),
    (17, 'DK', 'admin'),
    (18, 'public', 'recipes'),
    (19, 'public', 'class_ingredients'),
    (20, 'MU', 'class_ingredients'),
    (21, 'public', 'booking'),
    (22, 'public', 'shoplist'),
    (23, 'public', 'admin'),
    (24, 'MU', 'admin');

-- Note: SERIAL in PostgreSQL auto-increments id. If you want to continue auto-incrementing from the highest id, run:
-- SELECT setval('role_permissions_id_seq', (SELECT MAX(id) FROM role_permissions));
