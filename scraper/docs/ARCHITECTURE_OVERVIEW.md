# Architecture Overview

This document provides a comprehensive overview of the HappyCow scraper architecture, updated for sector-based scraping, per-sector saving, Supabase-backed resume, and restaurant data enhancement.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    HappyCow Scraper                         │
├─────────────────────────────────────────────────────────────┤
│  Main Entry Point (main.py)                               │
│  ├── Command-line interface                               │
│  ├── Sector orchestration                                 │
│  ├── Session management (list/resume)                     │
│  ├── Enhancement orchestration                            │
│  └── Error handling                                       │
├─────────────────────────────────────────────────────────────┤
│  Core Library (sectorscraper/)                            │
│  ├── sector_grid.py (6x8 grid)                            │
│  ├── url_generator.py (sector URLs)                       │
│  ├── page_loader.py (headless Selenium)                   │
│  ├── data_extractor.py (DOM parsing)                      │
│  ├── sector_scraper.py (per-sector save)                  │
│  ├── session_manager.py (Supabase progress + resume)      │
│  └── reviews_enhancer.py (restaurant enhancement)        │
├─────────────────────────────────────────────────────────────┤
│  Database Layer (database.py)                             │
│  ├── Supabase integration                                 │
│  ├── Restaurant data storage                              │
│  ├── Progress tracking                                    │
│  ├── Duplicate prevention                                 │
│  └── Enhancement filtering                                │
├─────────────────────────────────────────────────────────────┤
│  Data Models (models.py)                                  │
│  ├── Restaurant model                                     │
│  ├── Validation rules                                     │
│  └── Serialization                                        │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. HappyCowSectorScraper (Main Orchestrator)
**File**: `sectorscraper/sector_scraper.py`

**Responsibilities**:
- Coordinates the entire sector-based scraping workflow
- Manages per-sector processing and saving
- Handles session initialization and completion
- Integrates all other components

**Key Methods**:
- `scrape_all_sectors()`: Main scraping method for all sectors
- `scrape_single_sector()`: Process individual sector
- `scrape_sectors_by_region()`: Process specific regions

### 2. SingaporeSectorGrid (Grid Management)
**File**: `sectorscraper/sector_grid.py`

**Responsibilities**:
- Generates 6x8 grid covering Singapore
- Defines sector boundaries and centers
- Manages geographic coordinates
- Handles region-based filtering

**Key Methods**:
- `generate_sectors()`: Create all 48 sectors
- `get_sector_center()`: Get center coordinates for sector
- `get_sectors_by_region()`: Filter sectors by region

### 3. HappyCowURLGenerator (URL Management)
**File**: `sectorscraper/url_generator.py`

**Responsibilities**:
- Builds searchmap URLs for each sector
- Manages URL parameters and coordinates
- Handles URL validation and formatting

**Key Methods**:
- `generate_sector_url()`: Create URL for specific sector
- `build_searchmap_url()`: Construct complete searchmap URL

### 4. HappyCowPageLoader (Page Loading)
**File**: `sectorscraper/page_loader.py`

**Responsibilities**:
- Loads HappyCow searchmap pages using Selenium
- Manages headless Chrome WebDriver
- Handles page loading and waiting
- Manages browser lifecycle

**Key Methods**:
- `load_page()`: Load specific URL
- `wait_for_page_load()`: Wait for page to be ready
- `close()`: Clean up browser resources

### 5. HappyCowDataExtractor (Data Extraction)
**File**: `sectorscraper/data_extractor.py`

**Responsibilities**:
- Extracts restaurant data from loaded pages
- Parses `[data-marker-id]` and `.details.hidden` elements
- Handles coordinate extraction and validation
- Manages data cleaning and normalization

**Key Methods**:
- `extract_restaurants_from_page()`: Main extraction method
- `_extract_restaurant_info_from_card()`: Parse individual restaurant
- `_extract_coordinates()`: Extract lat/lng coordinates

### 6. ReviewsEnhancer (Restaurant Enhancement)
**File**: `sectorscraper/reviews_enhancer.py`

**Responsibilities**:
- Scrapes individual restaurant review pages
- Extracts detailed information (phone, address, description, etc.)
- Handles enhancement data processing
- Manages review page navigation

**Key Methods**:
- `fetch_details()`: Main enhancement method
- `_parse_page()`: Parse review page data
- `_extract_*()`: Individual field extraction methods

### 7. ScrapingSessionManager (Session Management)
**File**: `sectorscraper/session_manager.py`

**Responsibilities**:
- Manages scraping sessions with unique IDs
- Tracks sector progress and completion
- Enables resume functionality
- Handles error recovery

**Key Methods**:
- `start_session()`: Initialize new session
- `resume_session()`: Resume interrupted session
- `update_progress()`: Update session progress
- `complete_session()`: Mark session as completed

## Processing Flow

### 1. Scraping Flow (Sector-based)
```
User Command → Main.py → HappyCowSectorScraper → SessionManager
                ↓
        Create Session ID → Start Progress Tracking
                ↓
    For each sector:
        Generate URL → Load Page → Extract Data → Save to DB → Update Progress
```

### 2. Enhancement Flow (Review Pages)
```
User Command → Main.py → ReviewsEnhancer → DatabaseManager
                ↓
    Fetch incomplete restaurants → For each restaurant:
        Load review page → Extract details → Update database
```

### 3. Session Management
```
Session Start → Track Progress → Handle Interruptions → Resume Capability
```

## Database Schema

### Restaurants Table
```sql
CREATE TABLE restaurants (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    phone TEXT,
    website TEXT,
    cow_reviews TEXT,
    description TEXT,
    category TEXT,
    price_range TEXT,
    rating DECIMAL(4,2),
    review_count INTEGER,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    is_vegan BOOLEAN DEFAULT FALSE,
    is_vegetarian BOOLEAN DEFAULT FALSE,
    has_veg_options BOOLEAN DEFAULT FALSE,
    features TEXT[],
    hours TEXT,
    images_links TEXT[],
    happycow_url TEXT,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(latitude, longitude)  -- Coordinate-based duplicate prevention
);
```

### Progress Tracking Table
```sql
CREATE TABLE scraping_progress (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    total_sectors INTEGER NOT NULL,
    completed_sectors INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    is_completed BOOLEAN DEFAULT FALSE
);
```

## Configuration Management

### Environment Variables
```env
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Scraping
DELAY_BETWEEN_REQUESTS=2
MAX_RETRIES=3
USER_AGENT_ROTATION=True

# Enhancement
ENHANCE_DELAY_BETWEEN_PAGES=3  # Delay between page requests (seconds)

# Batch Processing
DEFAULT_BATCH_SIZE=20
MIN_BATCH_SIZE=5
MAX_BATCH_SIZE=100
```

### Command-Line Options

#### Scraping Commands
```bash
# Scrape all sectors
python main.py scrape

# Scrape specific number of sectors
python main.py scrape --max 10

# Start from specific sector
python main.py scrape --start 5 --max 10

# Scrape specific region
python main.py scrape --region central
```

#### Enhancement Commands
```bash
# Enhance all restaurants
python main.py enhance

# Enhance specific number
python main.py enhance --limit 50

# Enhance specific restaurant
python main.py enhance --id 123

# Start from specific ID
python main.py enhance --start-id 500
```

#### Session Management
```bash
# List available sessions
python main.py list-sessions

# Resume interrupted session
python main.py resume SESSION_ID
```

#### Utility Commands
```bash
# Test database connection
python main.py test

# Clear database and logs
python main.py clear-db

# Clear database, logs, and sessions
python main.py clear-db --include-sessions
```

## Error Handling & Recovery

### Database Errors
- **Connection failures**: Automatic retry with exponential backoff
- **Unique constraint violations**: Graceful handling of duplicates
- **Transaction failures**: Rollback and retry mechanisms

### Scraping Errors
- **Page load failures**: Retry with different strategies
- **Element not found**: Fallback extraction methods
- **Session corruption**: Resume from last successful batch

### Progress Recovery
- **Session tracking**: Unique IDs for each scraping run
- **Batch checkpointing**: Save progress after each batch
- **Resume capability**: Continue from last successful batch

## Performance Considerations

### Memory Management
- **Batch processing**: Process small batches instead of loading everything
- **Resource cleanup**: Proper WebDriver and connection management
- **Progress tracking**: Minimal memory footprint for session data

### Database Performance
- **Batch insertion**: Insert multiple records in single transaction
- **Index optimization**: Fast queries on coordinates and restaurant types
- **Connection pooling**: Efficient database connection management

### Network Optimization
- **Rate limiting**: Respectful scraping with delays
- **Retry logic**: Handle network failures gracefully
- **User agent rotation**: Avoid detection and blocking

## Testing Strategy

### Unit Tests
- **Model validation**: Test Restaurant model creation and validation
- **Database operations**: Test CRUD operations and constraints
- **Parser logic**: Test data extraction and cleaning

### Integration Tests
- **End-to-end scraping**: Test complete scraping workflow
- **Database integration**: Test data persistence and retrieval
- **Session management**: Test progress tracking and resume functionality

### Debug Tools
- **Coordinate extraction**: Test different extraction methods
- **Cluster expansion**: Test map interaction and zooming
- **Batch processing**: Test batch size and progress tracking

## Deployment Considerations

### Environment Setup
- **Python version**: 3.11.5 with specific dependencies
- **Chrome/Chromium**: Required for Selenium WebDriver
- **Supabase account**: Database hosting and management

### Monitoring
- **Log files**: Comprehensive logging in `logs/` directory
- **Progress tracking**: Real-time progress updates
- **Error reporting**: Detailed error messages and stack traces

### Maintenance
- **Session cleanup**: Remove old sessions periodically
- **Database optimization**: Regular maintenance and indexing
- **Log rotation**: Manage log file sizes and retention

## Future Enhancements

### Scalability
- **Distributed scraping**: Multiple instances with shared progress tracking
- **Load balancing**: Distribute scraping load across multiple workers
- **Caching**: Cache extracted data for faster processing

### Features
- **Multi-location support**: Scrape multiple cities or regions
- **Real-time updates**: Live progress monitoring and notifications
- **Data analytics**: Advanced reporting and statistics

### Performance
- **Async processing**: Asynchronous batch processing
- **Parallel extraction**: Concurrent marker extraction
- **Optimized algorithms**: Improved coordinate extraction methods
