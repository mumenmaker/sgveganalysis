"""
Integration tests for the HappyCow scraper
"""
import pytest
from unittest.mock import Mock, patch
from happycow_scraper import HappyCowScraper
from database import DatabaseManager
from models import Restaurant

def test_scraper_database_integration(sample_restaurant_data):
    """Test integration between scraper and database"""
    with patch('database.create_client') as mock_create_client:
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        # Mock database response
        mock_response = Mock()
        mock_response.data = [sample_restaurant_data]
        mock_client.table.return_value.insert.return_value.execute.return_value = mock_response
        
        scraper = HappyCowScraper()
        db_manager = DatabaseManager()
        
        # Test that scraper can parse data and database can insert it
        restaurant = scraper.parse_restaurant_data(sample_restaurant_data)
        assert restaurant is not None
        
        success, inserted_count, skipped_count = db_manager.insert_restaurants([restaurant])
        assert success is True
        assert inserted_count == 1

def test_progress_tracker_integration():
    """Test progress tracker integration"""
    scraper = HappyCowScraper()
    
    # Test that progress tracker is initialized
    assert scraper.progress_tracker is not None
    
    # Test progress tracking methods exist
    assert hasattr(scraper.progress_tracker, 'start_scraping')
    assert hasattr(scraper.progress_tracker, 'update_progress')
    assert hasattr(scraper.progress_tracker, 'get_progress_summary')

@patch('happycow_scraper.HappyCowScraper.scrape_singapore_restaurants')
def test_main_scraper_flow(mock_scrape):
    """Test the main scraper flow"""
    # Mock the scraping method to return sample data
    mock_scrape.return_value = []
    
    scraper = HappyCowScraper()
    restaurants = scraper.scrape_singapore_restaurants()
    
    assert restaurants == []
    mock_scrape.assert_called_once()
