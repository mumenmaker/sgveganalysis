#!/usr/bin/env python3
"""
Test script to insert a sample restaurant into the database
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_database_insert():
    """Test inserting a sample restaurant into the database"""
    print("=== Database Insert Test ===\n")
    
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        print("❌ Missing Supabase credentials!")
        print("Please check your .env file for SUPABASE_URL and SUPABASE_KEY")
        return False
    
    try:
        # Create Supabase client
        supabase: Client = create_client(url, key)
        print("✅ Successfully connected to Supabase")
        
        # Test data
        test_restaurant = {
            'name': 'Test Vegan Restaurant',
            'address': '123 Test Street, Singapore',
            'phone': '+65 1234 5678',
            'website': 'https://test-restaurant.com',
            'description': 'A test vegan restaurant for database testing',
            'cuisine_type': 'Vegan',
            'price_range': '$$',
            'rating': 4.5,
            'review_count': 25,
            'is_vegan': True,
            'is_vegetarian': False,
            'has_veg_options': False,
            'latitude': 1.3521,
            'longitude': 103.8198,
            'features': ['WiFi', 'Outdoor Seating'],
            'hours': 'Mon-Sun: 9:00 AM - 10:00 PM',
            'happycow_url': 'https://www.happycow.net/reviews/test-restaurant',
            'scraped_at': datetime.now().isoformat()
        }
        
        print("Inserting test restaurant...")
        result = supabase.table('restaurants').insert(test_restaurant).execute()
        
        if result.data:
            print("✅ Successfully inserted test restaurant!")
            print(f"Restaurant ID: {result.data[0].get('id')}")
            print(f"Name: {result.data[0].get('name')}")
            print(f"Rating: {result.data[0].get('rating')}")
            print(f"Is Vegan: {result.data[0].get('is_vegan')}")
            
            # Clean up test data
            print("\nCleaning up test data...")
            supabase.table('restaurants').delete().eq('name', 'Test Vegan Restaurant').execute()
            print("✅ Test data cleaned up")
            
            return True
        else:
            print("❌ Failed to insert test restaurant")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_existing_restaurants():
    """Check if there are any existing restaurants in the database"""
    print("\n=== Checking Existing Restaurants ===")
    
    try:
        load_dotenv()
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        supabase: Client = create_client(url, key)
        
        # Get all restaurants
        result = supabase.table('restaurants').select('*').execute()
        
        print(f"✅ Found {len(result.data)} restaurants in database")
        
        if result.data:
            print("\nSample restaurants:")
            for i, restaurant in enumerate(result.data[:5]):
                print(f"  {i+1}. {restaurant.get('name', 'Unknown')}")
                print(f"     Rating: {restaurant.get('rating', 'N/A')}")
                print(f"     Is Vegan: {restaurant.get('is_vegan', 'N/A')}")
                print(f"     Address: {restaurant.get('address', 'N/A')}")
                print()
        else:
            print("No restaurants found in database")
            
    except Exception as e:
        print(f"❌ Error checking existing restaurants: {e}")

if __name__ == "__main__":
    print("Database Insert Test")
    print("=" * 50)
    
    # Test database insert
    if test_database_insert():
        print("\n✅ Database insert test completed successfully")
        
        # Check existing restaurants
        check_existing_restaurants()
        
    else:
        print("\n❌ Database insert test failed")
        print("\nPlease make sure:")
        print("1. You have created the tables in Supabase (run database/create_tables.sql)")
        print("2. Your .env file has correct SUPABASE_URL and SUPABASE_KEY")
        print("3. The tables are accessible from your Supabase project")
        sys.exit(1)
