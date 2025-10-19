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

def test_coordinate_extraction_only():
    """Test just the coordinate extraction without full scraping"""
    logger.info("🔍 Testing coordinate extraction only...")

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
        time.sleep(15)  # Wait for coordinates to load

        # Get restaurant elements
        restaurant_elements = driver.find_elements(By.CSS_SELECTOR, '.venue-item')
        logger.info(f"Found {len(restaurant_elements)} restaurant elements")

        if not restaurant_elements:
            logger.warning("No restaurant elements found")
            return False

        # Test coordinate extraction for first few elements
        for i, element in enumerate(restaurant_elements[:3]):
            logger.info(f"\n--- Testing element {i+1} ---")
            
            # Get basic info
            try:
                name_elem = element.find_element(By.CSS_SELECTOR, '.venue-name, .name, h3, h4, a')
                name = name_elem.text.strip()
                logger.info(f"Name: {name}")
            except:
                logger.info("Name: Could not extract")
            
            # Check for coordinates on the main element
            lat = element.get_attribute('data-lat')
            lng = element.get_attribute('data-lng')
            data_id = element.get_attribute('data-id')
            
            logger.info(f"Main element - data-id: {data_id}, data-lat: {lat}, data-lng: {lng}")
            
            if lat and lng:
                logger.info(f"✅ Found coordinates on main element: {lat}, {lng}")
            else:
                logger.info("❌ No coordinates on main element")
                
                # Try to find coordinates in page source using data-id
                if data_id:
                    try:
                        page_source = driver.page_source
                        import re
                        
                        # Look for the data-id in the page source and extract coordinates
                        pattern = rf'data-id="{data_id}"[^>]*data-lat="([^"]+)"[^>]*data-lng="([^"]+)"'
                        match = re.search(pattern, page_source)
                        if match:
                            logger.info(f"✅ Found coordinates in page source: {match.group(1)}, {match.group(2)}")
                        else:
                            logger.info("❌ No coordinates found in page source")
                    except Exception as e:
                        logger.info(f"❌ Error searching page source: {e}")

        return True

    except Exception as e:
        logger.error(f"Error testing coordinate extraction: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🔍 Testing Coordinate Extraction Only")
    print("=" * 50)
    if test_coordinate_extraction_only():
        print("\n✅ Test completed successfully")
    else:
        print("\n❌ Test failed")
