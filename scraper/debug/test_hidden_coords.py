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

def test_hidden_coordinates():
    """Test if coordinates are available in hidden details elements without interaction."""
    logger.info("Testing hidden coordinates without interaction...")

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

        # Look for hidden details elements directly
        logger.info("--- Looking for hidden details elements ---")
        hidden_details = driver.find_elements(By.CSS_SELECTOR, 'div.details.hidden')
        logger.info("Found {} hidden details elements".format(len(hidden_details)))

        if hidden_details:
            logger.info("Found hidden details elements!")
            coord_count = 0
            for i, detail in enumerate(hidden_details):
                logger.info("\n--- Hidden Detail {} ---".format(i+1))
                logger.info("Classes: {}".format(detail.get_attribute('class')))
                
                # Check for data attributes
                data_id = detail.get_attribute('data-id')
                data_lat = detail.get_attribute('data-lat')
                data_lng = detail.get_attribute('data-lng')
                
                if data_lat and data_lng:
                    coord_count += 1
                    logger.info("Coordinates found: ID={}, Lat={}, Lng={}".format(data_id, data_lat, data_lng))
                else:
                    logger.info("No coordinates found")
            
            if coord_count > 0:
                logger.info("Successfully found {} coordinate pairs in hidden details!".format(coord_count))
                return True
            else:
                logger.warning("No coordinates found in hidden details")
        else:
            logger.warning("No hidden details elements found")

        # Also check for any elements with coordinates
        logger.info("\n--- Looking for any elements with coordinates ---")
        coord_elements = driver.find_elements(By.CSS_SELECTOR, '[data-lat], [data-lng]')
        logger.info("Found {} elements with coordinate attributes".format(len(coord_elements)))

        coord_count = 0
        for i, elem in enumerate(coord_elements):
            lat = elem.get_attribute('data-lat')
            lng = elem.get_attribute('data-lng')
            if lat and lng:
                coord_count += 1
                logger.info("  Coordinate {}: Lat={}, Lng={}".format(coord_count, lat, lng))

        if coord_count > 0:
            logger.info("Found {} coordinate pairs!".format(coord_count))
            return True
        else:
            logger.warning("No coordinates found anywhere")
            return False

    except Exception as e:
        logger.error("Error during hidden coordinates test: {}".format(e))
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("Testing Hidden Coordinates")
    print("=" * 50)
    if test_hidden_coordinates():
        print("\nTest completed successfully")
    else:
        print("\nTest failed")
