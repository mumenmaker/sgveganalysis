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
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_page_source_coordinates():
    """Test coordinate extraction from page source after JavaScript loads"""
    logger.info("🔍 Testing coordinate extraction from page source...")

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

        # Get the page source after JavaScript execution
        page_source = driver.page_source
        
        # Look for coordinate patterns in the page source
        coord_patterns = [
            (r'data-lat="([^"]+)"', 'data-lat attributes'),
            (r'data-lng="([^"]+)"', 'data-lng attributes'),
            (r'"lat":\s*([0-9.]+)', 'lat in JSON'),
            (r'"lng":\s*([0-9.]+)', 'lng in JSON'),
            (r'"latitude":\s*([0-9.]+)', 'latitude in JSON'),
            (r'"longitude":\s*([0-9.]+)', 'longitude in JSON'),
            (r'lat:\s*([0-9.]+)', 'lat in JS'),
            (r'lng:\s*([0-9.]+)', 'lng in JS')
        ]
        
        logger.info("🔍 Searching for coordinate patterns in page source...")
        for pattern, description in coord_patterns:
            matches = re.findall(pattern, page_source)
            if matches:
                logger.info(f"✅ Found {len(matches)} {description}: {matches[:5]}")
            else:
                logger.info(f"❌ No {description} found")
        
        # Look for data-id patterns
        data_id_pattern = r'data-id="([^"]+)"'
        data_ids = re.findall(data_id_pattern, page_source)
        logger.info(f"Found {len(data_ids)} data-id attributes: {data_ids[:5]}")
        
        # Try to find the relationship between data-id and coordinates
        if data_ids:
            # Test the first data-id
            test_id = data_ids[0]
            logger.info(f"Testing coordinate extraction for data-id: {test_id}")
            
            # Look for coordinates near this data-id
            pattern = rf'data-id="{test_id}"[^>]*data-lat="([^"]+)"[^>]*data-lng="([^"]+)"'
            match = re.search(pattern, page_source)
            if match:
                logger.info(f"✅ Found coordinates for data-id {test_id}: lat={match.group(1)}, lng={match.group(2)}")
            else:
                logger.info(f"❌ No coordinates found for data-id {test_id}")
                
                # Try alternative pattern
                pattern2 = rf'data-id="{test_id}"[^>]*?data-lat="([^"]+)"[^>]*?data-lng="([^"]+)"'
                match2 = re.search(pattern2, page_source, re.DOTALL)
                if match2:
                    logger.info(f"✅ Found coordinates (alt pattern) for data-id {test_id}: lat={match2.group(1)}, lng={match2.group(2)}")
                else:
                    logger.info(f"❌ No coordinates found with alternative pattern for data-id {test_id}")
        
        # Look for any elements with coordinates
        coord_elements = driver.find_elements(By.CSS_SELECTOR, '[data-lat], [data-lng]')
        logger.info(f"Found {len(coord_elements)} elements with coordinate attributes")
        
        for i, elem in enumerate(coord_elements[:5]):
            lat = elem.get_attribute('data-lat')
            lng = elem.get_attribute('data-lng')
            tag_name = elem.tag_name
            class_name = elem.get_attribute('class')
            data_id = elem.get_attribute('data-id')
            logger.info(f"Coord element {i+1}: {tag_name}.{class_name} (data-id={data_id}) - lat={lat}, lng={lng}")

        return True

    except Exception as e:
        logger.error(f"Error testing page source coordinates: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🔍 Testing Page Source Coordinate Extraction")
    print("=" * 50)
    if test_page_source_coordinates():
        print("\n✅ Test completed successfully")
    else:
        print("\n❌ Test failed")
