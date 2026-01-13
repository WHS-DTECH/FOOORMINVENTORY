-- PostgreSQL compatible schema for Neon
-- Batch: recipe_favorites

CREATE TABLE recipe_favorites (
    id SERIAL PRIMARY KEY,
    user_email TEXT NOT NULL,
    recipe_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_email, recipe_id)
    -- FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE -- Uncomment after recipes table is created
);

INSERT INTO recipe_favorites (id, user_email, recipe_id, created_at) VALUES
(1, 'marykediplock@westlandhigh.school.nz', 24, '2025-12-19 02:19:16');
