#!/usr/bin/env python3
"""
Test script to verify the image downloader setup.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from image_downloader import ImageDownloader

def test_setup():
    """Test the basic setup."""
    print("🧪 Testing Image Downloader Setup")
    print("=" * 40)
    
    # Check environment variables
    print("1. Checking environment variables...")
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if supabase_url and supabase_key:
        print("   ✅ SUPABASE_URL: SET")
        print("   ✅ SUPABASE_KEY: SET")
    else:
        print("   ❌ Missing environment variables")
        return False
    
    # Initialize downloader
    print("\n2. Initializing downloader...")
    try:
        downloader = ImageDownloader()
        print("   ✅ Downloader initialized")
    except Exception as e:
        print(f"   ❌ Failed to initialize: {e}")
        return False
    
    # Test setup
    print("\n3. Testing setup...")
    try:
        if downloader.setup():
            print("   ✅ Setup successful")
        else:
            print("   ❌ Setup failed")
            return False
    except Exception as e:
        print(f"   ❌ Setup error: {e}")
        return False
    
    # Test database connection
    print("\n4. Testing database connection...")
    try:
        restaurants = downloader.database_manager.get_restaurants_with_images(limit=1)
        print(f"   ✅ Database connected - found {len(restaurants)} restaurants with images")
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False
    
    # Test storage access
    print("\n5. Testing storage access...")
    try:
        stats = downloader.get_storage_stats()
        print(f"   ✅ Storage accessible - {stats.get('total_files', 0)} files")
    except Exception as e:
        print(f"   ❌ Storage error: {e}")
        return False
    
    print("\n🎉 All tests passed! The image downloader is ready to use.")
    return True

if __name__ == "__main__":
    success = test_setup()
    sys.exit(0 if success else 1)
