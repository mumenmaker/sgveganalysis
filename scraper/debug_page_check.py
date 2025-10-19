#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to check what's happening with the HappyCow page
"""
import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Add the scraper directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config

def debug_page():
    """Debug the HappyCow page to see what's happening"""
    print("🔍 Debugging HappyCow page...")
    
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
        # Build URL exactly like the scraper
        params = Config.SINGAPORE_PARAMS.copy()
        params['page'] = str(1)
        url = "{}?".format(Config.SEARCH_URL) + "&".join(["{}={}".format(k, v) for k, v in params.items()])
        
        print(f"🌐 Loading URL: {url}")
        driver.get(url)
        
        print("⏳ Waiting for page to load...")
        time.sleep(15)
        
        # Check page title
        title = driver.title
        print(f"📄 Page title: {title}")
        
        # Check if we're on the right page
        if "happycow" not in title.lower():
            print("❌ Not on HappyCow page!")
            return False
        
        # Check for various selectors
        selectors_to_try = [
            '.venue-item',
            '.restaurant-item', 
            '.search-result',
            '.result-item',
            '.item',
            '[class*="venue"]',
            '[class*="restaurant"]',
            '[class*="result"]',
            '[class*="item"]',
            'div[data-id]',
            'div[data-lat]',
            'div[data-lng]'
        ]
        
        print("\n🔍 Checking for restaurant elements...")
        for selector in selectors_to_try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"  {selector}: {len(elements)} elements")
            if elements and len(elements) > 0:
                print(f"    First element text: '{elements[0].text.strip()[:100]}...'")
                print(f"    First element classes: '{elements[0].get_attribute('class')}'")
                print(f"    First element data-id: '{elements[0].get_attribute('data-id')}'")
                print(f"    First element data-lat: '{elements[0].get_attribute('data-lat')}'")
                print(f"    First element data-lng: '{elements[0].get_attribute('data-lng')}'")
        
        # Check for any divs with coordinates
        coord_elements = driver.find_elements(By.CSS_SELECTOR, '[data-lat][data-lng]')
        print(f"\n📍 Elements with coordinates: {len(coord_elements)}")
        
        # Check page source for clues
        page_source = driver.page_source
        print(f"\n📊 Page source length: {len(page_source)}")
        
        # Look for common patterns
        if "venue" in page_source.lower():
            print("✅ Found 'venue' in page source")
        if "restaurant" in page_source.lower():
            print("✅ Found 'restaurant' in page source")
        if "singapore" in page_source.lower():
            print("✅ Found 'singapore' in page source")
        
        # Check for error messages
        if "error" in page_source.lower():
            print("❌ Found 'error' in page source")
        if "blocked" in page_source.lower():
            print("❌ Found 'blocked' in page source")
        if "forbidden" in page_source.lower():
            print("❌ Found 'forbidden' in page source")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🚀 Starting HappyCow Page Debug")
    print("=" * 50)
    
    if debug_page():
        print("\n✅ Debug completed successfully!")
    else:
        print("\n❌ Debug failed!")
