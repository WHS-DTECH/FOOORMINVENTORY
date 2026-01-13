-- NEON/POSTGRESQL BATCH FOR TABLE: user_roles
-- Drop table if exists (for re-runs)
DROP TABLE IF EXISTS user_roles;

-- Create table (PostgreSQL syntax)
CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    role TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(email, role)
);

-- Insert data
INSERT INTO user_roles (id, email, role, created_at) VALUES
    (1, 'janetwebster@westlandhigh.school.nz', 'DK', '2025-12-16 10:27:52'),
    (2, 'adriennereeves@westlandhigh.school.nz', 'DK', '2025-12-17 21:54:17'),
    (3, 'marykediplock@westlandhigh.school.nz', 'VP', '2025-12-19 02:00:52');

-- Note: SERIAL in PostgreSQL auto-increments id. If you want to continue auto-incrementing from the highest id, run:
-- SELECT setval('user_roles_id_seq', (SELECT MAX(id) FROM user_roles));
