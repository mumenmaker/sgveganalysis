#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for hcowscraper library
"""

import sys
import os
import logging

# Add the scraper directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hcowscraper import VeggiemapScraper
from config import Config

def test_library_import():
    """Test that the library imports correctly"""
    print("🧪 Testing library imports...")
    
    try:
        from hcowscraper import VeggiemapScraper, MarkerExtractor, RestaurantParser
        print("✅ All library components imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_scraper_initialization():
    """Test scraper initialization"""
    print("🧪 Testing scraper initialization...")
    
    try:
        scraper = VeggiemapScraper(headless=True, enable_database=True)
        print("✅ Scraper initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("🧪 Testing database connection...")
    
    try:
        scraper = VeggiemapScraper(enable_database=True)
        if scraper.test_database_connection():
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_coordinate_extraction():
    """Test coordinate extraction (without full scraping)"""
    print("🧪 Testing coordinate extraction...")
    
    try:
        scraper = VeggiemapScraper(enable_database=False)
        url = f"{Config.VEGGIEMAP_URL}?" + "&".join([f"{k}={v}" for k, v in Config.SINGAPORE_VEGGIEMAP_PARAMS.items()])
        
        print(f"Testing URL: {url}")
        coordinates = scraper.scrape_with_coordinates_only(url)
        
        if coordinates:
            print(f"✅ Found {len(coordinates)} coordinates")
            print("Sample coordinates:")
            for i, coord in enumerate(coordinates[:3], 1):
                print(f"  {i}. Lat: {coord.get('latitude')}, Lng: {coord.get('longitude')}")
            return True
        else:
            print("❌ No coordinates found")
            return False
            
    except Exception as e:
        print(f"❌ Coordinate extraction error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing hcowscraper library")
    print("=" * 50)
    
    tests = [
        ("Library Import", test_library_import),
        ("Scraper Initialization", test_scraper_initialization),
        ("Database Connection", test_database_connection),
        ("Coordinate Extraction", test_coordinate_extraction)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Summary: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Library is ready to use.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
