# Coordinate and Duplicate Fixes

## Issues Identified

1. **Missing Latitude/Longitude Coordinates**: The scraper was not extracting coordinate data from the HappyCow website
2. **Duplicate Restaurant Records**: The database had no unique constraints, allowing the same restaurant to be inserted multiple times

## Fixes Implemented

### 1. Coordinate Extraction Enhancement

**Problem**: The scraper was not capturing latitude and longitude coordinates from the restaurant data.

**Solution**: Enhanced the `scrape_with_selenium` method in `happycow_scraper.py` to:

- Extract coordinates from element data attributes (`data-lat`, `data-lng`, etc.)
- Parse coordinate patterns from various data attribute formats
- Search for coordinate data in the page source (JavaScript data)
- Use multiple regex patterns to find coordinates in different formats

**Code Changes**:
```python
# Try to extract coordinates from data attributes
try:
    lat = element.get_attribute('data-lat')
    lng = element.get_attribute('data-lng')
    if lat and lng:
        restaurant_data['latitude'] = float(lat)
        restaurant_data['longitude'] = float(lng)
except (ValueError, TypeError):
    pass

# Try to extract coordinates from page source
coord_patterns = [
    r'"lat":\s*(\d+\.\d+),\s*"lng":\s*(\d+\.\d+)',
    r'"latitude":\s*(\d+\.\d+),\s*"longitude":\s*(\d+\.\d+)',
    # ... more patterns
]
```

### 2. Duplicate Prevention

**Problem**: The database allowed duplicate restaurant entries with the same name.

**Solution**: Added a unique constraint to the database schema and enhanced error handling.

**Database Schema Changes**:
```sql
-- Add unique constraint to prevent duplicate restaurants
ALTER TABLE restaurants ADD CONSTRAINT unique_restaurant_name UNIQUE (name);
```

**Code Changes**:
- Enhanced `DatabaseManager.insert_restaurants()` to handle unique constraint violations
- Added proper error handling for duplicate key violations
- Improved logging for duplicate detection

### 3. Testing and Verification

**New Test Script**: `test_coordinates_and_duplicates.py`
- Tests coordinate extraction from scraped data
- Verifies duplicate handling in database
- Checks current database status

## Usage

### 1. Update Database Schema

Run the updated SQL script in your Supabase dashboard:
```sql
-- Run the updated database/create_tables.sql script
-- This will add the unique constraint
```

### 2. Test the Fixes

```bash
cd /Users/zeldon/projects/mmaker/sgveganalysis/scraper
conda activate py3115
python test_coordinates_and_duplicates.py
```

### 3. Run the Scraper

```bash
python main.py
```

## Expected Results

1. **Coordinates**: Restaurant records should now include latitude and longitude data
2. **No Duplicates**: The unique constraint will prevent duplicate restaurant entries
3. **Better Error Handling**: Clear logging when duplicates are detected and skipped

## Database Schema Updates

The updated schema includes:
- Unique constraint on restaurant name
- Proper coordinate fields (latitude, longitude)
- Enhanced error handling for constraint violations

## Monitoring

Use the test script to monitor:
- Coordinate extraction success rate
- Duplicate detection and handling
- Database insertion statistics

## Troubleshooting

If coordinates are still missing:
1. Check if HappyCow has changed their data structure
2. Verify the coordinate extraction patterns in the code
3. Run the debug script to inspect the page source

If duplicates still occur:
1. Verify the unique constraint was applied to the database
2. Check the database logs for constraint violations
3. Ensure the scraper is using the updated database manager
