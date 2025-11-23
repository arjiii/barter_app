-- Update items status from 'pending' to 'available' so they show on discovery page
-- Run this in phpMyAdmin SQL tab

USE bayanihan_exchange;

UPDATE items 
SET status = 'available' 
WHERE status = 'pending';

-- Verify the update
SELECT id, title, status FROM items;










