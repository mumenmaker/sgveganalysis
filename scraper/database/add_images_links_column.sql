-- =====================================================
-- Add images_links column to existing restaurants table
-- =====================================================
-- Run this script in Supabase SQL Editor to add the images_links column
-- to your existing restaurants table

-- Add the images_links column
ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS images_links TEXT[];

-- Add a comment to document the column
COMMENT ON COLUMN restaurants.images_links IS 'Array of restaurant image URLs from HappyCow review pages';

-- Verify the column was added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'restaurants' 
AND column_name = 'images_links';
