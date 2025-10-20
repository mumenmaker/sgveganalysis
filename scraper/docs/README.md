# Documentation

This folder contains comprehensive documentation for the sector-based HappyCow scraper with per-sector saving and Supabase-backed resume capability.

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

- Sector-based scraping (6x8 grid)
- Per-sector saving to Supabase (fault tolerant)
- Session tracking and resume in `scraping_progress`
- CLI commands for listing/resuming sessions

## Commands

```bash
# Scrape all sectors
python main.py scrape

# Start from sector N / process max M
python main.py scrape --start 13 --max 5

# Regions (if defined)
python main.py scrape --region central

# Sessions
python main.py list-sessions
python main.py resume SESSION_ID

# Utilities
python main.py test
python main.py clear-db
```

## Data Flow (Sector mode)

1. `sector_grid.py` → generate 48 sectors
2. `url_generator.py` → build `searchmap` URLs
3. `page_loader.py` → load in headless Chrome
4. `data_extractor.py` → parse `[data-marker-id]` and `.details.hidden`
5. `sector_scraper.py` → save to DB right after each sector
6. `session_manager.py` → update `scraping_progress` each sector

## Contributing

When adding new features or fixing bugs, please update the relevant documentation files.
