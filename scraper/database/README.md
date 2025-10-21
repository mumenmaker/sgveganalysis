# HappyCow Singapore Scraper Database

## Overview
This database stores restaurant data scraped from HappyCow's Singapore searchmap, including enhanced details from individual restaurant review pages.

## Quick Start

### 1. Initialize Database
Run the SQL script in your Supabase SQL Editor:
```sql
-- Copy and paste the contents of setup_fresh_database.sql
```

### 2. Verify Setup
```bash
python main.py test
```

## Database Schema

### Tables

#### `restaurants` - Main restaurant data
| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PRIMARY KEY | Auto-incrementing ID |
| `name` | TEXT NOT NULL | Restaurant name |
| `address` | TEXT | Street address |
| `phone` | TEXT | Contact phone number |
| `website` | TEXT | Restaurant website URL |
| `cow_reviews` | TEXT | HappyCow reviews page URL |
| `description` | TEXT | Restaurant description |
| `category` | TEXT | Food category (e.g., "Asian", "Western") |
| `price_range` | TEXT | Price level ("Inexpensive", "Moderate", "Expensive") |
| `rating` | DECIMAL(4,2) | Average rating (0.0-5.0) |
| `review_count` | INTEGER | Number of reviews |
| `latitude` | DECIMAL(10,8) | GPS latitude |
| `longitude` | DECIMAL(11,8) | GPS longitude |
| `is_vegan` | BOOLEAN | True if vegan restaurant |
| `is_vegetarian` | BOOLEAN | True if vegetarian restaurant |
| `has_veg_options` | BOOLEAN | True if has vegetarian options |
| `features` | TEXT[] | Array of features (e.g., "outdoor seating", "delivery") |
| `hours` | TEXT | Opening hours |
| `images_links` | TEXT[] | Array of restaurant image URLs |
| `happycow_url` | TEXT | Original HappyCow URL |
| `scraped_at` | TIMESTAMP | When data was scraped |
| `created_at` | TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | Last update time |

#### `scraping_progress` - Session tracking
| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PRIMARY KEY | Session ID |
| `session_id` | VARCHAR(255) UNIQUE | Unique session identifier |
| `total_sectors` | INTEGER | Total sectors to process |
| `completed_sectors` | INTEGER | Sectors completed |
| `started_at` | TIMESTAMP | Session start time |
| `completed_at` | TIMESTAMP | Session completion time |
| `is_completed` | BOOLEAN | Whether session is finished |

### Constraints & Indexes

#### Unique Constraints
- `unique_restaurant_location` on `(latitude, longitude)` - Prevents duplicate restaurants at same location

#### Indexes
- `idx_restaurants_name` on `name`
- `idx_restaurants_rating` on `rating`
- `idx_restaurants_is_vegan` on `is_vegan`
- `idx_restaurants_is_vegetarian` on `is_vegetarian`
- `idx_restaurants_has_veg_options` on `has_veg_options`
- `idx_restaurants_scraped_at` on `scraped_at`
- `idx_restaurants_latitude` on `latitude`
- `idx_restaurants_longitude` on `longitude`

## Data Models

### Restaurant Model (Pydantic)
```python
class Restaurant(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    cow_reviews: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price_range: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_vegan: bool = False
    is_vegetarian: bool = False
    has_veg_options: bool = False
    features: List[str] = Field(default_factory=list)
    hours: Optional[str] = None
    images_links: List[str] = Field(default_factory=list)
    happycow_url: Optional[str] = None
    scraped_at: datetime = Field(default_factory=datetime.now)
```

## Usage Examples

### Check Database Status
```bash
python main.py test
```

### Scrape Restaurants
```bash
# Scrape all sectors
python main.py scrape

# Scrape specific number of sectors
python main.py scrape --max 10

# Scrape specific region
python main.py scrape --region central
```

### Enhance Restaurant Data
```bash
# Enhance all restaurants
python main.py enhance

# Enhance specific number
python main.py enhance --limit 50

# Enhance specific restaurant
python main.py enhance --id 500

# Start from specific ID
python main.py enhance --start-id 300
```

### Session Management
```bash
# List active sessions
python main.py list-sessions

# Resume interrupted session
python main.py resume SESSION_ID
```

### Database Maintenance
```bash
# Clear all data
python main.py clear-db

# Clear data and sessions
python main.py clear-db --include-sessions
```

## Configuration

### Environment Variables
```bash
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Enhancement Configuration
ENHANCE_DELAY_BETWEEN_PAGES=3  # Delay between page requests (seconds)
```

## Data Quality

### Duplicate Prevention
- **Location-based**: Unique constraint on `(latitude, longitude)`
- **Automatic**: Database prevents duplicate restaurants at same location
- **Smart**: Allows restaurants with same name at different locations

### Data Validation
- **Coordinates**: Required for all restaurants
- **Names**: Required, cannot be empty
- **Types**: Boolean fields for restaurant categories
- **Arrays**: Features and images stored as PostgreSQL arrays

### Enhancement Logic
- **Smart Filtering**: Only enhances restaurants missing 2+ fields
- **Comprehensive**: Extracts phone, address, description, category, price_range, rating, review_count, hours, features, images
- **Resumable**: Can resume interrupted enhancement sessions

## Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check environment variables
echo $SUPABASE_URL
echo $SUPABASE_KEY

# Test connection
python main.py test
```

#### Enhancement Too Slow
```bash
# Reduce delay (not recommended)
ENHANCE_DELAY_BETWEEN_PAGES=1 python main.py enhance --limit 10

# Use smaller batches
python main.py enhance --limit 5
```

#### CAPTCHA Issues
```bash
# Increase delay
ENHANCE_DELAY_BETWEEN_PAGES=5 python main.py enhance --limit 10

# Use start-id to resume
python main.py enhance --start-id 500
```

### Performance Tips

1. **Batch Processing**: Use `--limit` for smaller batches
2. **Resume Capability**: Use `--start-id` to resume from specific points
3. **Targeted Enhancement**: Use `--id` for specific restaurants
4. **Session Management**: Use `list-sessions` and `resume` for interrupted jobs

## File Structure

```
database/
├── README.md                    # This documentation
├── setup_fresh_database.sql    # Complete database setup script
└── check_restaurants.py       # Database status checker
```

## Support

For issues or questions:
1. Check the main README.md
2. Review configuration in config.py
3. Test database connection with `python main.py test`
4. Check logs for detailed error messages