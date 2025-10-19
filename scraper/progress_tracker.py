import json
import os
from typing import List, Dict, Optional
from datetime import datetime
import logging

class ProgressTracker:
    """Track scraping progress and enable resume functionality"""
    
    def __init__(self, progress_file: str = 'scraping_progress.json'):
        self.progress_file = progress_file
        self.logger = logging.getLogger(__name__)
        self.progress_data = self.load_progress()
    
    def load_progress(self) -> Dict:
        """Load progress from file"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading progress file: {e}")
        return {
            'started_at': None,
            'last_updated': None,
            'total_restaurants': 0,
            'scraped_restaurants': 0,
            'failed_restaurants': 0,
            'completed': False,
            'current_page': 1,
            'scraped_restaurant_names': []
        }
    
    def save_progress(self):
        """Save current progress to file"""
        try:
            self.progress_data['last_updated'] = datetime.now().isoformat()
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving progress: {e}")
    
    def start_scraping(self):
        """Mark scraping as started"""
        self.progress_data['started_at'] = datetime.now().isoformat()
        self.progress_data['completed'] = False
        self.save_progress()
    
    def update_progress(self, scraped_count: int, failed_count: int = 0):
        """Update scraping progress"""
        self.progress_data['scraped_restaurants'] = scraped_count
        self.progress_data['failed_restaurants'] = failed_count
        self.save_progress()
    
    def add_scraped_restaurant(self, restaurant_name: str):
        """Add a scraped restaurant to the list"""
        if restaurant_name not in self.progress_data['scraped_restaurant_names']:
            self.progress_data['scraped_restaurant_names'].append(restaurant_name)
            self.save_progress()
    
    def is_restaurant_scraped(self, restaurant_name: str) -> bool:
        """Check if a restaurant has already been scraped"""
        return restaurant_name in self.progress_data['scraped_restaurant_names']
    
    def mark_completed(self):
        """Mark scraping as completed"""
        self.progress_data['completed'] = True
        self.progress_data['last_updated'] = datetime.now().isoformat()
        self.save_progress()
    
    def get_resume_info(self) -> Dict:
        """Get information for resuming scraping"""
        return {
            'can_resume': not self.progress_data['completed'] and self.progress_data['scraped_restaurants'] > 0,
            'scraped_count': self.progress_data['scraped_restaurants'],
            'failed_count': self.progress_data['failed_restaurants'],
            'started_at': self.progress_data['started_at'],
            'last_updated': self.progress_data['last_updated']
        }
    
    def clear_progress(self):
        """Clear progress file (start fresh)"""
        if os.path.exists(self.progress_file):
            os.remove(self.progress_file)
        self.progress_data = self.load_progress()
        self.logger.info("Progress cleared - starting fresh")
    
    def get_progress_summary(self) -> str:
        """Get a summary of current progress"""
        if not self.progress_data['started_at']:
            return "No scraping session in progress"
        
        total = self.progress_data['total_restaurants']
        scraped = self.progress_data['scraped_restaurants']
        failed = self.progress_data['failed_restaurants']
        
        if total > 0:
            percentage = (scraped / total) * 100
            return f"Progress: {scraped}/{total} restaurants ({percentage:.1f}%) - {failed} failed"
        else:
            return f"Progress: {scraped} restaurants scraped - {failed} failed"
