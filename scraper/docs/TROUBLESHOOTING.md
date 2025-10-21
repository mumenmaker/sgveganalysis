# Troubleshooting Guide

## Common Issues

### Database Connection Issues

**Problem**: `Failed to connect to Supabase`

**Solutions**:
1. Check your `.env` file has correct `SUPABASE_URL` and `SUPABASE_KEY`
2. Verify your Supabase project is active
3. Check your internet connection
4. Ensure your Supabase credentials have the correct permissions
5. Run the database setup scripts in Supabase SQL Editor

### Selenium Issues

**Problem**: `WebDriver not found` or Chrome crashes

**Solutions**:
1. Install Chrome/Chromium browser
2. Install ChromeDriver: `brew install chromedriver` (macOS)
3. Check Chrome version compatibility
4. Try running in non-headless mode for debugging

### Coordinate Extraction Issues

**Problem**: Coordinates are `None` in database

**Solutions**:
1. Check if the page has loaded completely (wait longer)
2. Verify the page structure hasn't changed
3. Check if coordinates are in different elements
4. Use debug scripts to inspect page source

### Duplicate Records

**Problem**: Getting duplicate restaurant entries

**Solutions**:
1. Check the unique constraint in database
2. Verify coordinate extraction is working
3. Check if the same restaurant appears in multiple locations
4. Use the `clear-db` command to start fresh

### Per-Sector Saving / Progress Issues

**Problem**: Progress updates fail or scraping stalls on a sector

**Solutions**:
1. Verify database connection is stable
2. Check if session is corrupted (use `list-sessions`)
3. Resume with `resume SESSION_ID`
4. Start a new session if the old one is completed
5. Monitor logs for sector-specific errors

### Enhancement Issues

**Problem**: Enhancement command fails or gets stuck

**Solutions**:
1. Check if restaurants have `cow_reviews` links
2. Verify the delay setting (`ENHANCE_DELAY_BETWEEN_PAGES`)
3. Use smaller limits (`--limit 10`) for testing
4. Check for CAPTCHA or throttling (increase delay)
5. Use `--start-id` to resume from specific point

**Problem**: Enhancement extracts no data

**Solutions**:
1. Check if review page structure has changed
2. Verify CSS selectors in `reviews_enhancer.py`
3. Test with single restaurant (`--id 123`)
4. Check if restaurant has missing fields (use `--limit 1`)

**Problem**: Enhancement is too slow

**Solutions**:
1. Reduce delay (not recommended): `ENHANCE_DELAY_BETWEEN_PAGES=1`
2. Use smaller batches: `--limit 5`
3. Target specific restaurants: `--id 123`
4. Use `--start-id` to resume from specific point

### Session Management Issues

**Problem**: Cannot resume interrupted sessions

**Solutions**:
1. Check session ID is correct (use `list-sessions`)
2. Verify database has progress tracking data (`scraping_progress`)
3. Check if session was marked as completed
4. Use `clear-db` to start fresh if needed

### Memory Issues

**Problem**: Scraper runs out of memory

**Solutions**:
1. Reduce batch size (use `--batch-size 10`)
2. Clear progress more frequently
3. Use smaller batch sizes for large datasets
4. Close browser instances properly
5. Monitor system resources during scraping

## Debug Commands

```bash
# Test database connection
python main.py test

# List available scraping sessions
python main.py list-sessions

# Resume interrupted session
python main.py resume SESSION_ID

# Start from sector / limit maximum sectors
python main.py scrape --start 5 --max 10

# Clear database and start fresh
python main.py clear-db

# Clear database, logs, and sessions
python main.py clear-db --include-sessions

# Enhancement commands
python main.py enhance --limit 5          # Test with small batch
python main.py enhance --id 123           # Test specific restaurant
python main.py enhance --start-id 500    # Resume from specific ID

# Show help and all options
python main.py help

# Run with debug logging
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
```

## Getting Help

1. Check the logs in `logs/scraper.log`
2. Run debug scripts in the `debug/` folder
3. Check the database with `database/check_restaurants.py`
4. Review the test cases in `tests/` folder
