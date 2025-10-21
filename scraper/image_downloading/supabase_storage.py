"""
Supabase Storage integration for uploading and managing images.
"""

import os
from typing import List, Optional, Dict, Any
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_BUCKET_NAME, STORAGE_FOLDER


class SupabaseStorageManager:
    """Manages image uploads to Supabase Storage."""
    
    def __init__(self):
        """Initialize Supabase client."""
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.bucket_name = SUPABASE_BUCKET_NAME
        self.storage_folder = STORAGE_FOLDER
    
    def create_bucket_if_not_exists(self) -> bool:
        """
        Create the storage bucket if it doesn't exist.
        
        Returns:
            True if bucket exists or was created successfully
        """
        try:
            # Try to get bucket info
            buckets = self.supabase.storage.list_buckets()
            bucket_names = [bucket['name'] for bucket in buckets]
            
            if self.bucket_name in bucket_names:
                print(f"✅ Bucket '{self.bucket_name}' already exists")
                return True
            
            # Create bucket
            result = self.supabase.storage.create_bucket(
                self.bucket_name,
                options={
                    'public': True,  # Make images publicly accessible
                    'file_size_limit': 10 * 1024 * 1024,  # 10MB limit
                    'allowed_mime_types': ['image/jpeg', 'image/png', 'image/webp']
                }
            )
            
            if result:
                print(f"✅ Created bucket '{self.bucket_name}'")
                return True
            else:
                print(f"❌ Failed to create bucket '{self.bucket_name}'")
                return False
                
        except Exception as e:
            print(f"❌ Error managing bucket '{self.bucket_name}': {e}")
            return False
    
    def upload_image(self, image_bytes: bytes, filename: str) -> Optional[str]:
        """
        Upload image to Supabase Storage.
        
        Args:
            image_bytes: Image data to upload
            filename: Filename for the image
            
        Returns:
            Public URL of uploaded image or None if upload failed
        """
        try:
            # Create full path
            file_path = f"{self.storage_folder}/{filename}"
            
            # Upload file
            result = self.supabase.storage.from_(self.bucket_name).upload(
                file_path,
                image_bytes,
                file_options={
                    'content-type': 'image/jpeg',
                    'cache-control': 'max-age=31536000'  # 1 year cache
                }
            )
            
            if result:
                # Get public URL
                public_url = self.supabase.storage.from_(self.bucket_name).get_public_url(file_path)
                print(f"✅ Uploaded: {filename} -> {public_url}")
                return public_url
            else:
                print(f"❌ Failed to upload: {filename}")
                return None
                
        except Exception as e:
            print(f"❌ Error uploading {filename}: {e}")
            return None
    
    def delete_image(self, filename: str) -> bool:
        """
        Delete image from Supabase Storage.
        
        Args:
            filename: Filename to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            file_path = f"{self.storage_folder}/{filename}"
            result = self.supabase.storage.from_(self.bucket_name).remove([file_path])
            
            if result:
                print(f"✅ Deleted: {filename}")
                return True
            else:
                print(f"❌ Failed to delete: {filename}")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting {filename}: {e}")
            return False
    
    def list_images(self, restaurant_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List images in storage.
        
        Args:
            restaurant_id: Filter by restaurant ID (optional)
            
        Returns:
            List of image information
        """
        try:
            files = self.supabase.storage.from_(self.bucket_name).list(self.storage_folder)
            
            if restaurant_id:
                # Filter by restaurant ID
                prefix = f"restaurant_{restaurant_id}_"
                files = [f for f in files if f['name'].startswith(prefix)]
            
            return files
            
        except Exception as e:
            print(f"❌ Error listing images: {e}")
            return []
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Returns:
            Dictionary with storage stats
        """
        try:
            files = self.supabase.storage.from_(self.bucket_name).list(self.storage_folder)
            
            total_files = len(files)
            total_size = sum(f.get('metadata', {}).get('size', 0) for f in files)
            
            return {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'bucket_name': self.bucket_name,
                'storage_folder': self.storage_folder
            }
            
        except Exception as e:
            print(f"❌ Error getting storage stats: {e}")
            return {}
