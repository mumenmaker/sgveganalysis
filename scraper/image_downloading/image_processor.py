"""
Image processing utilities for downloading and optimizing images.
"""

import io
import hashlib
from typing import Optional, Tuple
from PIL import Image, ImageOps
import requests
from config import MAX_IMAGE_SIZE, IMAGE_QUALITY, SUPPORTED_FORMATS, MAX_FILE_SIZE_MB, DOWNLOAD_TIMEOUT


class ImageProcessor:
    """Handles image downloading, processing, and optimization."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def download_image(self, url: str) -> Optional[bytes]:
        """
        Download image from URL with error handling.
        
        Args:
            url: Image URL to download
            
        Returns:
            Image bytes or None if download failed
        """
        try:
            response = self.session.get(url, timeout=DOWNLOAD_TIMEOUT, stream=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if not any(fmt.lower() in content_type for fmt in ['image', 'jpeg', 'png', 'webp']):
                print(f"⚠️  Invalid content type for {url}: {content_type}")
                return None
            
            # Check file size
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > MAX_FILE_SIZE_MB * 1024 * 1024:
                print(f"⚠️  Image too large: {url} ({content_length} bytes)")
                return None
            
            return response.content
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to download {url}: {e}")
            return None
    
    def process_image(self, image_bytes: bytes, url: str) -> Optional[bytes]:
        """
        Process and optimize image.
        
        Args:
            image_bytes: Raw image data
            url: Original URL for logging
            
        Returns:
            Processed image bytes or None if processing failed
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary (for JPEG output)
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparent images
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large
            if image.size[0] > MAX_IMAGE_SIZE[0] or image.size[1] > MAX_IMAGE_SIZE[1]:
                image.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
            
            # Optimize image
            image = ImageOps.exif_transpose(image)  # Handle EXIF orientation
            
            # Save as optimized JPEG
            output = io.BytesIO()
            image.save(
                output, 
                format='JPEG', 
                quality=IMAGE_QUALITY, 
                optimize=True,
                progressive=True
            )
            
            processed_bytes = output.getvalue()
            print(f"✅ Processed image: {len(processed_bytes)} bytes (was {len(image_bytes)} bytes)")
            return processed_bytes
            
        except Exception as e:
            print(f"❌ Failed to process image from {url}: {e}")
            return None
    
    def generate_filename(self, url: str, restaurant_id: int, index: int) -> str:
        """
        Generate a unique filename for the image.
        
        Args:
            url: Original image URL
            restaurant_id: Restaurant ID
            index: Image index in the array
            
        Returns:
            Generated filename
        """
        # Create hash from URL for uniqueness
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        return f"restaurant_{restaurant_id}_{index}_{url_hash}.jpg"
    
    def get_image_info(self, image_bytes: bytes) -> dict:
        """
        Get image information.
        
        Args:
            image_bytes: Image data
            
        Returns:
            Dictionary with image info
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            return {
                'width': image.size[0],
                'height': image.size[1],
                'format': image.format,
                'mode': image.mode,
                'size_bytes': len(image_bytes)
            }
        except Exception as e:
            print(f"❌ Failed to get image info: {e}")
            return {}
