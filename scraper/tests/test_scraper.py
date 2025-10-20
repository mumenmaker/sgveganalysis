"""
Tests for the HappyCow scraper
"""
import pytest
from unittest.mock import Mock, patch
from hcowscraper import VeggiemapScraper

def test_scraper_initialization():
    """Test scraper initialization"""
    scraper = VeggiemapScraper()
    
    assert hasattr(scraper, 'logger')
    assert hasattr(scraper, 'marker_extractor')
    assert hasattr(scraper, 'restaurant_parser')

def test_scraper_initialization_without_database():
    """Test scraper initialization without database"""
    scraper = VeggiemapScraper(enable_database=False)
    
    assert scraper.db_manager is None

def test_restaurant_parser_valid(sample_restaurant_data):
    """Test parsing valid restaurant data"""
    scraper = VeggiemapScraper()
    restaurant = scraper.restaurant_parser.parse_marker_data(sample_restaurant_data)
    
    assert restaurant is not None
    assert restaurant.name == 'Test Vegan Restaurant'
    assert restaurant.is_vegan == True

def test_restaurant_parser_invalid():
    """Test parsing invalid restaurant data"""
    scraper = VeggiemapScraper()
    
    # Test with empty data
    restaurant = scraper.restaurant_parser.parse_marker_data({})
    assert restaurant is None
    
    # Test with None
    restaurant = scraper.restaurant_parser.parse_marker_data(None)
    assert restaurant is None
    
    # Test with missing name
    restaurant = scraper.restaurant_parser.parse_marker_data({'address': '123 Test St'})
    assert restaurant is None

def test_restaurant_parser_coordinates():
    """Test parsing restaurant data with coordinates"""
    scraper = VeggiemapScraper()
    
    data = {
        'name': 'Test Restaurant',
        'latitude': 1.3521,
        'longitude': 103.8198
    }
    
    restaurant = scraper.restaurant_parser.parse_marker_data(data)
    
    assert restaurant.latitude == 1.3521
    assert restaurant.longitude == 103.8198

def test_restaurant_parser_no_coordinates():
    """Test parsing restaurant data without coordinates"""
    scraper = VeggiemapScraper()
    
    data = {
        'name': 'Test Restaurant'
    }
    
    restaurant = scraper.restaurant_parser.parse_marker_data(data)
    
    # Restaurant parser requires coordinates, so it should return None
    assert restaurant is None
