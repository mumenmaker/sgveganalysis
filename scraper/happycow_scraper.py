#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean HappyCow Scraper - Database Components Only
Ready for new veggiemap implementation
"""
import logging
import os
from typing import List, Dict, Optional
from models import Restaurant
from progress_tracker import ProgressTracker

class HappyCowScraper:
    def __init__(self, enable_resume: bool = True):
        self.progress_tracker = ProgressTracker() if enable_resume else None
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def parse_restaurant_data(self, restaurant_data: Dict) -> Optional[Restaurant]:
        """Parse restaurant data into Restaurant model"""
        try:
            if not restaurant_data or not restaurant_data.get('name'):
                return None
                
            # Extract coordinates
            lat = restaurant_data.get('latitude')
            lng = restaurant_data.get('longitude')
            latitude = float(lat) if lat else None
            longitude = float(lng) if lng else None
            
            # Create Restaurant object
            restaurant = Restaurant(
                name=restaurant_data.get('name', ''),
                address=restaurant_data.get('address', ''),
                phone=restaurant_data.get('phone', ''),
                website=restaurant_data.get('website', ''),
                description=restaurant_data.get('description', ''),
                cuisine_type=restaurant_data.get('cuisine_type', ''),
                price_range=restaurant_data.get('price_range', ''),
                rating=restaurant_data.get('rating'),
                review_count=restaurant_data.get('review_count'),
                is_vegan=restaurant_data.get('is_vegan', False),
                is_vegetarian=restaurant_data.get('is_vegetarian', False),
                has_veg_options=restaurant_data.get('has_veg_options', False),
                latitude=latitude,
                longitude=longitude,
                features=restaurant_data.get('features', []),
                hours=restaurant_data.get('hours', ''),
                happycow_url=restaurant_data.get('url', '')
            )
            
            return restaurant
            
        except Exception as e:
            self.logger.error(f"Error parsing restaurant data: {e}")
            return None
    
    def save_to_json(self, restaurants: List[Restaurant], filename: str = 'logs/singapore_restaurants.json', append: bool = True):
        """Save restaurants to JSON file"""
        try:
            # Ensure logs directory exists
            os.makedirs('logs', exist_ok=True)
            
            # Convert restaurants to dictionaries
            restaurant_dicts = [restaurant.model_dump() for restaurant in restaurants]
            
            if append and os.path.exists(filename):
                # Load existing data
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except:
                    existing_data = []
                
                # Add new restaurants, avoiding duplicates
                existing_names = {r.get('name') for r in existing_data}
                new_restaurants = [r for r in restaurant_dicts if r.get('name') not in existing_names]
                restaurant_dicts = existing_data + new_restaurants
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(restaurant_dicts, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Saved {len(restaurant_dicts)} restaurants to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving to JSON: {e}")
    
    def scrape_singapore_restaurants(self, resume: bool = True, max_pages: int = 50) -> List[Restaurant]:
        """
        Main scraping method - TO BE IMPLEMENTED
        This will be replaced with the new veggiemap scraper
        """
        self.logger.info("Scraping method not yet implemented - ready for new veggiemap implementation")
        return []
