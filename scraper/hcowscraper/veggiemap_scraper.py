#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veggiemap Scraper for HappyCow
Main scraper class that coordinates marker extraction and restaurant parsing
"""

import logging
import time
from typing import List, Optional, Dict
from .marker_extractor import MarkerExtractor
from .restaurant_parser import RestaurantParser
from models import Restaurant
from database import DatabaseManager

class VeggiemapScraper:
    """Main scraper for HappyCow veggiemap"""
    
    def __init__(self, headless: bool = True, enable_database: bool = True):
        self.headless = headless
        self.enable_database = enable_database
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.marker_extractor = MarkerExtractor(headless=headless)
        self.restaurant_parser = RestaurantParser()
        self.db_manager = DatabaseManager() if enable_database else None
        
        # Setup logging
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def scrape_singapore_restaurants(self, url: str, use_cluster_expansion: bool = True) -> List[Restaurant]:
        """Scrape Singapore restaurants from veggiemap"""
        try:
            self.logger.info(f"Starting Singapore restaurant scraping from: {url}")
            
            # Step 1: Extract markers from the map
            self.logger.info("Step 1: Extracting markers from veggiemap...")
            
            if use_cluster_expansion:
                self.logger.info("Using cluster expansion method to get individual restaurants...")
                markers_data = self.marker_extractor.extract_markers_with_cluster_expansion(url)
            else:
                self.logger.info("Using standard extraction method...")
                markers_data = self.marker_extractor.extract_all_markers(url)
            
            if not markers_data:
                self.logger.warning("No markers found on the veggiemap")
                return []
            
            self.logger.info(f"Found {len(markers_data)} markers on the map")
            
            # Step 2: Parse markers into Restaurant objects
            self.logger.info("Step 2: Parsing markers into restaurant data...")
            restaurants = self.restaurant_parser.parse_multiple_markers(markers_data)
            
            if not restaurants:
                self.logger.warning("No restaurants could be parsed from markers")
                return []
            
            self.logger.info(f"Successfully parsed {len(restaurants)} restaurants")
            
            # Step 3: Save to database if enabled
            if self.enable_database and self.db_manager and self.db_manager.supabase:
                self.logger.info("Step 3: Saving restaurants to database...")
                success, inserted_count, skipped_count = self.db_manager.insert_restaurants(restaurants)
                
                if success:
                    self.logger.info(f"Database operation completed: {inserted_count} inserted, {skipped_count} skipped")
                else:
                    self.logger.error("Failed to save restaurants to database")
            else:
                self.logger.info("Database saving disabled or not available")
            
            # Step 4: Display summary
            self._display_summary(restaurants)
            
            return restaurants
            
        except Exception as e:
            self.logger.error(f"Error in Singapore restaurant scraping: {e}")
            return []
        finally:
            # Clean up
            self.marker_extractor.close_driver()
    
    def scrape_with_coordinates_only(self, url: str) -> List[Dict]:
        """Scrape only coordinates from markers (faster, for testing)"""
        try:
            self.logger.info(f"Scraping coordinates only from: {url}")
            
            if not self.marker_extractor.load_veggiemap_page(url):
                return []
            
            # Try different extraction methods
            coordinates = []
            
            # Method 1: Direct attributes
            coords_1 = self.marker_extractor.extract_markers_by_attributes()
            coordinates.extend(coords_1)
            
            # Method 2: JavaScript access
            coords_2 = self.marker_extractor.extract_markers_by_javascript()
            coordinates.extend(coords_2)
            
            # Remove duplicates
            unique_coordinates = self.marker_extractor._remove_duplicate_coordinates(coordinates)
            
            self.logger.info(f"Found {len(unique_coordinates)} unique coordinates")
            return unique_coordinates
            
        except Exception as e:
            self.logger.error(f"Error scraping coordinates: {e}")
            return []
        finally:
            self.marker_extractor.close_driver()
    
    def test_database_connection(self) -> bool:
        """Test database connection"""
        try:
            if not self.db_manager or not self.db_manager.supabase:
                self.logger.error("Database manager not available")
                return False
            
            # Try a simple query
            result = self.db_manager.supabase.table('restaurants').select('id').limit(1).execute()
            self.logger.info("Database connection test successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Database connection test failed: {e}")
            return False
    
    def _display_summary(self, restaurants: List[Restaurant]):
        """Display scraping summary"""
        if not restaurants:
            self.logger.info("No restaurants to display")
            return
        
        # Count by type
        vegan_count = sum(1 for r in restaurants if r.is_vegan)
        vegetarian_count = sum(1 for r in restaurants if r.is_vegetarian)
        veg_options_count = sum(1 for r in restaurants if r.has_veg_options)
        
        # Count with coordinates
        with_coords = sum(1 for r in restaurants if r.latitude and r.longitude)
        
        self.logger.info("=== SCRAPING SUMMARY ===")
        self.logger.info(f"Total restaurants: {len(restaurants)}")
        self.logger.info(f"With coordinates: {with_coords}")
        self.logger.info(f"Vegan restaurants: {vegan_count}")
        self.logger.info(f"Vegetarian restaurants: {vegetarian_count}")
        self.logger.info(f"Restaurants with veg options: {veg_options_count}")
        
        # Show sample restaurants
        self.logger.info("\nSample restaurants:")
        for i, restaurant in enumerate(restaurants[:5], 1):
            coord_status = "✅" if restaurant.latitude and restaurant.longitude else "❌"
            vegan_status = "🌱" if restaurant.is_vegan else "🥗" if restaurant.is_vegetarian else "🍽️"
            self.logger.info(f"  {i}. {restaurant.name} {vegan_status} {coord_status}")
    
    def get_restaurant_statistics(self) -> Dict:
        """Get statistics about scraped restaurants"""
        try:
            if not self.db_manager or not self.db_manager.supabase:
                return {"error": "Database not available"}
            
            # Get total count
            total_result = self.db_manager.supabase.table('restaurants').select('id', count='exact').execute()
            total_count = total_result.count if hasattr(total_result, 'count') else len(total_result.data)
            
            # Get count with coordinates
            coord_result = self.db_manager.supabase.table('restaurants').select('id', count='exact').not_.is_('latitude', 'null').not_.is_('longitude', 'null').execute()
            coord_count = coord_result.count if hasattr(coord_result, 'count') else len(coord_result.data)
            
            # Get vegan count
            vegan_result = self.db_manager.supabase.table('restaurants').select('id', count='exact').eq('is_vegan', True).execute()
            vegan_count = vegan_result.count if hasattr(vegan_result, 'count') else len(vegan_result.data)
            
            return {
                "total_restaurants": total_count,
                "with_coordinates": coord_count,
                "vegan_restaurants": vegan_count,
                "coordinate_coverage": (coord_count / total_count * 100) if total_count > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {"error": str(e)}
