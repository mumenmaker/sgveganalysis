"""
Configuration for image downloading and processing.
"""

import os
from typing import List

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET_NAME = "restaurant-images"

# Image Processing Configuration
MAX_IMAGE_SIZE = (800, 600)  # Resize images to max 800x600
IMAGE_QUALITY = 85  # JPEG quality (1-100)
SUPPORTED_FORMATS = ["JPEG", "PNG", "WEBP"]
MAX_FILE_SIZE_MB = 5  # Maximum file size in MB

# Download Configuration
DOWNLOAD_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds between retries
BATCH_SIZE = 10  # Process images in batches

# Storage Configuration
STORAGE_FOLDER = "restaurants"  # Folder in Supabase Storage
BACKUP_ORIGINAL_URLS = True  # Keep original URLs in a backup field

# Progress Tracking
PROGRESS_FILE = "image_download_progress.json"
