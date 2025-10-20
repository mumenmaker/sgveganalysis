#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for cluster expansion functionality
"""

import sys
import os
import logging

# Add the scraper directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hcowscraper import VeggiemapScraper
from config import Config

def test_cluster_expansion():
    """Test cluster expansion functionality"""
    print("🔍 Testing cluster expansion functionality...")
    
    try:
        scraper = VeggiemapScraper(enable_database=False)
        url = f"{Config.VEGGIEMAP_URL}?" + "&".join([f"{k}={v}" for k, v in Config.SINGAPORE_VEGGIEMAP_PARAMS.items()])
        
        print(f"Testing URL: {url}")
        print("This will take longer as it zooms in and expands clusters...")
        
        # Test with cluster expansion
        restaurants = scraper.scrape_singapore_restaurants(url, use_cluster_expansion=True)
        
        if restaurants:
            print(f"✅ Found {len(restaurants)} restaurants with cluster expansion")
            
            # Show sample restaurants
            print("\nSample restaurants:")
            for i, restaurant in enumerate(restaurants[:5], 1):
                coord_status = "✅" if restaurant.latitude and restaurant.longitude else "❌"
                vegan_status = "🌱" if restaurant.is_vegan else "🥗" if restaurant.is_vegetarian else "🍽️"
                print(f"  {i}. {restaurant.name} {vegan_status} {coord_status}")
                if restaurant.latitude and restaurant.longitude:
                    print(f"     Coordinates: {restaurant.latitude}, {restaurant.longitude}")
            
            return True
        else:
            print("❌ No restaurants found with cluster expansion")
            return False
            
    except Exception as e:
        print(f"❌ Cluster expansion test error: {e}")
        return False

def test_standard_vs_cluster():
    """Compare standard extraction vs cluster expansion"""
    print("🔍 Comparing standard vs cluster expansion methods...")
    
    try:
        scraper = VeggiemapScraper(enable_database=False)
        url = f"{Config.VEGGIEMAP_URL}?" + "&".join([f"{k}={v}" for k, v in Config.SINGAPORE_VEGGIEMAP_PARAMS.items()])
        
        print("Testing standard extraction...")
        standard_restaurants = scraper.scrape_singapore_restaurants(url, use_cluster_expansion=False)
        print(f"Standard method found: {len(standard_restaurants)} restaurants")
        
        print("\nTesting cluster expansion...")
        cluster_restaurants = scraper.scrape_singapore_restaurants(url, use_cluster_expansion=True)
        print(f"Cluster expansion found: {len(cluster_restaurants)} restaurants")
        
        print(f"\n📊 Comparison:")
        print(f"  Standard method: {len(standard_restaurants)} restaurants")
        print(f"  Cluster expansion: {len(cluster_restaurants)} restaurants")
        print(f"  Improvement: {len(cluster_restaurants) - len(standard_restaurants)} more restaurants")
        
        return len(cluster_restaurants) > len(standard_restaurants)
        
    except Exception as e:
        print(f"❌ Comparison test error: {e}")
        return False

def main():
    """Run cluster expansion tests"""
    print("🚀 Testing HappyCow Cluster Expansion")
    print("=" * 50)
    
    tests = [
        ("Cluster Expansion", test_cluster_expansion),
        ("Standard vs Cluster", test_standard_vs_cluster)
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
        print("🎉 All cluster expansion tests passed!")
    else:
        print("⚠️ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
