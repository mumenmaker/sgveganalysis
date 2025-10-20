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
from .batch_progress_tracker import BatchProgressTracker
from models import Restaurant
from database import DatabaseManager
from config import Config

class VeggiemapScraper:
    """Main scraper for HappyCow veggiemap"""
    
    def __init__(self, headless: bool = True, enable_database: bool = True, batch_size: int = None):
        self.headless = headless
        self.enable_database = enable_database
        self.batch_size = batch_size or Config.DEFAULT_BATCH_SIZE
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.marker_extractor = MarkerExtractor(headless=headless)
        self.restaurant_parser = RestaurantParser()
        self.db_manager = DatabaseManager() if enable_database else None
        self.progress_tracker = None
        
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
    
    def scrape_singapore_restaurants(self, url: str, use_cluster_expansion: bool = True, resume_session: str = None) -> List[Restaurant]:
        """Scrape Singapore restaurants from veggiemap with batch processing"""
        try:
            self.logger.info(f"Starting Singapore restaurant scraping from: {url}")
            
            # Initialize progress tracker
            if self.enable_database and self.db_manager:
                self.progress_tracker = BatchProgressTracker(self.db_manager, self.batch_size)
                
                # Resume existing session if provided
                if resume_session:
                    if not self.progress_tracker.resume_scraping_session(resume_session):
                        self.logger.warning(f"Could not resume session {resume_session}, starting new session")
                        resume_session = None
                else:
                    resume_session = None
            
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
            
            # Step 2: Start progress tracking
            if self.progress_tracker and not resume_session:
                if not self.progress_tracker.start_scraping_session(len(markers_data)):
                    self.logger.warning("Failed to start progress tracking, continuing without it")
                    self.progress_tracker = None
            
            # Step 3: Process markers in batches
            self.logger.info(f"Step 3: Processing {len(markers_data)} markers in batches of {self.batch_size}")
            all_restaurants = []
            total_inserted = 0
            total_skipped = 0
            
            for i in range(0, len(markers_data), self.batch_size):
                batch_markers = markers_data[i:i + self.batch_size]
                batch_num = (i // self.batch_size) + 1
                
                self.logger.info(f"Processing batch {batch_num}: markers {i+1}-{min(i+self.batch_size, len(markers_data))}")
                
                # Parse batch of markers
                batch_restaurants = self.restaurant_parser.parse_multiple_markers(batch_markers)
                
                if batch_restaurants:
                    # Process batch (insert to database if enabled)
                    if self.progress_tracker:
                        success, inserted_count, skipped_count = self.progress_tracker.process_batch(batch_restaurants)
                        if success:
                            total_inserted += inserted_count
                            total_skipped += skipped_count
                        else:
                            self.logger.error(f"Failed to process batch {batch_num}")
                            break
                    else:
                        # No progress tracking, just collect restaurants
                        all_restaurants.extend(batch_restaurants)
                    
                    self.logger.info(f"Batch {batch_num} completed: {len(batch_restaurants)} restaurants processed")
                else:
                    self.logger.warning(f"Batch {batch_num}: No restaurants could be parsed from {len(batch_markers)} markers")
                
                # Small delay between batches to avoid overwhelming the database
                if i + self.batch_size < len(markers_data):
                    time.sleep(1)
            
            # Step 4: Complete progress tracking
            if self.progress_tracker:
                self.progress_tracker.complete_scraping_session()
                progress_summary = self.progress_tracker.get_progress_summary()
                self.logger.info(f"Scraping completed: {progress_summary['processed_restaurants']}/{progress_summary['total_restaurants']} restaurants processed")
            
            # Step 5: Display summary
            if self.progress_tracker:
                self._display_batch_summary(total_inserted, total_skipped)
            else:
                self._display_summary(all_restaurants)
            
            return all_restaurants if not self.progress_tracker else []
            
        except Exception as e:
            self.logger.error(f"Error in Singapore restaurant scraping: {e}")
            if self.progress_tracker:
                self.progress_tracker._record_error(str(e))
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
    
    def _display_batch_summary(self, total_inserted: int, total_skipped: int):
        """Display batch processing summary"""
        self.logger.info("=== BATCH PROCESSING SUMMARY ===")
        self.logger.info(f"Total inserted: {total_inserted}")
        self.logger.info(f"Total skipped (duplicates): {total_skipped}")
        self.logger.info(f"Batch size: {self.batch_size}")
        self.logger.info("=================================")
    
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
