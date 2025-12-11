-- Migration: Add blockchain_tx_hash column to user_ratings table
-- Run this if the column doesn't exist in your existing database

ALTER TABLE user_ratings 
ADD COLUMN blockchain_tx_hash VARCHAR(255) NULL 
AFTER comment;

-- Verify the column was added
-- SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
-- FROM INFORMATION_SCHEMA.COLUMNS 
-- WHERE TABLE_NAME = 'user_ratings' AND COLUMN_NAME = 'blockchain_tx_hash';

