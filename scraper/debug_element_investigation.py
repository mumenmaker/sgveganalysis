#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to investigate what elements contain restaurant data
"""
import sys
import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Add the scraper directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def investigate_elements():
    """Investigate what elements contain restaurant data"""
    print("🔍 Investigating Restaurant Elements")
    print("=" * 50)
    
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
        # Build URL
        params = Config.SINGAPORE_PARAMS.copy()
        params['page'] = str(1)
        url = "{}?".format(Config.SEARCH_URL) + "&".join(["{}={}".format(k, v) for k, v in params.items()])
        
        print(f"🌐 Loading page: {url}")
        driver.get(url)
        
        print("⏳ Waiting for page to load...")
        time.sleep(15)
        
        # Test different selectors
        selectors_to_test = [
            'div[data-marker-id]',
            '.venue-item',
            '.restaurant-item',
            '.search-result',
            '.result-item',
            '.item',
            '[class*="venue"]',
            '[class*="restaurant"]',
            '[class*="result"]',
            '[class*="item"]',
            'div[class*="card"]',
            'div[class*="listing"]',
            'div[class*="restaurant"]',
            'div[class*="venue"]'
        ]
        
        print("\n📊 Testing different selectors:")
        print("-" * 40)
        
        for selector in selectors_to_test:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"🔍 Selector: {selector}")
                print(f"   Found: {len(elements)} elements")
                
                if elements:
                    # Check first few elements for text content
                    for i, element in enumerate(elements[:3]):
                        text = element.text.strip()
                        classes = element.get_attribute('class')
                        tag = element.tag_name
                        print(f"   Element {i+1}: {tag} - Classes: {classes}")
                        print(f"   Text: '{text[:100]}{'...' if len(text) > 100 else ''}'")
                        
                        # Check for data attributes
                        data_attrs = {}
                        for attr in ['data-id', 'data-marker-id', 'data-lat', 'data-lng', 'data-name', 'data-address']:
                            value = element.get_attribute(attr)
                            if value:
                                data_attrs[attr] = value
                        
                        if data_attrs:
                            print(f"   Data attributes: {data_attrs}")
                        print()
                
                print()
                
            except Exception as e:
                print(f"   Error with selector {selector}: {e}")
                print()
        
        # Look for any elements with restaurant-like text
        print("\n🔍 Looking for elements with restaurant-like text:")
        print("-" * 50)
        
        # Get all divs and check for restaurant-like content
        all_divs = driver.find_elements(By.TAG_NAME, 'div')
        restaurant_like_divs = []
        
        for div in all_divs:
            text = div.text.strip()
            if text and len(text) > 10:  # Has substantial text
                # Check if it looks like restaurant data
                if any(keyword in text.lower() for keyword in ['restaurant', 'cafe', 'vegan', 'vegetarian', 'food', 'dining']):
                    classes = div.get_attribute('class')
                    restaurant_like_divs.append((div, text, classes))
        
        print(f"Found {len(restaurant_like_divs)} divs with restaurant-like content")
        
        for i, (div, text, classes) in enumerate(restaurant_like_divs[:5]):  # Show first 5
            print(f"\n🍽️  Restaurant-like div {i+1}:")
            print(f"   Classes: {classes}")
            print(f"   Text: '{text[:200]}{'...' if len(text) > 200 else ''}'")
            
            # Check for data attributes
            data_attrs = {}
            for attr in ['data-id', 'data-marker-id', 'data-lat', 'data-lng', 'data-name', 'data-address']:
                value = div.get_attribute(attr)
                if value:
                    data_attrs[attr] = value
            
            if data_attrs:
                print(f"   Data attributes: {data_attrs}")
        
        print(f"\n✅ Investigation completed!")
        
    except Exception as e:
        print(f"❌ Error during investigation: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    investigate_elements()
