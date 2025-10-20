# sgveganalysis

HappyCow Singapore restaurant scraper and data pipeline.

## What this does

- Scrapes HappyCow's search map for Singapore using a 48-sector grid
- Extracts restaurant details from DOM cards with `data-marker-id` and `.details.hidden`
- Saves results to Supabase `restaurants` (unique on `(latitude, longitude)`) immediately after each sector
- Tracks scraping sessions in Supabase `scraping_progress`
- Supports listing sessions and resuming incomplete runs

## Quick start

```bash
cd scraper
pip install -r requirements.txt

# Configure environment (create .env)
# SUPABASE_URL=...
# SUPABASE_KEY=...

# One-off: create tables in Supabase (run SQL in Supabase SQL editor)
#   - scraper/database/setup_fresh_database.sql

# Test connection
python main.py test

# Scrape all sectors (headless)
python main.py scrape

# List available sessions
python main.py list-sessions

# Resume a session
python main.py resume SESSION_ID

# Clear DB records and logs
python main.py clear-db
```

## Key commands

- `python main.py scrape [--start N] [--max N] [--region NAME]`
- `python main.py list-sessions`
- `python main.py resume SESSION_ID`
- `python main.py test`
- `python main.py clear-db`

## Project layout (scraper)

```
scraper/
  main.py                      # CLI + orchestration
  config.py                    # Settings and HappyCow URL parameters
  database.py                  # Supabase client + inserts
  models.py                    # Pydantic models
  sectorscraper/               # Sector-based scraping library
    sector_grid.py             # 6x8 grid covering Singapore
    url_generator.py           # Builds searchmap URLs per sector
    page_loader.py             # Selenium headless Chrome loader
    data_extractor.py          # Extracts data from DOM elements
    sector_scraper.py          # Coordinates per-sector scraping and saving
    session_manager.py         # Supabase-backed session tracking/resume
  database/
    setup_fresh_database.sql   # Tables including scraping_progress
    update_progress_table.sql  # Optional enhancements
  docs/                        # Detailed docs
```

## Resume & progress (overview)

- Progress is stored in Supabase table `scraping_progress` (counts + completion flag)
- Each run creates a unique `session_id`
- After each sector:
  - Restaurants are inserted (duplicates auto-skipped by DB)
  - `scraping_progress` is updated with counts and timestamps
- You can resume any in-progress session with `python main.py resume SESSION_ID`

See `scraper/docs/README.md` and `scraper/docs/ARCHITECTURE_OVERVIEW.md` for more.
