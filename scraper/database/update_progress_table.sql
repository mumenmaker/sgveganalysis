-- Update scraping_progress table for batch processing and progress tracking
-- Run this in the Supabase SQL Editor

-- Add new columns for batch processing
ALTER TABLE scraping_progress 
ADD COLUMN IF NOT EXISTS batch_size INTEGER DEFAULT 20,
ADD COLUMN IF NOT EXISTS current_batch INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_batches INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS processed_restaurants INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_batch_completed_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS error_message TEXT,
ADD COLUMN IF NOT EXISTS resume_from_batch INTEGER DEFAULT 0;

-- Update the existing columns to be more descriptive
ALTER TABLE scraping_progress 
ALTER COLUMN scraped_count SET DEFAULT 0,
ALTER COLUMN failed_count SET DEFAULT 0,
ALTER COLUMN is_completed SET DEFAULT FALSE;

-- Create index for batch processing
CREATE INDEX IF NOT EXISTS idx_scraping_progress_current_batch ON scraping_progress(current_batch);
CREATE INDEX IF NOT EXISTS idx_scraping_progress_resume_from_batch ON scraping_progress(resume_from_batch);

-- Add a function to get the latest progress for a session
CREATE OR REPLACE FUNCTION get_latest_progress(session_id_param TEXT)
RETURNS TABLE (
    session_id TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    last_updated TIMESTAMP WITH TIME ZONE,
    total_restaurants INTEGER,
    processed_restaurants INTEGER,
    current_batch INTEGER,
    total_batches INTEGER,
    batch_size INTEGER,
    is_completed BOOLEAN,
    resume_from_batch INTEGER,
    error_message TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        sp.session_id,
        sp.started_at,
        sp.last_updated,
        sp.total_restaurants,
        sp.processed_restaurants,
        sp.current_batch,
        sp.total_batches,
        sp.batch_size,
        sp.is_completed,
        sp.resume_from_batch,
        sp.error_message
    FROM scraping_progress sp
    WHERE sp.session_id = session_id_param
    ORDER BY sp.last_updated DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Add a function to update progress
CREATE OR REPLACE FUNCTION update_scraping_progress(
    session_id_param TEXT,
    processed_count INTEGER,
    current_batch_param INTEGER,
    is_completed_param BOOLEAN DEFAULT FALSE,
    error_msg TEXT DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    UPDATE scraping_progress 
    SET 
        processed_restaurants = processed_count,
        current_batch = current_batch_param,
        is_completed = is_completed_param,
        error_message = error_msg,
        last_updated = NOW(),
        last_batch_completed_at = CASE 
            WHEN is_completed_param THEN NOW() 
            ELSE last_batch_completed_at 
        END
    WHERE session_id = session_id_param;
    
    -- If no rows were updated, insert a new record
    IF NOT FOUND THEN
        INSERT INTO scraping_progress (
            session_id, 
            processed_restaurants, 
            current_batch, 
            is_completed, 
            error_message
        ) VALUES (
            session_id_param, 
            processed_count, 
            current_batch_param, 
            is_completed_param, 
            error_msg
        );
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Verify the updated table structure
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'scraping_progress' 
ORDER BY ordinal_position;
