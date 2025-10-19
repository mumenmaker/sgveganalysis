# -*- coding: utf-8 -*-
import logging
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_pagination_accumulation():
    """Test if pagination properly accumulates restaurants from multiple pages"""
    logger.info("Testing pagination accumulation...")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)

    try:
        all_restaurants = []
        max_pages = 3  # Test with 3 pages
        
        for page in range(1, max_pages + 1):
            logger.info(f"Processing page {page}/{max_pages}...")
            
            # Build URL with parameters for current page
            params = Config.SINGAPORE_PARAMS.copy()
            params['page'] = str(page)
            url = f"{Config.SEARCH_URL}?" + "&".join([f"{k}={v}" for k, v in params.items()])
            
            logger.info(f"Loading page {page}: {url}")
            driver.get(url)
            
            # Wait for page to load
            logger.info(f"Waiting for page {page} to load...")
            time.sleep(15)
            
            # Find restaurant elements on this page
            restaurant_elements = driver.find_elements(By.CSS_SELECTOR, '.venue-item')
            logger.info(f"Found {len(restaurant_elements)} restaurant elements on page {page}")
            
            if not restaurant_elements:
                logger.warning(f"No restaurant elements found on page {page}")
                break
            
            # Extract restaurant names from this page
            page_restaurants = []
            for i, element in enumerate(restaurant_elements):
                try:
                    # Just get the name for testing
                    name = element.text.strip().split('\n')[0] if element.text.strip() else f"Restaurant {i+1}"
                    page_restaurants.append(name)
                    if i < 3:  # Show first 3 for debugging
                        logger.info(f"  Restaurant {i+1}: {name}")
                except Exception as e:
                    logger.warning(f"Error extracting restaurant {i+1} from page {page}: {e}")
                    continue
            
            logger.info(f"Successfully extracted {len(page_restaurants)} restaurants from page {page}")
            all_restaurants.extend(page_restaurants)
            
            # If no restaurants were extracted from this page, we've likely reached the end
            if len(page_restaurants) == 0:
                logger.info(f"No restaurants extracted from page {page}, stopping pagination")
                break
            
            # Add delay between pages
            if page < max_pages:
                logger.info(f"Waiting before loading page {page + 1}...")
                time.sleep(2)
        
        logger.info(f"Total restaurants accumulated: {len(all_restaurants)}")
        
        # Check for duplicates
        unique_restaurants = list(set(all_restaurants))
        logger.info(f"Unique restaurants: {len(unique_restaurants)}")
        
        if len(unique_restaurants) < len(all_restaurants):
            logger.warning(f"Found {len(all_restaurants) - len(unique_restaurants)} duplicate restaurants")
        
        return len(all_restaurants), len(unique_restaurants)

    except Exception as e:
        logger.error("Error during pagination test: {}".format(e))
        return 0, 0
    finally:
        driver.quit()

if __name__ == "__main__":
    print("Testing Pagination Accumulation")
    print("=" * 50)
    total_count, unique_count = test_pagination_accumulation()
    print("\nResults:")
    print("  Total restaurants: {}".format(total_count))
    print("  Unique restaurants: {}".format(unique_count))
    
    if total_count > 81:
        print("\n✅ Pagination is working - getting restaurants from multiple pages!")
    else:
        print("\n❌ Pagination issue - only getting restaurants from first page!")
