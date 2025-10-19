#!/usr/bin/env python3
"""
Debug script to see what's happening with Selenium extraction
"""

import os
import sys
import logging
from dotenv import load_dotenv
from happycow_scraper import HappyCowScraper

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_selenium_extraction():
    """Debug the Selenium extraction process"""
    print("=== Debug Selenium Extraction ===\n")
    
    # Load environment variables
    load_dotenv()
    
    # Initialize scraper
    scraper = HappyCowScraper(enable_resume=False, use_selenium=True)
    
    try:
        # Setup Selenium
        logger.info("Setting up Selenium WebDriver...")
        driver = scraper.setup_selenium()
        if not driver:
            logger.error("Failed to setup Selenium")
            return False
        
        # Build URL
        from config import Config
        url = f"{Config.SEARCH_URL}?s={Config.SINGAPORE_PARAMS['s']}&location={Config.SINGAPORE_PARAMS['location']}&lat={Config.SINGAPORE_PARAMS['lat']}&lng={Config.SINGAPORE_PARAMS['lng']}&page={Config.SINGAPORE_PARAMS['page']}&zoom={Config.SINGAPORE_PARAMS['zoom']}&metric={Config.SINGAPORE_PARAMS['metric']}&limit={Config.SINGAPORE_PARAMS['limit']}&order={Config.SINGAPORE_PARAMS['order']}"
        
        logger.info(f"Loading page: {url}")
        driver.get(url)
        
        # Wait for page to load
        logger.info("Waiting for page to load...")
        import time
        time.sleep(10)
        
        # Find restaurant elements
        from selenium.webdriver.common.by import By
        restaurant_elements = driver.find_elements(By.CSS_SELECTOR, '.venue-item')
        logger.info(f"Found {len(restaurant_elements)} restaurant elements")
        
        if not restaurant_elements:
            logger.error("No restaurant elements found")
            return False
        
        # Debug the first 3 elements
        logger.info("Debugging first 3 restaurant elements:")
        for i, element in enumerate(restaurant_elements[:3]):
            try:
                logger.info(f"\n--- Restaurant Element {i+1} ---")
                
                # Get all text
                full_text = element.text.strip()
                logger.info(f"Full text: {full_text[:200]}...")
                
                # Split by lines
                lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                logger.info(f"Lines ({len(lines)}): {lines}")
                
                # Try to extract data
                restaurant_data = {}
                if lines:
                    restaurant_data['name'] = lines[0]
                    logger.info(f"Name: {restaurant_data['name']}")
                    
                    # Look for rating
                    for line in lines:
                        if '(' in line and ')' in line and any(char.isdigit() for char in line):
                            logger.info(f"Potential rating line: {line}")
                            try:
                                import re
                                rating_match = re.search(r'(\d+\.?\d*)', line)
                                if rating_match:
                                    restaurant_data['rating'] = float(rating_match.group(1))
                                    logger.info(f"Rating: {restaurant_data['rating']}")
                                review_match = re.search(r'\((\d+)\)', line)
                                if review_match:
                                    restaurant_data['review_count'] = int(review_match.group(1))
                                    logger.info(f"Review count: {restaurant_data['review_count']}")
                            except ValueError as e:
                                logger.warning(f"Error parsing rating: {e}")
                    
                    # Look for type
                    for line in lines:
                        if any(word in line.lower() for word in ['vegan', 'vegetarian', 'veg-friendly', 'restaurant', 'cafe']):
                            restaurant_data['type'] = line
                            logger.info(f"Type: {restaurant_data['type']}")
                            break
                    
                    # Look for address
                    for line in reversed(lines):
                        if any(word in line.lower() for word in ['mi', 'km', 'miles', 'singapore', 'road', 'street', 'avenue']):
                            restaurant_data['address'] = line
                            logger.info(f"Address: {restaurant_data['address']}")
                            break
                    
                    logger.info(f"Final restaurant data: {restaurant_data}")
                
            except Exception as e:
                logger.error(f"Error processing element {i+1}: {e}")
        
        # Close Selenium
        scraper.close_selenium()
        
        return True
        
    except Exception as e:
        logger.error(f"Error during debug: {e}")
        return False

if __name__ == "__main__":
    print("Debug Selenium Extraction")
    print("=" * 50)
    
    if debug_selenium_extraction():
        print("\n✅ Debug completed successfully!")
    else:
        print("\n❌ Debug failed")
        sys.exit(1)
