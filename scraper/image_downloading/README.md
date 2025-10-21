# Image Downloader

This module downloads restaurant images from HappyCow and uploads them to Supabase Storage, then updates the restaurant records with the new URLs.

## Features

- **Image Download**: Downloads images from HappyCow URLs
- **Image Processing**: Optimizes and resizes images for web use
- **Supabase Storage**: Uploads processed images to Supabase Storage
- **Database Updates**: Updates restaurant records with new image URLs
- **Progress Tracking**: Tracks processing progress and allows resuming
- **Error Handling**: Robust error handling and retry mechanisms
- **Backup**: Backs up original URLs before replacing them

## Setup

### 1. Install Dependencies

```bash
cd scraper/image_downloading
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the `scraper` directory with:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### 3. Supabase Storage Setup

The script will automatically create a storage bucket named `restaurant-images` if it doesn't exist.

## Usage

### Basic Usage

```bash
# Process all restaurants with images
python image_downloader.py

# Process only first 10 restaurants
python image_downloader.py --limit 10

# Skip already processed restaurants (default)
python image_downloader.py --skip-processed

# Retry failed restaurants
python image_downloader.py --retry-failed

# Show storage statistics
python image_downloader.py --stats

# Reset progress tracking
python image_downloader.py --reset-progress
```

### Programmatic Usage

```python
from image_downloader import ImageDownloader

# Initialize downloader
downloader = ImageDownloader()

# Setup storage
downloader.setup()

# Process all images
result = downloader.process_all_images(limit=10)

# Get storage stats
stats = downloader.get_storage_stats()
```

## Configuration

Edit `config.py` to customize:

- **Image Processing**: Max size, quality, supported formats
- **Download Settings**: Timeout, retries, batch size
- **Storage**: Bucket name, folder structure
- **Progress**: Progress file location

## File Structure

```
scraper/image_downloading/
├── requirements.txt          # Python dependencies
├── config.py               # Configuration settings
├── image_processor.py      # Image download and processing
├── supabase_storage.py     # Supabase Storage integration
├── database_manager.py      # Database operations
├── progress_tracker.py     # Progress tracking
├── image_downloader.py     # Main orchestrator
└── README.md              # This file
```

## Process Flow

1. **Setup**: Create storage bucket and initialize components
2. **Fetch Restaurants**: Get restaurants with `images_links` field
3. **Download Images**: Download each image from HappyCow URLs
4. **Process Images**: Resize, optimize, and convert to JPEG
5. **Upload to Storage**: Upload processed images to Supabase Storage
6. **Update Database**: Replace original URLs with new Supabase URLs
7. **Track Progress**: Save progress for resuming interrupted processes

## Image Processing

- **Format**: Converts all images to JPEG
- **Size**: Resizes to max 800x600 pixels
- **Quality**: 85% JPEG quality
- **Optimization**: Progressive JPEG encoding
- **Transparency**: Converts transparent images to white background

## Error Handling

- **Download Failures**: Retries failed downloads up to 3 times
- **Processing Errors**: Logs errors and continues with next image
- **Upload Failures**: Tracks failed uploads for retry
- **Database Errors**: Rolls back changes on database failures

## Progress Tracking

The system tracks progress in `image_download_progress.json`:

- **Restaurant Progress**: Which restaurants have been processed
- **Image Progress**: How many images processed vs total
- **Error Logging**: Detailed error messages for debugging
- **Resume Capability**: Can resume interrupted processing

## Storage Structure

Images are stored in Supabase Storage as:

```
restaurant-images/
└── restaurants/
    ├── restaurant_1_0_abc123.jpg
    ├── restaurant_1_1_def456.jpg
    ├── restaurant_2_0_ghi789.jpg
    └── ...
```

## Database Changes

The script makes these database changes:

1. **Backup Original URLs**: Saves original URLs to `original_image_urls` field
2. **Update Image URLs**: Replaces `images_links` with new Supabase URLs
3. **Progress Tracking**: Optional progress table for detailed tracking

## Monitoring

### Progress Monitoring

```python
from progress_tracker import ProgressTracker

tracker = ProgressTracker()
summary = tracker.get_progress_summary()
print(f"Progress: {summary['restaurant_progress']['percentage']}%")
```

### Storage Monitoring

```python
from supabase_storage import SupabaseStorageManager

storage = SupabaseStorageManager()
stats = storage.get_storage_stats()
print(f"Total files: {stats['total_files']}")
print(f"Total size: {stats['total_size_mb']} MB")
```

## Troubleshooting

### Common Issues

1. **Storage Bucket Not Found**: Run setup to create bucket
2. **Permission Errors**: Check Supabase key permissions
3. **Download Failures**: Check network connectivity and URL validity
4. **Processing Errors**: Verify image format support

### Debug Mode

Enable debug logging by setting environment variable:

```bash
export DEBUG=1
python image_downloader.py
```

### Reset Everything

```bash
# Reset progress
python image_downloader.py --reset-progress

# Clear storage (manual cleanup required)
# Delete files in Supabase Storage dashboard
```

## Performance

- **Batch Processing**: Processes restaurants in configurable batches
- **Rate Limiting**: Built-in delays to avoid overwhelming servers
- **Memory Efficient**: Processes images one at a time
- **Resume Capable**: Can resume interrupted processing

## Security

- **URL Validation**: Validates image URLs before processing
- **File Size Limits**: Prevents processing of oversized files
- **Content Type Checking**: Verifies image content types
- **Error Isolation**: Failures don't affect other images
