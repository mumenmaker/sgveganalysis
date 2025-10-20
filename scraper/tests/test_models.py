"""
Tests for the Restaurant model
"""
import pytest
from models import Restaurant

def test_restaurant_creation(sample_restaurant_data):
    """Test creating a Restaurant object with valid data"""
    restaurant = Restaurant(**sample_restaurant_data)
    
    assert restaurant.name == 'Test Vegan Restaurant'
    assert restaurant.is_vegan == True
    assert restaurant.latitude == 1.3521
    assert restaurant.longitude == 103.8198
    assert len(restaurant.features) == 2

def test_restaurant_required_fields():
    """Test that Restaurant requires a name"""
    with pytest.raises(ValueError):
        Restaurant()

def test_restaurant_optional_fields():
    """Test that Restaurant works with minimal data"""
    restaurant = Restaurant(name="Test Restaurant")
    
    assert restaurant.name == "Test Restaurant"
    assert restaurant.address is None
    assert restaurant.is_vegan == False
    assert restaurant.latitude is None
    assert restaurant.longitude is None

def test_restaurant_model_dump(sample_restaurant_data):
    """Test that model_dump() works correctly"""
    restaurant = Restaurant(**sample_restaurant_data)
    data = restaurant.model_dump()
    
    assert data['name'] == 'Test Vegan Restaurant'
    assert data['is_vegan'] == True
    assert data['latitude'] == 1.3521
