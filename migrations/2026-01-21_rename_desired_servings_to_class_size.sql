-- Migration: Rename desired_servings to class_size in class_bookings
ALTER TABLE class_bookings RENAME COLUMN desired_servings TO class_size;