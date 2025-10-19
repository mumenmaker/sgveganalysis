#!/usr/bin/env python3
"""
Test script to test the paginated scraper
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from happycow_scraper import HappyCowScraper
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_paginated_scraper():
    """Test the paginated scraper"""
    try:
        logger.info("🔍 Testing paginated scraper...")
        
        # Initialize scraper with Selenium
        scraper = HappyCowScraper(use_selenium=True, enable_resume=False)
        
        # Test paginated scraping (limit to 3 pages for testing)
        logger.info("Testing first 3 pages manually...")
        
        # Setup Selenium
        driver = scraper.setup_selenium()
        if not driver:
            logger.error("Failed to setup Selenium")
            return False
        
        total_restaurants = 0
        
        for page in range(1, 4):  # Test first 3 pages
            logger.info(f"Testing page {page}...")
            
            # Build URL for this page
            from config import Config
            params = Config.SINGAPORE_PARAMS.copy()
            params['page'] = str(page)
            url = f"{Config.SEARCH_URL}?" + "&".join([f"{k}={v}" for k, v in params.items()])
            
            logger.info(f"Loading page {page}: {url}")
            driver.get(url)
            
            # Wait for page to load
            import time
            time.sleep(10)
            
            # Find restaurant elements
            from selenium.webdriver.common.by import By
            restaurant_elements = driver.find_elements(By.CSS_SELECTOR, '.venue-item')
            logger.info(f"Found {len(restaurant_elements)} restaurant elements on page {page}")
            
            total_restaurants += len(restaurant_elements)
        
        # Close Selenium
        scraper.close_selenium()
        
        logger.info(f"Total restaurants found across 3 pages: {total_restaurants}")
        
        if total_restaurants > 81:
            logger.info(f"✅ SUCCESS! Found {total_restaurants} restaurants (more than the previous 81)")
        else:
            logger.warning(f"❌ Still only found {total_restaurants} restaurants")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Paginated Scraper")
    print("=" * 50)
    
    success = test_paginated_scraper()
    
    if success:
        print("\n✅ Test completed successfully")
    else:
        print("\n❌ Test failed")
