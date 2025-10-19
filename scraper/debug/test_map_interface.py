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
from selenium.webdriver.common.action_chains import ActionChains
from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_map_interface():
    """Test if the page requires interaction to load restaurant data"""
    logger.info("Testing map interface...")

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

        # Check initial state
        logger.info("--- Initial state ---")
        venue_items = driver.find_elements(By.CSS_SELECTOR, '.venue-item')
        logger.info("Initial venue-item count: {}".format(len(venue_items)))

        # Look for search button or trigger elements
        logger.info("--- Looking for search/trigger elements ---")
        search_buttons = driver.find_elements(By.CSS_SELECTOR, 'button, input[type="submit"], [class*="search"], [class*="submit"]')
        logger.info("Found {} potential search/trigger elements".format(len(search_buttons)))
        
        for i, btn in enumerate(search_buttons[:5]):
            logger.info("  Button {}: {} - '{}'".format(i+1, btn.tag_name, btn.text.strip()[:50]))

        # Try clicking on the map area
        logger.info("--- Trying to interact with map ---")
        map_elements = driver.find_elements(By.CSS_SELECTOR, '[class*="map"], [id*="map"], [class*="leaflet"]')
        if map_elements:
            logger.info("Found {} map elements, trying to click on first one".format(len(map_elements)))
            try:
                map_elem = map_elements[0]
                ActionChains(driver).move_to_element(map_elem).click().perform()
                time.sleep(3)
                
                # Check if restaurant elements appeared
                venue_items_after = driver.find_elements(By.CSS_SELECTOR, '.venue-item')
                logger.info("Venue-item count after map click: {}".format(len(venue_items_after)))
            except Exception as e:
                logger.warning("Error clicking map: {}".format(e))

        # Try scrolling to trigger loading
        logger.info("--- Trying to scroll to trigger loading ---")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        venue_items_after_scroll = driver.find_elements(By.CSS_SELECTOR, '.venue-item')
        logger.info("Venue-item count after scroll: {}".format(len(venue_items_after_scroll)))

        # Check for any elements that might contain restaurant data
        logger.info("--- Looking for any elements with restaurant-like content ---")
        all_divs = driver.find_elements(By.CSS_SELECTOR, 'div')
        restaurant_divs = []
        for div in all_divs:
            text = div.text.strip()
            if text and any(word in text.lower() for word in ['restaurant', 'cafe', 'food', 'vegetarian', 'vegan']):
                restaurant_divs.append(div)
        
        logger.info("Found {} divs with restaurant-like content".format(len(restaurant_divs)))
        for i, div in enumerate(restaurant_divs[:3]):
            logger.info("  Div {}: '{}'".format(i+1, div.text.strip()[:100]))

    except Exception as e:
        logger.error("Error during map interface test: {}".format(e))
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("Testing Map Interface")
    print("=" * 50)
    if test_map_interface():
        print("\nTest completed successfully")
    else:
        print("\nTest failed")