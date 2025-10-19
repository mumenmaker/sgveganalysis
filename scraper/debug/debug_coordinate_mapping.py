#!/usr/bin/env python3
"""
Debug script to understand coordinate mapping in HappyCow
"""

import os
import sys
import re
import time
import json
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

def debug_coordinate_mapping():
    """Debug coordinate mapping in HappyCow"""
    print("🔍 Debugging Coordinate Mapping in HappyCow")
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
        
        # Extract restaurant data with marker IDs
        print("\n🔍 Extracting restaurant data with marker IDs:")
        print("-" * 50)
        
        restaurants = []
        for i, element in enumerate(elements[:5]):  # First 5 for debugging
            try:
                # Get basic info
                name_elem = element.find_element(By.CSS_SELECTOR, '.venue-name, .name, h3, h4')
                name = name_elem.text.strip()
                
                # Get marker ID
                marker_id = element.get_attribute('data-marker-id')
                venue_id = element.get_attribute('data-id')
                
                restaurants.append({
                    'index': i,
                    'name': name,
                    'marker_id': marker_id,
                    'venue_id': venue_id
                })
                
                print(f"Restaurant {i+1}: {name}")
                print(f"  Marker ID: {marker_id}")
                print(f"  Venue ID: {venue_id}")
                print()
                
            except Exception as e:
                print(f"Error extracting restaurant {i+1}: {e}")
        
        # Now look for coordinate data in page source
        print("\n🔍 Looking for coordinate data in page source:")
        print("-" * 50)
        
        page_source = driver.page_source
        
        # Look for various coordinate patterns
        coord_patterns = [
            r'data-lat="([^"]*)"',
            r'data-lng="([^"]*)"',
            r'"lat":\s*(\d+\.\d+)',
            r'"lng":\s*(\d+\.\d+)',
            r'"latitude":\s*(\d+\.\d+)',
            r'"longitude":\s*(\d+\.\d+)'
        ]
        
        found_coords = {}
        for pattern in coord_patterns:
            matches = re.findall(pattern, page_source)
            if matches:
                found_coords[pattern] = matches
                print(f"Pattern {pattern}: Found {len(matches)} matches")
                print(f"  First 5: {matches[:5]}")
        
        # Look for JavaScript data structures
        print("\n🔍 Looking for JavaScript data structures:")
        print("-" * 50)
        
        # Look for arrays of coordinates
        js_patterns = [
            r'lat:\s*\[([^\]]+)\]',
            r'lng:\s*\[([^\]]+)\]',
            r'latitude:\s*\[([^\]]+)\]',
            r'longitude:\s*\[([^\]]+)\]',
            r'coordinates:\s*\[([^\]]+)\]',
            r'venues:\s*\[([^\]]+)\]',
            r'restaurants:\s*\[([^\]]+)\]'
        ]
        
        for pattern in js_patterns:
            matches = re.findall(pattern, page_source)
            if matches:
                print(f"Found JS pattern: {pattern}")
                for i, match in enumerate(matches[:2]):
                    print(f"  Match {i+1}: {match[:200]}...")
        
        # Look for marker data
        print("\n🔍 Looking for marker data:")
        print("-" * 50)
        
        marker_patterns = [
            r'markers:\s*\[([^\]]+)\]',
            r'markerData:\s*\{([^}]+)\}',
            r'venueData:\s*\{([^}]+)\}',
            r'locationData:\s*\{([^}]+)\}'
        ]
        
        for pattern in marker_patterns:
            matches = re.findall(pattern, page_source)
            if matches:
                print(f"Found marker pattern: {pattern}")
                for i, match in enumerate(matches[:2]):
                    print(f"  Match {i+1}: {match[:200]}...")
        
        # Look for specific coordinate arrays
        print("\n🔍 Looking for coordinate arrays:")
        print("-" * 50)
        
        # Try to find arrays of coordinates
        coord_array_patterns = [
            r'\[(\d+\.\d+,\s*\d+\.\d+)\]',
            r'\{lat:\s*(\d+\.\d+),\s*lng:\s*(\d+\.\d+)\}',
            r'\{latitude:\s*(\d+\.\d+),\s*longitude:\s*(\d+\.\d+)\}'
        ]
        
        for pattern in coord_array_patterns:
            matches = re.findall(pattern, page_source)
            if matches:
                print(f"Found coordinate array pattern: {pattern}")
                print(f"  Found {len(matches)} coordinate pairs")
                for i, match in enumerate(matches[:5]):
                    print(f"    {i+1}: {match}")
        
        # Try to find the mapping between marker IDs and coordinates
        print("\n🔍 Looking for marker-coordinate mapping:")
        print("-" * 50)
        
        # Look for patterns that might map marker IDs to coordinates
        mapping_patterns = [
            r'markerId:\s*(\d+).*?lat:\s*(\d+\.\d+).*?lng:\s*(\d+\.\d+)',
            r'id:\s*(\d+).*?lat:\s*(\d+\.\d+).*?lng:\s*(\d+\.\d+)',
            r'index:\s*(\d+).*?lat:\s*(\d+\.\d+).*?lng:\s*(\d+\.\d+)'
        ]
        
        for pattern in mapping_patterns:
            matches = re.findall(pattern, page_source, re.DOTALL)
            if matches:
                print(f"Found mapping pattern: {pattern}")
                for i, match in enumerate(matches[:5]):
                    print(f"  {i+1}: {match}")
        
        # Save page source for manual analysis
        print("\n🔍 Saving page source for manual analysis...")
        with open('page_source_debug.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("Page source saved to page_source_debug.html")
        
        # Try to find the specific coordinate extraction logic
        print("\n🔍 Looking for coordinate extraction logic:")
        print("-" * 50)
        
        # Look for the specific patterns we're trying to extract
        extraction_patterns = [
            r'data-lat="([^"]*)"',
            r'data-lng="([^"]*)"',
            r'getAttribute\(["\']data-lat["\']\)',
            r'getAttribute\(["\']data-lng["\']\)'
        ]
        
        for pattern in extraction_patterns:
            matches = re.findall(pattern, page_source)
            if matches:
                print(f"Found extraction pattern: {pattern}")
                print(f"  Found {len(matches)} matches")
                for i, match in enumerate(matches[:3]):
                    print(f"    {i+1}: {match}")
        
        print("\n✅ Debug analysis complete!")
        print("Check page_source_debug.html for manual analysis")
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()
            print("\n✅ Selenium WebDriver closed")

if __name__ == "__main__":
    debug_coordinate_mapping()
