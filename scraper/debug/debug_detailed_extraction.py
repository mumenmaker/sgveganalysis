#!/usr/bin/env python3
"""
Detailed debug script to analyze the exact extraction logic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from happycow_scraper import HappyCowScraper
import logging
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_detailed_extraction():
    """Debug the exact extraction logic step by step"""
    try:
        logger.info("🔍 Starting detailed extraction debug...")
        
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
        
        # Debug the first element with the exact same logic as the scraper
        logger.info("🔍 Debugging first element with exact scraper logic:")
        element = restaurant_elements[0]
        
        try:
            restaurant_data = {}
            
            # Get all text and split by lines (exact same logic)
            full_text = element.text.strip()
            lines = [line.strip() for line in full_text.split('\n') if line.strip()]
            
            logger.info(f"Full text: {full_text}")
            logger.info(f"Lines: {lines}")
            
            if lines:
                restaurant_data['name'] = lines[0]  # First line is usually the name
                logger.info(f"✅ Name extracted: {restaurant_data['name']}")
                
                # Try to extract rating and review count (exact same logic)
                for i, line in enumerate(lines):
                    logger.info(f"Processing line {i}: '{line}'")
                    
                    # Look for rating (usually a decimal number on its own line)
                    if re.match(r'^\d+\.?\d*$', line) and '.' in line:
                        logger.info(f"  → Rating pattern match: {line}")
                        try:
                            restaurant_data['rating'] = float(line)
                            logger.info(f"  → Rating extracted: {restaurant_data['rating']}")
                        except ValueError as e:
                            logger.warning(f"  → Rating conversion failed: {e}")
                    
                    # Look for review count in parentheses
                    if '(' in line and ')' in line:
                        logger.info(f"  → Review count pattern match: {line}")
                        try:
                            review_match = re.search(r'\((\d+)\)', line)
                            if review_match:
                                restaurant_data['review_count'] = int(review_match.group(1))
                                logger.info(f"  → Review count extracted: {restaurant_data['review_count']}")
                        except ValueError as e:
                            logger.warning(f"  → Review count conversion failed: {e}")
                
                # Try to extract restaurant type
                for line in lines:
                    if any(word in line.lower() for word in ['vegan', 'vegetarian', 'veg-friendly', 'restaurant', 'cafe']):
                        restaurant_data['type'] = line
                        logger.info(f"  → Type extracted: {restaurant_data['type']}")
                        break
                
                # Try to extract address
                for line in reversed(lines):
                    if any(word in line.lower() for word in ['mi', 'km', 'miles', 'singapore', 'road', 'street', 'avenue']):
                        restaurant_data['address'] = line
                        logger.info(f"  → Address extracted: {restaurant_data['address']}")
                        break
                
                # Try to extract URL
                try:
                    link_elem = element.find_element(By.CSS_SELECTOR, 'a')
                    if link_elem:
                        href = link_elem.get_attribute('href')
                        if href:
                            restaurant_data['url'] = href
                            logger.info(f"  → URL extracted: {restaurant_data['url']}")
                except Exception as e:
                    logger.warning(f"  → URL extraction failed: {e}")
                
                # Try to extract coordinates
                try:
                    lat = element.get_attribute('data-lat')
                    lng = element.get_attribute('data-lng')
                    if lat and lng:
                        restaurant_data['latitude'] = float(lat)
                        restaurant_data['longitude'] = float(lng)
                        logger.info(f"  → Coordinates extracted: {lat}, {lng}")
                    else:
                        logger.info(f"  → No coordinates on main element")
                except (ValueError, TypeError) as e:
                    logger.warning(f"  → Coordinate extraction failed: {e}")
                
                # Determine restaurant type
                restaurant_type = restaurant_data.get('type', '').lower()
                restaurant_data['is_vegan'] = 'vegan' in restaurant_type
                restaurant_data['is_vegetarian'] = 'vegetarian' in restaurant_type
                restaurant_data['has_veg_options'] = 'veg' in restaurant_type or 'friendly' in restaurant_type
                
                logger.info(f"Final restaurant data: {restaurant_data}")
                
                # Check if this would be added to restaurants list
                if restaurant_data.get('name'):
                    logger.info(f"✅ Restaurant would be added: {restaurant_data.get('name')}")
                else:
                    logger.warning(f"❌ Restaurant would NOT be added - no name")
            else:
                logger.warning("❌ No lines found in element")
                
        except Exception as e:
            logger.error(f"Error processing element: {e}")
        
        # Close Selenium
        scraper.close_selenium()
        
        return True
        
    except Exception as e:
        logger.error(f"Error during debug: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Debug Detailed Restaurant Extraction")
    print("=" * 50)
    
    success = debug_detailed_extraction()
    
    if success:
        print("\n✅ Debug completed successfully")
    else:
        print("\n❌ Debug failed")
