#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to test duplicate detection logic
"""
import sys
import os
import logging

# Add the scraper directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from models import Restaurant
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_duplicate_detection():
    """Test the duplicate detection logic"""
    print("🔍 Testing Duplicate Detection Logic")
    print("=" * 50)
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    if not db_manager.supabase:
        print("❌ Failed to connect to database")
        return
    
    print("✅ Connected to database")
    
    # Create a test restaurant
    test_restaurant = Restaurant(
        name="Test Restaurant",
        address="123 Test Street",
        latitude=1.307464,
        longitude=103.853439,
        is_vegan=True,
        is_vegetarian=False,
        has_veg_options=True,
        scraped_at=datetime.now()
    )
    
    print(f"\n📝 Test Restaurant:")
    print(f"   Name: {test_restaurant.name}")
    print(f"   Address: {test_restaurant.address}")
    print(f"   Coordinates: ({test_restaurant.latitude}, {test_restaurant.longitude})")
    
    # Test 1: Check if restaurant exists (should be False for empty database)
    print(f"\n🔍 Test 1: Checking if restaurant exists in empty database...")
    exists = db_manager.check_restaurant_exists(
        test_restaurant.name,
        test_restaurant.address,
        test_restaurant.latitude,
        test_restaurant.longitude
    )
    print(f"   Result: {exists} (should be False)")
    
    # Test 2: Insert the restaurant
    print(f"\n📥 Test 2: Inserting test restaurant...")
    success, inserted_count, skipped_count = db_manager.insert_restaurants([test_restaurant], skip_duplicates=True)
    print(f"   Success: {success}")
    print(f"   Inserted: {inserted_count}")
    print(f"   Skipped: {skipped_count}")
    
    # Test 3: Check if restaurant exists after insertion (should be True)
    print(f"\n🔍 Test 3: Checking if restaurant exists after insertion...")
    exists = db_manager.check_restaurant_exists(
        test_restaurant.name,
        test_restaurant.address,
        test_restaurant.latitude,
        test_restaurant.longitude
    )
    print(f"   Result: {exists} (should be True)")
    
    # Test 4: Try to insert the same restaurant again
    print(f"\n📥 Test 4: Trying to insert the same restaurant again...")
    success, inserted_count, skipped_count = db_manager.insert_restaurants([test_restaurant], skip_duplicates=True)
    print(f"   Success: {success}")
    print(f"   Inserted: {inserted_count}")
    print(f"   Skipped: {skipped_count}")
    
    # Test 5: Check with slightly different coordinates
    print(f"\n🔍 Test 5: Checking with slightly different coordinates...")
    test_restaurant2 = Restaurant(
        name="Test Restaurant 2",
        address="456 Test Avenue",
        latitude=1.307465,  # Slightly different
        longitude=103.853440,  # Slightly different
        is_vegan=False,
        is_vegetarian=True,
        has_veg_options=True,
        scraped_at=datetime.now()
    )
    
    exists = db_manager.check_restaurant_exists(
        test_restaurant2.name,
        test_restaurant2.address,
        test_restaurant2.latitude,
        test_restaurant2.longitude
    )
    print(f"   Result: {exists} (should be False)")
    
    # Test 6: Insert the second restaurant
    print(f"\n📥 Test 6: Inserting second test restaurant...")
    success, inserted_count, skipped_count = db_manager.insert_restaurants([test_restaurant2], skip_duplicates=True)
    print(f"   Success: {success}")
    print(f"   Inserted: {inserted_count}")
    print(f"   Skipped: {skipped_count}")
    
    print(f"\n✅ Duplicate detection test completed!")

if __name__ == "__main__":
    test_duplicate_detection()
