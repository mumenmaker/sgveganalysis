#!/usr/bin/env python3
"""
HappyCow Singapore Restaurant Scraper
Scrapes restaurant data from HappyCow veggiemap and stores it in Supabase database
"""

import logging
import os
import sys
from hcowscraper import VeggiemapScraper
from config import Config

def setup_logging():
    """Setup logging configuration"""
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/scraper.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def test_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    
    try:
        scraper = VeggiemapScraper(enable_database=True)
        if scraper.test_database_connection():
            print("✅ Database connection successful!")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_coordinates_only():
    """Test coordinate extraction only (faster for testing)"""
    print("🗺️ Testing coordinate extraction...")
    
    try:
        scraper = VeggiemapScraper(enable_database=False)
        url = f"{Config.VEGGIEMAP_URL}?" + "&".join([f"{k}={v}" for k, v in Config.SINGAPORE_VEGGIEMAP_PARAMS.items()])
        
        coordinates = scraper.scrape_with_coordinates_only(url)
        
        if coordinates:
            print(f"✅ Found {len(coordinates)} coordinates")
            print("Sample coordinates:")
            for i, coord in enumerate(coordinates[:5], 1):
                print(f"  {i}. Lat: {coord.get('latitude')}, Lng: {coord.get('longitude')}")
            return True
        else:
            print("❌ No coordinates found")
            return False
            
    except Exception as e:
        print(f"❌ Coordinate extraction error: {e}")
        return False

def scrape_restaurants():
    """Scrape restaurants from veggiemap"""
    print("🍽️ Starting restaurant scraping from HappyCow veggiemap...")
    
    try:
        scraper = VeggiemapScraper(enable_database=True)
        
        # Build URL
        url = f"{Config.VEGGIEMAP_URL}?" + "&".join([f"{k}={v}" for k, v in Config.SINGAPORE_VEGGIEMAP_PARAMS.items()])
        print(f"Scraping from: {url}")
        
        # Scrape restaurants with cluster expansion
        restaurants = scraper.scrape_singapore_restaurants(url, use_cluster_expansion=True)
        
        if restaurants:
            print(f"✅ Successfully scraped {len(restaurants)} restaurants")
            
            # Show statistics
            stats = scraper.get_restaurant_statistics()
            if "error" not in stats:
                print(f"📊 Database statistics:")
                print(f"   Total restaurants: {stats['total_restaurants']}")
                print(f"   With coordinates: {stats['with_coordinates']}")
                print(f"   Vegan restaurants: {stats['vegan_restaurants']}")
                print(f"   Coordinate coverage: {stats['coordinate_coverage']:.1f}%")
            
            return True
        else:
            print("❌ No restaurants found")
            return False
            
    except Exception as e:
        print(f"❌ Scraping error: {e}")
        return False

def clear_database():
    """Clear database records and logs"""
    print("🗑️ Clearing database records and logs...")
    
    try:
        scraper = VeggiemapScraper(enable_database=True)
        
        if scraper.db_manager and scraper.db_manager.supabase:
            # Delete all restaurants
            result = scraper.db_manager.supabase.table('restaurants').delete().neq('id', 0).execute()
            print("✅ Successfully deleted all restaurant records from database")
            
            # Remove log files
            log_dir = 'logs'
            if os.path.exists(log_dir):
                for filename in os.listdir(log_dir):
                    file_path = os.path.join(log_dir, filename)
                    if os.path.isfile(file_path) and (filename.endswith('.log') or filename.endswith('.json')):
                        os.remove(file_path)
                        print(f"   Removed {file_path}")
            
            print("✅ Database cleared successfully!")
            print("   - All restaurant records deleted")
            print("   - Log files removed")
            print("   - Ready for fresh scraping")
            return True
        else:
            print("❌ No database connection available")
            return False
            
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False

def show_help():
    """Show help information"""
    print("HappyCow Singapore Restaurant Scraper")
    print("=====================================")
    print("Commands:")
    print("  python main.py test        - Test database connection")
    print("  python main.py test-coords - Test coordinate extraction only")
    print("  python main.py scrape      - Scrape restaurants from veggiemap")
    print("  python main.py clear-db    - Clear database records and logs")
    print("  python main.py help        - Show this help")
    print("  python main.py             - Run full scraping (default)")
    print("")
    print("The scraper will:")
    print("  - Load the HappyCow veggiemap for Singapore")
    print("  - Zoom in systematically to expand marker clusters")
    print("  - Extract individual restaurant coordinates and data")
    print("  - Save results to your Supabase database")

def main():
    """Main function to run the scraper"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            test_database_connection()
            return
        elif command == "test-coords":
            test_coordinates_only()
            return
        elif command == "scrape":
            scrape_restaurants()
            return
        elif command == "clear-db":
            clear_database()
            return
        elif command == "help":
            show_help()
            return
        else:
            print(f"Unknown command: {command}")
            print("Use 'python main.py help' for available commands")
            return
    
    # Default: run full scraping
    logger.info("Starting HappyCow Singapore Restaurant Scraper")
    print("🚀 Starting HappyCow Singapore Restaurant Scraper")
    print("=" * 60)
    
    try:
        success = scrape_restaurants()
        if success:
            print("\n🎉 Scraping completed successfully!")
            print("Check your Supabase database for the results.")
        else:
            print("\n❌ Scraping failed")
            print("Check the logs for more details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        print("\n⏹️ Scraping interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()