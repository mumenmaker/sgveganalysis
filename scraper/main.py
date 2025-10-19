#!/usr/bin/env python3
"""
HappyCow Singapore Restaurant Scraper
Scrapes restaurant data from HappyCow and stores it in Supabase database
"""

import logging
import os
import sys
from typing import List
from happycow_scraper import HappyCowScraper
from database import DatabaseManager
from models import Restaurant

def setup_logging():
    """Setup logging configuration"""
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/scraper.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main function to run the scraper"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Add signal handler for graceful shutdown
    import signal
    def signal_handler(sig, frame):
        logger.info("Received interrupt signal. Saving progress...")
        # The scraper will handle saving progress in its exception handling
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Parse command line arguments
    max_pages = 50  # Default value
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_database_connection()
            return
        elif sys.argv[1] == "clear":
            # Clear progress and start fresh
            setup_logging()
            logger = logging.getLogger(__name__)
            logger.info("Progress cleared. Starting fresh scraping session...")
            from progress_tracker import ProgressTracker
            tracker = ProgressTracker()
            tracker.clear_progress()
            print("✅ Progress cleared successfully!")
            return
        elif sys.argv[1] == "clear-db":
            # Clear database records
            setup_logging()
            logger = logging.getLogger(__name__)
            logger.info("Clearing database records...")

            from database import DatabaseManager
            db_manager = DatabaseManager()

            if db_manager.supabase:
                try:
                    # Delete all restaurants
                    result = db_manager.supabase.table('restaurants').delete().neq('id', 0).execute()
                    logger.info(f"Successfully deleted all restaurant records from database")

                    # Also clear progress
                    from progress_tracker import ProgressTracker
                    tracker = ProgressTracker()
                    tracker.clear_progress()
                    logger.info("Progress tracking also cleared")

                    # Clear log files and progress files
                    import os
                    import glob
                    
                    # Remove log files
                    log_files = [
                        'logs/scraper.log',
                        'logs/scraping_progress.json',
                        'logs/singapore_restaurants.json'
                    ]
                    
                    for log_file in log_files:
                        if os.path.exists(log_file):
                            os.remove(log_file)
                            logger.info(f"Removed {log_file}")
                    
                    # Remove any other log files in logs directory
                    for log_file in glob.glob('logs/*.log'):
                        if os.path.exists(log_file):
                            os.remove(log_file)
                            logger.info(f"Removed {log_file}")
                    
                    logger.info("Log files and progress files cleared")

                    print("✅ Database cleared successfully!")
                    print("   - All restaurant records deleted")
                    print("   - Progress tracking cleared")
                    print("   - Log files removed")
                    print("   - Ready for fresh scraping")

                except Exception as e:
                    logger.error(f"Error clearing database: {e}")
                    print(f"❌ Error clearing database: {e}")
                    sys.exit(1)
            else:
                logger.error("No database connection available")
                print("❌ No database connection available")
                sys.exit(1)
        elif sys.argv[1] == "status":
            # Show current scraping status
            setup_logging()
            logger = logging.getLogger(__name__)
            from progress_tracker import ProgressTracker
            tracker = ProgressTracker()
            progress_info = tracker.get_resume_info()
            
            if progress_info['can_resume']:
                print("📊 Current Scraping Status:")
                print(f"   Started: {progress_info['started_at']}")
                print(f"   Last updated: {progress_info['last_updated']}")
                print(f"   Total restaurants found: {progress_info['total_restaurants']}")
                print(f"   Scraped restaurants: {progress_info['scraped_count']}")
                print(f"   Failed restaurants: {progress_info['failed_count']}")
                print(f"   Progress: {tracker.get_progress_summary()}")
            else:
                print("📊 No active scraping session found")
            return
        elif sys.argv[1].isdigit():
            # First argument is max_pages
            max_pages = int(sys.argv[1])
            logger.info(f"Using max_pages: {max_pages}")
        elif len(sys.argv) > 2 and sys.argv[2].isdigit():
            # Second argument is max_pages
            max_pages = int(sys.argv[2])
            logger.info(f"Using max_pages: {max_pages}")
    
    logger.info("Starting HappyCow Singapore Restaurant Scraper")
    logger.info(f"Max pages to scrape: {max_pages}")
    
    try:
        # Initialize scraper and database
        from database import DatabaseManager
        scraper = HappyCowScraper()
        db_manager = DatabaseManager()
        
        # Check database connection
        if not db_manager.supabase:
            logger.error("Database connection failed. Please check your Supabase credentials.")
            return False
        
        # Create tables if they don't exist
        logger.info("Setting up database tables...")
        if not db_manager.create_tables():
            logger.error("Failed to create database tables")
            return False
        
        # Check for resume option
        resume_info = scraper.progress_tracker.get_resume_info() if scraper.progress_tracker else None
        if resume_info and resume_info['can_resume']:
            logger.info("Previous scraping session detected. Resuming...")
            logger.info(f"Progress: {scraper.progress_tracker.get_progress_summary()}")
        
        # Scrape restaurants
        logger.info("Starting to scrape restaurants from HappyCow...")
        restaurants = scraper.scrape_singapore_restaurants(resume=True, max_pages=max_pages)
        
        if not restaurants:
            logger.warning("No new restaurants found. This might be due to:")
            logger.warning("1. All restaurants already scraped (resume mode)")
            logger.warning("2. Website structure changes")
            logger.warning("3. Rate limiting or blocking")
            logger.warning("4. Network issues")
            return False
        
        logger.info(f"Successfully scraped {len(restaurants)} new restaurants")
        
        # Save to JSON file as backup (with duplicate handling)
        scraper.save_to_json(restaurants, 'logs/singapore_restaurants.json', append=True)
        
        # Display summary
        logger.info("=== SCRAPING COMPLETE ===")
        logger.info(f"Total restaurants scraped: {len(restaurants)}")
        
        # Show some statistics
        vegan_count = sum(1 for r in restaurants if r.is_vegan)
        vegetarian_count = sum(1 for r in restaurants if r.is_vegetarian)
        veg_options_count = sum(1 for r in restaurants if r.has_veg_options)
        
        logger.info(f"Vegan restaurants: {vegan_count}")
        logger.info(f"Vegetarian restaurants: {vegetarian_count}")
        logger.info(f"Restaurants with veg options: {veg_options_count}")
        
        return True
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def test_database_connection():
    """Test database connection and basic operations"""
    logger = logging.getLogger(__name__)
    
    try:
        db_manager = DatabaseManager()
        
        if not db_manager.supabase:
            logger.error("Database connection failed")
            return False
        
        # Test basic query
        restaurants = db_manager.get_restaurants(limit=5)
        logger.info(f"Database connection successful. Found {len(restaurants)} restaurants in database")
        
        return True
        
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
