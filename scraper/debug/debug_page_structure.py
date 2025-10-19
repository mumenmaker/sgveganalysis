#!/usr/bin/env python3
"""
Debug page structure to understand what's happening
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def debug_page_structure():
    """Debug page structure to understand what's happening"""
    print("🔍 Debugging Page Structure")
    print("=" * 50)
    
    driver = None
    try:
        # Setup Selenium
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36')
        
        driver = webdriver.Chrome(options=options)
        
        # Load the page
        url = "https://www.happycow.net/searchmap?s=3&location=Central+Singapore%2C+Singapore&lat=1.34183&lng=103.861&page=1&zoom=11&metric=mi&limit=81&order=default"
        print(f"Loading page: {url}")
        driver.get(url)
        
        # Wait for page to load
        print("Waiting for page to load...")
        time.sleep(10)  # Wait longer
        
        # Check page title
        print(f"Page title: {driver.title}")
        
        # Check if page loaded correctly
        print(f"Current URL: {driver.current_url}")
        
        # Look for different selectors
        selectors_to_try = [
            '.venue-item',
            '.card-listing',
            '.venue',
            '[data-id]',
            '.restaurant',
            '.listing',
            '.item'
        ]
        
        print("\n🔍 Testing different selectors:")
        print("-" * 40)
        
        for selector in selectors_to_try:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"  {selector}: Found {len(elements)} elements")
                if len(elements) > 0:
                    print(f"    First element classes: {elements[0].get_attribute('class')}")
                    print(f"    First element tag: {elements[0].tag_name}")
            except Exception as e:
                print(f"  {selector}: Error - {e}")
        
        # Check for any divs with data attributes
        print("\n🔍 Looking for divs with data attributes:")
        print("-" * 40)
        
        try:
            data_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-id]')
            print(f"Found {len(data_elements)} divs with data-id")
            
            if len(data_elements) > 0:
                for i, elem in enumerate(data_elements[:3]):
                    print(f"  Element {i+1}:")
                    print(f"    Classes: {elem.get_attribute('class')}")
                    print(f"    Data-id: {elem.get_attribute('data-id')}")
                    print(f"    Data-marker-id: {elem.get_attribute('data-marker-id')}")
        except Exception as e:
            print(f"Error finding data elements: {e}")
        
        # Check for any elements with coordinates
        print("\n🔍 Looking for elements with coordinates:")
        print("-" * 40)
        
        try:
            coord_elements = driver.find_elements(By.CSS_SELECTOR, '[data-lat]')
            print(f"Found {len(coord_elements)} elements with data-lat")
            
            if len(coord_elements) > 0:
                for i, elem in enumerate(coord_elements[:3]):
                    print(f"  Element {i+1}:")
                    print(f"    Classes: {elem.get_attribute('class')}")
                    print(f"    Data-lat: {elem.get_attribute('data-lat')}")
                    print(f"    Data-lng: {elem.get_attribute('data-lng')}")
        except Exception as e:
            print(f"Error finding coordinate elements: {e}")
        
        # Check page source for restaurant data
        print("\n🔍 Checking page source for restaurant data:")
        print("-" * 40)
        
        page_source = driver.page_source
        if 'venue-item' in page_source:
            print("✅ Found 'venue-item' in page source")
        else:
            print("❌ 'venue-item' not found in page source")
        
        if 'data-lat' in page_source:
            print("✅ Found 'data-lat' in page source")
        else:
            print("❌ 'data-lat' not found in page source")
        
        if 'Kunthaville' in page_source:
            print("✅ Found 'Kunthaville' in page source")
        else:
            print("❌ 'Kunthaville' not found in page source")
        
        # Save page source for manual inspection
        with open('debug_page_source.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("Page source saved to debug_page_source.html")
        
        print("\n✅ Page structure debug complete!")
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()
            print("\n✅ Selenium WebDriver closed")

if __name__ == "__main__":
    debug_page_structure()
