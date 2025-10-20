# Architecture Overview

This document provides a comprehensive overview of the HappyCow scraper architecture, updated for sector-based scraping, per-sector saving, and Supabase-backed resume.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    HappyCow Scraper                         │
├─────────────────────────────────────────────────────────────┤
│  Main Entry Point (main.py)                               │
│  ├── Command-line interface                               │
│  ├── Sector orchestration                                 │
│  ├── Session management (list/resume)                     │
│  └── Error handling                                       │
├─────────────────────────────────────────────────────────────┤
│  Core Library (sectorscraper/)                            │
│  ├── sector_grid.py (6x8 grid)                            │
│  ├── url_generator.py (sector URLs)                       │
│  ├── page_loader.py (headless Selenium)                   │
│  ├── data_extractor.py (DOM parsing)                      │
│  ├── sector_scraper.py (per-sector save)                  │
│  └── session_manager.py (Supabase progress + resume)      │
├─────────────────────────────────────────────────────────────┤
│  Database Layer (database.py)                             │
│  ├── Supabase integration                                 │
│  ├── Restaurant data storage                              │
│  ├── Progress tracking                                    │
│  └── Duplicate prevention                                 │
├─────────────────────────────────────────────────────────────┤
│  Data Models (models.py)                                  │
│  ├── Restaurant model                                     │
│  ├── Validation rules                                     │
│  └── Serialization                                        │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. VeggiemapScraper (Main Orchestrator)
**File**: `hcowscraper/veggiemap_scraper.py`

**Responsibilities**:
- Coordinates the entire scraping workflow
- Manages batch processing logic
- Handles session initialization and completion
- Integrates all other components

**Key Methods**:
- `scrape_singapore_restaurants()`: Main scraping method with batch processing
- `scrape_with_coordinates_only()`: Fast coordinate extraction for testing
- `test_database_connection()`: Database connectivity testing

### 2. MarkerExtractor (Map Interaction)
**File**: `hcowscraper/marker_extractor.py`

**Responsibilities**:
- Loads HappyCow veggiemap pages
- Performs cluster expansion and zooming
- Extracts coordinates using multiple methods
- Handles Selenium WebDriver management

**Key Methods**:
- `extract_markers_with_cluster_expansion()`: Main extraction with cluster expansion
- `extract_markers_by_attributes()`: Direct attribute extraction
- `extract_markers_by_page_source()`: Regex-based extraction
- `extract_markers_by_javascript()`: JavaScript-based extraction

### 3. RestaurantParser (Data Processing)
**File**: `hcowscraper/restaurant_parser.py`

**Responsibilities**:
- Converts marker data to Restaurant objects
- Validates coordinates and required fields
- Handles data cleaning and normalization
- Manages batch parsing operations

**Key Methods**:
- `parse_marker_data()`: Parse single marker to Restaurant
- `parse_multiple_markers()`: Parse batch of markers
- `_extract_*()`: Individual field extraction methods

### 4. ClusterHandler (Map Expansion)
**File**: `hcowscraper/cluster_handler.py`

**Responsibilities**:
- Manages systematic map zooming
- Handles cluster expansion logic
- Extracts individual restaurant markers
- Manages zoom level transitions

**Key Methods**:
- `expand_all_clusters()`: Systematic cluster expansion
- `get_individual_markers()`: Extract individual markers
- `_zoom_in()`: Zoom management
- `_get_current_zoom_level()`: Zoom level detection

### 5. BatchProgressTracker (Progress Management)
**File**: `hcowscraper/batch_progress_tracker.py`

**Responsibilities**:
- Manages scraping sessions with unique IDs
- Tracks batch progress and completion
- Enables resume functionality
- Handles error recovery

**Key Methods**:
- `start_scraping_session()`: Initialize new session
- `resume_scraping_session()`: Resume interrupted session
- `process_batch()`: Process and track batch completion
- `complete_scraping_session()`: Mark session as completed

## Batch Processing Flow

### 1. Session Initialization
```
User Command → Main.py → VeggiemapScraper → BatchProgressTracker
                ↓
        Create Session ID → Start Progress Tracking
```

### 2. Marker Extraction
```
VeggiemapScraper → MarkerExtractor → ClusterHandler
        ↓
    Load Page → Zoom In → Extract Coordinates
```

### 3. Batch Processing Loop
```
For each batch:
    Extract batch markers → Parse to restaurants → Insert to database → Update progress
```

### 4. Session Completion
```
All batches processed → Mark session complete → Clean up resources
```

## Database Schema

### Restaurants Table
```sql
CREATE TABLE restaurants (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    -- ... other fields
    UNIQUE(latitude, longitude)  -- Coordinate-based duplicate prevention
);
```

### Progress Tracking Table
```sql
CREATE TABLE scraping_progress (
    id SERIAL PRIMARY KEY,
    session_id TEXT UNIQUE NOT NULL,
    total_restaurants INTEGER,
    processed_restaurants INTEGER,
    current_batch INTEGER,
    total_batches INTEGER,
    batch_size INTEGER,
    is_completed BOOLEAN,
    error_message TEXT
);
```

## Configuration Management

### Environment Variables
```env
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Batch Processing
DEFAULT_BATCH_SIZE=20
MIN_BATCH_SIZE=5
MAX_BATCH_SIZE=100

# Scraping
DELAY_BETWEEN_REQUESTS=2
MAX_RETRIES=3
USER_AGENT_ROTATION=True
```

### Command-Line Options
```bash
python main.py scrape --batch-size 50
python main.py scrape --resume SESSION_ID
python main.py list-sessions
python main.py clear-db
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
