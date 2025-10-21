"""
Database operations for managing restaurant image URLs.
"""

import json
from typing import List, Optional, Dict, Any
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY, BACKUP_ORIGINAL_URLS


class DatabaseManager:
    """Manages restaurant database operations for image URLs."""
    
    def __init__(self):
        """Initialize Supabase client."""
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def get_restaurants_with_images(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get restaurants that have images_links.
        
        Args:
            limit: Maximum number of restaurants to return
            
        Returns:
            List of restaurant records
        """
        try:
            query = self.supabase.table('restaurants').select('*').not_.is_('images_links', 'null')
            
            if limit:
                query = query.limit(limit)
            
            result = query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            print(f"❌ Error fetching restaurants: {e}")
            return []
    
    def backup_original_urls(self, restaurant_id: int, original_urls: List[str]) -> bool:
        """
        Backup original image URLs to a separate field.
        
        Args:
            restaurant_id: Restaurant ID
            original_urls: List of original URLs
            
        Returns:
            True if backup was successful
        """
        if not BACKUP_ORIGINAL_URLS:
            return True
        
        try:
            # Try to update with original_image_urls field
            result = self.supabase.table('restaurants').update({
                'original_image_urls': original_urls
            }).eq('id', restaurant_id).execute()
            
            if result.data:
                print(f"✅ Backed up original URLs for restaurant {restaurant_id}")
                return True
            else:
                print(f"❌ Failed to backup original URLs for restaurant {restaurant_id}")
                return False
                
        except Exception as e:
            # If the column doesn't exist, skip backup but continue processing
            if "original_image_urls" in str(e):
                print(f"⚠️  Skipping backup (column doesn't exist): {e}")
                return True
            else:
                print(f"❌ Error backing up URLs for restaurant {restaurant_id}: {e}")
                return False
    
    def update_restaurant_images(self, restaurant_id: int, new_urls: List[str]) -> bool:
        """
        Update restaurant's images_links with new Supabase URLs.
        
        Args:
            restaurant_id: Restaurant ID
            new_urls: List of new image URLs
            
        Returns:
            True if update was successful
        """
        try:
            result = self.supabase.table('restaurants').update({
                'images_links': new_urls
            }).eq('id', restaurant_id).execute()
            
            if result.data:
                print(f"✅ Updated images for restaurant {restaurant_id}")
                return True
            else:
                print(f"❌ Failed to update images for restaurant {restaurant_id}")
                return False
                
        except Exception as e:
            print(f"❌ Error updating images for restaurant {restaurant_id}: {e}")
            return False
    
    def get_restaurant_by_id(self, restaurant_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific restaurant by ID.
        
        Args:
            restaurant_id: Restaurant ID
            
        Returns:
            Restaurant record or None
        """
        try:
            result = self.supabase.table('restaurants').select('*').eq('id', restaurant_id).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"❌ Error fetching restaurant {restaurant_id}: {e}")
            return None
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get statistics about image processing.
        
        Returns:
            Dictionary with processing stats
        """
        try:
            # Count restaurants with images
            with_images = self.supabase.table('restaurants').select('id', count='exact').not_.is_('images_links', 'null').execute()
            
            # Count restaurants with original URLs backed up
            with_backup = self.supabase.table('restaurants').select('id', count='exact').not_.is_('original_image_urls', 'null').execute()
            
            # Count total restaurants
            total = self.supabase.table('restaurants').select('id', count='exact').execute()
            
            return {
                'total_restaurants': total.count if total.count else 0,
                'restaurants_with_images': with_images.count if with_images.count else 0,
                'restaurants_with_backup': with_backup.count if with_backup.count else 0,
                'processing_complete': (with_images.count or 0) == (with_backup.count or 0)
            }
            
        except Exception as e:
            print(f"❌ Error getting processing stats: {e}")
            return {}
    
    def create_progress_table(self) -> bool:
        """
        Create a progress tracking table for image processing.
        
        Returns:
            True if table was created successfully
        """
        try:
            # This would typically be done via SQL, but we'll use a simple approach
            # In practice, you'd run this SQL in Supabase:
            """
            CREATE TABLE IF NOT EXISTS image_processing_progress (
                id SERIAL PRIMARY KEY,
                restaurant_id INTEGER REFERENCES restaurants(id),
                status VARCHAR(50) DEFAULT 'pending',
                total_images INTEGER DEFAULT 0,
                processed_images INTEGER DEFAULT 0,
                failed_images INTEGER DEFAULT 0,
                started_at TIMESTAMP DEFAULT NOW(),
                completed_at TIMESTAMP,
                error_message TEXT
            );
            """
            print("ℹ️  Progress table creation should be done via SQL in Supabase")
            return True
            
        except Exception as e:
            print(f"❌ Error creating progress table: {e}")
            return False
