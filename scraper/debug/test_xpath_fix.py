#!/usr/bin/env python3
"""
Test XPath selector for finding sibling details elements
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def test_xpath_selector():
    """Test XPath selector for finding sibling details elements"""
    print("🔍 Testing XPath Selector for Sibling Details Elements")
    print("=" * 60)
    
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
        time.sleep(5)
        
        # Find restaurant elements
        elements = driver.find_elements(By.CSS_SELECTOR, '.venue-item')
        print(f"Found {len(elements)} restaurant elements")
        
        if len(elements) == 0:
            print("❌ No restaurant elements found!")
            return
        
        # Test different XPath selectors
        print("\n🔍 Testing different XPath selectors:")
        print("-" * 50)
        
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
            
            # Test different XPath selectors
            xpath_selectors = [
                "following-sibling::div[contains(@class, 'details') and contains(@class, 'hidden')]",
                "following-sibling::div[@class='details hidden']",
                "following-sibling::div[contains(@class, 'details')]",
                "following-sibling::*[contains(@class, 'details')]",
                "..//div[contains(@class, 'details') and contains(@class, 'hidden')]",
                "..//div[@class='details hidden']",
                "..//div[contains(@class, 'details')]"
            ]
            
            for j, xpath in enumerate(xpath_selectors):
                try:
                    print(f"  XPath {j+1}: {xpath}")
                    details_element = element.find_element(By.XPATH, xpath)
                    if details_element:
                        lat = details_element.get_attribute('data-lat')
                        lng = details_element.get_attribute('data-lng')
                        print(f"    ✅ Found details element: lat={lat}, lng={lng}")
                        if lat and lng:
                            print(f"    🎯 SUCCESS: Coordinates found!")
                            break
                        else:
                            print(f"    ❌ No coordinates in details element")
                    else:
                        print(f"    ❌ No details element found")
                except Exception as e:
                    print(f"    ❌ Error: {e}")
            
            # Try to find all div elements with class containing 'details'
            try:
                print(f"  Looking for all details divs...")
                all_details = driver.find_elements(By.CSS_SELECTOR, 'div.details.hidden')
                print(f"    Found {len(all_details)} details divs on page")
                
                if len(all_details) > 0:
                    # Check if any have coordinates
                    for k, details_div in enumerate(all_details[:5]):
                        lat = details_div.get_attribute('data-lat')
                        lng = details_div.get_attribute('data-lng')
                        if lat and lng:
                            print(f"    Details div {k+1}: lat={lat}, lng={lng}")
            except Exception as e:
                print(f"    Error finding details divs: {e}")
            
            print("-" * 30)
        
        print("\n✅ XPath selector test complete!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()
            print("\n✅ Selenium WebDriver closed")

if __name__ == "__main__":
    test_xpath_selector()
