# Development Guide

## Setup Development Environment

### Prerequisites
- Python 3.11.5
- pip
- pytest (for testing)
- Chrome/Chromium (for Selenium)

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
├── tests/           # Test files
├── debug/           # Debug scripts (temporary)
├── docs/            # Documentation
├── database/        # Database setup and utilities
├── models.py        # Data models
├── database.py      # Database operations
├── config.py        # Configuration
├── happycow_scraper.py  # Main scraper
├── progress_tracker.py # Progress tracking
└── main.py          # Entry point
```
