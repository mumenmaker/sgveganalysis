#!/usr/bin/env python3
"""
Example usage of the HappyCow scraper and database operations
"""

import logging
from database import DatabaseManager
from happycow_scraper import HappyCowScraper

def example_scrape_and_store():
    """Example: Scrape restaurants and store in database"""
    print("=== HappyCow Scraper Example ===\n")
    
    # Initialize components
    scraper = HappyCowScraper()
    db_manager = DatabaseManager()
    
    # Check database connection
    if not db_manager.supabase:
        print("❌ Database connection failed. Please check your Supabase credentials.")
        return
    
    print("✅ Database connection successful")
    
    # Scrape restaurants (this might take a while)
    print("🔄 Scraping restaurants from HappyCow...")
    restaurants = scraper.scrape_singapore_restaurants()
    
    if not restaurants:
        print("❌ No restaurants found")
        return
    
    print(f"✅ Found {len(restaurants)} restaurants")
    
    # Store in database
    print("🔄 Storing restaurants in database...")
    if db_manager.insert_restaurants(restaurants):
        print("✅ Successfully stored all restaurants")
    else:
        print("❌ Failed to store restaurants")
        return
    
    # Show some statistics
    vegan_count = sum(1 for r in restaurants if r.is_vegan)
    vegetarian_count = sum(1 for r in restaurants if r.is_vegetarian)
    veg_options_count = sum(1 for r in restaurants if r.has_veg_options)
    
    print(f"\n📊 Statistics:")
    print(f"   Total restaurants: {len(restaurants)}")
    print(f"   Vegan restaurants: {vegan_count}")
    print(f"   Vegetarian restaurants: {vegetarian_count}")
    print(f"   Restaurants with veg options: {veg_options_count}")

def example_query_database():
    """Example: Query the database for different types of restaurants"""
    print("\n=== Database Query Examples ===\n")
    
    db_manager = DatabaseManager()
    
    if not db_manager.supabase:
        print("❌ Database connection failed")
        return
    
    # Get all restaurants
    print("🔄 Getting all restaurants...")
    all_restaurants = db_manager.get_restaurants(limit=10)
    print(f"✅ Found {len(all_restaurants)} restaurants")
    
    # Get vegan restaurants
    print("\n🔄 Getting vegan restaurants...")
    vegan_restaurants = db_manager.get_vegan_restaurants(limit=5)
    print(f"✅ Found {len(vegan_restaurants)} vegan restaurants")
    
    for restaurant in vegan_restaurants[:3]:  # Show first 3
        print(f"   - {restaurant['name']} (Rating: {restaurant.get('rating', 'N/A')})")
    
    # Search for specific restaurants
    print("\n🔄 Searching for 'vegan' restaurants...")
    search_results = db_manager.search_restaurants("vegan", limit=5)
    print(f"✅ Found {len(search_results)} restaurants matching 'vegan'")
    
    # Get restaurants near a location (requires PostGIS)
    print("\n🔄 Getting restaurants near Marina Bay...")
    try:
        nearby_restaurants = db_manager.get_restaurants_by_location(
            lat=1.2833, lng=103.8607, radius_km=2.0
        )
        print(f"✅ Found {len(nearby_restaurants)} restaurants near Marina Bay")
        
        for restaurant in nearby_restaurants[:3]:
            distance = restaurant.get('distance_km', 'N/A')
            print(f"   - {restaurant['name']} ({distance:.2f} km away)")
    except Exception as e:
        print(f"⚠️  Location-based search failed (PostGIS might not be enabled): {e}")

def example_restaurant_details():
    """Example: Show detailed information about a restaurant"""
    print("\n=== Restaurant Details Example ===\n")
    
    db_manager = DatabaseManager()
    
    if not db_manager.supabase:
        print("❌ Database connection failed")
        return
    
    # Get a restaurant with details
    restaurants = db_manager.get_restaurants(limit=1)
    
    if not restaurants:
        print("❌ No restaurants found in database")
        return
    
    restaurant = restaurants[0]
    
    print(f"🏪 Restaurant: {restaurant['name']}")
    print(f"📍 Address: {restaurant.get('address', 'N/A')}")
    print(f"📞 Phone: {restaurant.get('phone', 'N/A')}")
    print(f"🌐 Website: {restaurant.get('website', 'N/A')}")
    print(f"🍽️  Cuisine: {restaurant.get('cuisine_type', 'N/A')}")
    print(f"💰 Price Range: {restaurant.get('price_range', 'N/A')}")
    print(f"⭐ Rating: {restaurant.get('rating', 'N/A')}")
    print(f"📝 Reviews: {restaurant.get('review_count', 'N/A')}")
    print(f"🌱 Type: ", end="")
    
    if restaurant.get('is_vegan'):
        print("Vegan")
    elif restaurant.get('is_vegetarian'):
        print("Vegetarian")
    elif restaurant.get('has_veg_options'):
        print("Veg-Friendly")
    else:
        print("Regular")
    
    print(f"🕒 Hours: {restaurant.get('hours', 'N/A')}")
    print(f"🔗 HappyCow URL: {restaurant.get('happycow_url', 'N/A')}")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    print("HappyCow Singapore Restaurant Scraper - Example Usage")
    print("=" * 60)
    
    # Run examples
    try:
        # Uncomment the line below to run the full scraper
        # example_scrape_and_store()
        
        example_query_database()
        example_restaurant_details()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Example interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        logging.exception("Full error details:")
