"""
Tests for database functionality
"""

import pytest
from database import DatabaseManager
from models import Restaurant
from datetime import datetime


class TestDatabaseManager:
    """Test cases for DatabaseManager"""
    
    def test_database_connection(self, test_env):
        """Test database connection"""
        db_manager = DatabaseManager()
        assert db_manager.supabase is not None
        assert test_env['SUPABASE_URL'] is not None
        assert test_env['SUPABASE_KEY'] is not None
    
    def test_create_tables(self, test_env):
        """Test table creation"""
        db_manager = DatabaseManager()
        if db_manager.supabase:
            result = db_manager.create_tables()
            assert result is True
    
    def test_check_restaurant_exists(self, test_env):
        """Test restaurant existence check"""
        db_manager = DatabaseManager()
        if db_manager.supabase:
            # Test with non-existent restaurant
            exists = db_manager.check_restaurant_exists("Non-existent Restaurant")
            assert exists is False
    
    def test_insert_single_restaurant(self, test_env, mock_restaurant_data):
        """Test inserting a single restaurant"""
        db_manager = DatabaseManager()
        if not db_manager.supabase:
            pytest.skip("No database connection")
        
        # Create Restaurant object
        restaurant = Restaurant(**mock_restaurant_data)
        
        # Insert restaurant
        success, inserted_count, skipped_count = db_manager.insert_restaurants(
            [restaurant], skip_duplicates=False
        )
        
        assert success is True
        assert inserted_count == 1
        assert skipped_count == 0
    
    def test_duplicate_detection(self, test_env, mock_restaurant_data):
        """Test duplicate detection"""
        db_manager = DatabaseManager()
        if not db_manager.supabase:
            pytest.skip("No database connection")
        
        # Create Restaurant object with unique name
        import uuid
        unique_name = f"Test Duplicate Restaurant {uuid.uuid4().hex[:8]}"
        restaurant_data = mock_restaurant_data.copy()
        restaurant_data['name'] = unique_name
        restaurant = Restaurant(**restaurant_data)
        
        # Insert first time
        success1, inserted_count1, skipped_count1 = db_manager.insert_restaurants(
            [restaurant], skip_duplicates=True
        )
        
        # Insert second time (should be skipped)
        success2, inserted_count2, skipped_count2 = db_manager.insert_restaurants(
            [restaurant], skip_duplicates=True
        )
        
        assert success1 is True
        assert success2 is True
        assert inserted_count1 == 1
        assert inserted_count2 == 0
        assert skipped_count2 == 1
    
    def test_get_restaurants(self, test_env):
        """Test retrieving restaurants from database"""
        db_manager = DatabaseManager()
        if not db_manager.supabase:
            pytest.skip("No database connection")
        
        restaurants = db_manager.get_restaurants(limit=5)
        assert isinstance(restaurants, list)
        assert len(restaurants) <= 5
    
    def test_restaurant_data_integrity(self, test_env, mock_restaurant_data):
        """Test that restaurant data is stored correctly"""
        db_manager = DatabaseManager()
        if not db_manager.supabase:
            pytest.skip("No database connection")
        
        # Create and insert restaurant with unique name
        import uuid
        unique_name = f"Test Integrity Restaurant {uuid.uuid4().hex[:8]}"
        restaurant_data = mock_restaurant_data.copy()
        restaurant_data['name'] = unique_name
        restaurant = Restaurant(**restaurant_data)
        
        success, inserted_count, skipped_count = db_manager.insert_restaurants(
            [restaurant], skip_duplicates=False
        )
        
        assert success is True
        assert inserted_count == 1
        
        # Retrieve and verify data by querying for our specific restaurant
        try:
            result = db_manager.supabase.table('restaurants').select('*').eq('name', unique_name).execute()
            if result.data:
                stored_restaurant = result.data[0]
                assert stored_restaurant['name'] == unique_name
                assert stored_restaurant['rating'] == mock_restaurant_data['rating']
                assert stored_restaurant['is_vegan'] == mock_restaurant_data['is_vegan']
            else:
                pytest.fail(f"Restaurant with name '{unique_name}' not found in database")
        except Exception as e:
            pytest.fail(f"Error querying database: {e}")
