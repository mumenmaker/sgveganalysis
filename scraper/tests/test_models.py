"""
Tests for data models
"""

import pytest
from datetime import datetime
from models import Restaurant


class TestRestaurant:
    """Test cases for Restaurant model"""
    
    def test_restaurant_creation(self):
        """Test creating a Restaurant object"""
        restaurant = Restaurant(
            name="Test Restaurant",
            address="123 Test St",
            rating=4.5,
            review_count=25,
            is_vegan=True
        )
        
        assert restaurant.name == "Test Restaurant"
        assert restaurant.address == "123 Test St"
        assert restaurant.rating == 4.5
        assert restaurant.review_count == 25
        assert restaurant.is_vegan is True
        assert restaurant.is_vegetarian is False
        assert restaurant.has_veg_options is False
    
    def test_restaurant_creation_minimal(self):
        """Test creating a Restaurant with minimal data"""
        restaurant = Restaurant(name="Test Restaurant")
        
        assert restaurant.name == "Test Restaurant"
        assert restaurant.address is None
        assert restaurant.rating is None
        assert restaurant.review_count is None
        assert restaurant.is_vegan is False
        assert restaurant.is_vegetarian is False
        assert restaurant.has_veg_options is False
    
    def test_restaurant_creation_vegetarian(self):
        """Test creating a vegetarian restaurant"""
        restaurant = Restaurant(
            name="Vegetarian Restaurant",
            is_vegetarian=True,
            has_veg_options=True
        )
        
        assert restaurant.is_vegetarian is True
        assert restaurant.has_veg_options is True
        assert restaurant.is_vegan is False
    
    def test_restaurant_creation_veg_options(self):
        """Test creating a restaurant with veg options"""
        restaurant = Restaurant(
            name="Regular Restaurant",
            has_veg_options=True
        )
        
        assert restaurant.has_veg_options is True
        assert restaurant.is_vegan is False
        assert restaurant.is_vegetarian is False
    
    def test_restaurant_dict_conversion(self):
        """Test converting Restaurant to dictionary"""
        restaurant = Restaurant(
            name="Test Restaurant",
            address="123 Test St",
            rating=4.5,
            review_count=25,
            is_vegan=True,
            features=["WiFi", "Outdoor Seating"],
            scraped_at=datetime.now()
        )
        
        restaurant_dict = restaurant.model_dump()
        
        assert isinstance(restaurant_dict, dict)
        assert restaurant_dict['name'] == "Test Restaurant"
        assert restaurant_dict['address'] == "123 Test St"
        assert restaurant_dict['rating'] == 4.5
        assert restaurant_dict['review_count'] == 25
        assert restaurant_dict['is_vegan'] is True
        assert restaurant_dict['features'] == ["WiFi", "Outdoor Seating"]
        assert 'scraped_at' in restaurant_dict
    
    def test_restaurant_validation(self):
        """Test restaurant data validation"""
        # Test with valid data
        restaurant = Restaurant(
            name="Valid Restaurant",
            rating=5.0,
            review_count=100
        )
        assert restaurant.rating == 5.0
        assert restaurant.review_count == 100
        
        # Test with edge case rating
        restaurant = Restaurant(
            name="Edge Case Restaurant",
            rating=0.0,
            review_count=0
        )
        assert restaurant.rating == 0.0
        assert restaurant.review_count == 0
    
    def test_restaurant_coordinates(self):
        """Test restaurant with coordinates"""
        restaurant = Restaurant(
            name="Located Restaurant",
            latitude=1.3521,
            longitude=103.8198
        )
        
        assert restaurant.latitude == 1.3521
        assert restaurant.longitude == 103.8198
    
    def test_restaurant_features(self):
        """Test restaurant with features"""
        features = ["WiFi", "Outdoor Seating", "Parking", "Delivery"]
        restaurant = Restaurant(
            name="Feature-rich Restaurant",
            features=features
        )
        
        assert restaurant.features == features
        assert len(restaurant.features) == 4
    
    def test_restaurant_hours(self):
        """Test restaurant with hours"""
        hours = "Mon-Sun: 9:00 AM - 10:00 PM"
        restaurant = Restaurant(
            name="Open Restaurant",
            hours=hours
        )
        
        assert restaurant.hours == hours
    
    def test_restaurant_urls(self):
        """Test restaurant with URLs"""
        website = "https://restaurant.com"
        happycow_url = "https://happycow.net/restaurant"
        
        restaurant = Restaurant(
            name="URL Restaurant",
            website=website,
            happycow_url=happycow_url
        )
        
        assert restaurant.website == website
        assert restaurant.happycow_url == happycow_url
