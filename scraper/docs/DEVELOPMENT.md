# Development Guide

## Setup Development Environment

### Prerequisites
- Python 3.11.5
- pip
- pytest (for testing)
- Chrome/Chromium (for Selenium)
- Supabase account (for database)

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v
```

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for functions and classes
- Keep functions small and focused

### Debugging

- Use the `debug/` folder for temporary debugging scripts
- Remove debug scripts once issues are resolved
- Use logging for production debugging

### Project Structure

```
scraper/
├── tests/                    # Test files
├── debug/                    # Debug scripts (temporary)
├── docs/                     # Documentation
├── database/                 # Database setup and utilities
├── hcowscraper/             # Core scraping library
│   ├── veggiemap_scraper.py # Main scraper class
│   ├── marker_extractor.py  # Marker extraction logic
│   ├── restaurant_parser.py # Restaurant data parsing
│   ├── cluster_handler.py   # Map cluster expansion
│   └── batch_progress_tracker.py # Batch processing & progress tracking
├── models.py                 # Data models
├── database.py               # Database operations
├── config.py                 # Configuration with batch settings
└── main.py                   # Entry point with batch processing
```

## Architecture Overview

### Core Components

1. **VeggiemapScraper**: Main orchestrator class
   - Coordinates marker extraction and restaurant parsing
   - Manages batch processing workflow
   - Handles progress tracking and session management

2. **MarkerExtractor**: Handles map interaction and coordinate extraction
   - Loads HappyCow veggiemap pages
   - Performs cluster expansion and zooming
   - Extracts coordinates using multiple methods

3. **RestaurantParser**: Converts marker data to Restaurant objects
   - Parses marker data into structured restaurant information
   - Validates coordinates and required fields
   - Handles data cleaning and normalization

4. **BatchProgressTracker**: Manages batch processing and progress tracking
   - Tracks scraping sessions with unique IDs
   - Saves progress after each batch
   - Enables resume functionality for interrupted scrapes

5. **ClusterHandler**: Manages map cluster expansion
   - Systematically zooms in to reveal individual markers
   - Handles different zoom levels and marker types
   - Extracts individual restaurant coordinates

### Batch Processing Flow

1. **Initialize**: Create session and start progress tracking
2. **Extract**: Get all markers from the veggiemap
3. **Process**: Split markers into batches and process each batch
4. **Insert**: Save each batch to database immediately
5. **Track**: Update progress after each batch
6. **Complete**: Mark session as completed

### Database Schema

- **restaurants**: Main data table with restaurant information
- **scraping_progress**: Progress tracking with session management
- **Unique constraints**: Prevent duplicate restaurants by coordinates
