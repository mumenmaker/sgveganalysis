"""
Tests for the HappyCow scraper
"""
import pytest
from unittest.mock import Mock, patch
from happycow_scraper import HappyCowScraper

def test_scraper_initialization():
    """Test scraper initialization"""
    scraper = HappyCowScraper()
    
    assert scraper.progress_tracker is not None
    assert hasattr(scraper, 'logger')

def test_scraper_initialization_without_resume():
    """Test scraper initialization without resume functionality"""
    scraper = HappyCowScraper(enable_resume=False)
    
    assert scraper.progress_tracker is None

def test_parse_restaurant_data_valid(sample_restaurant_data):
    """Test parsing valid restaurant data"""
    scraper = HappyCowScraper()
    restaurant = scraper.parse_restaurant_data(sample_restaurant_data)
    
    assert restaurant is not None
    assert restaurant.name == 'Test Vegan Restaurant'
    assert restaurant.is_vegan == True

def test_parse_restaurant_data_invalid():
    """Test parsing invalid restaurant data"""
    scraper = HappyCowScraper()
    
    # Test with empty data
    restaurant = scraper.parse_restaurant_data({})
    assert restaurant is None
    
    # Test with None
    restaurant = scraper.parse_restaurant_data(None)
    assert restaurant is None
    
    # Test with missing name
    restaurant = scraper.parse_restaurant_data({'address': '123 Test St'})
    assert restaurant is None

def test_parse_restaurant_data_coordinates():
    """Test parsing restaurant data with coordinates"""
    scraper = HappyCowScraper()
    
    data = {
        'name': 'Test Restaurant',
        'latitude': '1.3521',
        'longitude': '103.8198'
    }
    
    restaurant = scraper.parse_restaurant_data(data)
    
    assert restaurant.latitude == 1.3521
    assert restaurant.longitude == 103.8198

def test_parse_restaurant_data_no_coordinates():
    """Test parsing restaurant data without coordinates"""
    scraper = HappyCowScraper()
    
    data = {
        'name': 'Test Restaurant'
    }
    
    restaurant = scraper.parse_restaurant_data(data)
    
    assert restaurant.latitude is None
    assert restaurant.longitude is None
