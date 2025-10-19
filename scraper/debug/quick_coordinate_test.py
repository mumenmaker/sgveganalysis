#!/usr/bin/env python3
"""
Quick test to verify coordinate extraction is working
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def quick_coordinate_test():
    """Quick test to verify coordinate extraction"""
    print("🔍 Quick Coordinate Extraction Test")
    print("=" * 40)
    
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
        print(f"Loading page...")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Find restaurant elements
        elements = driver.find_elements(By.CSS_SELECTOR, '.venue-item')
        print(f"Found {len(elements)} restaurant elements")
        
        if len(elements) == 0:
            print("❌ No restaurant elements found!")
            return
        
        # Test coordinate extraction on first 3 restaurants
        print("\n🔍 Testing coordinate extraction:")
        print("-" * 40)
        
        for i, element in enumerate(elements[:3]):
            print(f"\n--- Restaurant {i+1} ---")
            
            # Get basic info
            try:
                name_elem = element.find_element(By.CSS_SELECTOR, '.venue-name, .name, h3, h4')
                name = name_elem.text.strip()
                print(f"Name: {name}")
            except Exception as e:
                print(f"Name: Could not extract - {e}")
                continue
            
            # Get the data-id from the main element
            main_id = element.get_attribute('data-id')
            print(f"Data ID: {main_id}")
            
            # Look for details element with same data-id
            try:
                details_element = driver.find_element(By.CSS_SELECTOR, f'div.details.hidden[data-id="{main_id}"]')
                if details_element:
                    lat = details_element.get_attribute('data-lat')
                    lng = details_element.get_attribute('data-lng')
                    print(f"✅ Found coordinates: lat={lat}, lng={lng}")
                else:
                    print("❌ No details element found")
            except Exception as e:
                print(f"❌ Error finding details element: {e}")
            
            print("-" * 30)
        
        print("\n✅ Quick coordinate test complete!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()
            print("\n✅ Selenium WebDriver closed")

if __name__ == "__main__":
    quick_coordinate_test()
