-- Migration: Add raw_text column to recipe_upload for storing raw extracted text
ALTER TABLE recipe_upload ADD COLUMN raw_text TEXT;