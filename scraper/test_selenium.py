#!/usr/bin/env python3
"""
Test Selenium to see if we can get the dynamic content
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_selenium_scraping():
    """Test Selenium to get dynamic content"""
    print("=== Testing Selenium Scraping ===\n")
    
    try:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36')
        
        print("Setting up Chrome WebDriver...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        # Build URL
        url = "https://www.happycow.net/searchmap?s=3&location=Central+Singapore%2C+Singapore&lat=1.34183&lng=103.861&page=1&zoom=11&metric=mi&limit=81&order=default"
        
        print(f"Loading page: {url}")
        driver.get(url)
        
        # Wait for page to load
        print("Waiting for page to load...")
        time.sleep(10)
        
        # Check page title
        print(f"Page title: {driver.title}")
        
        # Look for restaurant elements
        print("\n=== Looking for restaurant elements ===")
        
        # Try different selectors
        selectors_to_try = [
            '.restaurant-item',
            '.venue-item', 
            '.listing-item',
            '.search-result',
            '.business-item',
            '.place-item',
            '[data-venue]',
            '.restaurant',
            '.venue',
            '.listing'
        ]
        
        for selector in selectors_to_try:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ Found {len(elements)} elements with selector: {selector}")
                    for i, elem in enumerate(elements[:3]):
                        text = elem.text.strip()
                        if text:
                            print(f"  Element {i+1}: {text[:100]}...")
                else:
                    print(f"❌ No elements found with selector: {selector}")
            except Exception as e:
                print(f"❌ Error with selector {selector}: {e}")
        
        # Look for any divs that might contain restaurant data
        print("\n=== Looking for any divs with content ===")
        all_divs = driver.find_elements(By.TAG_NAME, 'div')
        print(f"Total divs found: {len(all_divs)}")
        
        # Look for divs with restaurant-like content
        restaurant_divs = []
        for div in all_divs:
            try:
                text = div.text.strip().lower()
                if any(word in text for word in ['restaurant', 'cafe', 'food', 'dining', 'vegan', 'vegetarian']):
                    if len(text) > 10 and len(text) < 200:
                        restaurant_divs.append(div)
            except:
                continue
        
        print(f"Found {len(restaurant_divs)} divs with restaurant-like content")
        for i, div in enumerate(restaurant_divs[:5]):
            try:
                text = div.text.strip()
                print(f"  Restaurant div {i+1}: {text[:150]}...")
            except:
                continue
        
        # Check if there are any network requests or AJAX calls
        print("\n=== Checking for network requests ===")
        try:
            # Get page source to see if any data was loaded
            page_source = driver.page_source
            print(f"Page source length: {len(page_source)}")
            
            # Look for restaurant data in the page source
            if 'restaurant' in page_source.lower():
                print("✅ Found 'restaurant' in page source")
            else:
                print("❌ No 'restaurant' found in page source")
            
            # Look for any JSON data
            if '{"' in page_source or '[' in page_source:
                print("✅ Found JSON-like data in page source")
            else:
                print("❌ No JSON-like data found in page source")
                
        except Exception as e:
            print(f"❌ Error checking page source: {e}")
        
        # Wait a bit more to see if data loads
        print("\n=== Waiting for additional data to load ===")
        time.sleep(5)
        
        # Check again for restaurant elements
        restaurant_elements = driver.find_elements(By.CSS_SELECTOR, '.restaurant-item, .venue-item, .listing-item')
        print(f"Restaurant elements after waiting: {len(restaurant_elements)}")
        
        if restaurant_elements:
            print("✅ Found restaurant elements after waiting!")
            for i, elem in enumerate(restaurant_elements[:3]):
                try:
                    text = elem.text.strip()
                    print(f"  Restaurant {i+1}: {text[:100]}...")
                except:
                    continue
        else:
            print("❌ Still no restaurant elements found")
            
            # Show some of the page content
            print("\n=== Page content preview ===")
            body = driver.find_element(By.TAG_NAME, 'body')
            print(f"Body text preview: {body.text[:500]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    test_selenium_scraping()
