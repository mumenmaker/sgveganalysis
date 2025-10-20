#!/usr/bin/env python3
"""
HappyCow Singapore Restaurant Scraper
Scrapes restaurant data from HappyCow's searchmap by sectors and stores it in Supabase
"""

import sys
import os
import logging
import time
from typing import List, Optional

# Add the scraper directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from database import DatabaseManager
from models import Restaurant
from sectorscraper import HappyCowSectorScraper, SingaporeSectorGrid, ScrapingSessionManager
from sectorscraper import ReviewsEnhancer

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
        if db_manager.test_connection():
            print("✅ Database connection successful!")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_sector_scraping():
    """Test sector scraping with a few sectors"""
    print("🗺️ Testing sector scraping...")
    
    try:
        scraper = HappyCowSectorScraper(headless=True, delay_between_sectors=1)
        
        # Test with first 3 sectors
        restaurants = scraper.scrape_all_sectors(start_sector=0, max_sectors=3)
        
        if restaurants:
            print(f"✅ Found {len(restaurants)} restaurants from 3 sectors")
            print("Sample restaurants:")
            for i, restaurant in enumerate(restaurants[:3], 1):
                print(f"  {i}. {restaurant.get('name', 'Unknown')} - ({restaurant.get('latitude')}, {restaurant.get('longitude')})")
            return True
        else:
            print("❌ No restaurants found")
            return False
            
    except Exception as e:
        print(f"❌ Sector scraping error: {e}")
        return False
    finally:
        scraper.page_loader.close_driver()

def scrape_restaurants(start_sector: int = 0, max_sectors: Optional[int] = None, region: Optional[str] = None):
    """Scrape restaurants from all sectors with immediate database saving"""
    print("🍽️ Starting comprehensive restaurant scraping...")
    print("💾 Restaurants will be saved to database after each sector")
    
    try:
        scraper = HappyCowSectorScraper(headless=True, delay_between_sectors=2)
        
        if region:
            print(f"Scraping restaurants in region: {region}")
            restaurants = scraper.scrape_sectors_by_region(region, save_to_db=True)
        else:
            print(f"Scraping restaurants from sectors {start_sector + 1} onwards")
            if max_sectors:
                print(f"Maximum sectors to process: {max_sectors}")
            restaurants = scraper.scrape_all_sectors(start_sector=start_sector, max_sectors=max_sectors, save_to_db=True)
        
        if restaurants:
            print(f"✅ Successfully scraped {len(restaurants)} restaurants")
            print("✅ All restaurants have been saved to database during scraping")
            
            # Show statistics
            show_scraping_statistics(restaurants)
            return True
        else:
            print("❌ No restaurants found")
            return False
            
    except Exception as e:
        print(f"❌ Scraping error: {e}")
        return False
    finally:
        scraper.page_loader.close_driver()

def save_restaurants_to_database(restaurants: List[dict]) -> bool:
    """Save restaurants to Supabase database"""
    try:
        db_manager = DatabaseManager()
        
        if not db_manager.supabase:
            print("❌ No database connection available")
            return False
        
        # Convert to Restaurant models
        restaurant_models = []
        for restaurant_data in restaurants:
            try:
                restaurant = Restaurant(
                    name=restaurant_data.get('name', 'Unknown Restaurant'),
                    address=restaurant_data.get('address', 'Address not available'),
                    latitude=restaurant_data.get('latitude'),
                    longitude=restaurant_data.get('longitude'),
                    phone=restaurant_data.get('phone', ''),
                    website=restaurant_data.get('website', ''),
                    rating=restaurant_data.get('rating', 0.0),
                    price_range=restaurant_data.get('price_range', ''),
                    cuisine_type=restaurant_data.get('cuisine_type', ''),
                    hours=restaurant_data.get('hours', ''),
                    description=restaurant_data.get('description', ''),
                    is_vegan=restaurant_data.get('is_vegan', False),
                    is_vegetarian=restaurant_data.get('is_vegetarian', False),
                    has_veg_options=restaurant_data.get('has_veg_options', False)
                )
                restaurant_models.append(restaurant)
            except Exception as e:
                print(f"Warning: Skipping invalid restaurant data: {e}")
                continue
        
        if not restaurant_models:
            print("❌ No valid restaurant models to save")
            return False
        
        # Insert restaurants in batches
        batch_size = 20
        total_inserted = 0
        total_skipped = 0
        
        for i in range(0, len(restaurant_models), batch_size):
            batch = restaurant_models[i:i + batch_size]
            success, inserted, skipped = db_manager.insert_restaurants(batch)
            
            if success:
                total_inserted += inserted
                total_skipped += skipped
                print(f"Batch {i//batch_size + 1}: {inserted} inserted, {skipped} skipped")
            else:
                print(f"❌ Failed to insert batch {i//batch_size + 1}")
                return False
        
        print(f"✅ Database insertion completed: {total_inserted} inserted, {total_skipped} skipped")
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def show_scraping_statistics(restaurants: List[dict]):
    """Show statistics about scraped restaurants"""
    if not restaurants:
        return
    
    total = len(restaurants)
    with_coords = sum(1 for r in restaurants if r.get('latitude') and r.get('longitude'))
    vegan_count = sum(1 for r in restaurants if r.get('is_vegan'))
    vegetarian_count = sum(1 for r in restaurants if r.get('is_vegetarian'))
    veg_options_count = sum(1 for r in restaurants if r.get('has_veg_options'))
    
    print(f"\n📊 Scraping Statistics:")
    print(f"   Total restaurants: {total}")
    print(f"   With coordinates: {with_coords} ({with_coords/total*100:.1f}%)")
    print(f"   Vegan restaurants: {vegan_count}")
    print(f"   Vegetarian restaurants: {vegetarian_count}")
    print(f"   Veg-friendly restaurants: {veg_options_count}")

def enhance_restaurants(limit: int = None):
    """Enhance existing rows by scraping their cow_reviews pages for missing fields"""
    print("🧩 Enhancing existing restaurant rows from cow_reviews pages...")
    try:
        db = DatabaseManager()
        if not db.supabase:
            print("❌ No database connection available")
            return False

        # Use a very large limit if none specified to get all rows
        effective_limit = limit if limit is not None else 10000
        rows = db.get_incomplete_restaurants(limit=effective_limit)
        if not rows:
            print("✅ Nothing to enhance (no rows with missing fields or cow_reviews)")
            return True

        print(f"Found {len(rows)} rows to enhance")
        enhancer = ReviewsEnhancer(headless=True)
        updated_count = 0

        try:
            for r in rows:
                rid = r.get('id')
                url = r.get('cow_reviews')
                missing_fields = r.get('missing_fields', [])
                if not rid or not url:
                    continue
                
                print(f"🔄 Enhancing {r.get('name', 'Unknown')} (missing: {', '.join(missing_fields)})")
                
                details = enhancer.fetch_details(url)
                if not details:
                    print(f"  ❌ Failed to fetch details")
                    continue

                fields = {
                    'phone': details.get('phone') or r.get('phone'),
                    'address': details.get('address') or r.get('address'),
                    'description': details.get('description') or r.get('description'),
                    'category': details.get('category') or r.get('category'),
                    'price_range': details.get('price_range') or r.get('price_range'),
                    'hours': details.get('hours') or r.get('hours'),
                }

                # Optional numeric fields
                if details.get('rating') is not None:
                    fields['rating'] = details['rating']
                if details.get('review_count') is not None:
                    fields['review_count'] = details['review_count']
                # Array features if available
                if details.get('features'):
                    fields['features'] = details['features']
                # Array images if available
                if details.get('images_links'):
                    fields['images_links'] = details['images_links']

                if db.update_restaurant_fields(rid, fields):
                    updated_count += 1
                    print(f"  ✅ Enhanced successfully")
                else:
                    print(f"  ❌ Failed to update database")

        finally:
            enhancer.close()

        print(f"✅ Enhanced {updated_count} row(s)")
        return True

    except Exception as e:
        print(f"❌ Enhance error: {e}")
        return False
def list_sessions():
    """List available scraping sessions"""
    print("📋 Available Scraping Sessions:")
    
    try:
        db_manager = DatabaseManager()
        if not db_manager.supabase:
            print("❌ No database connection available")
            return False
        
        session_manager = ScrapingSessionManager(db_manager)
        sessions = session_manager.get_available_sessions()
        
        if not sessions:
            print("   No sessions found")
            return True
        
        for session in sessions:
            status = "✅ Completed" if session['is_completed'] else "🔄 In Progress"
            print(f"   Session: {session['session_id']}")
            print(f"   Status: {status}")
            print(f"   Started: {session['started_at']}")
            print(f"   Progress: {session['completed_sectors']}/{session['total_sectors']} sectors")
            print(f"   Failed: {session['failed_sectors']} sectors")
            print(f"   Last Updated: {session['last_updated']}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error listing sessions: {e}")
        return False

def resume_session(session_id: str):
    """Resume a specific session"""
    print(f"🔄 Resuming session: {session_id}")
    
    try:
        scraper = HappyCowSectorScraper(headless=True, delay_between_sectors=2)
        
        # Setup session manager
        db_manager = DatabaseManager()
        if not scraper._setup_session_manager(db_manager):
            print("❌ Failed to setup session manager")
            return False
        
        # Resume the session
        if not scraper.resume_session(session_id):
            print(f"❌ Failed to resume session {session_id}")
            return False
        
        # Get session progress
        progress = scraper.get_session_progress()
        if progress:
            print(f"📊 Session Progress:")
            print(f"   Total sectors: {progress['total_sectors']}")
            print(f"   Completed: {progress['completed_sectors']}")
            print(f"   Failed: {progress['failed_sectors']}")
            print(f"   Current sector: {progress['current_sector']}")
            print()
        
        # Continue scraping from where it left off
        restaurants = scraper.scrape_all_sectors(session_id=session_id, save_to_db=True)
        
        if restaurants:
            print(f"✅ Successfully resumed and completed session")
            print(f"📊 Total restaurants: {len(restaurants)}")
            return True
        else:
            print("❌ No restaurants found during resume")
            return False
            
    except Exception as e:
        print(f"❌ Error resuming session: {e}")
        return False
    finally:
        scraper.page_loader.close_driver()

def clear_database(include_sessions: bool = False):
    """Clear database records and logs. Optionally clear session records."""
    print("🗑️ Clearing database records and logs...")
    
    try:
        db_manager = DatabaseManager()
        
        if db_manager.supabase:
            # Delete all restaurants
            result = db_manager.supabase.table('restaurants').delete().neq('id', 0).execute()
            print("✅ Successfully deleted all restaurant records from database")

            # Optionally delete session progress
            if include_sessions:
                try:
                    db_manager.supabase.table('scraping_progress').delete().neq('id', 0).execute()
                    print("✅ Successfully deleted all scraping_progress session records")
                except Exception as e:
                    print(f"❌ Error deleting scraping_progress records: {e}")
            
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
            if include_sessions:
                print("   - All scraping_progress session records deleted")
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
    print("  python main.py test-sectors            - Test sector scraping (3 sectors)")
    print("  python main.py scrape                  - Scrape all 48 sectors")
    print("  python main.py scrape --start N        - Start from sector N")
    print("  python main.py scrape --max N           - Process maximum N sectors")
    print("  python main.py scrape --region REGION  - Scrape specific region")
    print("  python main.py list-sessions          - List available scraping sessions")
    print("  python main.py resume SESSION_ID      - Resume a specific session")
    print("  python main.py clear-db                - Clear restaurants + logs")
    print("  python main.py clear-db --include-sessions  - Also clear scraping_progress sessions")
    print("  python main.py enhance                - Enhance all existing rows via cow_reviews page")
    print("  python main.py enhance --limit N       - Enhance only N rows (default: all rows)")
    print("  python main.py help                   - Show this help")
    print("  python main.py                        - Run full scraping (default)")
    print("")
    print("Regions:")
    print("  central, east, west, north, northeast, south")
    print("")
    print("The scraper will:")
    print("  - Divide Singapore into 48 sectors (6x8 grid)")
    print("  - Scrape each sector for up to 81 restaurants")
    print("  - Extract restaurant data including coordinates")
    print("  - Save results to your Supabase database")
    print("  - Handle duplicates using coordinate-based unique constraints")

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
        elif command == "test-sectors":
            test_sector_scraping()
            return
        elif command == "list-sessions":
            list_sessions()
            return
        elif command == "resume":
            if len(sys.argv) < 3:
                print("❌ Session ID required for resume command")
                print("Use 'python main.py list-sessions' to see available sessions")
                return
            session_id = sys.argv[2]
            resume_session(session_id)
            return
        elif command == "scrape":
            # Parse scrape arguments
            start_sector = 0
            max_sectors = None
            region = None
            
            i = 2
            while i < len(sys.argv):
                arg = sys.argv[i]
                if arg == "--start" and i + 1 < len(sys.argv):
                    try:
                        start_sector = int(sys.argv[i + 1])
                        i += 2
                    except ValueError:
                        print("❌ Invalid start sector. Must be a number.")
                        return
                elif arg == "--max" and i + 1 < len(sys.argv):
                    try:
                        max_sectors = int(sys.argv[i + 1])
                        i += 2
                    except ValueError:
                        print("❌ Invalid max sectors. Must be a number.")
                        return
                elif arg == "--region" and i + 1 < len(sys.argv):
                    region = sys.argv[i + 1]
                    i += 2
                else:
                    print(f"❌ Unknown argument: {arg}")
                    print("Use 'python main.py help' for available options")
                    return
            
            scrape_restaurants(start_sector=start_sector, max_sectors=max_sectors, region=region)
            return
        elif command == "enhance":
            # Parse limit argument
            limit = None
            if len(sys.argv) > 2:
                try:
                    if sys.argv[2] == "--limit" and len(sys.argv) > 3:
                        limit = int(sys.argv[3])
                    elif sys.argv[2].startswith("--limit="):
                        limit = int(sys.argv[2].split("=")[1])
                except ValueError:
                    print("❌ Invalid limit value. Please provide a positive integer.")
                    return
            
            enhance_restaurants(limit=limit)
            return
        elif command == "clear-db":
            # Optional flag: --include-sessions
            include_sessions = False
            if len(sys.argv) > 2 and sys.argv[2] == "--include-sessions":
                include_sessions = True
            clear_database(include_sessions=include_sessions)
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