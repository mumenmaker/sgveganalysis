#!/usr/bin/env python3
"""
Test script to verify coordinates are being saved to database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from happycow_scraper import HappyCowScraper
from database import DatabaseManager
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_coordinates_database():
    """Test if coordinates are being saved to database"""
    try:
        logger.info("🔍 Testing coordinate extraction and database insertion...")
        
        # Initialize scraper with Selenium
        scraper = HappyCowScraper(use_selenium=True, enable_resume=False)
        
        # Run scraper
        logger.info("Running scraper with 1 page...")
        restaurants = scraper.scrape_singapore_restaurants()
        
        if not restaurants:
            logger.error("No restaurants scraped")
            return False
        
        logger.info(f"Scraped {len(restaurants)} restaurants")
        
        # Check if any restaurants have coordinates
        restaurants_with_coords = [r for r in restaurants if r.latitude and r.longitude]
        logger.info(f"Restaurants with coordinates: {len(restaurants_with_coords)}")
        
        if restaurants_with_coords:
            logger.info("✅ Coordinates are being extracted!")
            for i, r in enumerate(restaurants_with_coords[:3]):  # Show first 3
                logger.info(f"  {i+1}. {r.name}: {r.latitude}, {r.longitude}")
        else:
            logger.warning("❌ No coordinates found in scraped restaurants")
            return False
        
        # Test database insertion
        logger.info("Testing database insertion...")
        db_manager = DatabaseManager()
        
        # Insert first 3 restaurants with coordinates
        test_restaurants = restaurants_with_coords[:3]
        result = db_manager.insert_restaurants(test_restaurants, skip_duplicates=True)
        
        if result:
            logger.info("✅ Successfully inserted restaurants into database")
            
            # Check if coordinates are in database
            logger.info("Checking database for coordinates...")
            try:
                # Query the database to check coordinates
                response = db_manager.supabase.table('restaurants').select('name, latitude, longitude').limit(3).execute()
                
                if response.data:
                    logger.info("Database records with coordinates:")
                    for record in response.data:
                        logger.info(f"  {record['name']}: lat={record['latitude']}, lng={record['longitude']}")
                    
                    # Check if any have coordinates
                    has_coords = any(record.get('latitude') and record.get('longitude') for record in response.data)
                    if has_coords:
                        logger.info("✅ Coordinates are being saved to database!")
                        return True
                    else:
                        logger.warning("❌ No coordinates found in database records")
                        return False
                else:
                    logger.warning("❌ No records found in database")
                    return False
            except Exception as e:
                logger.error(f"Error querying database: {e}")
                return False
        else:
            logger.error("❌ Failed to insert restaurants into database")
            return False
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Coordinate Database Insertion")
    print("=" * 50)
    
    success = test_coordinates_database()
    
    if success:
        print("\n✅ Test completed successfully - coordinates are working!")
    else:
        print("\n❌ Test failed - coordinates issue found")
