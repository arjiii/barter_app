-- Migration: Add location columns to users and items tables
-- Run this SQL script on your MySQL database to add the location feature

-- Add location column to users table (optional field)
ALTER TABLE users 
ADD COLUMN location VARCHAR(255) NULL 
AFTER role;

-- Add location column to items table (optional field)
ALTER TABLE items 
ADD COLUMN location VARCHAR(255) NULL 
AFTER images;
