"""
Pytest configuration and fixtures for HappyCow scraper tests
"""

import os
import sys
import pytest
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the scraper modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

@pytest.fixture
def test_env():
    """Ensure test environment variables are loaded"""
    load_dotenv()
    return {
        'SUPABASE_URL': os.getenv('SUPABASE_URL'),
        'SUPABASE_KEY': os.getenv('SUPABASE_KEY')
    }

@pytest.fixture
def mock_restaurant_data():
    """Mock restaurant data for testing"""
    return {
        'name': 'Test Vegan Restaurant',
        'address': '123 Test Street, Singapore',
        'phone': '+65 1234 5678',
        'website': 'https://test-restaurant.com',
        'description': 'A test vegan restaurant',
        'cuisine_type': 'Vegan',
        'price_range': '$$',
        'rating': 4.5,
        'review_count': 25,
        'is_vegan': True,
        'is_vegetarian': False,
        'has_veg_options': False,
        'latitude': 1.3521,
        'longitude': 103.8198,
        'features': ['WiFi', 'Outdoor Seating'],
        'hours': 'Mon-Sun: 9:00 AM - 10:00 PM',
        'happycow_url': 'https://www.happycow.net/reviews/test-restaurant'
    }
