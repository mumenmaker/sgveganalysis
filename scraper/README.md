# HappyCow Singapore Restaurant Scraper

Sector-based Selenium scraper for HappyCow's search map (Singapore), with per-sector saving and Supabase-backed resume capability.

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
# Scrape all 48 sectors (headless)
python main.py scrape

# Start from sector N, limit to M sectors
python main.py scrape --start 13 --max 5

# Scrape a specific region (if defined in grid helper)
python main.py scrape --region central

# List available sessions (from Supabase)
python main.py list-sessions

# Resume a session by ID
python main.py resume 349b319c-2abf-4773-9098-f6ae7b177aef

# Test database connection
python main.py test

# Clear database records and logs
python main.py clear-db

# Show help
python main.py help
```

## Project Structure

```
scraper/
├── main.py                    # CLI + sector orchestration
├── database.py                # Database operations
├── models.py                  # Data models
├── config.py                  # Configuration and URL parameters
├── sectorscraper/             # Core sector-based scraping library
│   ├── sector_grid.py         # 6x8 grid covering Singapore
│   ├── url_generator.py       # Builds URLs per sector
│   ├── page_loader.py         # Headless Selenium loader
│   ├── data_extractor.py      # Extracts details from DOM
│   ├── sector_scraper.py      # Per-sector extraction + DB save
│   └── session_manager.py     # Session tracking + resume
├── database/                  # Database setup files
├── debug/                     # Debug and testing files
├── tests/                     # Test files
├── logs/                      # Runtime logs and data
└── docs/                      # Documentation
```

## Features

- ✅ **Sector grid scraping**: 48 sectors (6x8) to bypass pagination limits
- ✅ **Per-sector saving**: Insert immediately after each sector (fault tolerant)
- ✅ **Supabase progress**: `scraping_progress` stores counts and status
- ✅ **Resume runs**: `list-sessions` and `resume SESSION_ID`
- ✅ **Duplicate handling**: DB unique constraint on `(latitude, longitude)`
- ✅ **Headless**: Selenium runs without opening a Chrome window

## How resume works

- On start, a unique `session_id` is created and written to `scraping_progress`
- After each sector, restaurants are inserted and progress counts are updated
- If interrupted, run `python main.py list-sessions` to get the `session_id`, then `python main.py resume SESSION_ID`
- The scraper continues with remaining sectors and marks the session complete when done

## Documentation

- Overview: `docs/README.md`
- Architecture: `docs/ARCHITECTURE_OVERVIEW.md`
- Database Setup: `database/setup_fresh_database.sql`
- Dev Guide: `docs/DEVELOPMENT.md`
- Troubleshooting: `docs/TROUBLESHOOTING.md`

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