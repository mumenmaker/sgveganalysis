#!/usr/bin/env python3
"""
Example demonstrating the resume functionality of the HappyCow scraper
"""

import time
import logging
from progress_tracker import ProgressTracker
from happycow_scraper import HappyCowScraper

def simulate_interrupted_scraping():
    """Simulate an interrupted scraping session"""
    print("=== Simulating Interrupted Scraping ===\n")
    
    # Initialize scraper with progress tracking
    scraper = HappyCowScraper(enable_resume=True)
    
    print("🔄 Starting scraping session...")
    scraper.progress_tracker.start_scraping()
    
    # Simulate scraping some restaurants
    print("🔄 Simulating scraping 3 restaurants...")
    for i in range(3):
        restaurant_name = f"Test Restaurant {i+1}"
        scraper.progress_tracker.add_scraped_restaurant(restaurant_name)
        scraper.progress_tracker.update_progress(i+1, 0)
        print(f"   ✅ Scraped: {restaurant_name}")
        time.sleep(0.5)  # Simulate processing time
    
    print("\n⚠️  Simulating interruption (Ctrl+C)...")
    print("   (In real scenario, this would be an actual interruption)")
    
    # Show current status
    print(f"\n📊 Current Status: {scraper.progress_tracker.get_progress_summary()}")
    resume_info = scraper.progress_tracker.get_resume_info()
    print(f"🔄 Can resume: {resume_info['can_resume']}")
    print(f"📅 Last updated: {resume_info['last_updated']}")

def demonstrate_resume():
    """Demonstrate resuming from previous session"""
    print("\n=== Demonstrating Resume Functionality ===\n")
    
    # Initialize scraper
    scraper = HappyCowScraper(enable_resume=True)
    
    # Check if we can resume
    resume_info = scraper.progress_tracker.get_resume_info()
    
    if resume_info['can_resume']:
        print("✅ Previous session detected - can resume!")
        print(f"📊 Progress: {scraper.progress_tracker.get_progress_summary()}")
        print(f"📅 Started at: {resume_info['started_at']}")
        print(f"📅 Last updated: {resume_info['last_updated']}")
        
        print("\n🔄 Resuming scraping...")
        print("   (In real scenario, this would continue from where it left off)")
        
        # Simulate resuming
        print("🔄 Checking which restaurants were already scraped...")
        for i in range(5):
            restaurant_name = f"Test Restaurant {i+1}"
            if scraper.progress_tracker.is_restaurant_scraped(restaurant_name):
                print(f"   ⏭️  Skipping already scraped: {restaurant_name}")
            else:
                print(f"   🔄 Scraping new restaurant: {restaurant_name}")
                scraper.progress_tracker.add_scraped_restaurant(restaurant_name)
                time.sleep(0.3)
        
        # Mark as completed
        scraper.progress_tracker.mark_completed()
        print("\n✅ Scraping session completed!")
        
    else:
        print("❌ No previous session found - starting fresh")
        print("   (This would start a new scraping session)")

def show_progress_management():
    """Show how to manage progress files"""
    print("\n=== Progress Management ===\n")
    
    tracker = ProgressTracker()
    
    print("📊 Current Status:")
    print(f"   {tracker.get_progress_summary()}")
    
    resume_info = tracker.get_resume_info()
    print(f"\n🔄 Resume Information:")
    print(f"   Can resume: {resume_info['can_resume']}")
    print(f"   Scraped count: {resume_info['scraped_count']}")
    print(f"   Failed count: {resume_info['failed_count']}")
    
    if resume_info['can_resume']:
        print(f"\n📁 Progress file: logs/scraping_progress.json")
        print(f"   (Contains: {len(tracker.progress_data['scraped_restaurant_names'])} restaurant names)")
        
        print(f"\n🛠️  Management options:")
        print(f"   python main.py status  - Check current status")
        print(f"   python main.py clear   - Clear progress and start fresh")
        print(f"   python main.py         - Resume scraping")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    print("HappyCow Scraper - Resume Functionality Demo")
    print("=" * 50)
    
    try:
        # Simulate interrupted scraping
        simulate_interrupted_scraping()
        
        # Demonstrate resume
        demonstrate_resume()
        
        # Show progress management
        show_progress_management()
        
        print("\n" + "=" * 50)
        print("✅ Demo completed!")
        print("\n💡 Key Features Demonstrated:")
        print("   • Progress tracking with checkpoint system")
        print("   • Automatic resume detection")
        print("   • Duplicate prevention")
        print("   • Progress file management")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error in demo: {e}")
        logging.exception("Full error details:")
