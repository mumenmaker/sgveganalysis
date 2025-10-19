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

def find_hidden_coordinates():
    """Find coordinates in hidden elements"""
    logger.info("🔍 Finding coordinates in hidden elements...")

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
        time.sleep(10)  # Give extra time for all elements to render

        # Get restaurant elements
        restaurant_elements = driver.find_elements(By.CSS_SELECTOR, '.venue-item')
        logger.info(f"Found {len(restaurant_elements)} restaurant elements")

        if not restaurant_elements:
            logger.warning("No restaurant elements found")
            return False

        # Check the first few restaurants
        for i, element in enumerate(restaurant_elements[:3]):
            logger.info(f"\n--- Restaurant {i+1} ---")
            
            # Get the data-id
            data_id = element.get_attribute('data-id')
            logger.info(f"Data ID: {data_id}")
            
            # Look for hidden details element with same data-id
            try:
                details_element = driver.find_element(By.CSS_SELECTOR, f'div.details.hidden[data-id="{data_id}"]')
                if details_element:
                    lat = details_element.get_attribute('data-lat')
                    lng = details_element.get_attribute('data-lng')
                    logger.info(f"✅ Found coordinates in details element: lat={lat}, lng={lng}")
                else:
                    logger.info("❌ No details element found")
            except Exception as e:
                logger.info(f"❌ Error finding details element: {e}")
            
            # Try alternative selectors for hidden elements
            try:
                # Look for any element with the same data-id that has coordinates
                coord_element = driver.find_element(By.CSS_SELECTOR, f'[data-id="{data_id}"][data-lat]')
                if coord_element:
                    lat = coord_element.get_attribute('data-lat')
                    lng = coord_element.get_attribute('data-lng')
                    logger.info(f"✅ Found coordinates in element with data-id: lat={lat}, lng={lng}")
                else:
                    logger.info("❌ No element with data-id and coordinates found")
            except Exception as e:
                logger.info(f"❌ Error finding element with data-id: {e}")
            
            # Check if coordinates are in the element's parent or children
            try:
                # Check parent element
                parent = element.find_element(By.XPATH, '..')
                parent_lat = parent.get_attribute('data-lat')
                parent_lng = parent.get_attribute('data-lng')
                if parent_lat and parent_lng:
                    logger.info(f"✅ Found coordinates in parent: lat={parent_lat}, lng={parent_lng}")
                else:
                    logger.info("❌ No coordinates in parent element")
            except Exception as e:
                logger.info(f"❌ Error checking parent: {e}")
            
            # Check if coordinates are in JavaScript data
            try:
                # Look for JavaScript variables that might contain coordinates
                js_coords = driver.execute_script("""
                    // Look for common JavaScript patterns
                    var scripts = document.getElementsByTagName('script');
                    for (var i = 0; i < scripts.length; i++) {
                        var script = scripts[i];
                        if (script.textContent && script.textContent.includes('data-lat')) {
                            return script.textContent.substring(0, 500);
                        }
                    }
                    return null;
                """)
                
                if js_coords:
                    logger.info(f"✅ Found coordinates in JavaScript: {js_coords[:200]}...")
                else:
                    logger.info("❌ No coordinates found in JavaScript")
            except Exception as e:
                logger.info(f"❌ Error checking JavaScript: {e}")

        # Look for all elements with coordinates
        logger.info("\n🔍 Looking for all elements with coordinates...")
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
        logger.error(f"Error finding hidden coordinates: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🔍 Finding Hidden Coordinates")
    print("=" * 50)
    if find_hidden_coordinates():
        print("\n✅ Test completed successfully")
    else:
        print("\n❌ Test failed")
