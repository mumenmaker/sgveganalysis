#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Restaurant Parser for HappyCow Data
Handles parsing and validation of restaurant data extracted from markers
"""

import re
import logging
from typing import Dict, Optional, List
from models import Restaurant

class RestaurantParser:
    """Parse and validate restaurant data from HappyCow markers"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def parse_marker_data(self, marker_data: Dict) -> Optional[Restaurant]:
        """Parse marker data into Restaurant object"""
        try:
            if not marker_data:
                return None
            
            # Extract basic information
            name = self._extract_name(marker_data)
            if not name:
                self.logger.warning("No restaurant name found in marker data")
                return None
            
            # Extract coordinates
            latitude = marker_data.get('latitude')
            longitude = marker_data.get('longitude')
            
            if latitude is None or longitude is None:
                self.logger.warning(f"No coordinates found for restaurant: {name}")
                return None
            
            # Create Restaurant object
            restaurant = Restaurant(
                name=name,
                address=self._extract_address(marker_data),
                phone=self._extract_phone(marker_data),
                website=self._extract_website(marker_data),
                description=self._extract_description(marker_data),
                cuisine_type=self._extract_cuisine_type(marker_data),
                price_range=self._extract_price_range(marker_data),
                rating=self._extract_rating(marker_data),
                review_count=self._extract_review_count(marker_data),
                is_vegan=self._extract_is_vegan(marker_data),
                is_vegetarian=self._extract_is_vegetarian(marker_data),
                has_veg_options=self._extract_has_veg_options(marker_data),
                latitude=float(latitude),
                longitude=float(longitude),
                features=self._extract_features(marker_data),
                hours=self._extract_hours(marker_data),
                happycow_url=self._extract_happycow_url(marker_data)
            )
            
            self.logger.debug(f"Successfully parsed restaurant: {name}")
            return restaurant
            
        except Exception as e:
            self.logger.error(f"Error parsing marker data: {e}")
            return None
    
    def _extract_name(self, data: Dict) -> Optional[str]:
        """Extract restaurant name"""
        # Try multiple possible name fields
        name_fields = ['name', 'title', 'restaurant_name', 'popup_text']
        
        for field in name_fields:
            if field in data and data[field]:
                name = str(data[field]).strip()
                if name and len(name) > 2:  # Basic validation
                    return name
        
        return None
    
    def _extract_address(self, data: Dict) -> Optional[str]:
        """Extract restaurant address"""
        address_fields = ['address', 'location', 'address_text']
        
        for field in address_fields:
            if field in data and data[field]:
                address = str(data[field]).strip()
                if address and len(address) > 5:  # Basic validation
                    return address
        
        return None
    
    def _extract_phone(self, data: Dict) -> Optional[str]:
        """Extract phone number"""
        phone_fields = ['phone', 'telephone', 'contact']
        
        for field in phone_fields:
            if field in data and data[field]:
                phone = str(data[field]).strip()
                # Basic phone validation
                if re.search(r'[\+]?[0-9\s\-\(\)]{7,}', phone):
                    return phone
        
        return None
    
    def _extract_website(self, data: Dict) -> Optional[str]:
        """Extract website URL"""
        website_fields = ['website', 'url', 'web', 'site']
        
        for field in website_fields:
            if field in data and data[field]:
                website = str(data[field]).strip()
                # Basic URL validation
                if re.match(r'https?://', website):
                    return website
        
        return None
    
    def _extract_description(self, data: Dict) -> Optional[str]:
        """Extract restaurant description"""
        desc_fields = ['description', 'desc', 'about', 'info']
        
        for field in desc_fields:
            if field in data and data[field]:
                desc = str(data[field]).strip()
                if desc and len(desc) > 10:  # Basic validation
                    return desc
        
        return None
    
    def _extract_cuisine_type(self, data: Dict) -> Optional[str]:
        """Extract cuisine type"""
        cuisine_fields = ['cuisine', 'cuisine_type', 'type', 'category']
        
        for field in cuisine_fields:
            if field in data and data[field]:
                cuisine = str(data[field]).strip()
                if cuisine and len(cuisine) > 2:
                    return cuisine
        
        return None
    
    def _extract_price_range(self, data: Dict) -> Optional[str]:
        """Extract price range"""
        price_fields = ['price', 'price_range', 'cost', 'budget']
        
        for field in price_fields:
            if field in data and data[field]:
                price = str(data[field]).strip()
                if price and len(price) > 0:
                    return price
        
        return None
    
    def _extract_rating(self, data: Dict) -> Optional[float]:
        """Extract rating"""
        rating_fields = ['rating', 'score', 'stars', 'rate']
        
        for field in rating_fields:
            if field in data and data[field]:
                try:
                    rating = float(data[field])
                    if 0 <= rating <= 5:  # Valid rating range
                        return rating
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def _extract_review_count(self, data: Dict) -> Optional[int]:
        """Extract review count"""
        review_fields = ['review_count', 'reviews', 'num_reviews', 'review_count']
        
        for field in review_fields:
            if field in data and data[field]:
                try:
                    count = int(data[field])
                    if count >= 0:
                        return count
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def _extract_is_vegan(self, data: Dict) -> bool:
        """Extract vegan status"""
        vegan_indicators = [
            'is_vegan', 'vegan', 'vegan_status', 'vegan_only'
        ]
        
        for field in vegan_indicators:
            if field in data:
                value = data[field]
                if isinstance(value, bool):
                    return value
                elif isinstance(value, str):
                    return value.lower() in ['true', 'yes', '1', 'vegan']
        
        # Check for vegan keywords in text
        text_fields = ['name', 'description', 'popup_text', 'cuisine_type']
        for field in text_fields:
            if field in data and data[field]:
                text = str(data[field]).lower()
                if 'vegan' in text and 'vegetarian' not in text:
                    return True
        
        return False
    
    def _extract_is_vegetarian(self, data: Dict) -> bool:
        """Extract vegetarian status"""
        veg_indicators = [
            'is_vegetarian', 'vegetarian', 'veg_status', 'vegetarian_only'
        ]
        
        for field in veg_indicators:
            if field in data:
                value = data[field]
                if isinstance(value, bool):
                    return value
                elif isinstance(value, str):
                    return value.lower() in ['true', 'yes', '1', 'vegetarian']
        
        # Check for vegetarian keywords in text
        text_fields = ['name', 'description', 'popup_text', 'cuisine_type']
        for field in text_fields:
            if field in data and data[field]:
                text = str(data[field]).lower()
                if 'vegetarian' in text and 'vegan' not in text:
                    return True
        
        return False
    
    def _extract_has_veg_options(self, data: Dict) -> bool:
        """Extract veg options status"""
        veg_options_indicators = [
            'has_veg_options', 'veg_options', 'vegetarian_options', 'vegan_options'
        ]
        
        for field in veg_options_indicators:
            if field in data:
                value = data[field]
                if isinstance(value, bool):
                    return value
                elif isinstance(value, str):
                    return value.lower() in ['true', 'yes', '1']
        
        # Check for veg options keywords in text
        text_fields = ['description', 'popup_text', 'features']
        for field in text_fields:
            if field in data and data[field]:
                text = str(data[field]).lower()
                if any(keyword in text for keyword in ['veg options', 'vegetarian options', 'vegan options']):
                    return True
        
        return False
    
    def _extract_features(self, data: Dict) -> List[str]:
        """Extract restaurant features"""
        features = []
        
        # Look for features in various fields
        feature_fields = ['features', 'amenities', 'facilities', 'services']
        
        for field in feature_fields:
            if field in data and data[field]:
                if isinstance(data[field], list):
                    features.extend(data[field])
                elif isinstance(data[field], str):
                    # Split by common separators
                    feature_list = re.split(r'[,;|]', data[field])
                    features.extend([f.strip() for f in feature_list if f.strip()])
        
        # Remove duplicates and empty strings
        unique_features = list(set([f for f in features if f]))
        return unique_features
    
    def _extract_hours(self, data: Dict) -> Optional[str]:
        """Extract operating hours"""
        hours_fields = ['hours', 'opening_hours', 'schedule', 'time']
        
        for field in hours_fields:
            if field in data and data[field]:
                hours = str(data[field]).strip()
                if hours and len(hours) > 5:  # Basic validation
                    return hours
        
        return None
    
    def _extract_happycow_url(self, data: Dict) -> Optional[str]:
        """Extract HappyCow URL"""
        url_fields = ['url', 'happycow_url', 'link', 'page_url']
        
        for field in url_fields:
            if field in data and data[field]:
                url = str(data[field]).strip()
                if url and ('happycow' in url.lower() or url.startswith('http')):
                    return url
        
        return None
    
    def parse_multiple_markers(self, markers_data: List[Dict]) -> List[Restaurant]:
        """Parse multiple markers into Restaurant objects"""
        restaurants = []
        
        for marker_data in markers_data:
            try:
                restaurant = self.parse_marker_data(marker_data)
                if restaurant:
                    restaurants.append(restaurant)
            except Exception as e:
                self.logger.warning(f"Error parsing marker: {e}")
                continue
        
        self.logger.info(f"Successfully parsed {len(restaurants)} restaurants from {len(markers_data)} markers")
        return restaurants
