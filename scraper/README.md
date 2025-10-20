# HappyCow Singapore Restaurant Scraper

A Python scraper that extracts restaurant data from HappyCow's veggiemap for Singapore and stores it in a Supabase database with batch processing and progress tracking.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up Environment
Create a `.env` file:
```env
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
DELAY_BETWEEN_REQUESTS=2
MAX_RETRIES=3
USER_AGENT_ROTATION=True
```

### 3. Set up Database
Run the database setup script in your Supabase SQL Editor:
- Copy contents from `database/setup_fresh_database.sql`
- Paste and run in Supabase SQL Editor

### 4. Run the Scraper
```bash
# Basic scraping with default batch size (20)
python main.py

# Scraping with custom batch size
python main.py scrape --batch-size 50

# Resume interrupted scraping session
python main.py scrape --resume SESSION_ID

# List available scraping sessions
python main.py list-sessions

# Test database connection
python main.py test

# Test coordinate extraction only
python main.py test-coords

# Clear database and start fresh
python main.py clear-db

# Show help
python main.py help
```

## Project Structure

```
scraper/
├── main.py                    # Main scraper script with batch processing
├── database.py                # Database operations
├── models.py                  # Data models
├── config.py                  # Configuration with batch settings
├── hcowscraper/               # Core scraping library
│   ├── veggiemap_scraper.py   # Main scraper class
│   ├── marker_extractor.py   # Marker extraction logic
│   ├── restaurant_parser.py  # Restaurant data parsing
│   ├── cluster_handler.py    # Map cluster expansion
│   └── batch_progress_tracker.py # Batch processing & progress tracking
├── database/                  # Database setup files
├── debug/                     # Debug and testing files
├── tests/                     # Test files
├── logs/                      # Runtime logs and data
└── docs/                      # Documentation
```

## Features

- ✅ **Veggiemap Integration**: Scrapes from HappyCow's interactive veggiemap
- ✅ **Batch Processing**: Processes restaurants in configurable batches (5-100)
- ✅ **Progress Tracking**: Saves progress after each batch with session management
- ✅ **Resume Functionality**: Resume interrupted scraping sessions
- ✅ **Cluster Expansion**: Automatically zooms in to extract individual restaurants
- ✅ **Coordinate Extraction**: Multiple methods for reliable coordinate extraction
- ✅ **Database Integration**: Stores data in Supabase with proper schema
- ✅ **Duplicate Prevention**: Coordinate-based unique constraints
- ✅ **Error Handling**: Comprehensive error handling and recovery
- ✅ **Session Management**: Track and manage multiple scraping sessions

## Batch Processing

The scraper processes restaurants in configurable batches for better reliability:

- **Default batch size**: 20 restaurants per batch
- **Configurable range**: 5-100 restaurants per batch
- **Progress tracking**: Saves progress after each batch
- **Session management**: Unique session IDs for tracking
- **Resume capability**: Continue interrupted sessions

### Batch Processing Flow:
1. Extract all markers from the veggiemap
2. Process markers in batches (e.g., 20 at a time)
3. Insert each batch to database immediately
4. Update progress tracking after each batch
5. Complete session when all batches processed

## Documentation

- **Full Documentation**: `docs/README.md`
- **Database Setup**: `database/DATABASE_SETUP.md`
- **Development Guide**: `docs/DEVELOPMENT.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`

## Testing

```bash
# Run all tests
python run_tests.py

# Run specific test
python -m pytest tests/test_scraper.py
```

## Debugging

Debug files are available in the `debug/` folder for troubleshooting:
- `debug/debug_coordinates.py` - Coordinate extraction debugging
- `debug/debug_page_structure.py` - Page structure analysis
- `debug/check_database.py` - Database verification

## License

This project is for educational and research purposes.