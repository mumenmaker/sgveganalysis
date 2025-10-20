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

def scrape_restaurants(batch_size: int = None, resume_session: str = None):
    """Scrape restaurants from veggiemap"""
    print("🍽️ Starting restaurant scraping from HappyCow veggiemap...")
    
    try:
        # Validate batch size
        if batch_size:
            if batch_size < Config.MIN_BATCH_SIZE or batch_size > Config.MAX_BATCH_SIZE:
                print(f"❌ Batch size must be between {Config.MIN_BATCH_SIZE} and {Config.MAX_BATCH_SIZE}")
                return False
            print(f"📦 Using batch size: {batch_size}")
        else:
            batch_size = Config.DEFAULT_BATCH_SIZE
            print(f"📦 Using default batch size: {batch_size}")
        
        scraper = VeggiemapScraper(enable_database=True, batch_size=batch_size)
        
        # Build URL
        url = f"{Config.VEGGIEMAP_URL}?" + "&".join([f"{k}={v}" for k, v in Config.SINGAPORE_VEGGIEMAP_PARAMS.items()])
        print(f"Scraping from: {url}")
        
        # Scrape restaurants with cluster expansion
        restaurants = scraper.scrape_singapore_restaurants(url, use_cluster_expansion=True, resume_session=resume_session)
        
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

def list_sessions():
    """List available scraping sessions"""
    print("📋 Listing available scraping sessions...")
    
    try:
        scraper = VeggiemapScraper(enable_database=True)
        
        if scraper.db_manager and scraper.db_manager.supabase:
            from hcowscraper.batch_progress_tracker import BatchProgressTracker
            tracker = BatchProgressTracker(scraper.db_manager)
            sessions = tracker.get_available_sessions()
            
            if sessions:
                print(f"Found {len(sessions)} sessions:")
                for session in sessions:
                    status = "✅ Completed" if session['is_completed'] else "🔄 In Progress"
                    print(f"  {session['session_id'][:8]}... - {status} - {session['processed_restaurants']}/{session['total_restaurants']} restaurants")
                return True
            else:
                print("No sessions found")
                return True
        else:
            print("❌ No database connection available")
            return False
            
    except Exception as e:
        print(f"❌ Error listing sessions: {e}")
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
            
            # Clear progress tracking
            result = scraper.db_manager.supabase.table('scraping_progress').delete().neq('id', 0).execute()
            print("✅ Cleared all progress tracking records")
            
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
            print("   - All progress tracking cleared")
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
    print("  python main.py test                    - Test database connection")
    print("  python main.py test-coords            - Test coordinate extraction only")
    print("  python main.py scrape                 - Scrape restaurants from veggiemap")
    print("  python main.py scrape --batch-size N  - Scrape with custom batch size")
    print("  python main.py scrape --resume SESSION - Resume interrupted scraping session")
    print("  python main.py list-sessions          - List available scraping sessions")
    print("  python main.py clear-db               - Clear database records and logs")
    print("  python main.py help                   - Show this help")
    print("  python main.py                        - Run full scraping (default)")
    print("")
    print("Batch Processing:")
    print(f"  - Default batch size: {Config.DEFAULT_BATCH_SIZE}")
    print(f"  - Batch size range: {Config.MIN_BATCH_SIZE}-{Config.MAX_BATCH_SIZE}")
    print("  - Progress is saved after each batch")
    print("  - Interrupted scrapes can be resumed")
    print("")
    print("The scraper will:")
    print("  - Load the HappyCow veggiemap for Singapore")
    print("  - Zoom in systematically to expand marker clusters")
    print("  - Extract individual restaurant coordinates and data")
    print("  - Process restaurants in batches for better reliability")
    print("  - Save results to your Supabase database with progress tracking")

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
            # Parse scrape arguments
            batch_size = None
            resume_session = None
            
            i = 2
            while i < len(sys.argv):
                arg = sys.argv[i]
                if arg == "--batch-size" and i + 1 < len(sys.argv):
                    try:
                        batch_size = int(sys.argv[i + 1])
                        i += 2
                    except ValueError:
                        print("❌ Invalid batch size. Must be a number.")
                        return
                elif arg == "--resume" and i + 1 < len(sys.argv):
                    resume_session = sys.argv[i + 1]
                    i += 2
                else:
                    print(f"❌ Unknown argument: {arg}")
                    print("Use 'python main.py help' for available options")
                    return
            
            scrape_restaurants(batch_size=batch_size, resume_session=resume_session)
            return
        elif command == "list-sessions":
            list_sessions()
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