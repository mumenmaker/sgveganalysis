#!/usr/bin/env python3
"""
Script to check database status and create tables if needed
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_database_status():
    """Check database status and create tables if needed"""
    print("=== Database Status Check ===\n")
    
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        print("❌ Missing Supabase credentials!")
        print("Please check your .env file for SUPABASE_URL and SUPABASE_KEY")
        return False
    
    print(f"✅ Supabase URL: {url}")
    print(f"✅ Supabase Key: {key[:20]}...")
    
    try:
        # Create Supabase client
        supabase: Client = create_client(url, key)
        print("✅ Successfully connected to Supabase")
        
        # Check if restaurants table exists
        print("\n=== Checking Tables ===")
        try:
            # Try to query the restaurants table
            result = supabase.table('restaurants').select('*').limit(1).execute()
            print("✅ restaurants table exists")
            print(f"✅ Table has {len(result.data)} records")
            
            if result.data:
                print("Sample record:")
                for key, value in result.data[0].items():
                    print(f"  {key}: {value}")
            
        except Exception as e:
            print(f"❌ restaurants table does not exist or is not accessible: {e}")
            
            # Create the table
            print("\n=== Creating Tables ===")
            create_tables(supabase)
        
        # Check for other tables
        try:
            result = supabase.table('scraping_progress').select('*').limit(1).execute()
            print("✅ scraping_progress table exists")
        except:
            print("❌ scraping_progress table does not exist")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False

def create_tables(supabase: Client):
    """Create necessary tables in Supabase"""
    try:
        print("Creating restaurants table...")
        
        # Create restaurants table using SQL
        create_restaurants_sql = """
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
        """
        
        # Execute the SQL
        result = supabase.rpc('exec_sql', {'sql': create_restaurants_sql}).execute()
        print("✅ restaurants table created successfully")
        
        # Create indexes
        print("Creating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_restaurants_name ON restaurants(name);",
            "CREATE INDEX IF NOT EXISTS idx_restaurants_rating ON restaurants(rating);",
            "CREATE INDEX IF NOT EXISTS idx_restaurants_is_vegan ON restaurants(is_vegan);",
            "CREATE INDEX IF NOT EXISTS idx_restaurants_is_vegetarian ON restaurants(is_vegetarian);",
            "CREATE INDEX IF NOT EXISTS idx_restaurants_scraped_at ON restaurants(scraped_at);"
        ]
        
        for index_sql in indexes:
            try:
                supabase.rpc('exec_sql', {'sql': index_sql}).execute()
                print(f"✅ Index created: {index_sql.split('idx_')[1].split(' ')[0]}")
            except Exception as e:
                print(f"⚠️  Index creation failed (may already exist): {e}")
        
        # Create scraping_progress table
        print("Creating scraping_progress table...")
        create_progress_sql = """
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
        """
        
        supabase.rpc('exec_sql', {'sql': create_progress_sql}).execute()
        print("✅ scraping_progress table created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        print("\nTrying alternative method...")
        
        # Try to create tables using direct SQL execution
        try:
            # This might work if the RPC function doesn't exist
            print("Attempting to create tables using direct SQL...")
            
            # For now, let's just test if we can insert a test record
            test_data = {
                'name': 'Test Restaurant',
                'address': 'Test Address',
                'rating': 4.5,
                'is_vegan': True
            }
            
            result = supabase.table('restaurants').insert(test_data).execute()
            print("✅ Test insert successful - table exists and is accessible")
            
            # Clean up test data
            supabase.table('restaurants').delete().eq('name', 'Test Restaurant').execute()
            print("✅ Test data cleaned up")
            
            return True
            
        except Exception as e2:
            print(f"❌ Alternative method also failed: {e2}")
            return False

def check_existing_data():
    """Check if there's existing data in the database"""
    print("\n=== Checking Existing Data ===")
    
    try:
        load_dotenv()
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            print("❌ Missing Supabase credentials")
            return
        
        supabase: Client = create_client(url, key)
        
        # Check restaurants table
        try:
            result = supabase.table('restaurants').select('*').limit(5).execute()
            print(f"✅ Found {len(result.data)} restaurants in database")
            
            if result.data:
                print("\nSample restaurants:")
                for i, restaurant in enumerate(result.data[:3]):
                    print(f"  {i+1}. {restaurant.get('name', 'Unknown')} - Rating: {restaurant.get('rating', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Error querying restaurants: {e}")
        
        # Check scraping progress
        try:
            result = supabase.table('scraping_progress').select('*').execute()
            print(f"✅ Found {len(result.data)} scraping sessions")
            
            if result.data:
                for session in result.data:
                    print(f"  Session: {session.get('session_id', 'Unknown')} - Scraped: {session.get('scraped_count', 0)}")
        
        except Exception as e:
            print(f"❌ Error querying scraping progress: {e}")
            
    except Exception as e:
        print(f"❌ Error checking existing data: {e}")

if __name__ == "__main__":
    print("Database Status Checker")
    print("=" * 50)
    
    # Check database status
    if check_database_status():
        print("\n✅ Database check completed successfully")
        
        # Check existing data
        check_existing_data()
        
    else:
        print("\n❌ Database check failed")
        sys.exit(1)
