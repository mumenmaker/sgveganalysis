# Database Setup Guide

## Overview
This guide helps you set up the Supabase database for the HappyCow Singapore Restaurant Scraper with coordinate-based duplicate prevention.

## 🆕 **NEW: Coordinate-Based Unique Constraint**

The database now uses **latitude and longitude coordinates** as the unique constraint instead of restaurant names. This prevents duplicate locations while allowing the same restaurant name at different locations (franchises).

### Benefits:
- ✅ **Prevents duplicate locations** - Same coordinates can't be inserted twice
- ✅ **Allows franchises** - Multiple "McDonald's" at different locations
- ✅ **Language independent** - Works with any language restaurant names
- ✅ **More reliable** - Physical location is more accurate than name matching

## Solution: Fresh Database Setup

### Step 1: Go to Supabase Dashboard
1. Open your Supabase project dashboard
2. Go to the **SQL Editor** tab (in the left sidebar)

### Step 2: Run the Fresh Setup Script
1. Copy the contents of `database/setup_fresh_database.sql` (recommended)
2. OR copy the contents of `database/create_tables.sql` (basic setup)
3. Paste it into the SQL Editor
4. Click **Run** to execute the script

### Step 3: Verify Tables Created
After running the SQL script, you should see:
- `restaurants` table in the **Table Editor**
- `scraping_progress` table in the **Table Editor**
- Both tables should be visible in your Supabase dashboard
- **Unique constraint** on `(latitude, longitude)` to prevent duplicate locations

### Step 4: Test Database Connection
Run the test script to verify everything is working:

```bash
cd /Users/zeldon/projects/mmaker/sgveganalysis/scraper
conda activate py3115
python test_coordinates_and_duplicates.py
```

### Step 5: Run the Scraper
Once the tables are created, run the scraper:

```bash
python main.py
```

## What the SQL Script Creates

### `restaurants` table:
- Stores all restaurant information with coordinate fields
- **Unique constraint** on `(latitude, longitude)` prevents duplicate locations
- Includes fields for name, address, rating, cuisine type, coordinates, etc.
- Has indexes for better performance on common queries

### `scraping_progress` table:
- Tracks scraping progress and sessions
- Stores session information and statistics
- Helps with resume functionality and progress tracking

## 🆕 **New Features**

### Coordinate-Based Duplicate Prevention:
- **Primary constraint**: `UNIQUE (latitude, longitude)`
- **Fallback logic**: Name + address checking when coordinates are missing
- **Smart duplicate detection**: Prevents same location, allows different locations

### Enhanced Data Model:
- **Coordinate fields**: `latitude` and `longitude` for precise location tracking
- **Performance indexes**: Fast queries on coordinates, ratings, and restaurant types
- **Flexible constraints**: Handles missing coordinates gracefully

## Troubleshooting

### If you get permission errors:
1. Make sure you're using the correct Supabase project
2. Check that your API key has the right permissions
3. Verify the table names match exactly

### If tables still don't appear:
1. Check the Supabase dashboard for any error messages
2. Try refreshing the page
3. Make sure you're in the correct project

### If you get unique constraint violations:
1. This is **expected behavior** - it means the coordinate-based duplicate prevention is working
2. The scraper will automatically skip duplicate locations
3. Check the logs for "Skipping duplicate" messages

## 🆕 **Coordinate Extraction**

The scraper now extracts coordinates from restaurant data:
- **Primary method**: Data attributes on restaurant elements
- **Fallback method**: JavaScript data in page source
- **Multiple patterns**: Various coordinate formats supported
- **Graceful handling**: Works even when coordinates are missing

## Next Steps

Once the tables are created:
1. **Coordinate extraction** will work automatically
2. **Duplicate prevention** will prevent same locations
3. **Franchise support** will allow same names at different locations
4. **Resume functionality** will work with coordinate-based tracking
5. **Query capabilities** will be enhanced with location data

The scraper is now **coordinate-aware** and **duplicate-resistant**!
