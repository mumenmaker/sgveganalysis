#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to test coordinate extraction from div.details.hidden elements
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

def debug_coordinate_extraction():
    """Debug coordinate extraction from div.details.hidden elements"""
    print("🔍 Debugging coordinate extraction from div.details.hidden elements...")
    
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
        # Build URL exactly like the main scraper
        params = Config.SINGAPORE_PARAMS.copy()
        params['page'] = str(1)  # Test with page 1
        url = "{}?".format(Config.SEARCH_URL) + "&".join(["{}={}".format(k, v) for k, v in params.items()])
        
        print("Loading page: {}".format(url))
        driver.get(url)
        
        print("Waiting for page to load...")
        time.sleep(15) # Use the same wait time as the scraper

        # Look for div[data-marker-id] elements
        print("\n--- Looking for div[data-marker-id] elements ---")
        marker_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-marker-id]')
        print("Found {} div[data-marker-id] elements".format(len(marker_elements)))

        if marker_elements:
            print("Inspecting first 5 marker elements:")
            for i, element in enumerate(marker_elements[:5]):
                print(f"\n  Marker Element {i+1}:")
                print(f"    Tag name: {element.tag_name}")
                print(f"    Classes: {element.get_attribute('class')}")
                print(f"    data-marker-id: {element.get_attribute('data-marker-id')}")

                # Look for associated hidden details
                marker_id = element.get_attribute('data-marker-id')
                if marker_id:
                    try:
                        details_element = driver.find_element(By.CSS_SELECTOR, f'div.details.hidden[data-marker-id="{marker_id}"]')
                        lat = details_element.get_attribute('data-lat')
                        lng = details_element.get_attribute('data-lng')
                        print(f"    Associated hidden details (data-marker-id={marker_id}):")
                        print(f"      Classes: {details_element.get_attribute('class')}")
                        print(f"      data-lat: {lat}")
                        print(f"      data-lng: {lng}")
                        if lat and lng:
                            print(f"      ✅ Coordinates found: {lat}, {lng}")
                        else:
                            print(f"      ❌ No coordinates found")
                    except Exception as e:
                        print(f"    ❌ No associated hidden details found for data-marker-id={marker_id}: {e}")
        else:
            print("No div[data-marker-id] elements found.")

        # Also look for any hidden details elements with coordinates
        print("\n--- Looking for any hidden details elements with coordinates ---")
        hidden_details = driver.find_elements(By.CSS_SELECTOR, 'div.details.hidden')
        print("Found {} hidden details elements".format(len(hidden_details)))

        coord_count = 0
        for i, detail in enumerate(hidden_details[:10]):  # Check first 10
            lat = detail.get_attribute('data-lat')
            lng = detail.get_attribute('data-lng')
            marker_id = detail.get_attribute('data-marker-id')
            if lat and lng:
                coord_count += 1
                print(f"  Hidden Detail {i+1}: data-marker-id={marker_id}, lat={lat}, lng={lng}")
        
        if coord_count > 0:
            print(f"\n✅ Found {coord_count} hidden details elements with coordinates!")
        else:
            print(f"\n❌ No coordinates found in hidden details elements")

        # Also check for any elements with coordinates
        print("\n--- Looking for any elements with coordinates ---")
        coord_elements = driver.find_elements(By.CSS_SELECTOR, '[data-lat], [data-lng]')
        print("Found {} elements with coordinate attributes".format(len(coord_elements)))

        coord_count = 0
        for i, elem in enumerate(coord_elements[:10]):  # Check first 10
            lat = elem.get_attribute('data-lat')
            lng = elem.get_attribute('data-lng')
            if lat and lng:
                coord_count += 1
                print(f"  Element {i+1}: lat={lat}, lng={lng}")

        if coord_count > 0:
            print(f"\n✅ Found {coord_count} elements with coordinates!")
        else:
            print(f"\n❌ No coordinates found anywhere")

    except Exception as e:
        print("Error during coordinate extraction debug: {}".format(e))
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_coordinate_extraction()
