"""
Main Sector Scraper for HappyCow SearchMap
Coordinates the scraping of all 48 sectors
"""

import time
import logging
from typing import List, Dict, Optional
from .sector_grid import SingaporeSectorGrid
from .url_generator import HappyCowURLGenerator
from .page_loader import HappyCowPageLoader
from .data_extractor import HappyCowDataExtractor

class HappyCowSectorScraper:
    """Main scraper that coordinates scraping all sectors"""
    
    def __init__(self, headless: bool = True, delay_between_sectors: int = 2):
        self.logger = logging.getLogger(__name__)
        self.headless = headless
        self.delay_between_sectors = delay_between_sectors
        
        # Initialize components
        self.sector_grid = SingaporeSectorGrid()
        self.url_generator = HappyCowURLGenerator()
        self.page_loader = HappyCowPageLoader(headless=headless)
        
        # Scraping state
        self.scraped_sectors = []
        self.failed_sectors = []
        self.total_restaurants = 0
    
    def scrape_all_sectors(self, start_sector: int = 0, max_sectors: Optional[int] = None, save_to_db: bool = True) -> List[Dict]:
        """Scrape all sectors and optionally save to database after each sector"""
        try:
            self.logger.info("Starting comprehensive sector scraping")
            
            # Generate all sectors
            sectors = self.sector_grid.generate_sectors()
            
            # Apply limits
            if max_sectors:
                sectors = sectors[start_sector:start_sector + max_sectors]
            else:
                sectors = sectors[start_sector:]
            
            self.logger.info(f"Scraping {len(sectors)} sectors (starting from sector {start_sector + 1})")
            
            all_restaurants = []
            
            for i, sector in enumerate(sectors):
                sector_num = start_sector + i + 1
                self.logger.info(f"Processing sector {sector_num}/{len(sectors) + start_sector}: {sector['name']}")
                
                try:
                    # Scrape this sector
                    sector_restaurants = self._scrape_single_sector(sector)
                    
                    if sector_restaurants:
                        all_restaurants.extend(sector_restaurants)
                        self.scraped_sectors.append(sector)
                        self.total_restaurants += len(sector_restaurants)
                        self.logger.info(f"Sector {sector_num} completed: {len(sector_restaurants)} restaurants")
                        
                        # Save to database immediately if requested
                        if save_to_db:
                            self._save_sector_to_database(sector_restaurants, sector_num)
                    else:
                        self.logger.warning(f"Sector {sector_num} returned no restaurants")
                        self.failed_sectors.append(sector)
                    
                    # Delay between sectors
                    if i < len(sectors) - 1:
                        time.sleep(self.delay_between_sectors)
                        
                except Exception as e:
                    self.logger.error(f"Error scraping sector {sector_num}: {e}")
                    self.failed_sectors.append(sector)
                    continue
            
            self.logger.info(f"Scraping completed: {len(all_restaurants)} total restaurants from {len(self.scraped_sectors)} sectors")
            return all_restaurants
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive sector scraping: {e}")
            return []
        finally:
            self.page_loader.close_driver()
    
    def scrape_single_sector(self, sector: Dict) -> List[Dict]:
        """Scrape a single sector"""
        return self._scrape_single_sector(sector)
    
    def _scrape_single_sector(self, sector: Dict) -> List[Dict]:
        """Internal method to scrape a single sector"""
        try:
            # Generate URL for this sector
            url = self.url_generator.generate_sector_url(sector)
            if not url:
                self.logger.error(f"Failed to generate URL for sector {sector['name']}")
                return []
            
            # Load the page
            if not self.page_loader.load_sector_page(url):
                self.logger.error(f"Failed to load page for sector {sector['name']}")
                return []
            
            # Extract restaurant data
            extractor = HappyCowDataExtractor(self.page_loader.driver)
            restaurants = extractor.extract_restaurants_from_page()
            
            if restaurants:
                self.logger.info(f"Extracted {len(restaurants)} restaurants from {sector['name']}")
                return restaurants
            else:
                self.logger.warning(f"No restaurants found in {sector['name']}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error scraping sector {sector['name']}: {e}")
            return []
    
    def _save_sector_to_database(self, restaurants: List[Dict], sector_num: int) -> bool:
        """Save a sector's restaurants to the database immediately"""
        try:
            from database import DatabaseManager
            from models import Restaurant
            
            db_manager = DatabaseManager()
            if not db_manager.supabase:
                self.logger.error("No database connection available")
                return False
            
            # Convert to Restaurant models
            restaurant_models = []
            for restaurant_data in restaurants:
                try:
                    restaurant = Restaurant(
                        name=restaurant_data.get('name', 'Unknown Restaurant'),
                        address=restaurant_data.get('address', 'Address not available'),
                        latitude=restaurant_data.get('latitude'),
                        longitude=restaurant_data.get('longitude'),
                        phone=restaurant_data.get('phone', ''),
                        website=restaurant_data.get('website', ''),
                        rating=restaurant_data.get('rating', 0.0),
                        price_range=restaurant_data.get('price_range', ''),
                        cuisine_type=restaurant_data.get('cuisine_type', ''),
                        hours=restaurant_data.get('hours', ''),
                        description=restaurant_data.get('description', ''),
                        is_vegan=restaurant_data.get('is_vegan', False),
                        is_vegetarian=restaurant_data.get('is_vegetarian', False),
                        has_veg_options=restaurant_data.get('has_veg_options', False)
                    )
                    restaurant_models.append(restaurant)
                except Exception as e:
                    self.logger.warning(f"Skipping invalid restaurant data: {e}")
                    continue
            
            if not restaurant_models:
                self.logger.warning(f"No valid restaurant models to save for sector {sector_num}")
                return False
            
            # Insert restaurants
            success, inserted, skipped = db_manager.insert_restaurants(restaurant_models)
            
            if success:
                self.logger.info(f"Sector {sector_num} saved to database: {inserted} inserted, {skipped} skipped")
                return True
            else:
                self.logger.error(f"Failed to save sector {sector_num} to database")
                return False
                
        except Exception as e:
            self.logger.error(f"Error saving sector {sector_num} to database: {e}")
            return False
    
    def scrape_sectors_by_region(self, region: str, save_to_db: bool = True) -> List[Dict]:
        """Scrape sectors in a specific region"""
        try:
            self.logger.info(f"Scraping sectors in region: {region}")
            
            # Get sectors for this region
            sectors = self.sector_grid.get_sectors_by_region(region)
            if not sectors:
                self.logger.warning(f"No sectors found for region: {region}")
                return []
            
            self.logger.info(f"Found {len(sectors)} sectors in {region}")
            
            all_restaurants = []
            
            for i, sector in enumerate(sectors):
                self.logger.info(f"Processing {region} sector {i+1}/{len(sectors)}: {sector['name']}")
                
                try:
                    sector_restaurants = self._scrape_single_sector(sector)
                    if sector_restaurants:
                        all_restaurants.extend(sector_restaurants)
                        self.scraped_sectors.append(sector)
                        self.total_restaurants += len(sector_restaurants)
                        
                        # Save to database immediately if requested
                        if save_to_db:
                            self._save_sector_to_database(sector_restaurants, i+1)
                    
                    # Delay between sectors
                    if i < len(sectors) - 1:
                        time.sleep(self.delay_between_sectors)
                        
                except Exception as e:
                    self.logger.error(f"Error scraping {region} sector {sector['name']}: {e}")
                    self.failed_sectors.append(sector)
                    continue
            
            self.logger.info(f"Region {region} completed: {len(all_restaurants)} restaurants from {len(sectors)} sectors")
            return all_restaurants
            
        except Exception as e:
            self.logger.error(f"Error scraping region {region}: {e}")
            return []
        finally:
            self.page_loader.close_driver()
    
    def get_scraping_summary(self) -> Dict:
        """Get a summary of the scraping results"""
        return {
            'total_sectors_processed': len(self.scraped_sectors),
            'failed_sectors': len(self.failed_sectors),
            'total_restaurants': self.total_restaurants,
            'scraped_sectors': [s['name'] for s in self.scraped_sectors],
            'failed_sector_names': [s['name'] for s in self.failed_sectors]
        }
    
    def print_scraping_summary(self):
        """Print a summary of the scraping results"""
        summary = self.get_scraping_summary()
        
        print("\n" + "="*60)
        print("SCRAPING SUMMARY")
        print("="*60)
        print(f"Total Sectors Processed: {summary['total_sectors_processed']}")
        print(f"Failed Sectors: {summary['failed_sectors']}")
        print(f"Total Restaurants: {summary['total_restaurants']}")
        
        if summary['scraped_sectors']:
            print(f"\nSuccessfully Scraped Sectors:")
            for sector in summary['scraped_sectors']:
                print(f"  ✅ {sector}")
        
        if summary['failed_sector_names']:
            print(f"\nFailed Sectors:")
            for sector in summary['failed_sector_names']:
                print(f"  ❌ {sector}")
        
        print("="*60)


if __name__ == "__main__":
    # Test the sector scraper
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Test with a few sectors
    scraper = HappyCowSectorScraper(headless=False, delay_between_sectors=1)
    
    print("Testing HappyCow Sector Scraper")
    print("="*50)
    
    try:
        # Test single sector
        print("\n1. Testing single sector scraping...")
        grid = SingaporeSectorGrid()
        sectors = grid.generate_sectors()
        test_sector = sectors[0]
        
        restaurants = scraper.scrape_single_sector(test_sector)
        if restaurants:
            print(f"✅ Single sector test: {len(restaurants)} restaurants")
        else:
            print("❌ Single sector test: No restaurants found")
        
        # Test small batch
        print("\n2. Testing small batch scraping...")
        restaurants = scraper.scrape_all_sectors(start_sector=0, max_sectors=3)
        if restaurants:
            print(f"✅ Batch test: {len(restaurants)} restaurants")
        else:
            print("❌ Batch test: No restaurants found")
        
        # Print summary
        scraper.print_scraping_summary()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        scraper.page_loader.close_driver()
