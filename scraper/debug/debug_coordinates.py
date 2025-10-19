#!/usr/bin/env python3
"""
Debug script to analyze coordinate extraction from HappyCow
"""

import os
import sys
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_selenium():
    """Setup Selenium WebDriver"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=options)
    return driver

def debug_coordinate_extraction():
    """Debug coordinate extraction from HappyCow"""
    print("🔍 Debugging Coordinate Extraction from HappyCow")
    print("=" * 60)
    
    driver = None
    try:
        # Setup Selenium
        print("Setting up Selenium WebDriver...")
        driver = setup_selenium()
        
        # Load the page
        url = "https://www.happycow.net/searchmap?s=3&location=Central+Singapore%2C+Singapore&lat=1.34183&lng=103.861&page=1&zoom=11&metric=mi&limit=81&order=default"
        print(f"Loading page: {url}")
        driver.get(url)
        
        # Wait for page to load
        print("Waiting for page to load...")
        time.sleep(5)
        
        # Find restaurant elements
        print("Looking for restaurant elements...")
        elements = driver.find_elements(By.CSS_SELECTOR, '.venue-item')
        print(f"Found {len(elements)} restaurant elements")
        
        if len(elements) == 0:
            print("❌ No restaurant elements found!")
            return
        
        # Debug first few elements
        print("\n🔍 Analyzing first 3 restaurant elements:")
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
            
            # Check all data attributes
            print("Data attributes:")
            try:
                attrs = driver.execute_script("""
                    var element = arguments[0];
                    var attrs = {};
                    for (var i = 0; i < element.attributes.length; i++) {
                        var attr = element.attributes[i];
                        if (attr.name.startsWith('data-')) {
                            attrs[attr.name] = attr.value;
                        }
                    }
                    return attrs;
                """, element)
                
                for attr_name, attr_value in attrs.items():
                    print(f"  {attr_name}: {attr_value}")
                    
            except Exception as e:
                print(f"  Error getting attributes: {e}")
            
            # Check for coordinate patterns in element HTML
            print("Element HTML (first 500 chars):")
            try:
                html = element.get_attribute('outerHTML')
                print(f"  {html[:500]}...")
            except Exception as e:
                print(f"  Error getting HTML: {e}")
            
            # Check for coordinate patterns in page source
            print("Checking page source for coordinate patterns...")
            try:
                page_source = driver.page_source
                
                # Look for various coordinate patterns
                patterns = [
                    r'"lat":\s*(\d+\.\d+)',
                    r'"lng":\s*(\d+\.\d+)',
                    r'"latitude":\s*(\d+\.\d+)',
                    r'"longitude":\s*(\d+\.\d+)',
                    r'data-lat="([^"]*)"',
                    r'data-lng="([^"]*)"',
                    r'data-latitude="([^"]*)"',
                    r'data-longitude="([^"]*)"'
                ]
                
                found_coords = {}
                for pattern in patterns:
                    matches = re.findall(pattern, page_source)
                    if matches:
                        found_coords[pattern] = matches[:5]  # First 5 matches
                
                if found_coords:
                    print("  Found coordinate patterns in page source:")
                    for pattern, matches in found_coords.items():
                        print(f"    {pattern}: {matches}")
                else:
                    print("  No coordinate patterns found in page source")
                    
            except Exception as e:
                print(f"  Error analyzing page source: {e}")
            
            print("-" * 30)
        
        # Check if coordinates are in JavaScript data
        print("\n🔍 Checking for JavaScript coordinate data:")
        try:
            # Look for common JavaScript patterns
            js_patterns = [
                r'venues\s*:\s*\[.*?\]',
                r'restaurants\s*:\s*\[.*?\]',
                r'locations\s*:\s*\[.*?\]',
                r'data\s*:\s*\[.*?\]'
            ]
            
            page_source = driver.page_source
            for pattern in js_patterns:
                matches = re.findall(pattern, page_source, re.DOTALL)
                if matches:
                    print(f"Found JavaScript data pattern: {pattern}")
                    for i, match in enumerate(matches[:2]):  # First 2 matches
                        print(f"  Match {i+1}: {match[:200]}...")
        except Exception as e:
            print(f"Error checking JavaScript data: {e}")
        
        # Check for map initialization data
        print("\n🔍 Checking for map initialization data:")
        try:
            # Look for map-related JavaScript
            map_patterns = [
                r'google\.maps\.LatLng\([^)]+\)',
                r'new\s+google\.maps\.LatLng\([^)]+\)',
                r'lat:\s*\d+\.\d+',
                r'lng:\s*\d+\.\d+',
                r'center:\s*\{[^}]+\}',
                r'zoom:\s*\d+'
            ]
            
            page_source = driver.page_source
            for pattern in map_patterns:
                matches = re.findall(pattern, page_source)
                if matches:
                    print(f"Found map pattern: {pattern}")
                    for match in matches[:3]:  # First 3 matches
                        print(f"  {match}")
        except Exception as e:
            print(f"Error checking map data: {e}")
            
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()
            print("\n✅ Selenium WebDriver closed")

if __name__ == "__main__":
    debug_coordinate_extraction()