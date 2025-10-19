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

def debug_dom_structure():
    """Debug the DOM structure to understand how coordinates are stored"""
    logger.info("🔍 Debugging DOM structure for coordinates...")

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

        # Get the page source after JavaScript execution
        page_source = driver.page_source
        
        # Look for coordinate patterns in the page source
        import re
        
        # Check for various coordinate patterns
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
        
        # Check for venue-item elements
        venue_items = driver.find_elements(By.CSS_SELECTOR, '.venue-item')
        logger.info(f"Found {len(venue_items)} venue-item elements")
        
        if venue_items:
            # Examine the first few elements in detail
            for i, element in enumerate(venue_items[:3]):
                logger.info(f"\n--- Venue Item {i+1} ---")
                logger.info(f"Text: {element.text.strip()[:100]}...")
                
                # Check all attributes
                attrs = driver.execute_script("""
                    var attrs = {};
                    for (var i = 0; i < arguments[0].attributes.length; i++) {
                        var attr = arguments[0].attributes[i];
                        attrs[attr.name] = attr.value;
                    }
                    return attrs;
                """, element)
                
                logger.info(f"All attributes: {attrs}")
                
                # Check for coordinate-related attributes
                coord_attrs = {k: v for k, v in attrs.items() if any(coord_word in k.lower() for coord_word in ['lat', 'lng', 'coord', 'location'])}
                if coord_attrs:
                    logger.info(f"Coordinate attributes: {coord_attrs}")
                else:
                    logger.info("No coordinate attributes found")
                
                # Check for data-id
                data_id = element.get_attribute('data-id')
                if data_id:
                    logger.info(f"Data ID: {data_id}")
                    
                    # Look for corresponding details element
                    try:
                        details_element = driver.find_element(By.CSS_SELECTOR, f'div.details.hidden[data-id="{data_id}"]')
                        if details_element:
                            details_attrs = driver.execute_script("""
                                var attrs = {};
                                for (var i = 0; i < arguments[0].attributes.length; i++) {
                                    var attr = arguments[0].attributes[i];
                                    attrs[attr.name] = attr.value;
                                }
                                return attrs;
                            """, details_element)
                            logger.info(f"Details element attributes: {details_attrs}")
                        else:
                            logger.info("No corresponding details element found")
                    except Exception as e:
                        logger.info(f"Error finding details element: {e}")
        
        # Look for any elements with coordinate data
        all_coord_elements = driver.find_elements(By.CSS_SELECTOR, '[data-lat], [data-lng], [data-latitude], [data-longitude]')
        logger.info(f"Found {len(all_coord_elements)} elements with coordinate attributes")
        
        for i, elem in enumerate(all_coord_elements[:5]):
            lat = elem.get_attribute('data-lat') or elem.get_attribute('data-latitude')
            lng = elem.get_attribute('data-lng') or elem.get_attribute('data-lng') or elem.get_attribute('data-longitude')
            tag_name = elem.tag_name
            class_name = elem.get_attribute('class')
            logger.info(f"Coord element {i+1}: {tag_name}.{class_name} - lat={lat}, lng={lng}")
        
        return True

    except Exception as e:
        logger.error(f"Error during DOM debugging: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🔍 Debugging DOM Structure for Coordinates")
    print("=" * 50)
    if debug_dom_structure():
        print("\n✅ Test completed successfully")
    else:
        print("\n❌ Test failed")
