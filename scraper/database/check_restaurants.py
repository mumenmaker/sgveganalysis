#!/usr/bin/env python3
"""
Script to check the Supabase restaurants table statistics.
Shows total records, records with coordinates, and sample data.
"""

import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the path so we can import from the scraper
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from database import DatabaseManager

def setup_logging():
    """Setup logging for the script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def check_restaurants_table():
    """Check the restaurants table and display statistics"""
    logger = setup_logging()
    
    try:
        # Initialize database connection
        logger.info("Connecting to Supabase database...")
        db_manager = DatabaseManager()
        
        if not db_manager.supabase:
            logger.error("Failed to connect to Supabase database")
            return False
        
        logger.info("✅ Successfully connected to Supabase database")
        
        # Get total count of restaurants
        logger.info("\n📊 Getting restaurant statistics...")
        total_result = db_manager.supabase.table('restaurants').select('id', count='exact').execute()
        total_count = total_result.count if hasattr(total_result, 'count') else len(total_result.data)
        
        # Get count of restaurants with coordinates
        coord_result = db_manager.supabase.table('restaurants').select('id', count='exact').not_.is_('latitude', 'null').not_.is_('longitude', 'null').execute()
        coord_count = coord_result.count if hasattr(coord_result, 'count') else len(coord_result.data)
        
        # Get count of restaurants without coordinates
        no_coord_result = db_manager.supabase.table('restaurants').select('id', count='exact').is_('latitude', 'null').execute()
        no_coord_count = no_coord_result.count if hasattr(no_coord_result, 'count') else len(no_coord_result.data)
        
        # Display statistics
        print("\n" + "="*60)
        print("🍽️  RESTAURANTS TABLE STATISTICS")
        print("="*60)
        print(f"📈 Total restaurants: {total_count}")
        print(f"📍 With coordinates: {coord_count}")
        print(f"❌ Without coordinates: {no_coord_count}")
        
        if total_count > 0:
            coord_percentage = (coord_count / total_count) * 100
            print(f"📊 Coordinate coverage: {coord_percentage:.1f}%")
        
        # Show sample restaurants with coordinates
        if coord_count > 0:
            print(f"\n🔍 Sample restaurants with coordinates:")
            sample_result = db_manager.supabase.table('restaurants').select('name, latitude, longitude, is_vegan, is_vegetarian').not_.is_('latitude', 'null').not_.is_('longitude', 'null').limit(5).execute()
            
            for i, restaurant in enumerate(sample_result.data, 1):
                vegan_status = "🌱 Vegan" if restaurant.get('is_vegan') else "🥗 Vegetarian" if restaurant.get('is_vegetarian') else "🍽️ Other"
                print(f"  {i}. {restaurant['name']} - {restaurant['latitude']}, {restaurant['longitude']} ({vegan_status})")
        
        # Show sample restaurants without coordinates
        if no_coord_count > 0:
            print(f"\n⚠️  Sample restaurants without coordinates:")
            no_coord_sample = db_manager.supabase.table('restaurants').select('name, latitude, longitude').is_('latitude', 'null').limit(3).execute()
            
            for i, restaurant in enumerate(no_coord_sample.data, 1):
                lat = restaurant.get('latitude')
                lng = restaurant.get('longitude')
                coord_status = f"lat={lat}, lng={lng}" if lat is not None or lng is not None else "No coordinates"
                print(f"  {i}. {restaurant['name']} - {coord_status}")
        
        # Show restaurant type breakdown
        print(f"\n📊 Restaurant type breakdown:")
        
        # Vegan restaurants
        vegan_result = db_manager.supabase.table('restaurants').select('id', count='exact').eq('is_vegan', True).execute()
        vegan_count = vegan_result.count if hasattr(vegan_result, 'count') else len(vegan_result.data)
        
        # Vegetarian restaurants
        vegetarian_result = db_manager.supabase.table('restaurants').select('id', count='exact').eq('is_vegetarian', True).execute()
        vegetarian_count = vegetarian_result.count if hasattr(vegetarian_result, 'count') else len(vegetarian_result.data)
        
        # Restaurants with veg options
        veg_options_result = db_manager.supabase.table('restaurants').select('id', count='exact').eq('has_veg_options', True).execute()
        veg_options_count = veg_options_result.count if hasattr(veg_options_result, 'count') else len(veg_options_result.data)
        
        print(f"  🌱 Vegan restaurants: {vegan_count}")
        print(f"  🥗 Vegetarian restaurants: {vegetarian_count}")
        print(f"  🍽️  Restaurants with veg options: {veg_options_count}")
        
        # Show recent restaurants
        print(f"\n🕒 Most recently scraped restaurants:")
        recent_result = db_manager.supabase.table('restaurants').select('name, scraped_at, latitude, longitude').order('scraped_at', desc=True).limit(3).execute()
        
        for i, restaurant in enumerate(recent_result.data, 1):
            coord_status = "✅" if restaurant.get('latitude') and restaurant.get('longitude') else "❌"
            print(f"  {i}. {restaurant['name']} - {restaurant['scraped_at']} {coord_status}")
        
        print("\n" + "="*60)
        print("✅ Database check completed successfully!")
        print("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking restaurants table: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Checking Supabase Restaurants Table")
    print("="*50)
    
    success = check_restaurants_table()
    
    if success:
        print("\n✅ Check completed successfully!")
    else:
        print("\n❌ Check failed!")
        sys.exit(1)
