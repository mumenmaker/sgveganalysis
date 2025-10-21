# Batch Processing Guide

This document explains the sector-based processing and progress tracking mechanisms in the HappyCow scraper.

## Overview

The scraper processes restaurants by sectors (geographic regions) to improve reliability, memory efficiency, and enable resume functionality for interrupted scrapes.

## Key Concepts

### Sector-based Processing
- **Grid System**: 6x8 grid covering Singapore (48 sectors total)
- **Per-sector Saving**: Each sector is saved to database immediately
- **Geographic Coverage**: Systematic coverage of all Singapore areas

### Session Management
- **Unique Session IDs**: Each scraping run gets a unique identifier
- **Progress Tracking**: Saves progress after each sector
- **Resume Capability**: Continue interrupted sessions from where they left off

### Database Integration
- **Immediate Insertion**: Each sector is saved to database immediately
- **Progress Tables**: Tracks session progress and sector completion
- **Error Recovery**: Handles database errors gracefully

## Usage

### Basic Sector Processing

```bash
# Process all sectors (48 total)
python main.py scrape

# Process specific number of sectors
python main.py scrape --max 10

# Start from specific sector
python main.py scrape --start 5 --max 10

# Process specific region
python main.py scrape --region central
```

### Session Management

```bash
# List available sessions
python main.py list-sessions

# Resume interrupted session
python main.py scrape --resume 09c36afe-d17b-4bb9-802e-ba5fbb042a28

# Clear all sessions and start fresh
python main.py clear-db
```

## Configuration

### Environment Variables

```env
# Batch processing settings
DEFAULT_BATCH_SIZE=20
MIN_BATCH_SIZE=5
MAX_BATCH_SIZE=100
```

### Command-Line Options

- `--max N`: Set maximum number of sectors to process
- `--start N`: Start from specific sector number
- `--region REGION`: Process specific region only
- `--resume SESSION_ID`: Resume interrupted session
- `list-sessions`: List available sessions
- `clear-db`: Clear database and sessions

## Architecture

### Batch Processing Flow

1. **Initialize Session**
   - Create unique session ID
   - Start progress tracking
   - Set up batch parameters

2. **Extract Markers**
   - Load HappyCow veggiemap
   - Extract all restaurant markers
   - Count total markers for batching

3. **Process Batches**
   - Split markers into batches
   - Process each batch sequentially
   - Insert batch to database immediately
   - Update progress tracking

4. **Complete Session**
   - Mark session as completed
   - Save final progress
   - Clean up resources

### Progress Tracking

The `scraping_progress` table tracks:
- Session ID and metadata
- Total restaurants and batches
- Current batch and progress
- Completion status
- Error messages

### Database Schema

```sql
-- Progress tracking table
CREATE TABLE scraping_progress (
    id SERIAL PRIMARY KEY,
    session_id TEXT UNIQUE NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    total_restaurants INTEGER DEFAULT 0,
    processed_restaurants INTEGER DEFAULT 0,
    current_batch INTEGER DEFAULT 0,
    total_batches INTEGER DEFAULT 0,
    batch_size INTEGER DEFAULT 20,
    is_completed BOOLEAN DEFAULT FALSE,
    error_message TEXT
);
```

## Benefits

### Reliability
- **Fault Tolerance**: Interrupted scrapes can be resumed
- **Progress Tracking**: Know exactly where the scraper stopped
- **Error Recovery**: Handle database errors gracefully

### Performance
- **Memory Efficiency**: Process small batches instead of loading everything
- **Database Performance**: Insert in manageable chunks
- **Resource Management**: Better control over system resources

### Usability
- **Session Management**: Track multiple scraping attempts
- **Resume Functionality**: Continue interrupted work
- **Progress Visibility**: See real-time progress updates

## Best Practices

### Batch Size Selection
- **Small batches (5-10)**: For testing or unstable connections
- **Medium batches (20-50)**: For normal operation
- **Large batches (50-100)**: For stable, high-performance systems

### Session Management
- **Regular cleanup**: Remove old sessions periodically
- **Monitor progress**: Check session status regularly
- **Resume promptly**: Don't let interrupted sessions sit too long

### Error Handling
- **Monitor logs**: Watch for batch processing errors
- **Check database**: Verify data integrity
- **Use debug commands**: Test components individually

## Troubleshooting

### Common Issues

1. **Batch processing fails**
   - Check batch size is within limits
   - Verify database connection
   - Check session status

2. **Cannot resume session**
   - Verify session ID is correct
   - Check if session was completed
   - Use `list-sessions` to see available sessions

3. **Memory issues**
   - Reduce batch size
   - Monitor system resources
   - Clear old sessions

### Debug Commands

```bash
# Test batch processing
python main.py scrape --batch-size 5

# Check session status
python main.py list-sessions

# Test database connection
python main.py test

# Clear and start fresh
python main.py clear-db
```

## Examples

### Basic Scraping
```bash
# Start new scraping session
python main.py scrape

# Check progress
python main.py list-sessions

# Resume if interrupted
python main.py scrape --resume SESSION_ID
```

### Custom Configuration
```bash
# Large batch for fast processing
python main.py scrape --batch-size 100

# Small batch for testing
python main.py scrape --batch-size 5

# Resume with different batch size
python main.py scrape --resume SESSION_ID --batch-size 30
```

### Session Management
```bash
# List all sessions
python main.py list-sessions

# Clear all data and start fresh
python main.py clear-db

# Test without database
python main.py test-coords
```
