# Troubleshooting Guide

## Common Issues

### Database Connection Issues

**Problem**: `Failed to connect to Supabase`

**Solutions**:
1. Check your `.env` file has correct `SUPABASE_URL` and `SUPABASE_KEY`
2. Verify your Supabase project is active
3. Check your internet connection
4. Ensure your Supabase credentials have the correct permissions

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

### Memory Issues

**Problem**: Scraper runs out of memory

**Solutions**:
1. Reduce batch size for database inserts
2. Clear progress more frequently
3. Use pagination to limit memory usage
4. Close browser instances properly

## Debug Commands

```bash
# Test database connection
python main.py test

# Clear database and start fresh
python main.py clear-db

# Check current status
python main.py status

# Run with debug logging
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
```

## Getting Help

1. Check the logs in `logs/scraper.log`
2. Run debug scripts in the `debug/` folder
3. Check the database with `database/check_restaurants.py`
4. Review the test cases in `tests/` folder
