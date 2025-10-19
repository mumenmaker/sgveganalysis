#!/usr/bin/env python3
"""
Test script to debug coordinate extraction in the paginated scraper
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from happycow_scraper import HappyCowScraper
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_coordinate_extraction():
    """Test coordinate extraction in paginated scraper"""
    try:
        logger.info("🔍 Testing coordinate extraction in paginated scraper...")
        
        # Initialize scraper with Selenium
        scraper = HappyCowScraper(use_selenium=True, enable_resume=False)
        
        # Setup Selenium
        driver = scraper.setup_selenium()
        if not driver:
            logger.error("Failed to setup Selenium")
            return False
        
        # Load the first page
        from config import Config
        params = Config.SINGAPORE_PARAMS.copy()
        url = f"{Config.SEARCH_URL}?" + "&".join([f"{k}={v}" for k, v in params.items()])
        
        logger.info(f"Loading page: {url}")
        driver.get(url)
        
        # Wait for page to load
        import time
        time.sleep(10)
        
        # Find restaurant elements
        from selenium.webdriver.common.by import By
        restaurant_elements = driver.find_elements(By.CSS_SELECTOR, '.venue-item')
        logger.info(f"Found {len(restaurant_elements)} restaurant elements")
        
        if not restaurant_elements:
            logger.error("No restaurant elements found")
            return False
        
        # Test coordinate extraction on first 3 restaurants
        for i in range(min(3, len(restaurant_elements))):
            element = restaurant_elements[i]
            logger.info(f"\n🔍 Testing restaurant {i+1}:")
            
            # Test the coordinate extraction method
            restaurant_data = scraper._extract_restaurant_data_from_element(element, i, driver)
            
            if restaurant_data:
                logger.info(f"  Name: {restaurant_data.get('name', 'N/A')}")
                logger.info(f"  Latitude: {restaurant_data.get('latitude', 'N/A')}")
                logger.info(f"  Longitude: {restaurant_data.get('longitude', 'N/A')}")
                
                # Check if coordinates were found
                if restaurant_data.get('latitude') and restaurant_data.get('longitude'):
                    logger.info(f"  ✅ Coordinates found: {restaurant_data['latitude']}, {restaurant_data['longitude']}")
                else:
                    logger.warning(f"  ❌ No coordinates found")
                    
                    # Debug: Check what attributes are available
                    logger.info(f"  🔍 Debugging element attributes:")
                    attrs = ['data-lat', 'data-lng', 'data-id', 'data-latitude', 'data-longitude']
                    for attr in attrs:
                        value = element.get_attribute(attr)
                        logger.info(f"    {attr}: {value}")
            else:
                logger.warning(f"  ❌ No restaurant data extracted")
        
        # Close Selenium
        scraper.close_selenium()
        
        return True
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Coordinate Extraction in Paginated Scraper")
    print("=" * 60)
    
    success = test_coordinate_extraction()
    
    if success:
        print("\n✅ Test completed successfully")
    else:
        print("\n❌ Test failed")
