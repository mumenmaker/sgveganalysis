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
        level=logging.INFO,
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
    
    logger.info("Starting HappyCow Singapore Restaurant Scraper")
    
    try:
        # Initialize scraper and database
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
            logger.warning("No new restaurants found. This might be due to:")
            logger.warning("1. All restaurants already scraped (resume mode)")
            logger.warning("2. Website structure changes")
            logger.warning("3. Rate limiting or blocking")
            logger.warning("4. Network issues")
            return False
        
        logger.info(f"Successfully scraped {len(restaurants)} new restaurants")
        
        # Save to JSON file as backup (with duplicate handling)
        scraper.save_to_json(restaurants, 'logs/singapore_restaurants.json', append=True)
        
        # Insert into database (with duplicate detection)
        logger.info("Inserting restaurants into database...")
        success, inserted_count, skipped_count = db_manager.insert_restaurants(restaurants, skip_duplicates=True)
        
        if success:
            logger.info(f"Database update complete: {inserted_count} new restaurants inserted, {skipped_count} duplicates skipped")
        else:
            logger.error("Failed to insert restaurants into database")
            return False
        
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
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            # Test mode
            setup_logging()
            test_database_connection()
        elif sys.argv[1] == "clear":
            # Clear progress and start fresh
            setup_logging()
            logger = logging.getLogger(__name__)
            from progress_tracker import ProgressTracker
            tracker = ProgressTracker()
            tracker.clear_progress()
            logger.info("Progress cleared. Starting fresh scraping session...")
            success = main()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "status":
            # Show current status
            setup_logging()
            from progress_tracker import ProgressTracker
            tracker = ProgressTracker()
            print(f"Scraping Status: {tracker.get_progress_summary()}")
            resume_info = tracker.get_resume_info()
            if resume_info['can_resume']:
                print(f"Can resume: Yes")
                print(f"Last updated: {resume_info['last_updated']}")
            else:
                print(f"Can resume: No")
        else:
            print("Usage: python main.py [test|clear|status]")
            print("  test   - Test database connection")
            print("  clear  - Clear progress and start fresh")
            print("  status - Show current scraping status")
            sys.exit(1)
    else:
        # Run scraper
        success = main()
        sys.exit(0 if success else 1)
