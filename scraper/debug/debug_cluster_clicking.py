#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to test cluster clicking and restaurant data extraction
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

def debug_cluster_clicking():
    """Debug cluster clicking to get restaurant data"""
    print("🔍 Debugging cluster clicking for restaurant data...")
    
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
        
        # Find all markers
        markers = driver.find_elements(By.CSS_SELECTOR, ".leaflet-marker-icon")
        print(f"Found {len(markers)} markers")
        
        # Try clicking each marker to see what happens
        restaurant_data = []
        
        for i, marker in enumerate(markers):
            try:
                print(f"\n🎯 Clicking marker {i+1}/{len(markers)}")
                
                # Get marker info before clicking
                marker_title = marker.get_attribute('title') or ''
                marker_class = marker.get_attribute('class') or ''
                print(f"  Before click - Title: '{marker_title}', Class: '{marker_class}'")
                
                # Click the marker
                driver.execute_script("arguments[0].click();", marker)
                time.sleep(2)  # Wait for response
                
                # Check for popup content
                popup_selectors = [
                    ".leaflet-popup-content",
                    ".leaflet-popup-content-wrapper",
                    "[class*='popup']",
                    "[class*='tooltip']"
                ]
                
                popup_found = False
                for selector in popup_selectors:
                    popups = driver.find_elements(By.CSS_SELECTOR, selector)
                    if popups:
                        popup_text = popups[0].text
                        if popup_text:
                            print(f"  ✅ Popup found with selector '{selector}': {popup_text[:100]}...")
                            restaurant_data.append({
                                'marker_index': i,
                                'popup_text': popup_text,
                                'marker_title': marker_title
                            })
                            popup_found = True
                            break
                
                if not popup_found:
                    print(f"  ❌ No popup found for marker {i+1}")
                
                # Try to close popup
                try:
                    close_buttons = driver.find_elements(By.CSS_SELECTOR, 
                        ".leaflet-popup-close-button, .leaflet-popup-close, [class*='close']")
                    if close_buttons:
                        close_buttons[0].click()
                        time.sleep(0.5)
                except:
                    pass
                
            except Exception as e:
                print(f"  ❌ Error clicking marker {i+1}: {e}")
                continue
        
        print(f"\n📊 Results:")
        print(f"Total markers clicked: {len(markers)}")
        print(f"Restaurants found: {len(restaurant_data)}")
        
        if restaurant_data:
            print("\n🍽️ Sample restaurant data:")
            for i, data in enumerate(restaurant_data[:3], 1):
                print(f"  {i}. Marker {data['marker_index']+1}: {data['popup_text'][:50]}...")
        
        return len(restaurant_data) > 0
        
    except Exception as e:
        print(f"❌ Debug error: {e}")
        return False
    finally:
        driver.quit()

def debug_zoom_and_click():
    """Debug zooming in and clicking clusters"""
    print("🔍 Debugging zoom and click approach...")
    
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
        time.sleep(10)
        
        # Try zooming in
        print("🔍 Attempting to zoom in...")
        try:
            # Method 1: JavaScript zoom
            driver.execute_script("""
                if (window.map) {
                    window.map.setZoom(15);
                }
            """)
            time.sleep(3)
            print("✅ Zoomed via JavaScript")
        except Exception as e:
            print(f"❌ JavaScript zoom failed: {e}")
        
        # Try zoom controls
        try:
            zoom_in_btn = driver.find_elements(By.CSS_SELECTOR, ".leaflet-control-zoom-in")
            if zoom_in_btn:
                for _ in range(5):  # Click zoom in 5 times
                    zoom_in_btn[0].click()
                    time.sleep(1)
                print("✅ Zoomed via controls")
        except Exception as e:
            print(f"❌ Control zoom failed: {e}")
        
        # Check for new markers after zoom
        markers_after_zoom = driver.find_elements(By.CSS_SELECTOR, ".leaflet-marker-icon")
        print(f"Markers after zoom: {len(markers_after_zoom)}")
        
        # Try clicking clusters
        cluster_markers = []
        for marker in markers_after_zoom:
            title = marker.get_attribute('title') or ''
            if 'markers' in title.lower() or 'cluster' in title.lower():
                cluster_markers.append(marker)
        
        print(f"Found {len(cluster_markers)} potential cluster markers")
        
        # Click cluster markers
        for i, cluster in enumerate(cluster_markers):
            try:
                print(f"🎯 Clicking cluster {i+1}")
                driver.execute_script("arguments[0].click();", cluster)
                time.sleep(3)  # Wait for cluster to expand
                
                # Check for new individual markers
                individual_markers = driver.find_elements(By.CSS_SELECTOR, 
                    ".leaflet-marker-icon:not([title*='markers']):not([title*='cluster'])")
                print(f"  Individual markers after click: {len(individual_markers)}")
                
            except Exception as e:
                print(f"  ❌ Error clicking cluster {i+1}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug error: {e}")
        return False
    finally:
        driver.quit()

def main():
    """Run cluster debugging tests"""
    print("🚀 Debugging HappyCow Cluster Interaction")
    print("=" * 60)
    
    tests = [
        ("Cluster Clicking", debug_cluster_clicking),
        ("Zoom and Click", debug_zoom_and_click)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 DEBUG RESULTS")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Summary: {passed}/{len(results)} tests passed")

if __name__ == "__main__":
    main()
