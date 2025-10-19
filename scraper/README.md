# HappyCow Singapore Restaurant Scraper

A Python scraper that extracts restaurant data from HappyCow for Singapore and stores it in a Supabase database.

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
python main.py
```

## Project Structure

```
scraper/
├── main.py                    # Main scraper script
├── happycow_scraper.py        # Core scraping logic
├── database.py                # Database operations
├── models.py                  # Data models
├── config.py                  # Configuration
├── progress_tracker.py        # Progress tracking
├── database/                  # Database setup files
├── debug/                     # Debug and testing files
├── examples/                  # Example usage files
├── tests/                     # Test files
├── logs/                      # Runtime logs and data
└── docs/                      # Documentation
```

## Features

- ✅ Scrapes restaurant data from HappyCow's Singapore search results
- ✅ Stores data in Supabase database with proper schema
- ✅ Coordinate-based duplicate prevention
- ✅ Resume functionality for interrupted scraping
- ✅ Rate limiting and error handling
- ✅ JSON backup of scraped data

## Documentation

- **Full Documentation**: `docs/README.md`
- **Database Setup**: `database/DATABASE_SETUP.md`
- **Project Organization**: `docs/PROJECT_ORGANIZATION.md`
- **Coordinate Fixes**: `docs/COORDINATE_AND_DUPLICATE_FIXES.md`
- **Unique Constraints**: `docs/COORDINATE_UNIQUE_CONSTRAINT.md`

## Examples

- **Basic Usage**: `examples/example_usage.py`
- **Resume Functionality**: `examples/resume_example.py`

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