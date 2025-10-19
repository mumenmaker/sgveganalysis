"""
Integration tests for the complete scraper workflow
"""

import pytest
import os
import tempfile
import json
from unittest.mock import patch, Mock
from happycow_scraper import HappyCowScraper
from database import DatabaseManager


class TestIntegration:
    """Integration tests for the complete scraper workflow"""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_full_scraper_workflow(self, test_env):
        """Test the complete scraper workflow (requires database)"""
        if not test_env['SUPABASE_URL'] or not test_env['SUPABASE_KEY']:
            pytest.skip("No database credentials available")
        
        # Initialize components
        scraper = HappyCowScraper(enable_resume=False, use_selenium=False)
        db_manager = DatabaseManager()
        
        if not db_manager.supabase:
            pytest.skip("No database connection")
        
        # Test database setup
        assert db_manager.create_tables() is True
        
        # Test scraper initialization
        assert scraper.session is not None
        assert scraper.use_selenium is False
    
    @pytest.mark.integration
    def test_json_save_and_load(self, mock_restaurant_data):
        """Test saving and loading restaurants to/from JSON"""
        scraper = HappyCowScraper(enable_resume=False, use_selenium=False)
        
        # Create test restaurant
        from models import Restaurant
        restaurant = Restaurant(**mock_restaurant_data)
        
        # Test JSON save
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            scraper.save_to_json([restaurant], temp_file, append=False)
            
            # Verify file was created and contains data
            assert os.path.exists(temp_file)
            
            with open(temp_file, 'r') as f:
                data = json.load(f)
                assert len(data) == 1
                assert data[0]['name'] == mock_restaurant_data['name']
                assert data[0]['rating'] == mock_restaurant_data['rating']
        
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    @pytest.mark.integration
    def test_progress_tracking(self):
        """Test progress tracking functionality"""
        scraper = HappyCowScraper(enable_resume=True, use_selenium=False)
        
        # Test progress tracker initialization
        assert scraper.progress_tracker is not None
        
        # Test progress tracking methods
        scraper.progress_tracker.start_scraping()
        scraper.progress_tracker.add_scraped_restaurant("Test Restaurant")
        scraper.progress_tracker.update_progress(1, 0)
        
        # Verify progress data
        progress = scraper.progress_tracker.get_progress_summary()
        assert "1" in progress  # Should contain the scraped count
    
    @pytest.mark.integration
    def test_restaurant_data_flow(self, mock_restaurant_data):
        """Test the complete data flow from raw data to database"""
        scraper = HappyCowScraper(enable_resume=False, use_selenium=False)
        
        # Test parsing raw data
        restaurant = scraper.parse_restaurant_data(mock_restaurant_data)
        assert restaurant is not None
        assert restaurant.name == mock_restaurant_data['name']
        
        # Test dictionary conversion
        restaurant_dict = restaurant.dict()
        assert isinstance(restaurant_dict, dict)
        assert restaurant_dict['name'] == mock_restaurant_data['name']
    
    @pytest.mark.integration
    @pytest.mark.selenium
    def test_selenium_integration(self):
        """Test Selenium integration (without actually starting browser)"""
        scraper = HappyCowScraper(enable_resume=False, use_selenium=True)
        
        # Test Selenium setup methods exist
        assert hasattr(scraper, 'setup_selenium')
        assert hasattr(scraper, 'close_selenium')
        assert hasattr(scraper, 'scrape_with_selenium')
        
        # Test that Selenium is disabled when use_selenium=False
        scraper_no_selenium = HappyCowScraper(enable_resume=False, use_selenium=False)
        driver = scraper_no_selenium.setup_selenium()
        assert driver is None
    
    @pytest.mark.integration
    def test_error_handling(self):
        """Test error handling in the scraper"""
        scraper = HappyCowScraper(enable_resume=False, use_selenium=False)
        
        # Test with invalid data
        restaurant = scraper.parse_restaurant_data(None)
        assert restaurant is None
        
        restaurant = scraper.parse_restaurant_data({})
        assert restaurant is None
        
        # Test with malformed data
        malformed_data = {
            'name': 'Test',
            'rating': 'invalid_rating'  # Should be a number
        }
        restaurant = scraper.parse_restaurant_data(malformed_data)
        # Should still create restaurant but with default values
        assert restaurant is not None
        assert restaurant.name == 'Test'
    
    @pytest.mark.integration
    def test_configuration_loading(self):
        """Test configuration loading"""
        from config import Config
        
        # Test that configuration values are loaded
        assert Config.BASE_URL is not None
        assert Config.SEARCH_URL is not None
        assert Config.SINGAPORE_PARAMS is not None
        assert 's' in Config.SINGAPORE_PARAMS
        assert 'location' in Config.SINGAPORE_PARAMS
    
    @pytest.mark.integration
    def test_duplicate_handling(self, mock_restaurant_data):
        """Test duplicate handling in JSON save"""
        scraper = HappyCowScraper(enable_resume=False, use_selenium=False)
        
        from models import Restaurant
        restaurant = Restaurant(**mock_restaurant_data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            # Save first time
            scraper.save_to_json([restaurant], temp_file, append=False)
            
            # Save second time (should handle duplicates)
            scraper.save_to_json([restaurant], temp_file, append=True)
            
            # Verify only one restaurant in file
            with open(temp_file, 'r') as f:
                data = json.load(f)
                assert len(data) == 1  # Should still be 1, not 2
        
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
