#!/usr/bin/env python3
"""
Quick test script to scrape only 3 restaurants and test database insertion
"""

import os
import sys
import logging
from dotenv import load_dotenv
from happycow_scraper import HappyCowScraper
from database import DatabaseManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_quick_scrape():
    """Test scraping just 3 restaurants and inserting into database"""
    print("=== Quick Scraper Test (3 restaurants) ===\n")
    
    # Load environment variables
    load_dotenv()
    
    # Initialize scraper and database manager
    scraper = HappyCowScraper(enable_resume=False, use_selenium=True)  # Disable resume for fresh test
    db_manager = DatabaseManager()
    
    try:
        # Test database connection
        logger.info("Testing database connection...")
        if not db_manager.supabase:
            logger.error("Failed to connect to Supabase")
            return False
        
        logger.info("✅ Database connection successful")
        
        # Create tables if they don't exist
        logger.info("Setting up database tables...")
        if not db_manager.create_tables():
            logger.error("Failed to create database tables")
            return False
        
        logger.info("✅ Database tables ready")
        
        # Scrape restaurants (this will get all 81, but we'll limit processing)
        logger.info("Starting to scrape restaurants from HappyCow...")
        restaurants = scraper.scrape_singapore_restaurants(resume=False)
        
        if not restaurants:
            logger.error("No restaurants found")
            return False
        
        logger.info(f"✅ Found {len(restaurants)} restaurants")
        
        # Take only the first 3 restaurants for testing
        test_restaurants = restaurants[:3]
        logger.info(f"Testing with first 3 restaurants:")
        for i, restaurant in enumerate(test_restaurants, 1):
            logger.info(f"  {i}. {restaurant.name}")
        
        # Save to JSON (backup)
        logger.info("Saving to JSON file...")
        scraper.save_to_json(test_restaurants, 'logs/test_restaurants.json', append=False)
        logger.info("✅ JSON file saved")
        
        # Insert into database
        logger.info("Inserting restaurants into database...")
        success, inserted_count, skipped_count = db_manager.insert_restaurants(test_restaurants, skip_duplicates=False)
        
        if success:
            logger.info(f"✅ Database insertion successful!")
            logger.info(f"   Inserted: {inserted_count} restaurants")
            logger.info(f"   Skipped: {skipped_count} duplicates")
            
            # Verify the data was inserted
            logger.info("Verifying data in database...")
            try:
                result = db_manager.supabase.table('restaurants').select('*').limit(5).execute()
                logger.info(f"✅ Found {len(result.data)} restaurants in database")
                
                if result.data:
                    logger.info("Sample restaurants in database:")
                    for i, restaurant in enumerate(result.data[:3]):
                        logger.info(f"  {i+1}. {restaurant.get('name', 'Unknown')} - Rating: {restaurant.get('rating', 'N/A')}")
                
            except Exception as e:
                logger.error(f"Error verifying data: {e}")
            
            return True
        else:
            logger.error("❌ Database insertion failed")
            return False
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
        return False

def check_database_status():
    """Check current status of database"""
    print("\n=== Database Status Check ===")
    
    try:
        load_dotenv()
        db_manager = DatabaseManager()
        
        if not db_manager.supabase:
            print("❌ No database connection")
            return
        
        # Check restaurants table
        result = db_manager.supabase.table('restaurants').select('*').execute()
        print(f"✅ Found {len(result.data)} restaurants in database")
        
        if result.data:
            print("\nSample restaurants:")
            for i, restaurant in enumerate(result.data[:5]):
                print(f"  {i+1}. {restaurant.get('name', 'Unknown')}")
                print(f"     Rating: {restaurant.get('rating', 'N/A')}")
                print(f"     Is Vegan: {restaurant.get('is_vegan', 'N/A')}")
                print(f"     Address: {restaurant.get('address', 'N/A')[:50]}...")
                print()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    print("Quick Scraper Test")
    print("=" * 50)
    
    # Run the quick test
    if test_quick_scrape():
        print("\n✅ Quick test completed successfully!")
        
        # Check database status
        check_database_status()
        
    else:
        print("\n❌ Quick test failed")
        sys.exit(1)
