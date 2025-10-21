"""
Progress tracking for image downloading and processing.
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from config import PROGRESS_FILE


class ProgressTracker:
    """Tracks progress of image downloading and processing."""
    
    def __init__(self, progress_file: str = PROGRESS_FILE):
        """Initialize progress tracker."""
        self.progress_file = progress_file
        self.progress_data = self.load_progress()
    
    def load_progress(self) -> Dict[str, Any]:
        """Load progress from file."""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Error loading progress file: {e}")
        
        return {
            'started_at': None,
            'last_updated': None,
            'total_restaurants': 0,
            'processed_restaurants': 0,
            'total_images': 0,
            'processed_images': 0,
            'failed_images': 0,
            'restaurant_progress': {},
            'errors': []
        }
    
    def save_progress(self) -> bool:
        """Save progress to file."""
        try:
            self.progress_data['last_updated'] = datetime.now().isoformat()
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress_data, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error saving progress: {e}")
            return False
    
    def start_processing(self, total_restaurants: int, total_images: int):
        """Start processing session."""
        self.progress_data.update({
            'started_at': datetime.now().isoformat(),
            'total_restaurants': total_restaurants,
            'total_images': total_images,
            'processed_restaurants': 0,
            'processed_images': 0,
            'failed_images': 0,
            'restaurant_progress': {},
            'errors': []
        })
        self.save_progress()
        print(f"🚀 Started processing {total_restaurants} restaurants with {total_images} images")
    
    def update_restaurant_progress(self, restaurant_id: int, status: str, 
                                 processed: int = 0, failed: int = 0, error: str = None):
        """Update progress for a specific restaurant."""
        self.progress_data['restaurant_progress'][str(restaurant_id)] = {
            'status': status,
            'processed': processed,
            'failed': failed,
            'error': error,
            'updated_at': datetime.now().isoformat()
        }
        
        if status == 'completed':
            self.progress_data['processed_restaurants'] += 1
        
        self.progress_data['processed_images'] += processed
        self.progress_data['failed_images'] += failed
        
        if error:
            self.progress_data['errors'].append({
                'restaurant_id': restaurant_id,
                'error': error,
                'timestamp': datetime.now().isoformat()
            })
        
        self.save_progress()
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get current progress summary."""
        total_restaurants = self.progress_data.get('total_restaurants', 0)
        processed_restaurants = self.progress_data.get('processed_restaurants', 0)
        total_images = self.progress_data.get('total_images', 0)
        processed_images = self.progress_data.get('processed_images', 0)
        failed_images = self.progress_data.get('failed_images', 0)
        
        restaurant_progress = (processed_restaurants / total_restaurants * 100) if total_restaurants > 0 else 0
        image_progress = (processed_images / total_images * 100) if total_images > 0 else 0
        
        return {
            'restaurant_progress': {
                'processed': processed_restaurants,
                'total': total_restaurants,
                'percentage': round(restaurant_progress, 2)
            },
            'image_progress': {
                'processed': processed_images,
                'total': total_images,
                'percentage': round(image_progress, 2)
            },
            'failed_images': failed_images,
            'errors': len(self.progress_data.get('errors', [])),
            'started_at': self.progress_data.get('started_at'),
            'last_updated': self.progress_data.get('last_updated')
        }
    
    def get_restaurant_status(self, restaurant_id: int) -> Optional[Dict[str, Any]]:
        """Get status for a specific restaurant."""
        return self.progress_data.get('restaurant_progress', {}).get(str(restaurant_id))
    
    def is_restaurant_processed(self, restaurant_id: int) -> bool:
        """Check if restaurant has been processed."""
        status = self.get_restaurant_status(restaurant_id)
        return status and status.get('status') == 'completed'
    
    def get_failed_restaurants(self) -> List[int]:
        """Get list of restaurants that failed processing."""
        failed = []
        for restaurant_id, status in self.progress_data.get('restaurant_progress', {}).items():
            if status.get('status') == 'failed':
                failed.append(int(restaurant_id))
        return failed
    
    def reset_progress(self):
        """Reset all progress."""
        self.progress_data = {
            'started_at': None,
            'last_updated': None,
            'total_restaurants': 0,
            'processed_restaurants': 0,
            'total_images': 0,
            'processed_images': 0,
            'failed_images': 0,
            'restaurant_progress': {},
            'errors': []
        }
        self.save_progress()
        print("🔄 Progress reset")
    
    def print_progress(self):
        """Print current progress to console."""
        summary = self.get_progress_summary()
        
        print("\n" + "="*50)
        print("📊 IMAGE PROCESSING PROGRESS")
        print("="*50)
        print(f"🏪 Restaurants: {summary['restaurant_progress']['processed']}/{summary['restaurant_progress']['total']} ({summary['restaurant_progress']['percentage']}%)")
        print(f"🖼️  Images: {summary['image_progress']['processed']}/{summary['image_progress']['total']} ({summary['image_progress']['percentage']}%)")
        print(f"❌ Failed Images: {summary['failed_images']}")
        print(f"⚠️  Errors: {summary['errors']}")
        
        if summary['started_at']:
            print(f"🚀 Started: {summary['started_at']}")
        if summary['last_updated']:
            print(f"🕒 Last Updated: {summary['last_updated']}")
        print("="*50)
