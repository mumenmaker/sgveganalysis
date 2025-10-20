"""
Pytest configuration and fixtures for HappyCow scraper tests
"""
import pytest
import os
import sys
from unittest.mock import Mock, patch

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def mock_database():
    """Mock database connection for testing"""
    mock_db = Mock()
    mock_db.supabase = Mock()
    return mock_db

@pytest.fixture
def sample_restaurant_data():
    """Sample restaurant data for testing"""
    return {
        'name': 'Test Vegan Restaurant',
        'address': '123 Test Street, Singapore',
        'phone': '+65 1234 5678',
        'website': 'https://testrestaurant.com',
        'description': 'A test vegan restaurant',
        'cuisine_type': 'Vegan',
        'price_range': '$$',
        'rating': 4.5,
        'review_count': 100,
        'is_vegan': True,
        'is_vegetarian': False,
        'has_veg_options': False,
        'latitude': 1.3521,
        'longitude': 103.8198,
        'features': ['WiFi', 'Outdoor Seating'],
        'hours': 'Mon-Sun: 9AM-10PM',
        'url': 'https://happycow.net/test-restaurant'
    }
