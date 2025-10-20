"""
Debug script for HappyCow SearchMap
Investigates what data is available on the searchmap page
"""

import sys
import os
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Add the scraper directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sectorscraper import SingaporeSectorGrid, HappyCowURLGenerator, HappyCowPageLoader, HappyCowDataExtractor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_searchmap():
    """Debug the searchmap page to see what data is available"""
    logger.info("🔍 Debugging HappyCow SearchMap page...")
    
    # Generate test sector and URL
    grid = SingaporeSectorGrid()
    sectors = grid.generate_sectors()
    url_gen = HappyCowURLGenerator()
    
    # Use a sector that should have restaurants (central Singapore)
    test_sector = sectors[10]  # Sector 2_3 (central area)
    test_url = url_gen.generate_sector_url(test_sector)
    
    print(f"Testing with sector: {test_sector['name']}")
    print(f"Center coordinates: ({test_sector['lat_center']}, {test_sector['lng_center']})")
    print(f"URL: {test_url}")
    
    # Load the page
    loader = HappyCowPageLoader(headless=False)  # Run in non-headless mode for visual debugging
    
    try:
        if loader.load_sector_page(test_url):
            print("✅ Page loaded successfully")
            
            driver = loader.driver
            
            # Wait a bit for content to load
            time.sleep(5)
            
            print("\n🔍 Page Analysis:")
            print("=" * 50)
            
            # 1. Check page title
            print(f"Page title: {driver.title}")
            
            # 2. Check for markers
            markers = driver.find_elements(By.CSS_SELECTOR, ".leaflet-marker-icon")
            print(f"Markers found: {len(markers)}")
            
            # 3. Check for results count
            results_count = loader.get_results_count()
            print(f"Results count: {results_count}")
            
            # 4. Check for error messages
            has_errors = loader.check_for_errors()
            print(f"Has errors: {has_errors}")
            
            # 5. Check page source for restaurant data
            page_source = driver.page_source
            print(f"Page source length: {len(page_source)} characters")
            
            # Look for restaurant-related keywords
            keywords = ['restaurant', 'cafe', 'food', 'vegan', 'vegetarian', 'marker', 'venue']
            for keyword in keywords:
                count = page_source.lower().count(keyword)
                print(f"'{keyword}' appears {count} times in page source")
            
            # 6. Check for JavaScript variables
            print("\n🔍 JavaScript Variables:")
            js_vars = [
                'window.restaurants',
                'window.markers', 
                'window.data',
                'window.searchResults',
                'window.venues'
            ]
            
            for var in js_vars:
                try:
                    result = driver.execute_script(f"return {var};")
                    if result:
                        print(f"  {var}: Found (Type: {type(result)}, Length: {len(result) if isinstance(result, (list, dict)) else 'N/A'})")
                        if isinstance(result, (list, dict)) and len(str(result)) < 500:
                            print(f"    Content: {result}")
                    else:
                        print(f"  {var}: Not found")
                except Exception as e:
                    print(f"  {var}: Error - {e}")
            
            # 7. Check for specific elements
            print("\n🔍 DOM Elements:")
            selectors = [
                '.leaflet-marker-icon',
                '.search-results',
                '.restaurant',
                '.venue',
                '[data-lat]',
                '[data-lng]',
                '.leaflet-popup',
                '.marker-popup'
            ]
            
            for selector in selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"  '{selector}': {len(elements)} elements")
                
                # Show attributes of first few elements
                if elements and len(elements) <= 3:
                    for i, el in enumerate(elements):
                        print(f"    Element {i+1}:")
                        for attr in ['data-lat', 'data-lng', 'title', 'alt', 'class']:
                            value = el.get_attribute(attr)
                            if value:
                                print(f"      {attr}: {value[:50]}...")
            
            # 8. Try to extract data using the extractor
            print("\n🔍 Data Extraction Test:")
            extractor = HappyCowDataExtractor(driver)
            restaurants = extractor.extract_restaurants_from_page()
            
            if restaurants:
                print(f"✅ Extracted {len(restaurants)} restaurants")
                for i, restaurant in enumerate(restaurants[:3]):
                    print(f"  Restaurant {i+1}: {restaurant}")
            else:
                print("❌ No restaurants extracted")
            
            # 9. Check if we need to wait longer or interact with the page
            print("\n🔍 Interaction Test:")
            try:
                # Try clicking on a marker if any exist
                if markers:
                    print(f"Attempting to click on first marker...")
                    markers[0].click()
                    time.sleep(2)
                    
                    # Check for popup
                    popups = driver.find_elements(By.CSS_SELECTOR, ".leaflet-popup")
                    print(f"Popups after click: {len(popups)}")
                    
                    if popups:
                        popup_content = popups[0].text
                        print(f"Popup content: {popup_content[:200]}...")
            except Exception as e:
                print(f"Interaction test failed: {e}")
            
        else:
            print("❌ Failed to load page")
            
    except Exception as e:
        logger.error(f"Error during debugging: {e}")
    finally:
        loader.close_driver()

if __name__ == "__main__":
    debug_searchmap()
