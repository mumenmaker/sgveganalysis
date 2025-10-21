"""
Main image downloader script that orchestrates the entire process.
"""

import os
import sys
import time
from typing import List, Dict, Any, Optional
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Add parent directory to path to import scraper modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from image_processor import ImageProcessor
from supabase_storage import SupabaseStorageManager
from database_manager import DatabaseManager
from progress_tracker import ProgressTracker
from config import BATCH_SIZE, RETRY_DELAY, MAX_RETRIES


class ImageDownloader:
    """Main class for downloading and processing restaurant images."""
    
    def __init__(self):
        """Initialize all components."""
        self.image_processor = ImageProcessor()
        self.storage_manager = SupabaseStorageManager()
        self.database_manager = DatabaseManager()
        self.progress_tracker = ProgressTracker()
    
    def setup(self) -> bool:
        """Setup storage bucket and database."""
        print("🔧 Setting up image downloader...")
        
        # Create storage bucket
        if not self.storage_manager.create_bucket_if_not_exists():
            print("❌ Failed to setup storage bucket")
            return False
        
        # Create progress table (optional)
        self.database_manager.create_progress_table()
        
        print("✅ Setup complete")
        return True
    
    def get_restaurants_to_process(self, limit: Optional[int] = None, 
                                 skip_processed: bool = True) -> List[Dict[str, Any]]:
        """Get restaurants that need image processing."""
        restaurants = self.database_manager.get_restaurants_with_images(limit)
        
        if skip_processed:
            # Filter out already processed restaurants
            restaurants = [
                r for r in restaurants 
                if not self.progress_tracker.is_restaurant_processed(r['id'])
            ]
        
        return restaurants
    
    def process_restaurant_images(self, restaurant: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process all images for a single restaurant.
        
        Args:
            restaurant: Restaurant record with images_links
            
        Returns:
            Processing result
        """
        restaurant_id = restaurant['id']
        restaurant_name = restaurant.get('name', f'Restaurant {restaurant_id}')
        image_urls = restaurant.get('images_links', [])
        
        if not image_urls:
            return {
                'success': True,
                'processed': 0,
                'failed': 0,
                'new_urls': [],
                'message': 'No images to process'
            }
        
        print(f"\n🏪 Processing {restaurant_name} (ID: {restaurant_id})")
        print(f"📸 Found {len(image_urls)} images")
        
        new_urls = []
        processed_count = 0
        failed_count = 0
        errors = []
        
        # Backup original URLs
        self.database_manager.backup_original_urls(restaurant_id, image_urls)
        
        for index, original_url in enumerate(image_urls):
            try:
                print(f"  📥 Downloading image {index + 1}/{len(image_urls)}: {original_url}")
                
                # Download image
                image_bytes = self.image_processor.download_image(original_url)
                if not image_bytes:
                    print(f"  ❌ Failed to download image {index + 1}")
                    failed_count += 1
                    errors.append(f"Download failed: {original_url}")
                    continue
                
                # Process image
                processed_bytes = self.image_processor.process_image(image_bytes, original_url)
                if not processed_bytes:
                    print(f"  ❌ Failed to process image {index + 1}")
                    failed_count += 1
                    errors.append(f"Processing failed: {original_url}")
                    continue
                
                # Generate filename
                filename = self.image_processor.generate_filename(original_url, restaurant_id, index)
                
                # Upload to Supabase Storage
                new_url = self.storage_manager.upload_image(processed_bytes, filename)
                if not new_url:
                    print(f"  ❌ Failed to upload image {index + 1}")
                    failed_count += 1
                    errors.append(f"Upload failed: {original_url}")
                    continue
                
                new_urls.append(new_url)
                processed_count += 1
                print(f"  ✅ Processed image {index + 1}: {filename}")
                
                # Small delay to avoid overwhelming the server
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  ❌ Error processing image {index + 1}: {e}")
                failed_count += 1
                errors.append(f"Unexpected error: {e}")
        
        # Update restaurant with new URLs if we processed any images
        if new_urls:
            success = self.database_manager.update_restaurant_images(restaurant_id, new_urls)
            if not success:
                print(f"  ❌ Failed to update database for restaurant {restaurant_id}")
                return {
                    'success': False,
                    'processed': processed_count,
                    'failed': failed_count,
                    'new_urls': new_urls,
                    'message': 'Database update failed',
                    'errors': errors
                }
        
        # Update progress
        status = 'completed' if processed_count > 0 else 'failed'
        self.progress_tracker.update_restaurant_progress(
            restaurant_id, status, processed_count, failed_count, 
            '; '.join(errors) if errors else None
        )
        
        print(f"  📊 Results: {processed_count} processed, {failed_count} failed")
        
        return {
            'success': True,
            'processed': processed_count,
            'failed': failed_count,
            'new_urls': new_urls,
            'message': f'Processed {processed_count} images successfully',
            'errors': errors
        }
    
    def process_all_images(self, limit: Optional[int] = None, 
                          skip_processed: bool = True) -> Dict[str, Any]:
        """
        Process images for all restaurants.
        
        Args:
            limit: Maximum number of restaurants to process
            skip_processed: Skip restaurants that have already been processed
            
        Returns:
            Overall processing results
        """
        print("🚀 Starting image processing for all restaurants...")
        
        # Get restaurants to process
        restaurants = self.get_restaurants_to_process(limit, skip_processed)
        
        if not restaurants:
            print("ℹ️  No restaurants to process")
            return {'success': True, 'message': 'No restaurants to process'}
        
        # Count total images
        total_images = sum(len(r.get('images_links', [])) for r in restaurants)
        
        # Start progress tracking
        self.progress_tracker.start_processing(len(restaurants), total_images)
        
        print(f"📊 Processing {len(restaurants)} restaurants with {total_images} total images")
        
        # Process restaurants in batches
        results = []
        for i in range(0, len(restaurants), BATCH_SIZE):
            batch = restaurants[i:i + BATCH_SIZE]
            
            print(f"\n🔄 Processing batch {i//BATCH_SIZE + 1}/{(len(restaurants) + BATCH_SIZE - 1)//BATCH_SIZE}")
            
            for restaurant in tqdm(batch, desc="Processing restaurants"):
                try:
                    result = self.process_restaurant_images(restaurant)
                    results.append(result)
                    
                    # Print progress
                    self.progress_tracker.print_progress()
                    
                except Exception as e:
                    print(f"❌ Unexpected error processing restaurant {restaurant['id']}: {e}")
                    results.append({
                        'success': False,
                        'processed': 0,
                        'failed': 0,
                        'new_urls': [],
                        'message': f'Unexpected error: {e}'
                    })
            
            # Delay between batches
            if i + BATCH_SIZE < len(restaurants):
                print(f"⏳ Waiting {RETRY_DELAY} seconds before next batch...")
                time.sleep(RETRY_DELAY)
        
        # Final summary
        total_processed = sum(r['processed'] for r in results)
        total_failed = sum(r['failed'] for r in results)
        successful_restaurants = sum(1 for r in results if r['success'])
        
        print(f"\n🎉 Processing complete!")
        print(f"📊 Results:")
        print(f"  🏪 Restaurants: {successful_restaurants}/{len(restaurants)} successful")
        print(f"  🖼️  Images: {total_processed} processed, {total_failed} failed")
        
        return {
            'success': True,
            'total_restaurants': len(restaurants),
            'successful_restaurants': successful_restaurants,
            'total_processed': total_processed,
            'total_failed': total_failed,
            'results': results
        }
    
    def retry_failed_restaurants(self) -> Dict[str, Any]:
        """Retry processing for restaurants that previously failed."""
        failed_restaurant_ids = self.progress_tracker.get_failed_restaurants()
        
        if not failed_restaurant_ids:
            print("ℹ️  No failed restaurants to retry")
            return {'success': True, 'message': 'No failed restaurants to retry'}
        
        print(f"🔄 Retrying {len(failed_restaurant_ids)} failed restaurants...")
        
        results = []
        for restaurant_id in failed_restaurant_ids:
            restaurant = self.database_manager.get_restaurant_by_id(restaurant_id)
            if restaurant:
                result = self.process_restaurant_images(restaurant)
                results.append(result)
        
        return {
            'success': True,
            'retried_restaurants': len(failed_restaurant_ids),
            'results': results
        }
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        return self.storage_manager.get_storage_stats()
    
    def cleanup_failed_images(self) -> bool:
        """Clean up any orphaned images in storage."""
        print("🧹 Cleaning up failed images...")
        # Implementation would depend on your specific needs
        return True


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Download and process restaurant images')
    parser.add_argument('--limit', type=int, help='Limit number of restaurants to process')
    parser.add_argument('--retry-failed', action='store_true', help='Retry failed restaurants')
    parser.add_argument('--skip-processed', action='store_true', default=True, help='Skip already processed restaurants')
    parser.add_argument('--stats', action='store_true', help='Show storage statistics')
    parser.add_argument('--reset-progress', action='store_true', help='Reset progress tracking')
    
    args = parser.parse_args()
    
    # Initialize downloader
    downloader = ImageDownloader()
    
    # Setup
    if not downloader.setup():
        print("❌ Setup failed")
        return 1
    
    # Handle different commands
    if args.reset_progress:
        downloader.progress_tracker.reset_progress()
        print("✅ Progress reset")
        return 0
    
    if args.stats:
        stats = downloader.get_storage_stats()
        print(f"📊 Storage Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        return 0
    
    if args.retry_failed:
        result = downloader.retry_failed_restaurants()
        print(f"🔄 Retry results: {result}")
        return 0
    
    # Process images
    result = downloader.process_all_images(
        limit=args.limit,
        skip_processed=args.skip_processed
    )
    
    print(f"🎉 Final result: {result}")
    return 0


if __name__ == "__main__":
    exit(main())
