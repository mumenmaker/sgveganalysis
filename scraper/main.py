#!/usr/bin/env python3
"""
HappyCow Singapore Restaurant Scraper - Clean Version
Ready for new veggiemap implementation
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
        db_manager = DatabaseManager()
        if db_manager.supabase:
            print("✅ Database connection successful!")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def main():
    """Main function to run the scraper"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Parse command line arguments
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

                    # Remove log files
                    log_dir = 'logs'
                    if os.path.exists(log_dir):
                        for filename in os.listdir(log_dir):
                            file_path = os.path.join(log_dir, filename)
                            if os.path.isfile(file_path) and (filename.endswith('.log') or filename.endswith('.json')):
                                os.remove(file_path)
                                logger.info(f"Removed {file_path}")
                    logger.info("Log files and progress files cleared")

                    print("✅ Database cleared successfully!")
                    print("   - All restaurant records deleted")
                    print("   - Progress tracking cleared")
                    print("   - Log files removed")
                    print("   - Ready for fresh scraping")
                    return

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
    
    logger.info("Starting HappyCow Singapore Restaurant Scraper")
    
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
        restaurants = scraper.scrape_singapore_restaurants(resume=True)
        
        if not restaurants:
            logger.warning("No restaurants found. Scraper implementation pending.")
            return False
        
        logger.info(f"Successfully scraped {len(restaurants)} restaurants")
        
        # Save to JSON file as backup
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

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
