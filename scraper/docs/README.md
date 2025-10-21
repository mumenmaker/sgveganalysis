# Documentation

This folder contains comprehensive documentation for the sector-based HappyCow scraper with per-sector saving, Supabase-backed resume capability, and restaurant data enhancement.

## Contents

- `README.md` - This file (overview)
- `DEVELOPMENT.md` - Development setup and guidelines
- `TROUBLESHOOTING.md` - Common issues and solutions
- `BATCH_PROCESSING.md` - Batch processing and progress tracking guide
- `ARCHITECTURE_OVERVIEW.md` - Comprehensive system architecture documentation

## Quick Start

1. See the main `README.md` in the project root for basic usage
2. Check `DEVELOPMENT.md` for setting up the development environment
3. Read `BATCH_PROCESSING.md` for understanding batch processing features
4. Review `ARCHITECTURE_OVERVIEW.md` for system architecture details
5. Refer to `TROUBLESHOOTING.md` if you encounter issues

## Updated Highlights

- **Sector-based scraping** (6x8 grid covering Singapore)
- **Per-sector saving** to Supabase (fault tolerant)
- **Session tracking and resume** in `scraping_progress` table
- **Restaurant enhancement** from individual review pages
- **Coordinate-based duplicate prevention**
- **CLI commands** for listing/resuming sessions and enhancement

## Commands

### Scraping Commands
```bash
# Scrape all sectors
python main.py scrape

# Start from sector N / process max M
python main.py scrape --start 13 --max 5

# Regions (if defined)
python main.py scrape --region central
```

### Session Management
```bash
# List available sessions
python main.py list-sessions

# Resume interrupted session
python main.py resume SESSION_ID
```

### Enhancement Commands
```bash
# Enhance all restaurants with missing data
python main.py enhance

# Enhance specific number of restaurants
python main.py enhance --limit 50

# Enhance specific restaurant by ID
python main.py enhance --id 123

# Start enhancement from specific ID
python main.py enhance --start-id 500
```

### Utility Commands
```bash
# Test database connection
python main.py test

# Clear database and logs
python main.py clear-db

# Clear database, logs, and sessions
python main.py clear-db --include-sessions
```

## Data Flow

### Scraping Flow (Sector-based)
1. `sector_grid.py` → generate 48 sectors covering Singapore
2. `url_generator.py` → build `searchmap` URLs for each sector
3. `page_loader.py` → load pages in headless Chrome
4. `data_extractor.py` → parse `[data-marker-id]` and `.details.hidden` elements
5. `sector_scraper.py` → save to database immediately after each sector
6. `session_manager.py` → update `scraping_progress` table each sector

### Enhancement Flow (Review Pages)
1. `database.py` → fetch restaurants missing key fields
2. `reviews_enhancer.py` → scrape individual review pages
3. Extract detailed data (phone, address, description, category, price_range, rating, review_count, hours, features, images)
4. Update database records with enhanced information
5. Progress tracking with time estimation

## Contributing

When adding new features or fixing bugs, please update the relevant documentation files.
