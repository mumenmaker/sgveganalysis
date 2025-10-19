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

def test_single_coordinate_extraction():
    """Test coordinate extraction from a single restaurant element"""
    logger.info("🔍 Testing single coordinate extraction...")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)

    try:
        # Use the base URL for Singapore search
        params = Config.SINGAPORE_PARAMS.copy()
        params['page'] = '1'
        url = f"{Config.SEARCH_URL}?" + "&".join([f"{k}={v}" for k, v in params.items()])

        logger.info(f"Loading page: {url}")
        driver.get(url)

        # Wait for the page to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.venue-item'))
        )
        time.sleep(5)  # Give extra time for all elements to render

        restaurant_elements = driver.find_elements(By.CSS_SELECTOR, '.venue-item')
        logger.info(f"Found {len(restaurant_elements)} restaurant elements")

        if not restaurant_elements:
            logger.warning("No restaurant elements found.")
            return False

        # Test the first element
        element = restaurant_elements[0]
        logger.info(f"Testing first element: {element.text.strip()[:50]}...")

        # Check all possible coordinate sources
        logger.info("🔍 Checking coordinate sources...")

        # 1. Check main element data attributes
        lat = element.get_attribute('data-lat')
        lng = element.get_attribute('data-lng')
        logger.info(f"Main element data-lat: {lat}")
        logger.info(f"Main element data-lng: {lng}")

        # 2. Check for data-id and look for details element
        main_id = element.get_attribute('data-id')
        logger.info(f"Main element data-id: {main_id}")

        if main_id:
            try:
                details_element = driver.find_element(By.CSS_SELECTOR, f'div.details.hidden[data-id="{main_id}"]')
                if details_element:
                    details_lat = details_element.get_attribute('data-lat')
                    details_lng = details_element.get_attribute('data-lng')
                    logger.info(f"Details element data-lat: {details_lat}")
                    logger.info(f"Details element data-lng: {details_lng}")
                else:
                    logger.info("No details element found")
            except Exception as e:
                logger.info(f"Error finding details element: {e}")

        # 3. Check other possible attributes
        for attr in ['data-latitude', 'data-longitude', 'data-coords', 'data-location']:
            value = element.get_attribute(attr)
            if value:
                logger.info(f"Attribute {attr}: {value}")

        # 4. Check if coordinates are in the page source
        page_source = driver.page_source
        if 'data-lat' in page_source:
            logger.info("✅ Found 'data-lat' in page source")
        else:
            logger.info("❌ No 'data-lat' found in page source")

        # 5. Look for any elements with coordinates
        coord_elements = driver.find_elements(By.CSS_SELECTOR, '[data-lat]')
        logger.info(f"Found {len(coord_elements)} elements with data-lat attribute")

        if coord_elements:
            for i, coord_elem in enumerate(coord_elements[:3]):  # Check first 3
                lat_val = coord_elem.get_attribute('data-lat')
                lng_val = coord_elem.get_attribute('data-lng')
                logger.info(f"Element {i+1} - data-lat: {lat_val}, data-lng: {lng_val}")

        return True

    except Exception as e:
        logger.error(f"Error during test: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🔍 Testing Single Coordinate Extraction")
    print("=" * 50)
    if test_single_coordinate_extraction():
        print("\n✅ Test completed successfully")
    else:
        print("\n❌ Test failed")
