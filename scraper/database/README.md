# Database Utilities

This folder contains utilities for managing and monitoring the Supabase database for the HappyCow scraper project.

## Files

### `check_restaurants.py`
A comprehensive script to check the status and statistics of the restaurants table in Supabase.

## Database Check Script

### Overview
The `check_restaurants.py` script provides detailed statistics about the restaurants table, including record counts, coordinate coverage, and restaurant type breakdowns.

### Features

#### 📊 **Statistics Display**
- Total number of restaurants in the database
- Number of restaurants with coordinates (latitude/longitude)
- Number of restaurants without coordinates
- Coordinate coverage percentage

#### 🍽️ **Restaurant Type Analysis**
- Vegan restaurants count
- Vegetarian restaurants count  
- Restaurants with vegetarian options count

#### 🔍 **Sample Data Display**
- Sample restaurants with coordinates (showing name, coordinates, and type)
- Sample restaurants without coordinates (if any)
- Most recently scraped restaurants

#### 📈 **Data Quality Metrics**
- Coordinate coverage percentage
- Recent scraping activity
- Data completeness indicators

### Usage

#### Basic Usage
```bash
cd /Users/zeldon/projects/mmaker/sgveganalysis/scraper
python database/check_restaurants.py
```

#### Using Python 3.11.5 (Recommended)
```bash
cd /Users/zeldon/projects/mmaker/sgveganalysis/scraper
/Users/zeldon/anaconda3/envs/py3115/bin/python database/check_restaurants.py
```

### Sample Output

```
🔍 Checking Supabase Restaurants Table
==================================================

============================================================
🍽️  RESTAURANTS TABLE STATISTICS
============================================================
📈 Total restaurants: 78
📍 With coordinates: 78
❌ Without coordinates: 0
📊 Coordinate coverage: 100.0%

🔍 Sample restaurants with coordinates:
  1. Kunthaville - 1.307464, 103.853439 (🌱 Vegan)
  2. MOON CHAY - 1.300178, 103.852196 (🌱 Vegan)
  3. Pure Heart 清心素食 - 1.344531, 103.855057 (🥗 Vegetarian)
  4. Toa Payoh Lorong 8 - Vegetarian Stall - 1.34039, 103.854286 (🥗 Vegetarian)
  5. Mahaprajna Snack Cafe 妙缘佛餐阁 - 1.335521, 103.857162 (🍽️ Other)

📊 Restaurant type breakdown:
  🌱 Vegan restaurants: 14
  🥗 Vegetarian restaurants: 38
  🍽️  Restaurants with veg options: 58

🕒 Most recently scraped restaurants:
  1. Vegetarian 素食 - Geylang Bahru - 2025-10-19T23:07:27.317885+00:00 ✅
  2. Delcie's Desserts and Cakes - 2025-10-19T23:07:24.721492+00:00 ✅
  3. Humble Food - 2025-10-19T23:07:22.131623+00:00 ✅

============================================================
✅ Database check completed successfully!
============================================================
```

### Prerequisites

#### Environment Setup
- Python 3.11.5 (recommended)
- Supabase client library
- Database connection configured

#### Required Environment Variables
The script uses the same database connection as the main scraper, requiring:
- `SUPABASE_URL`
- `SUPABASE_KEY`

These should be set in your `.env` file in the scraper root directory.

### Database Schema

The script queries the following fields from the `restaurants` table:

#### Core Fields
- `id` - Primary key
- `name` - Restaurant name
- `latitude` - Geographic latitude
- `longitude` - Geographic longitude
- `scraped_at` - Timestamp when scraped

#### Classification Fields
- `is_vegan` - Boolean: Is the restaurant vegan?
- `is_vegetarian` - Boolean: Is the restaurant vegetarian?
- `has_veg_options` - Boolean: Does the restaurant have vegetarian options?

### Error Handling

The script includes comprehensive error handling for:
- Database connection failures
- Query execution errors
- Data parsing issues
- Network connectivity problems

### Exit Codes

- `0` - Success: Database check completed successfully
- `1` - Error: Database connection failed or query error occurred

### Dependencies

The script imports from the main scraper modules:
- `database.DatabaseManager` - For Supabase connection
- Standard Python libraries: `os`, `sys`, `logging`, `pathlib`

### Troubleshooting

#### Common Issues

1. **Database Connection Failed**
   - Verify `.env` file contains correct `SUPABASE_URL` and `SUPABASE_KEY`
   - Check network connectivity
   - Ensure Supabase project is active

2. **Import Errors**
   - Ensure you're running from the correct directory (`/scraper/`)
   - Verify Python path includes the parent directory

3. **Permission Errors**
   - Make sure the script is executable: `chmod +x database/check_restaurants.py`
   - Check file permissions on the database folder

#### Debug Mode
For detailed logging, the script uses Python's logging module with INFO level. To see more detailed output, you can modify the logging level in the script.

### Integration

This script is designed to work seamlessly with the main HappyCow scraper project and can be used for:
- **Monitoring** - Regular database health checks
- **Validation** - Verifying scraper results
- **Debugging** - Investigating data quality issues
- **Reporting** - Generating database statistics

### Future Enhancements

Potential improvements for the script:
- Export statistics to CSV/JSON
- Historical trend analysis
- Coordinate validation (checking if coordinates are within Singapore bounds)
- Duplicate detection reporting
- Performance metrics (query execution times)

---

## Related Documentation

- [Main Scraper README](../README.md) - Overview of the HappyCow scraper
- [Database Setup](DATABASE_SETUP.md) - Database schema and setup instructions
- [Project Organization](../docs/PROJECT_ORGANIZATION.md) - Overall project structure
