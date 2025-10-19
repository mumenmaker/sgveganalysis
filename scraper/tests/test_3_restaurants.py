#!/usr/bin/env python3
"""
Test script to scrape exactly 3 restaurants and test database insertion
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

def test_3_restaurants():
    """Test scraping exactly 3 restaurants and inserting into database"""
    print("=== Test: Scrape 3 Restaurants Only ===\n")
    
    # Load environment variables
    load_dotenv()
    
    # Initialize scraper and database manager
    scraper = HappyCowScraper(enable_resume=False, use_selenium=True)
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
        
        # Get restaurant data using Selenium (but limit processing)
        logger.info("Getting restaurant data from HappyCow...")
        restaurant_data = scraper.scrape_with_selenium()
        
        if not restaurant_data:
            logger.error("No restaurant data found")
            return False
        
        logger.info(f"✅ Found {len(restaurant_data)} restaurants")
        
        # Take only the first 3 restaurants
        test_data = restaurant_data[:3]
        logger.info(f"Testing with first 3 restaurants:")
        for i, data in enumerate(test_data, 1):
            logger.info(f"  {i}. {data.get('name', 'Unknown')}")
        
        # Convert to Restaurant objects (but limit to 3)
        restaurants = []
        for i, data in enumerate(test_data):
            try:
                restaurant = scraper.parse_restaurant_data(data)
                if restaurant:
                    restaurants.append(restaurant)
                    logger.info(f"✅ Parsed restaurant {i+1}: {restaurant.name}")
                else:
                    logger.warning(f"❌ Failed to parse restaurant {i+1}")
            except Exception as e:
                logger.error(f"❌ Error parsing restaurant {i+1}: {e}")
        
        if not restaurants:
            logger.error("No restaurants could be parsed")
            return False
        
        logger.info(f"✅ Successfully parsed {len(restaurants)} restaurants")
        
        # Save to JSON (backup)
        logger.info("Saving to JSON file...")
        scraper.save_to_json(restaurants, 'logs/test_3_restaurants.json', append=False)
        logger.info("✅ JSON file saved")
        
        # Insert into database
        logger.info("Inserting restaurants into database...")
        success, inserted_count, skipped_count = db_manager.insert_restaurants(restaurants, skip_duplicates=False)
        
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

if __name__ == "__main__":
    print("Test: 3 Restaurants Only")
    print("=" * 50)
    
    # Run the test
    if test_3_restaurants():
        print("\n✅ Test completed successfully!")
        print("Check your Supabase dashboard to see the 3 restaurants in the database.")
    else:
        print("\n❌ Test failed")
        sys.exit(1)
