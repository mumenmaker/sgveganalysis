"""
Tests for scraper functionality
"""

import pytest
from unittest.mock import Mock, patch
from happycow_scraper import HappyCowScraper
from models import Restaurant


class TestHappyCowScraper:
    """Test cases for HappyCowScraper"""
    
    def test_scraper_initialization(self):
        """Test scraper initialization"""
        scraper = HappyCowScraper(enable_resume=False, use_selenium=False)
        assert scraper.session is not None
        assert scraper.use_selenium is False
        assert scraper.progress_tracker is None
    
    def test_scraper_initialization_with_selenium(self):
        """Test scraper initialization with Selenium"""
        scraper = HappyCowScraper(enable_resume=False, use_selenium=True)
        assert scraper.use_selenium is True
        assert scraper.driver is None
    
    def test_scraper_initialization_with_resume(self):
        """Test scraper initialization with resume functionality"""
        scraper = HappyCowScraper(enable_resume=True, use_selenium=False)
        assert scraper.progress_tracker is not None
    
    def test_parse_restaurant_data(self):
        """Test parsing restaurant data"""
        scraper = HappyCowScraper(enable_resume=False, use_selenium=False)
        
        # Test data
        restaurant_data = {
            'name': 'Test Restaurant',
            'address': '123 Test St',
            'rating': 4.5,
            'review_count': 25,
            'type': 'Vegan Restaurant',
            'url': 'https://test.com'
        }
        
        restaurant = scraper.parse_restaurant_data(restaurant_data)
        
        assert restaurant is not None
        assert restaurant.name == 'Test Restaurant'
        assert restaurant.address == '123 Test St'
        assert restaurant.rating == 4.5
        assert restaurant.review_count == 25
        assert restaurant.is_vegan is True  # Should be True because type contains 'Vegan'
    
    def test_parse_restaurant_data_invalid(self):
        """Test parsing invalid restaurant data"""
        scraper = HappyCowScraper(enable_resume=False, use_selenium=False)
        
        # Test with empty data
        restaurant = scraper.parse_restaurant_data({})
        assert restaurant is None
        
        # Test with None
        restaurant = scraper.parse_restaurant_data(None)
        assert restaurant is None
    
    def test_parse_restaurant_data_vegetarian(self):
        """Test parsing vegetarian restaurant data"""
        scraper = HappyCowScraper(enable_resume=False, use_selenium=False)
        
        restaurant_data = {
            'name': 'Test Vegetarian Restaurant',
            'type': 'Vegetarian Restaurant'
        }
        
        restaurant = scraper.parse_restaurant_data(restaurant_data)
        
        assert restaurant is not None
        assert restaurant.is_vegetarian is True
        assert restaurant.is_vegan is False
    
    def test_parse_restaurant_data_veg_options(self):
        """Test parsing restaurant with veg options"""
        scraper = HappyCowScraper(enable_resume=False, use_selenium=False)
        
        restaurant_data = {
            'name': 'Test Restaurant',
            'type': 'Veg-friendly Restaurant'
        }
        
        restaurant = scraper.parse_restaurant_data(restaurant_data)
        
        assert restaurant is not None
        assert restaurant.has_veg_options is True
        assert restaurant.is_vegan is False
        assert restaurant.is_vegetarian is False
    
    @patch('happycow_scraper.requests.Session.get')
    def test_make_request_success(self, mock_get):
        """Test successful HTTP request"""
        scraper = HappyCowScraper(enable_resume=False, use_selenium=False)
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'<html>Test content</html>'
        mock_get.return_value = mock_response
        
        response = scraper.make_request('https://test.com')
        
        assert response is not None
        assert response.status_code == 200
        mock_get.assert_called_once()
    
    @patch('happycow_scraper.requests.Session.get')
    def test_make_request_failure(self, mock_get):
        """Test failed HTTP request"""
        scraper = HappyCowScraper(enable_resume=False, use_selenium=False)
        
        # Mock failed response with requests exception
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection error")
        
        response = scraper.make_request('https://test.com')
        
        assert response is None
    
    def test_get_headers(self):
        """Test header generation"""
        scraper = HappyCowScraper(enable_resume=False, use_selenium=False)
        
        headers = scraper.get_headers()
        
        assert 'User-Agent' in headers
        assert 'Accept' in headers
        assert 'Accept-Language' in headers
        assert headers['Accept'] == 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    
    def test_selenium_setup(self):
        """Test Selenium setup (without actually starting browser)"""
        scraper = HappyCowScraper(enable_resume=False, use_selenium=True)
        
        # Test setup method exists
        assert hasattr(scraper, 'setup_selenium')
        assert hasattr(scraper, 'close_selenium')
    
    def test_selenium_disabled(self):
        """Test Selenium when disabled"""
        scraper = HappyCowScraper(enable_resume=False, use_selenium=False)
        
        driver = scraper.setup_selenium()
        assert driver is None
