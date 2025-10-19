#!/usr/bin/env python3
"""
Debug script to analyze why the scraper finds 81 elements but extracts 0 restaurants
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from happycow_scraper import HappyCowScraper
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_extraction():
    """Debug the extraction process to see why 0 restaurants are extracted"""
    try:
        logger.info("🔍 Starting extraction debug...")
        
        # Initialize scraper with Selenium
        scraper = HappyCowScraper(use_selenium=True, enable_resume=False)
        
        # Setup Selenium
        driver = scraper.setup_selenium()
        if not driver:
            logger.error("Failed to setup Selenium")
            return False
        
        # Load the page
        url = "https://www.happycow.net/searchmap?s=3&location=Central Singapore, Singapore&lat=1.34183&lng=103.861&page=1&zoom=11&metric=mi&limit=81&order=default"
        logger.info(f"Loading page: {url}")
        driver.get(url)
        
        # Wait for page to load
        import time
        time.sleep(5)
        
        # Find restaurant elements
        from selenium.webdriver.common.by import By
        restaurant_elements = driver.find_elements(By.CSS_SELECTOR, '.venue-item')
        logger.info(f"Found {len(restaurant_elements)} restaurant elements")
        
        if not restaurant_elements:
            logger.warning("No restaurant elements found")
            return False
        
        # Debug the first 3 elements
        logger.info("🔍 Debugging first 3 restaurant elements:")
        for i, element in enumerate(restaurant_elements[:3]):
            try:
                logger.info(f"\n--- Restaurant Element {i+1} ---")
                
                # Get all text
                full_text = element.text.strip()
                logger.info(f"Full text: {full_text}")
                
                # Split by lines
                lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                logger.info(f"Lines ({len(lines)}): {lines}")
                
                # Check if we can extract a name
                if lines:
                    name = lines[0]
                    logger.info(f"Potential name: {name}")
                    
                    # Check if this looks like a valid restaurant name
                    if len(name) > 2 and not name.isdigit():
                        logger.info(f"✅ Valid restaurant name: {name}")
                    else:
                        logger.warning(f"❌ Invalid restaurant name: {name}")
                else:
                    logger.warning("❌ No text lines found")
                
                # Check HTML structure
                html = element.get_attribute('outerHTML')
                logger.info(f"HTML (first 200 chars): {html[:200]}...")
                
                # Check for specific selectors
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, '.venue-name, .name, h3, h4, .title')
                    logger.info(f"Name element found: {name_elem.text.strip()}")
                except:
                    logger.warning("No name element found with common selectors")
                
            except Exception as e:
                logger.error(f"Error processing element {i+1}: {e}")
        
        # Close Selenium
        scraper.close_selenium()
        
        return True
        
    except Exception as e:
        logger.error(f"Error during debug: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Debug Restaurant Extraction")
    print("=" * 50)
    
    success = debug_extraction()
    
    if success:
        print("\n✅ Debug completed successfully")
    else:
        print("\n❌ Debug failed")
