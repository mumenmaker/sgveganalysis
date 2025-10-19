import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from happycow_scraper import HappyCowScraper

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_coordinate_debug():
    """Test coordinate extraction with debug logging"""
    logger.info("🔍 Testing coordinate extraction with debug logging...")

    try:
        # Initialize scraper
        scraper = HappyCowScraper(use_selenium=True, enable_resume=False)
        
        # Test just the paginated scraping (which should extract coordinates)
        logger.info("Running paginated scraper...")
        restaurants = scraper.scrape_with_selenium_paginated()
        
        logger.info(f"Extracted {len(restaurants)} restaurants")
        
        if not restaurants:
            logger.warning("No restaurants extracted")
            return False
        
        # Test just the first few restaurants to see debug output
        logger.info("Testing first 3 restaurants...")
        for i, restaurant_data in enumerate(restaurants[:3]):
            logger.info(f"Restaurant {i+1}: {restaurant_data.get('name', 'Unknown')}")
            logger.info(f"  Original coordinates: lat={restaurant_data.get('latitude')}, lng={restaurant_data.get('longitude')}")
            
            # Test the coordinate preservation logic
            original_latitude = restaurant_data.get('latitude')
            original_longitude = restaurant_data.get('longitude')
            
            if original_latitude and original_longitude:
                logger.info(f"  ✅ Has coordinates: {original_latitude}, {original_longitude}")
            else:
                logger.warning(f"  ❌ No coordinates found")
        
        return True

    except Exception as e:
        logger.error(f"Error in coordinate debug test: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Coordinate Debug Test")
    print("=" * 50)
    if test_coordinate_debug():
        print("\n✅ Test completed successfully")
    else:
        print("\n❌ Test failed")
