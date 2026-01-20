-- Migration: Add class_size to classes table if not exists
ALTER TABLE classes ADD COLUMN class_size INTEGER DEFAULT 24;
