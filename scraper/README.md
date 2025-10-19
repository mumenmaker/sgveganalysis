# HappyCow Singapore Restaurant Scraper

A Python scraper that extracts restaurant data from HappyCow for Singapore and stores it in a Supabase database.

## Features

- Scrapes restaurant data from HappyCow's Singapore search results
- Stores data in Supabase database with proper schema
- Includes rate limiting and error handling
- Saves data to JSON as backup
- Supports different restaurant types (vegan, vegetarian, veg-friendly)
- Location-based queries with PostGIS support

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up Supabase

1. Create a new project at [Supabase](https://supabase.com)
2. Get your project URL and anon key from the project settings
3. Create a `.env` file in the scraper directory:

```env
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
DELAY_BETWEEN_REQUESTS=2
MAX_RETRIES=3
USER_AGENT_ROTATION=True
```

### 3. Enable PostGIS (Optional)

For location-based queries, enable the PostGIS extension in your Supabase project:

1. Go to your Supabase dashboard
2. Navigate to Database > Extensions
3. Enable the "PostGIS" extension

## Usage

### Run the Scraper

```bash
# Normal run (will resume if interrupted)
python main.py

# Clear progress and start fresh
python main.py clear

# Check scraping status
python main.py status

# Test database connection
python main.py test
```

### Resume Functionality

The scraper automatically supports resuming interrupted scraping sessions:

- **Progress tracking**: Saves progress to `scraping_progress.json`
- **Duplicate detection**: Skips already scraped restaurants
- **Database duplicates**: Prevents duplicate entries in Supabase
- **JSON backup**: Merges new data with existing JSON file

### Command Line Options

- `python main.py` - Run scraper (resumes if interrupted)
- `python main.py clear` - Clear progress and start fresh
- `python main.py status` - Show current scraping status
- `python main.py test` - Test database connection

## Database Schema

The scraper creates a `restaurants` table with the following fields:

- `id`: Primary key
- `name`: Restaurant name
- `address`: Full address
- `phone`: Phone number
- `website`: Website URL
- `description`: Restaurant description
- `cuisine_type`: Type of cuisine
- `price_range`: Price range indicator
- `rating`: Average rating
- `review_count`: Number of reviews
- `latitude`/`longitude`: GPS coordinates
- `is_vegan`: Boolean for vegan restaurants
- `is_vegetarian`: Boolean for vegetarian restaurants
- `has_veg_options`: Boolean for veg-friendly restaurants
- `features`: Array of restaurant features
- `hours`: Operating hours
- `happycow_url`: Original HappyCow URL
- `scraped_at`: Timestamp of scraping
- `created_at`/`updated_at`: Database timestamps

## API Usage

The `DatabaseManager` class provides several methods for querying the data:

```python
from database import DatabaseManager

db = DatabaseManager()

# Get all restaurants
restaurants = db.get_restaurants(limit=100)

# Search restaurants
results = db.search_restaurants("vegan", limit=50)

# Get vegan restaurants only
vegan_restaurants = db.get_vegan_restaurants()

# Get restaurants near a location
nearby = db.get_restaurants_by_location(1.34183, 103.861, radius_km=5.0)
```

## Configuration

Edit `config.py` to modify scraper settings:

- `DELAY_BETWEEN_REQUESTS`: Delay between HTTP requests (seconds)
- `MAX_RETRIES`: Maximum retry attempts for failed requests
- `USER_AGENT_ROTATION`: Rotate user agents to avoid detection

## Output Files

- `singapore_restaurants.json`: JSON backup of scraped data
- `scraper.log`: Detailed logging information

## Error Handling

The scraper includes comprehensive error handling:

- Rate limiting to avoid being blocked
- Retry logic for failed requests
- User agent rotation
- Detailed logging for debugging

## Legal Considerations

- Respect HappyCow's robots.txt and terms of service
- Use reasonable delays between requests
- Consider reaching out to HappyCow for API access
- This scraper is for educational purposes

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check your Supabase credentials in `.env`
   - Ensure your Supabase project is active

2. **No Restaurants Found**
   - HappyCow may have changed their website structure
   - Check if you're being rate-limited
   - Verify network connectivity

3. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`

### Debug Mode

Enable debug logging by modifying the logging level in `main.py`:

```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes. Please respect HappyCow's terms of service and consider reaching out for official API access.
