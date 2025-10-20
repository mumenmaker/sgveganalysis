#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to investigate HappyCow veggiemap page structure
"""

import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Add the scraper directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

def debug_page_structure():
    """Debug the veggiemap page structure"""
    print("🔍 Debugging HappyCow veggiemap page structure...")
    
    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)
    
    try:
        # Build URL
        url = f"{Config.VEGGIEMAP_URL}?" + "&".join([f"{k}={v}" for k, v in Config.SINGAPORE_VEGGIEMAP_PARAMS.items()])
        print(f"Loading: {url}")
        
        driver.get(url)
        
        # Wait for page to load
        print("Waiting for page to load...")
        time.sleep(10)
        
        # Check for map container
        print("\n🗺️ Checking for map container...")
        map_containers = driver.find_elements(By.CLASS_NAME, "leaflet-container")
        print(f"Found {len(map_containers)} leaflet containers")
        
        if map_containers:
            print("✅ Map container found")
        else:
            print("❌ No map container found")
        
        # Check for marker pane
        print("\n📍 Checking for marker pane...")
        marker_panes = driver.find_elements(By.CLASS_NAME, "leaflet-marker-pane")
        print(f"Found {len(marker_panes)} marker panes")
        
        # Check for individual markers
        print("\n🎯 Checking for markers...")
        marker_selectors = [
            ".leaflet-marker-icon",
            ".leaflet-marker-icon[data-lat]",
            ".leaflet-marker-icon[data-lng]",
            "[class*='marker']",
            "[class*='leaflet']"
        ]
        
        for selector in marker_selectors:
            markers = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"  {selector}: {len(markers)} elements")
        
        # Check for JavaScript map instance
        print("\n🔧 Checking for JavaScript map instance...")
        try:
            map_exists = driver.execute_script("return typeof window.map !== 'undefined'")
            print(f"window.map exists: {map_exists}")
            
            if map_exists:
                layers_count = driver.execute_script("return Object.keys(window.map._layers || {}).length")
                print(f"Map layers count: {layers_count}")
                
                # Try to get layer details
                layer_info = driver.execute_script("""
                    const layers = [];
                    if (window.map && window.map._layers) {
                        for (let id in window.map._layers) {
                            const layer = window.map._layers[id];
                            layers.push({
                                id: id,
                                type: layer.constructor.name,
                                hasLatLng: typeof layer.getLatLng === 'function'
                            });
                        }
                    }
                    return layers;
                """)
                print(f"Layer details: {layer_info}")
            
        except Exception as e:
            print(f"JavaScript check error: {e}")
        
        # Check page source for coordinates
        print("\n📄 Checking page source for coordinates...")
        page_source = driver.page_source
        
        # Look for coordinate patterns
        import re
        lat_patterns = [
            r'data-lat="([^"]+)"',
            r'lat["\']?\s*[:=]\s*["\']?([0-9.-]+)',
            r'latitude["\']?\s*[:=]\s*["\']?([0-9.-]+)'
        ]
        
        lng_patterns = [
            r'data-lng="([^"]+)"',
            r'lng["\']?\s*[:=]\s*["\']?([0-9.-]+)',
            r'longitude["\']?\s*[:=]\s*["\']?([0-9.-]+)'
        ]
        
        for pattern in lat_patterns:
            matches = re.findall(pattern, page_source)
            if matches:
                print(f"Found latitude pattern '{pattern}': {matches[:5]}")  # Show first 5
        
        for pattern in lng_patterns:
            matches = re.findall(pattern, page_source)
            if matches:
                print(f"Found longitude pattern '{pattern}': {matches[:5]}")  # Show first 5
        
        # Check for any elements with data attributes
        print("\n🔍 Checking for elements with data attributes...")
        data_elements = driver.find_elements(By.CSS_SELECTOR, "[data-lat], [data-lng], [data-latitude], [data-longitude]")
        print(f"Found {len(data_elements)} elements with coordinate data attributes")
        
        for i, element in enumerate(data_elements[:5]):  # Show first 5
            try:
                tag = element.tag_name
                classes = element.get_attribute('class')
                data_lat = element.get_attribute('data-lat')
                data_lng = element.get_attribute('data-lng')
                print(f"  {i+1}. <{tag}> class='{classes}' data-lat='{data_lat}' data-lng='{data_lng}'")
            except:
                pass
        
        # Save page source for manual inspection
        print("\n💾 Saving page source for manual inspection...")
        with open('debug/veggiemap_page_source.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("Page source saved to debug/veggiemap_page_source.html")
        
    except Exception as e:
        print(f"❌ Debug error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_page_structure()
