# Project Organization

This document describes the organization of the HappyCow Singapore Restaurant Scraper project.

## Folder Structure

### 📁 `database/` - Database Setup Files
Contains all files related to database setup and management:
- `create_tables.sql` - Basic table creation script
- `setup_fresh_database.sql` - Complete database setup with constraints
- `DATABASE_SETUP.md` - Database setup guide
- `check_database_data.py` - Database verification script

### 📁 `debug/` - Debug and Analysis Files
Contains debugging and analysis scripts:
- `debug_coordinates.py` - Coordinate extraction debugging
- `debug_page_structure.py` - Page structure analysis
- `debug_coordinate_mapping.py` - Coordinate mapping analysis
- `analyze_html.py` - HTML analysis tools
- `check_database.py` - Database checking utilities
- `test_coordinate_fix.py` - Coordinate testing
- `quick_coordinate_test.py` - Quick coordinate tests
- `test_xpath_fix.py` - XPath selector testing

### 📁 `examples/` - Example Usage Files
Contains example scripts showing how to use the scraper:
- `example_usage.py` - Basic usage examples
- `resume_example.py` - Resume functionality examples

### 📁 `tests/` - Test Files
Contains all test files organized by functionality:
- `test_scraper.py` - Scraper functionality tests
- `test_database.py` - Database operation tests
- `test_models.py` - Data model tests
- `test_integration.py` - Integration tests
- Various other test files for specific components

### 📁 `logs/` - Runtime Logs and Data
Contains runtime logs and data files:
- `scraper.log` - Scraper execution logs
- `scraping_progress.json` - Progress tracking data
- `singapore_restaurants.json` - Scraped restaurant data
- `test_*.json` - Test data files

### 📁 `docs/` - Documentation Files
Contains all project documentation:
- `README.md` - Full project documentation
- `PROJECT_ORGANIZATION.md` - Project structure guide
- `COORDINATE_AND_DUPLICATE_FIXES.md` - Fix documentation
- `COORDINATE_UNIQUE_CONSTRAINT.md` - Constraint documentation

## Core Files (Root Directory)

### Main Application Files
- `main.py` - Main scraper script
- `happycow_scraper.py` - Core scraping logic
- `database.py` - Database operations
- `models.py` - Data models
- `config.py` - Configuration
- `progress_tracker.py` - Progress tracking

### Configuration Files
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (not in git)
- `.gitignore` - Git ignore rules
- `pytest.ini` - Pytest configuration
- `run_tests.py` - Test runner script

### Documentation
- `README.md` - Main project documentation
- `COORDINATE_AND_DUPLICATE_FIXES.md` - Fix documentation
- `COORDINATE_UNIQUE_CONSTRAINT.md` - Constraint documentation
- `PROJECT_ORGANIZATION.md` - This file

## Benefits of This Organization

1. **Clear Separation**: Database, debug, and example files are clearly separated
2. **Easy Navigation**: Related files are grouped together
3. **Maintainability**: Easier to find and maintain specific functionality
4. **Clean Root**: The root directory contains only core application files
5. **Documentation**: Each folder has a clear purpose and documentation

## Usage

- **For database setup**: Use files in `database/` folder
- **For debugging**: Use files in `debug/` folder
- **For examples**: Use files in `examples/` folder
- **For testing**: Use files in `tests/` folder
- **For logs and data**: Check files in `logs/` folder
- **For documentation**: Use files in `docs/` folder
- **For main usage**: Use files in root directory
