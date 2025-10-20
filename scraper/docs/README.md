# Documentation

This folder contains comprehensive documentation for the HappyCow scraper project with batch processing and progress tracking.

## Contents

- `README.md` - This file (overview)
- `DEVELOPMENT.md` - Development setup and guidelines
- `TROUBLESHOOTING.md` - Common issues and solutions
- `BATCH_PROCESSING.md` - Batch processing and progress tracking guide
- `ARCHITECTURE_OVERVIEW.md` - Comprehensive system architecture documentation

## Quick Start

1. See the main `README.md` in the project root for basic usage
2. Check `DEVELOPMENT.md` for setting up the development environment
3. Read `BATCH_PROCESSING.md` for understanding batch processing features
4. Review `ARCHITECTURE_OVERVIEW.md` for system architecture details
5. Refer to `TROUBLESHOOTING.md` if you encounter issues

## Key Features

### Batch Processing
- **Configurable batch sizes** (5-100 restaurants per batch)
- **Progress tracking** with session management
- **Resume functionality** for interrupted scrapes
- **Memory efficient** processing

### Veggiemap Integration
- **Interactive map scraping** from HappyCow's veggiemap
- **Cluster expansion** to extract individual restaurants
- **Multiple extraction methods** for reliable data collection
- **Coordinate validation** and deduplication

### Database Integration
- **Supabase integration** with proper schema
- **Progress tracking tables** for session management
- **Unique constraints** to prevent duplicates
- **Batch insertion** for better performance

## Contributing

When adding new features or fixing bugs, please update the relevant documentation files.
