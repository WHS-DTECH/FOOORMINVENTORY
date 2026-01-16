-- Migration: Add upload tracking fields to recipes table
ALTER TABLE recipes ADD COLUMN upload_method TEXT;
ALTER TABLE recipes ADD COLUMN uploaded_by TEXT;
ALTER TABLE recipes ADD COLUMN upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;