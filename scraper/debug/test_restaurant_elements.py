# -*- coding: utf-8 -*-
import logging
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_restaurant_elements():
    """Test restaurant elements using the exact same approach as the main scraper"""
    logger.info("Testing restaurant elements with exact scraper approach...")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)

    try:
        # Build URL exactly like the main scraper
        params = Config.SINGAPORE_PARAMS.copy()
        params['page'] = str(1)  # Test with page 1
        url = f"{Config.SEARCH_URL}?" + "&".join([f"{k}={v}" for k, v in params.items()])
        
        logger.info(f"Loading page: {url}")
        driver.get(url)
        
        # Wait exactly like the main scraper
        logger.info("Waiting for page to load...")
        time.sleep(15)  # Same wait time as main scraper
        
        # Find restaurant elements using the same selector
        restaurant_elements = driver.find_elements(By.CSS_SELECTOR, '.venue-item')
        logger.info(f"Found {len(restaurant_elements)} restaurant elements")
        
        if restaurant_elements:
            logger.info("Successfully found restaurant elements!")
            
            # Examine the first few elements
            for i, element in enumerate(restaurant_elements[:3]):
                logger.info(f"\n--- Restaurant Element {i+1} ---")
                logger.info(f"Tag name: {element.tag_name}")
                logger.info(f"Classes: {element.get_attribute('class')}")
                logger.info(f"Text content: '{element.text.strip()}'")
                
                # Check for data attributes
                data_attrs = ['data-id', 'data-lat', 'data-lng', 'data-coords']
                for attr in data_attrs:
                    value = element.get_attribute(attr)
                    if value:
                        logger.info(f"  {attr}: {value}")
                
                # Check for child elements
                children = element.find_elements(By.XPATH, './*')
                logger.info(f"  Child elements: {len(children)}")
                for j, child in enumerate(children[:3]):
                    logger.info(f"    Child {j+1}: {child.tag_name} - '{child.text.strip()[:50]}'")
            
            return True
        else:
            logger.warning("No restaurant elements found")
            
            # Try alternative selectors
            logger.info("Trying alternative selectors...")
            alt_selectors = [
                '.venue-item',
                '.restaurant-item',
                '.search-result',
                '.result-item',
                '.item',
                '[class*="venue"]',
                '[class*="restaurant"]',
                '[class*="result"]',
                '[class*="item"]'
            ]
            
            for selector in alt_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    logger.info(f"  Selector '{selector}': {len(elements)} elements")
                    if elements and len(elements) > 0:
                        first_elem = elements[0]
                        logger.info(f"    First element: {first_elem.tag_name} - '{first_elem.text.strip()[:100]}'")
                except Exception as e:
                    logger.warning(f"  Selector '{selector}' failed: {e}")
            
            return False

    except Exception as e:
        logger.error(f"Error during restaurant elements test: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("Testing Restaurant Elements (Exact Scraper Approach)")
    print("=" * 60)
    if test_restaurant_elements():
        print("\nTest completed successfully - found restaurant elements!")
    else:
        print("\nTest failed - no restaurant elements found")