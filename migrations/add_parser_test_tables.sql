-- Add parser_issue_flag to recipe_upload
ALTER TABLE recipe_upload ADD COLUMN parser_issue_flag BOOLEAN DEFAULT FALSE;

-- Create parser_test_recipes table
CREATE TABLE IF NOT EXISTS parser_test_recipes (
    id SERIAL PRIMARY KEY,
    recipe_id INTEGER REFERENCES recipes(id),
    upload_source_type VARCHAR(50),
    upload_source_detail TEXT,
    uploaded_by VARCHAR(255),
    upload_date TIMESTAMP,
    notes TEXT
);
