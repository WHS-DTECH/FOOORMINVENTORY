-- Migration: Add new fields to parser_debug table
-- Adds source_url, title, serving_size (integer), ingredients, instructions

ALTER TABLE parser_debug
    ADD COLUMN source_url TEXT,
    ADD COLUMN title TEXT,
    ADD COLUMN serving_size INTEGER,
    ADD COLUMN ingredients TEXT,
    ADD COLUMN instructions TEXT;
