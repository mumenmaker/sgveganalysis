import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_database_coordinates():
    """Check if coordinates are stored in the database"""
    logger.info("🔍 Checking database for coordinates...")

    try:
        # Initialize database manager
        db_manager = DatabaseManager()
        
        if not db_manager.supabase:
            logger.error("No database connection available")
            return False
        
        # Query restaurants with coordinates
        result = db_manager.supabase.table('restaurants').select('name, latitude, longitude').execute()
        restaurants = result.data
        
        logger.info(f"Found {len(restaurants)} restaurants in database")
        
        if not restaurants:
            logger.warning("No restaurants found in database")
            return False
        
        # Check how many have coordinates
        restaurants_with_coords = [r for r in restaurants if r.get('latitude') is not None and r.get('longitude') is not None]
        restaurants_without_coords = [r for r in restaurants if r.get('latitude') is None or r.get('longitude') is None]
        
        logger.info(f"Restaurants with coordinates: {len(restaurants_with_coords)}")
        logger.info(f"Restaurants without coordinates: {len(restaurants_without_coords)}")
        
        if restaurants_with_coords:
            logger.info("✅ Some restaurants have coordinates!")
            for i, restaurant in enumerate(restaurants_with_coords[:5]):  # Show first 5
                logger.info(f"  {i+1}. {restaurant['name']}: lat={restaurant['latitude']}, lng={restaurant['longitude']}")
        else:
            logger.warning("❌ No restaurants have coordinates")
            
            # Show a few examples of restaurants without coordinates
            logger.info("Examples of restaurants without coordinates:")
            for i, restaurant in enumerate(restaurants_without_coords[:5]):
                logger.info(f"  {i+1}. {restaurant['name']}: lat={restaurant['latitude']}, lng={restaurant['longitude']}")
        
        return len(restaurants_with_coords) > 0

    except Exception as e:
        logger.error(f"Error checking database coordinates: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Checking Database Coordinates")
    print("=" * 50)
    if check_database_coordinates():
        print("\n✅ Test completed successfully - coordinates found in database")
    else:
        print("\n❌ Test failed - no coordinates found in database")
