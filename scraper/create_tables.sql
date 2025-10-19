-- Create tables for HappyCow Singapore Restaurant Scraper
-- Run this in the Supabase SQL Editor

-- Create restaurants table
CREATE TABLE IF NOT EXISTS restaurants (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    phone TEXT,
    website TEXT,
    description TEXT,
    cuisine_type TEXT,
    price_range TEXT,
    rating DECIMAL(3,2),
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

-- Create scraping_progress table
CREATE TABLE IF NOT EXISTS scraping_progress (
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

-- Enable Row Level Security (RLS) if needed
-- ALTER TABLE restaurants ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE scraping_progress ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (adjust as needed)
-- CREATE POLICY "Allow public read access" ON restaurants FOR SELECT USING (true);
-- CREATE POLICY "Allow public insert access" ON restaurants FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Allow public update access" ON restaurants FOR UPDATE USING (true);
-- CREATE POLICY "Allow public delete access" ON restaurants FOR DELETE USING (true);

-- CREATE POLICY "Allow public read access" ON scraping_progress FOR SELECT USING (true);
-- CREATE POLICY "Allow public insert access" ON scraping_progress FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Allow public update access" ON scraping_progress FOR UPDATE USING (true);
-- CREATE POLICY "Allow public delete access" ON scraping_progress FOR DELETE USING (true);

-- Verify tables were created
SELECT 'restaurants' as table_name, COUNT(*) as row_count FROM restaurants
UNION ALL
SELECT 'scraping_progress' as table_name, COUNT(*) as row_count FROM scraping_progress;
