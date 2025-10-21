#!/usr/bin/env python3
"""
Convenience script to run the image downloader with common configurations.
"""

import os
import sys
from image_downloader import ImageDownloader


def main():
    """Main function with interactive menu."""
    print("🖼️  Restaurant Image Downloader")
    print("=" * 40)
    
    # Check environment variables
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        print("Please create a .env file in the scraper directory with:")
        print("SUPABASE_URL=your_supabase_url")
        print("SUPABASE_KEY=your_supabase_key")
        return 1
    
    # Initialize downloader
    downloader = ImageDownloader()
    
    # Setup
    print("🔧 Setting up...")
    if not downloader.setup():
        print("❌ Setup failed")
        return 1
    
    # Show menu
    while True:
        print("\n" + "=" * 40)
        print("📋 MENU OPTIONS")
        print("=" * 40)
        print("1. Process all restaurants (with progress tracking)")
        print("2. Process limited restaurants (e.g., first 10)")
        print("3. Retry failed restaurants")
        print("4. Show progress summary")
        print("5. Show storage statistics")
        print("6. Reset progress tracking")
        print("7. Exit")
        print("=" * 40)
        
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == "1":
            print("\n🚀 Processing all restaurants...")
            result = downloader.process_all_images()
            print(f"\n✅ Result: {result}")
            
        elif choice == "2":
            try:
                limit = int(input("Enter number of restaurants to process: "))
                print(f"\n🚀 Processing {limit} restaurants...")
                result = downloader.process_all_images(limit=limit)
                print(f"\n✅ Result: {result}")
            except ValueError:
                print("❌ Invalid number")
                
        elif choice == "3":
            print("\n🔄 Retrying failed restaurants...")
            result = downloader.retry_failed_restaurants()
            print(f"\n✅ Result: {result}")
            
        elif choice == "4":
            print("\n📊 Progress Summary:")
            downloader.progress_tracker.print_progress()
            
        elif choice == "5":
            print("\n📊 Storage Statistics:")
            stats = downloader.get_storage_stats()
            for key, value in stats.items():
                print(f"  {key}: {value}")
                
        elif choice == "6":
            confirm = input("Are you sure you want to reset progress? (y/N): ").strip().lower()
            if confirm == 'y':
                downloader.progress_tracker.reset_progress()
                print("✅ Progress reset")
            else:
                print("❌ Reset cancelled")
                
        elif choice == "7":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-7.")
    
    return 0


if __name__ == "__main__":
    exit(main())
