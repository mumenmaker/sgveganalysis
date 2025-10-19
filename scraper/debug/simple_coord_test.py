import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from happycow_scraper import HappyCowScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def simple_coordinate_test():
    """Simple test to check if coordinates are being extracted"""
    logger.info("🔍 Testing simple coordinate extraction...")

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
        
        # Check if any restaurants have coordinates
        restaurants_with_coords = [r for r in restaurants if r.get('latitude') is not None and r.get('longitude') is not None]
        restaurants_without_coords = [r for r in restaurants if r.get('latitude') is None or r.get('longitude') is None]
        
        logger.info(f"Restaurants with coordinates: {len(restaurants_with_coords)}")
        logger.info(f"Restaurants without coordinates: {len(restaurants_without_coords)}")
        
        if restaurants_with_coords:
            logger.info("✅ Some restaurants have coordinates!")
            for i, restaurant in enumerate(restaurants_with_coords[:5]):  # Show first 5
                logger.info(f"  {i+1}. {restaurant.get('name', 'Unknown')}: lat={restaurant.get('latitude')}, lng={restaurant.get('longitude')}")
        else:
            logger.warning("❌ No restaurants have coordinates")
            
            # Show a few examples of restaurants without coordinates
            logger.info("Examples of restaurants without coordinates:")
            for i, restaurant in enumerate(restaurants_without_coords[:5]):
                logger.info(f"  {i+1}. {restaurant.get('name', 'Unknown')}: lat={restaurant.get('latitude')}, lng={restaurant.get('longitude')}")
        
        return len(restaurants_with_coords) > 0

    except Exception as e:
        logger.error(f"Error in simple coordinate test: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Simple Coordinate Test")
    print("=" * 50)
    if simple_coordinate_test():
        print("\n✅ Test completed successfully - coordinates found")
    else:
        print("\n❌ Test failed - no coordinates found")
