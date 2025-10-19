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

def test_element_visibility():
    """Test if restaurant elements are visible and have content."""
    logger.info("🔍 Testing element visibility and content...")

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

        # Wait for elements to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.venue-item'))
        )
        time.sleep(10)  # Give extra time for content to load

        restaurant_elements = driver.find_elements(By.CSS_SELECTOR, '.venue-item')
        logger.info(f"Found {len(restaurant_elements)} restaurant elements")

        if not restaurant_elements:
            logger.warning("No restaurant elements found.")
            return False

        # Test first few elements for visibility and content
        for i, element in enumerate(restaurant_elements[:5]):
            logger.info(f"\n--- Testing element {i+1} ---")
            
            # Check if element is visible
            is_displayed = element.is_displayed()
            logger.info(f"  Is displayed: {is_displayed}")
            
            # Check if element is enabled
            is_enabled = element.is_enabled()
            logger.info(f"  Is enabled: {is_enabled}")
            
            # Get element text
            text_content = element.text.strip()
            logger.info(f"  Text content: '{text_content}'")
            
            # Get inner HTML
            inner_html = element.get_attribute('innerHTML')
            logger.info(f"  Inner HTML length: {len(inner_html) if inner_html else 0}")
            
            # Get outer HTML
            outer_html = element.get_attribute('outerHTML')
            logger.info(f"  Outer HTML length: {len(outer_html) if outer_html else 0}")
            
            # Check for specific child elements
            try:
                child_elements = element.find_elements(By.CSS_SELECTOR, '*')
                logger.info(f"  Child elements found: {len(child_elements)}")
                
                # Look for common restaurant info elements
                name_elements = element.find_elements(By.CSS_SELECTOR, 'h3, h4, .name, .title, .restaurant-name')
                logger.info(f"  Name elements: {len(name_elements)}")
                
                rating_elements = element.find_elements(By.CSS_SELECTOR, '.rating, .score, .stars')
                logger.info(f"  Rating elements: {len(rating_elements)}")
                
                address_elements = element.find_elements(By.CSS_SELECTOR, '.address, .location, .addr')
                logger.info(f"  Address elements: {len(address_elements)}")
                
            except Exception as e:
                logger.warning(f"  Error checking child elements: {e}")
            
            # Check element attributes
            all_attrs = driver.execute_script(
                "var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;",
                element
            )
            logger.info(f"  All attributes: {all_attrs}")
            
            # Check for data attributes
            data_id = element.get_attribute('data-id')
            data_lat = element.get_attribute('data-lat')
            data_lng = element.get_attribute('data-lng')
            logger.info(f"  Data attributes - ID: {data_id}, Lat: {data_lat}, Lng: {data_lng}")

        return True

    except Exception as e:
        logger.error(f"Error during visibility test: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🔍 Testing Element Visibility and Content")
    print("=" * 50)
    if test_element_visibility():
        print("\n✅ Test completed successfully")
    else:
        print("\n❌ Test failed")
