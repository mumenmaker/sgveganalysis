-- SQL script to fix RLS policies for image downloading
-- Run these commands in your Supabase SQL Editor

-- 1. Create the original_image_urls column if it doesn't exist
ALTER TABLE restaurants 
ADD COLUMN IF NOT EXISTS original_image_urls TEXT[];

-- 2. Disable RLS temporarily for storage.objects (for bucket creation)
-- This allows the script to create the bucket and upload files
ALTER TABLE storage.objects DISABLE ROW LEVEL SECURITY;

-- 3. Create a policy to allow public access to restaurant images
-- This allows anyone to read the images (for public display)
CREATE POLICY "Allow public read access to restaurant images" ON storage.objects
FOR SELECT USING (bucket_id = 'restaurant-images');

-- 4. Create a policy to allow authenticated users to upload restaurant images
-- This allows the script to upload images
CREATE POLICY "Allow authenticated users to upload restaurant images" ON storage.objects
FOR INSERT WITH CHECK (
  bucket_id = 'restaurant-images' AND 
  auth.role() = 'authenticated'
);

-- 5. Create a policy to allow authenticated users to update restaurant images
-- This allows the script to update/delete images if needed
CREATE POLICY "Allow authenticated users to update restaurant images" ON storage.objects
FOR UPDATE USING (
  bucket_id = 'restaurant-images' AND 
  auth.role() = 'authenticated'
);

-- 6. Create a policy to allow authenticated users to delete restaurant images
-- This allows the script to clean up failed uploads
CREATE POLICY "Allow authenticated users to delete restaurant images" ON storage.objects
FOR DELETE USING (
  bucket_id = 'restaurant-images' AND 
  auth.role() = 'authenticated'
);

-- 7. Re-enable RLS for storage.objects
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- 8. Create the storage bucket manually (if not already created)
-- You can also do this in the Supabase dashboard under Storage
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'restaurant-images',
  'restaurant-images', 
  true,
  10485760, -- 10MB limit
  ARRAY['image/jpeg', 'image/png', 'image/webp']
) ON CONFLICT (id) DO NOTHING;
