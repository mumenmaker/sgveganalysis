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

def test_restaurant_structure():
    """Test the actual structure of restaurant elements"""
    logger.info("Testing restaurant element structure...")

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

        # Look for restaurant elements
        logger.info("--- Looking for restaurant elements ---")
        restaurant_elements = driver.find_elements(By.CSS_SELECTOR, '.venue-item')
        logger.info("Found {} restaurant elements".format(len(restaurant_elements)))

        if restaurant_elements:
            # Examine the first few elements
            for i, element in enumerate(restaurant_elements[:3]):
                logger.info("\n--- Restaurant Element {} ---".format(i+1))
                logger.info("Tag name: {}".format(element.tag_name))
                logger.info("Classes: {}".format(element.get_attribute('class')))
                logger.info("Text content: '{}'".format(element.text.strip()))
                logger.info("HTML: {}".format(element.get_attribute('outerHTML')[:200] + "..."))
                
                # Check for child elements
                children = element.find_elements(By.XPATH, './*')
                logger.info("Child elements: {}".format(len(children)))
                for j, child in enumerate(children[:3]):
                    logger.info("  Child {}: {} - '{}'".format(j+1, child.tag_name, child.text.strip()[:50]))
                
                # Check for data attributes
                data_attrs = ['data-id', 'data-lat', 'data-lng', 'data-coords']
                for attr in data_attrs:
                    value = element.get_attribute(attr)
                    if value:
                        logger.info("  {}: {}".format(attr, value))
        else:
            logger.warning("No restaurant elements found")

        # Also check for any elements with restaurant-like content
        logger.info("\n--- Looking for any elements with restaurant content ---")
        all_elements = driver.find_elements(By.XPATH, '//*[contains(text(), "restaurant") or contains(text(), "cafe") or contains(text(), "food")]')
        logger.info("Found {} elements with restaurant-like content".format(len(all_elements)))
        
        for i, elem in enumerate(all_elements[:3]):
            logger.info("  Element {}: {} - '{}'".format(i+1, elem.tag_name, elem.text.strip()[:100]))

    except Exception as e:
        logger.error("Error during restaurant structure test: {}".format(e))
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("Testing Restaurant Element Structure")
    print("=" * 50)
    if test_restaurant_structure():
        print("\nTest completed successfully")
    else:
        print("\nTest failed")