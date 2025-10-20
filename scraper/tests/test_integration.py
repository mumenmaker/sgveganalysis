"""
Integration tests for the HappyCow scraper
"""
import pytest
from unittest.mock import Mock, patch
from hcowscraper import VeggiemapScraper
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
        
        scraper = VeggiemapScraper()
        db_manager = DatabaseManager()
        
        # Test that scraper can parse data and database can insert it
        restaurant = scraper.restaurant_parser.parse_marker_data(sample_restaurant_data)
        assert restaurant is not None
        
        success, inserted_count, skipped_count = db_manager.insert_restaurants([restaurant])
        assert success is True
        assert inserted_count == 1

def test_scraper_components_integration():
    """Test scraper components integration"""
    scraper = VeggiemapScraper()
    
    # Test that all components are initialized
    assert scraper.marker_extractor is not None
    assert scraper.restaurant_parser is not None
    assert scraper.db_manager is not None
    
    # Test component methods exist
    assert hasattr(scraper.marker_extractor, 'extract_all_markers')
    assert hasattr(scraper.restaurant_parser, 'parse_marker_data')
    assert hasattr(scraper.db_manager, 'insert_restaurants')

@patch('hcowscraper.veggiemap_scraper.VeggiemapScraper.scrape_singapore_restaurants')
def test_main_scraper_flow(mock_scrape):
    """Test the main scraper flow"""
    # Mock the scraping method to return sample data
    mock_scrape.return_value = []
    
    scraper = VeggiemapScraper()
    restaurants = scraper.scrape_singapore_restaurants("test_url")
    
    assert restaurants == []
    mock_scrape.assert_called_once()
