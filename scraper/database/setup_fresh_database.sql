-- =====================================================
-- Fresh Database Setup for HappyCow Singapore Scraper
-- =====================================================
-- Run this script in Supabase SQL Editor to create a fresh database
-- This will drop existing tables and recreate them with proper constraints

-- Drop existing tables if they exist (in correct order due to foreign keys)
DROP TABLE IF EXISTS scraping_progress CASCADE;
DROP TABLE IF EXISTS restaurants CASCADE;

-- Create restaurants table with coordinate-based unique constraint
CREATE TABLE restaurants (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    phone TEXT,
    website TEXT,
    cow_reviews TEXT,
    description TEXT,
    category TEXT,
    price_range TEXT,
    rating DECIMAL(4,2),
    review_count INTEGER,
    is_vegan BOOLEAN DEFAULT FALSE,
    is_vegetarian BOOLEAN DEFAULT FALSE,
    has_veg_options BOOLEAN DEFAULT FALSE,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    features TEXT[],
    hours TEXT,
    happycow_url TEXT,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_restaurants_name ON restaurants(name);
CREATE INDEX IF NOT EXISTS idx_restaurants_rating ON restaurants(rating);
CREATE INDEX IF NOT EXISTS idx_restaurants_is_vegan ON restaurants(is_vegan);
CREATE INDEX IF NOT EXISTS idx_restaurants_is_vegetarian ON restaurants(is_vegetarian);
CREATE INDEX IF NOT EXISTS idx_restaurants_has_veg_options ON restaurants(has_veg_options);
CREATE INDEX IF NOT EXISTS idx_restaurants_scraped_at ON restaurants(scraped_at);
CREATE INDEX IF NOT EXISTS idx_restaurants_latitude ON restaurants(latitude);
CREATE INDEX IF NOT EXISTS idx_restaurants_longitude ON restaurants(longitude);

-- Add unique constraint based on coordinates (prevents duplicate locations)
-- This is more reliable than name-based constraints
ALTER TABLE restaurants ADD CONSTRAINT unique_restaurant_location UNIQUE (latitude, longitude);

-- Create scraping_progress table
CREATE TABLE scraping_progress (
    id SERIAL PRIMARY KEY,
    session_id TEXT UNIQUE NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    total_restaurants INTEGER DEFAULT 0,
    scraped_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    is_completed BOOLEAN DEFAULT FALSE,
    scraped_restaurants TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for scraping_progress
CREATE INDEX IF NOT EXISTS idx_scraping_progress_session_id ON scraping_progress(session_id);
CREATE INDEX IF NOT EXISTS idx_scraping_progress_started_at ON scraping_progress(started_at);
CREATE INDEX IF NOT EXISTS idx_scraping_progress_is_completed ON scraping_progress(is_completed);

-- Optional: Enable Row Level Security (RLS) if needed
-- Uncomment the following lines if you want to enable RLS
-- ALTER TABLE restaurants ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE scraping_progress ENABLE ROW LEVEL SECURITY;

-- Optional: Create policies for public access
-- Uncomment the following lines if you want to allow public access
-- CREATE POLICY "Allow public read access" ON restaurants FOR SELECT USING (true);
-- CREATE POLICY "Allow public insert access" ON restaurants FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Allow public update access" ON restaurants FOR UPDATE USING (true);
-- CREATE POLICY "Allow public delete access" ON restaurants FOR DELETE USING (true);

-- CREATE POLICY "Allow public read access" ON scraping_progress FOR SELECT USING (true);
-- CREATE POLICY "Allow public insert access" ON scraping_progress FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Allow public update access" ON scraping_progress FOR UPDATE USING (true);
-- CREATE POLICY "Allow public delete access" ON scraping_progress FOR DELETE USING (true);

-- Verify tables were created successfully
SELECT 
    'restaurants' as table_name, 
    COUNT(*) as row_count 
FROM restaurants
UNION ALL
SELECT 
    'scraping_progress' as table_name, 
    COUNT(*) as row_count 
FROM scraping_progress;

-- Show table structure
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name IN ('restaurants', 'scraping_progress')
ORDER BY table_name, ordinal_position;

-- Show constraints
SELECT 
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
WHERE tc.table_name IN ('restaurants', 'scraping_progress')
ORDER BY tc.table_name, tc.constraint_type;
