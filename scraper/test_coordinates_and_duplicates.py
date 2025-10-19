#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for coordinate extraction and duplicate handling
"""

import logging
import os
from dotenv import load_dotenv
from happycow_scraper import HappyCowScraper
from database import DatabaseManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_coordinate_extraction():
    """Test if coordinates are being extracted"""
    print("=== Testing Coordinate Extraction ===")
    
    load_dotenv()
    
    # Initialize scraper
    scraper = HappyCowScraper(enable_resume=False, use_selenium=True)
    
    try:
        # Scrape a few restaurants
        restaurants = scraper.scrape_singapore_restaurants(resume=False)
        
        if restaurants:
            print("Found {} restaurants".format(len(restaurants)))
            
            # Check first few restaurants for coordinates
            for i, restaurant in enumerate(restaurants[:5]):
                print("\nRestaurant {}: {}".format(i+1, restaurant.name))
                print("  Address: {}".format(restaurant.address))
                print("  Latitude: {}".format(restaurant.latitude))
                print("  Longitude: {}".format(restaurant.longitude))
                print("  Rating: {}".format(restaurant.rating))
        else:
            print("No restaurants found")
            
    except Exception as e:
        print("Error during scraping: {}".format(e))
    finally:
        scraper.close_selenium()

def test_duplicate_handling():
    """Test duplicate handling in database"""
    print("\n=== Testing Duplicate Handling ===")
    
    load_dotenv()
    
    # Initialize database manager
    db_manager = DatabaseManager()
    if not db_manager.supabase:
        print("❌ No database connection")
        return
    
    # Create a test restaurant with unique coordinates
    from models import Restaurant
    from datetime import datetime
    import random
    
    # Use random coordinates to ensure uniqueness
    test_lat = 1.3000 + random.random() * 0.1  # Singapore latitude range
    test_lng = 103.8000 + random.random() * 0.1  # Singapore longitude range
    
    test_restaurant = Restaurant(
        name="Test Coordinate Duplicate Restaurant",
        address="123 Test Street, Singapore",
        rating=4.5,
        review_count=25,
        is_vegan=True,
        latitude=test_lat,
        longitude=test_lng,
        scraped_at=datetime.now()
    )
    
    print("Inserting test restaurant at coordinates ({}, {})...".format(test_lat, test_lng))
    success, inserted_count, skipped_count = db_manager.insert_restaurants([test_restaurant], skip_duplicates=False)
    
    if success:
        print("✅ First insertion: {} inserted, {} skipped".format(inserted_count, skipped_count))
        
        # Try to insert the same restaurant again
        print("Attempting to insert duplicate...")
        success2, inserted_count2, skipped_count2 = db_manager.insert_restaurants([test_restaurant], skip_duplicates=False)
        
        if success2:
            print("✅ Second insertion: {} inserted, {} skipped".format(inserted_count2, skipped_count2))
            if inserted_count2 == 0:
                print("✅ Duplicate handling working correctly!")
            else:
                print("❌ Duplicate was inserted - constraint not working")
        else:
            print("❌ Second insertion failed")
    else:
        print("❌ First insertion failed")

def check_database_status():
    """Check current database status"""
    print("\n=== Database Status Check ===")
    
    load_dotenv()
    
    db_manager = DatabaseManager()
    if not db_manager.supabase:
        print("❌ No database connection")
        return
    
    try:
        # Check total count
        result = db_manager.supabase.table('restaurants').select('id', count='exact').execute()
        print("Total restaurants in database: {}".format(result.count))
        
        # Check for restaurants with coordinates
        result = db_manager.supabase.table('restaurants').select('name, latitude, longitude').not_.is_('latitude', 'null').not_.is_('longitude', 'null').limit(5).execute()
        print("Restaurants with coordinates: {}".format(len(result.data)))
        
        if result.data:
            print("Sample restaurants with coordinates:")
            for r in result.data:
                print("  {}: lat={}, lng={}".format(r.get('name'), r.get('latitude'), r.get('longitude')))
        
        # Check for duplicates
        result = db_manager.supabase.table('restaurants').select('name').execute()
        names = [r['name'] for r in result.data]
        unique_names = set(names)
        duplicates = len(names) - len(unique_names)
        print("Total records: {}".format(len(names)))
        print("Unique names: {}".format(len(unique_names)))
        print("Duplicates: {}".format(duplicates))
        
    except Exception as e:
        print("Error checking database: {}".format(e))

if __name__ == "__main__":
    print("Testing Coordinate Extraction and Duplicate Handling")
    print("=" * 60)
    
    # Check current database status
    check_database_status()
    
    # Test coordinate extraction
    test_coordinate_extraction()
    
    # Test duplicate handling
    test_duplicate_handling()
    
    print("\n" + "=" * 60)
    print("Testing completed!")
