-- Alternative RLS policy fix for Supabase Storage
-- Run these commands in your Supabase SQL Editor

-- 1. Create the original_image_urls column if it doesn't exist
ALTER TABLE restaurants 
ADD COLUMN IF NOT EXISTS original_image_urls TEXT[];

-- 2. Create the storage bucket manually (this should work without RLS issues)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'restaurant-images',
  'restaurant-images', 
  true,
  10485760, -- 10MB limit
  ARRAY['image/jpeg', 'image/png', 'image/webp']
) ON CONFLICT (id) DO NOTHING;

-- 3. Create policies for the bucket (if you have permissions)
-- Note: These might fail if you don't have owner permissions
-- In that case, you'll need to create the bucket manually in the dashboard

-- Policy for public read access
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'objects' AND policyname = 'Allow public read access to restaurant images') THEN
    DROP POLICY "Allow public read access to restaurant images" ON storage.objects;
  END IF;
  
  CREATE POLICY "Allow public read access to restaurant images" ON storage.objects
  FOR SELECT USING (bucket_id = 'restaurant-images');
EXCEPTION
  WHEN insufficient_privilege THEN
    RAISE NOTICE 'Cannot create RLS policy - insufficient privileges. Please create bucket manually in dashboard.';
END $$;

-- Policy for authenticated users to upload
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'objects' AND policyname = 'Allow authenticated users to upload restaurant images') THEN
    DROP POLICY "Allow authenticated users to upload restaurant images" ON storage.objects;
  END IF;
  
  CREATE POLICY "Allow authenticated users to upload restaurant images" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'restaurant-images' AND 
    auth.role() = 'authenticated'
  );
EXCEPTION
  WHEN insufficient_privilege THEN
    RAISE NOTICE 'Cannot create RLS policy - insufficient privileges. Please create bucket manually in dashboard.';
END $$;
