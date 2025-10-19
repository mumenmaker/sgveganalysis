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

def test_page_elements():
    """Test what elements are actually present on the page"""
    logger.info("Testing page elements...")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)

    try:
        url = "{}?".format(Config.SEARCH_URL) + "&".join(["{}={}".format(k, v) for k, v in Config.SINGAPORE_PARAMS.items()])
        logger.info("Loading page: {}".format(url))
        driver.get(url)

        # Wait for page to load
        time.sleep(15)

        # Test different selectors
        selectors_to_test = [
            '.venue-item',
            '.restaurant-item',
            '.search-result',
            '.result-item',
            '.item',
            '[class*="venue"]',
            '[class*="restaurant"]',
            '[class*="result"]',
            '[class*="item"]',
            'div[data-id]',
            'div[data-lat]',
            'div[data-lng]'
        ]
        
        logger.info("--- Testing different selectors ---")
        for selector in selectors_to_test:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                logger.info("Selector '{}': {} elements found".format(selector, len(elements)))
                if elements and len(elements) > 0:
                    # Show first element details
                    first_elem = elements[0]
                    logger.info("  First element: {} - '{}'".format(first_elem.tag_name, first_elem.text.strip()[:100]))
            except Exception as e:
                logger.warning("  Selector '{}' failed: {}".format(selector, e))

        # Look for any div elements with data attributes
        logger.info("\n--- Looking for div elements with data attributes ---")
        divs_with_data = driver.find_elements(By.XPATH, '//div[@data-id or @data-lat or @data-lng]')
        logger.info("Found {} div elements with data attributes".format(len(divs_with_data)))
        
        for i, div in enumerate(divs_with_data[:5]):
            logger.info("  Div {}: classes='{}', data-id='{}', data-lat='{}', data-lng='{}'".format(
                i+1, 
                div.get_attribute('class'),
                div.get_attribute('data-id'),
                div.get_attribute('data-lat'),
                div.get_attribute('data-lng')
            ))

        # Check if there's a map interface
        logger.info("\n--- Checking for map interface ---")
        map_elements = driver.find_elements(By.CSS_SELECTOR, '[class*="map"], [id*="map"], [class*="leaflet"]')
        logger.info("Found {} map-related elements".format(len(map_elements)))

    except Exception as e:
        logger.error("Error during page elements test: {}".format(e))
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("Testing Page Elements")
    print("=" * 50)
    if test_page_elements():
        print("\nTest completed successfully")
    else:
        print("\nTest failed")