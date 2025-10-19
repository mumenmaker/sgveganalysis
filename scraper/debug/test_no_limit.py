#!/usr/bin/env python3
"""
Test script to see how many restaurants we get without the limit parameter
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from happycow_scraper import HappyCowScraper
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_no_limit():
    """Test scraping without limit parameter"""
    try:
        logger.info("🔍 Testing scraper without limit parameter...")
        
        # Initialize scraper with Selenium
        scraper = HappyCowScraper(use_selenium=True, enable_resume=False)
        
        # Setup Selenium
        driver = scraper.setup_selenium()
        if not driver:
            logger.error("Failed to setup Selenium")
            return False
        
        # Load the page
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
        
        if len(restaurant_elements) > 100:
            logger.info(f"✅ SUCCESS! Found {len(restaurant_elements)} restaurants (much more than the previous 81)")
        elif len(restaurant_elements) > 81:
            logger.info(f"✅ IMPROVEMENT! Found {len(restaurant_elements)} restaurants (more than the previous 81)")
        else:
            logger.warning(f"❌ Still only found {len(restaurant_elements)} restaurants")
        
        # Close Selenium
        scraper.close_selenium()
        
        return True
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing No Limit Parameter")
    print("=" * 50)
    
    success = test_no_limit()
    
    if success:
        print("\n✅ Test completed successfully")
    else:
        print("\n❌ Test failed")
