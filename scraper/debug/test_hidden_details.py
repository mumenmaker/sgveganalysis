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

def test_hidden_details():
    """Test if restaurant coordinates are in hidden details elements after interaction."""
    logger.info("🔍 Testing hidden details elements...")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)

    try:
        url = f"{Config.SEARCH_URL}?" + "&".join([f"{k}={v}" for k, v in Config.SINGAPORE_PARAMS.items()])
        logger.info(f"Loading page: {url}")
        driver.get(url)

        # Wait for page to load
        time.sleep(15)

        # Look for search buttons to trigger restaurant loading
        search_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"], [class*="search"], [class*="filter"]')
        logger.info(f"Found {len(search_buttons)} search/filter buttons")

        # Try clicking on search-related elements to trigger loading
        for i, button in enumerate(search_buttons[:5]):  # Try first 5
            try:
                logger.info(f"Trying to click button {i+1}: {button.text.strip()}")
                button.click()
                time.sleep(5)  # Wait for potential loading
                
                # Check if restaurants appeared
                restaurant_elements = driver.find_elements(By.CSS_SELECTOR, '[class*="restaurant"], [class*="venue"], [class*="listing"]')
                if len(restaurant_elements) > 0:
                    logger.info(f"✅ Found {len(restaurant_elements)} restaurant elements after clicking button {i+1}!")
                    break
                    
            except Exception as e:
                logger.warning(f"Error clicking button {i+1}: {e}")

        # Now look for hidden details elements
        logger.info("\n--- Looking for hidden details elements ---")
        hidden_details = driver.find_elements(By.CSS_SELECTOR, 'div.details.hidden')
        logger.info(f"Found {len(hidden_details)} hidden details elements")

        if hidden_details:
            logger.info("✅ Found hidden details elements!")
            for i, detail in enumerate(hidden_details[:10]):  # Check first 10
                logger.info(f"\n--- Hidden Detail {i+1} ---")
                logger.info(f"Classes: {detail.get_attribute('class')}")
                logger.info(f"Text: '{detail.text.strip()[:100]}...'")
                
                # Check for data attributes
                data_id = detail.get_attribute('data-id')
                data_lat = detail.get_attribute('data-lat')
                data_lng = detail.get_attribute('data-lng')
                
                if data_id or data_lat or data_lng:
                    logger.info(f"✅ Data attributes - ID: {data_id}, Lat: {data_lat}, Lng: {data_lng}")
                else:
                    logger.info("❌ No data attributes found")

        # Also look for any elements with data-lat and data-lng
        logger.info("\n--- Looking for any elements with coordinates ---")
        coord_elements = driver.find_elements(By.CSS_SELECTOR, '[data-lat], [data-lng]')
        logger.info(f"Found {len(coord_elements)} elements with coordinate attributes")

        for i, elem in enumerate(coord_elements[:10]):  # Check first 10
            logger.info(f"\n--- Coordinate Element {i+1} ---")
            logger.info(f"Tag: {elem.tag_name}")
            logger.info(f"Classes: {elem.get_attribute('class')}")
            logger.info(f"Text: '{elem.text.strip()[:100]}...'")
            
            data_id = elem.get_attribute('data-id')
            data_lat = elem.get_attribute('data-lat')
            data_lng = elem.get_attribute('data-lng')
            
            if data_lat and data_lng:
                logger.info(f"✅ Coordinates found: Lat={data_lat}, Lng={data_lng}")
            else:
                logger.info("❌ No coordinates found")

        # Try to trigger more restaurant loading by interacting with the page
        logger.info("\n--- Trying to trigger more restaurant loading ---")
        try:
            # Look for restaurant cards or listings
            restaurant_cards = driver.find_elements(By.CSS_SELECTOR, '[class*="card"], [class*="listing"], [class*="item"], [class*="result"]')
            logger.info(f"Found {len(restaurant_cards)} potential restaurant cards")
            
            # Try hovering over restaurant cards to trigger loading
            for i, card in enumerate(restaurant_cards[:5]):  # Try first 5
                try:
                    logger.info(f"Hovering over card {i+1}")
                    ActionChains(driver).move_to_element(card).perform()
                    time.sleep(2)  # Wait for potential loading
                    
                    # Check if more hidden details appeared
                    new_hidden_details = driver.find_elements(By.CSS_SELECTOR, 'div.details.hidden')
                    if len(new_hidden_details) > len(hidden_details):
                        logger.info(f"✅ More hidden details appeared after hovering: {len(new_hidden_details)}")
                        hidden_details = new_hidden_details
                        break
                        
                except Exception as e:
                    logger.warning(f"Error hovering over card {i+1}: {e}")

        except Exception as e:
            logger.warning(f"Error trying to trigger more loading: {e}")

        # Final check for coordinates
        logger.info("\n--- Final coordinate check ---")
        all_coord_elements = driver.find_elements(By.CSS_SELECTOR, '[data-lat], [data-lng]')
        logger.info(f"Total elements with coordinates: {len(all_coord_elements)}")
        
        coord_count = 0
        for elem in all_coord_elements:
            lat = elem.get_attribute('data-lat')
            lng = elem.get_attribute('data-lng')
            if lat and lng:
                coord_count += 1
                logger.info(f"  Coordinate {coord_count}: Lat={lat}, Lng={lng}")
        
        if coord_count > 0:
            logger.info(f"✅ Successfully found {coord_count} coordinate pairs!")
            return True
        else:
            logger.warning("❌ No coordinates found")
            return False

    except Exception as e:
        logger.error(f"Error during hidden details test: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🔍 Testing Hidden Details Elements")
    print("=" * 50)
    if test_hidden_details():
        print("\n✅ Test completed successfully")
    else:
        print("\n❌ Test failed")
