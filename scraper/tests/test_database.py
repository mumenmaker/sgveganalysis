"""
Tests for database operations
"""
import pytest
from unittest.mock import Mock, patch
from database import DatabaseManager

def test_database_manager_initialization():
    """Test DatabaseManager initialization"""
    with patch('database.create_client') as mock_create_client:
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        db_manager = DatabaseManager()
        
        assert db_manager.supabase is not None
        mock_create_client.assert_called_once()

def test_database_manager_no_credentials():
    """Test DatabaseManager when credentials are missing"""
    with patch('database.create_client', side_effect=Exception("No credentials")):
        db_manager = DatabaseManager()
        
        assert db_manager.supabase is None

@patch('database.create_client')
def test_create_tables(mock_create_client):
    """Test table creation"""
    mock_client = Mock()
    mock_create_client.return_value = mock_client
    
    db_manager = DatabaseManager()
    result = db_manager.create_tables()
    
    # Should return True if tables already exist or are created successfully
    assert result is True

@patch('database.create_client')
def test_insert_restaurants(mock_create_client, sample_restaurant_data):
    """Test inserting restaurants into database"""
    mock_client = Mock()
    mock_create_client.return_value = mock_client
    
    # Mock the insert operation
    mock_response = Mock()
    mock_response.data = [sample_restaurant_data]
    mock_client.table.return_value.insert.return_value.execute.return_value = mock_response
    
    db_manager = DatabaseManager()
    
    from models import Restaurant
    restaurant = Restaurant(**sample_restaurant_data)
    
    success, inserted_count, skipped_count = db_manager.insert_restaurants([restaurant])
    
    assert success is True
    assert inserted_count == 1
    assert skipped_count == 0
