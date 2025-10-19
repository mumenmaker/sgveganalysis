import requests
import time
import logging
import json
import re
import os
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import Config
from models import Restaurant
from progress_tracker import ProgressTracker

class HappyCowScraper:
    def __init__(self, enable_resume: bool = True, use_selenium: bool = True):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.progress_tracker = ProgressTracker() if enable_resume else None
        self.use_selenium = use_selenium
        self.driver = None
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
    
    def setup_selenium(self):
        """Setup Selenium WebDriver"""
        if not self.use_selenium:
            return None
            
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            return self.driver
        except Exception as e:
            self.logger.error(f"Failed to setup Selenium: {e}")
            return None
    
    def close_selenium(self):
        """Close Selenium WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def get_headers(self):
        """Get headers with random user agent"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def make_request(self, url: str, params: Dict = None, retries: int = 0) -> Optional[requests.Response]:
        """Make HTTP request with retry logic and rate limiting"""
        try:
            self.logger.info(f"Making request to: {url}")
            
            response = self.session.get(
                url, 
                params=params, 
                headers=self.get_headers(),
                timeout=30
            )
            response.raise_for_status()
            
            # Rate limiting
            time.sleep(Config.DELAY_BETWEEN_REQUESTS)
            return response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            if retries < Config.MAX_RETRIES:
                self.logger.info(f"Retrying... ({retries + 1}/{Config.MAX_RETRIES})")
                time.sleep(2 ** retries)  # Exponential backoff
                return self.make_request(url, params, retries + 1)
            return None
    
    def scrape_with_selenium(self) -> List[Dict]:
        """Scrape restaurants using Selenium for dynamic content"""
        if not self.use_selenium:
            return []
        
        try:
            self.logger.info("Setting up Selenium WebDriver...")
            driver = self.setup_selenium()
            if not driver:
                return []
            
            # Build URL with parameters
            url = f"{Config.SEARCH_URL}?s={Config.SINGAPORE_PARAMS['s']}&location={Config.SINGAPORE_PARAMS['location']}&lat={Config.SINGAPORE_PARAMS['lat']}&lng={Config.SINGAPORE_PARAMS['lng']}&page={Config.SINGAPORE_PARAMS['page']}&zoom={Config.SINGAPORE_PARAMS['zoom']}&metric={Config.SINGAPORE_PARAMS['metric']}&limit={Config.SINGAPORE_PARAMS['limit']}&order={Config.SINGAPORE_PARAMS['order']}"
            
            self.logger.info(f"Loading page: {url}")
            driver.get(url)
            
            # Wait for page to load and data to be populated
            self.logger.info("Waiting for page to load...")
            time.sleep(10)
            
            # Try to extract coordinates from page source (JavaScript data)
            try:
                page_source = driver.page_source
                # Look for coordinate patterns in JavaScript
                coord_patterns = [
                    r'"lat":\s*(\d+\.\d+),\s*"lng":\s*(\d+\.\d+)',
                    r'"latitude":\s*(\d+\.\d+),\s*"longitude":\s*(\d+\.\d+)',
                    r'lat:\s*(\d+\.\d+),\s*lng:\s*(\d+\.\d+)',
                    r'latitude:\s*(\d+\.\d+),\s*longitude:\s*(\d+\.\d+)'
                ]
                
                page_coordinates = {}
                for pattern in coord_patterns:
                    matches = re.findall(pattern, page_source)
                    if matches:
                        self.logger.info(f"Found {len(matches)} coordinate pairs in page source")
                        page_coordinates = {f"coord_{i}": (float(lat), float(lng)) for i, (lat, lng) in enumerate(matches)}
                        break
            except Exception as e:
                self.logger.warning(f"Error extracting coordinates from page source: {e}")
                page_coordinates = {}
            
            # Try to find restaurant elements using the correct selector
            restaurant_elements = driver.find_elements(By.CSS_SELECTOR, '.venue-item')
            self.logger.info(f"Found {len(restaurant_elements)} restaurant elements")
            
            if not restaurant_elements:
                self.logger.warning("No restaurant elements found with .venue-item selector")
                return []
            
            restaurants = []
            for i, element in enumerate(restaurant_elements):
                try:
                    restaurant_data = {}
                    
                    # Get all text and split by lines
                    full_text = element.text.strip()
                    lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                    
                    if lines:
                        restaurant_data['name'] = lines[0]  # First line is usually the name
                        
                        # Try to extract rating and review count
                        for line_idx, line in enumerate(lines):
                            # Look for rating (usually a decimal number on its own line)
                            if re.match(r'^\d+\.?\d*$', line) and '.' in line:
                                try:
                                    restaurant_data['rating'] = float(line)
                                except ValueError:
                                    pass
                            
                            # Look for review count in parentheses
                            if '(' in line and ')' in line:
                                try:
                                    review_match = re.search(r'\((\d+)\)', line)
                                    if review_match:
                                        restaurant_data['review_count'] = int(review_match.group(1))
                                except ValueError:
                                    pass
                        
                        # Try to extract restaurant type
                        for line in lines:
                            if any(word in line.lower() for word in ['vegan', 'vegetarian', 'veg-friendly', 'restaurant', 'cafe']):
                                restaurant_data['type'] = line
                                break
                        
                        # Try to extract address (usually the last line with location info)
                        for line in reversed(lines):
                            if any(word in line.lower() for word in ['mi', 'km', 'miles', 'singapore', 'road', 'street', 'avenue']):
                                restaurant_data['address'] = line
                                break
                        
                        # Try to extract URL
                        try:
                            link_elem = element.find_element(By.CSS_SELECTOR, 'a')
                            if link_elem:
                                href = link_elem.get_attribute('href')
                                if href:
                                    restaurant_data['url'] = href
                        except:
                            pass
                        
                        # Try to extract coordinates from data attributes on the main element
                        try:
                            lat = element.get_attribute('data-lat')
                            lng = element.get_attribute('data-lng')
                            if lat and lng:
                                restaurant_data['latitude'] = float(lat)
                                restaurant_data['longitude'] = float(lng)
                        except (ValueError, TypeError):
                            pass
                        
                        # If coordinates not found on main element, look for details element with same data-id
                        if not restaurant_data.get('latitude') or not restaurant_data.get('longitude'):
                            try:
                                # Get the data-id from the main element
                                main_id = element.get_attribute('data-id')
                                if main_id:
                                    # Look for details element with same data-id
                                    details_element = driver.find_element(By.CSS_SELECTOR, f'div.details.hidden[data-id="{main_id}"]')
                                    if details_element:
                                        lat = details_element.get_attribute('data-lat')
                                        lng = details_element.get_attribute('data-lng')
                                        if lat and lng:
                                            restaurant_data['latitude'] = float(lat)
                                            restaurant_data['longitude'] = float(lng)
                                            self.logger.debug(f"Found coordinates in details element: {lat}, {lng}")
                            except Exception as e:
                                self.logger.debug(f"Could not find details element for restaurant {i+1}: {e}")
                        
                        # Try to extract coordinates from other data attributes
                        try:
                            # Check for common coordinate attribute names
                            for attr in ['data-latitude', 'data-longitude', 'data-coords', 'data-location']:
                                value = element.get_attribute(attr)
                                if value:
                                    # Try to parse coordinate pairs
                                    coord_match = re.search(r'(\d+\.\d+),\s*(\d+\.\d+)', value)
                                    if coord_match:
                                        restaurant_data['latitude'] = float(coord_match.group(1))
                                        restaurant_data['longitude'] = float(coord_match.group(2))
                                        break
                        except (ValueError, TypeError):
                            pass
                        
                        # Determine restaurant type
                        restaurant_type = restaurant_data.get('type', '').lower()
                        restaurant_data['is_vegan'] = 'vegan' in restaurant_type
                        restaurant_data['is_vegetarian'] = 'vegetarian' in restaurant_type
                        restaurant_data['has_veg_options'] = 'veg' in restaurant_type or 'friendly' in restaurant_type
                        
                        if restaurant_data.get('name'):
                            restaurants.append(restaurant_data)
                            self.logger.info(f"Extracted restaurant {i+1}: {restaurant_data.get('name')}")
                
                except Exception as e:
                    self.logger.warning(f"Error extracting restaurant {i+1}: {e}")
                    continue
            
            self.logger.info(f"Successfully extracted {len(restaurants)} restaurants using Selenium")
            return restaurants
            
        except Exception as e:
            self.logger.error(f"Error in Selenium scraping: {e}")
            return []
        finally:
            self.close_selenium()
    
    def scrape_restaurant_details(self, restaurant_url: str) -> Dict:
        """Scrape detailed information from individual restaurant page"""
        try:
            response = self.make_request(restaurant_url)
            if not response:
                return {}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            details = {}
            
            # Extract address
            address_elem = soup.find('div', class_='address')
            if address_elem:
                details['address'] = address_elem.get_text(strip=True)
            
            # Extract phone
            phone_elem = soup.find('div', class_='phone')
            if phone_elem:
                details['phone'] = phone_elem.get_text(strip=True)
            
            # Extract website
            website_elem = soup.find('a', class_='website')
            if website_elem:
                details['website'] = website_elem.get('href')
            
            # Extract description
            desc_elem = soup.find('div', class_='description')
            if desc_elem:
                details['description'] = desc_elem.get_text(strip=True)
            
            # Extract hours
            hours_elem = soup.find('div', class_='hours')
            if hours_elem:
                details['hours'] = hours_elem.get_text(strip=True)
            
            # Extract features
            features = []
            feature_elems = soup.find_all('span', class_='feature')
            for elem in feature_elems:
                features.append(elem.get_text(strip=True))
            details['features'] = features
            
            return details
            
        except Exception as e:
            self.logger.error(f"Error scraping restaurant details: {e}")
            return {}
    
    def parse_restaurant_data(self, restaurant_data: Dict) -> Restaurant:
        """Parse restaurant data from search results"""
        try:
            # Check if restaurant_data is valid
            if not restaurant_data or not isinstance(restaurant_data, dict):
                return None
            
            # Extract basic information
            name = restaurant_data.get('name', '')
            
            # Check if we have at least a name
            if not name or not name.strip():
                return None
            address = restaurant_data.get('address', '')
            phone = restaurant_data.get('phone', '')
            website = restaurant_data.get('website', '')
            description = restaurant_data.get('description', '')
            
            # Extract coordinates
            lat = restaurant_data.get('lat')
            lng = restaurant_data.get('lng')
            latitude = float(lat) if lat else None
            longitude = float(lng) if lng else None
            
            # Extract rating and review count
            rating = restaurant_data.get('rating')
            review_count = restaurant_data.get('review_count')
            
            # Determine restaurant type
            restaurant_type = restaurant_data.get('type', '').lower()
            is_vegan = 'vegan' in restaurant_type
            is_vegetarian = 'vegetarian' in restaurant_type
            has_veg_options = 'veg' in restaurant_type or 'friendly' in restaurant_type
            
            # Extract cuisine type
            cuisine_type = restaurant_data.get('cuisine', '')
            
            # Extract price range
            price_range = restaurant_data.get('price_range', '')
            
            # Extract features
            features = restaurant_data.get('features', [])
            
            # Extract hours
            hours = restaurant_data.get('hours', '')
            
            # HappyCow URL
            happycow_url = restaurant_data.get('url', '')
            
            return Restaurant(
                name=name,
                address=address,
                phone=phone,
                website=website,
                description=description,
                cuisine_type=cuisine_type,
                price_range=price_range,
                rating=rating,
                review_count=review_count,
                latitude=latitude,
                longitude=longitude,
                is_vegan=is_vegan,
                is_vegetarian=is_vegetarian,
                has_veg_options=has_veg_options,
                features=features,
                hours=hours,
                happycow_url=happycow_url
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing restaurant data: {e}")
            return None
    
    def scrape_singapore_restaurants(self, resume: bool = True) -> List[Restaurant]:
        """Scrape all restaurants from Singapore search results with resume support"""
        restaurants = []
        
        # Check if we can resume from previous session
        if resume and self.progress_tracker:
            resume_info = self.progress_tracker.get_resume_info()
            if resume_info['can_resume']:
                self.logger.info(f"Resuming previous scraping session...")
                self.logger.info(f"Previously scraped: {resume_info['scraped_count']} restaurants")
                self.logger.info(f"Started at: {resume_info['started_at']}")
                self.logger.info(f"Last updated: {resume_info['last_updated']}")
            else:
                self.logger.info("Starting fresh scraping session")
                self.progress_tracker.start_scraping()
        elif self.progress_tracker:
            self.progress_tracker.start_scraping()
        
        try:
            if self.use_selenium:
                # Use Selenium for dynamic content
                restaurant_data = self.scrape_with_selenium()
            else:
                # Use traditional HTTP requests (likely won't work for dynamic content)
                restaurant_data = self.scrape_with_requests()
            
            if not restaurant_data:
                self.logger.error("No restaurant data found")
                return restaurants
            
            self.logger.info(f"Found {len(restaurant_data)} restaurants")
            
            # Update progress tracker with total count
            if self.progress_tracker:
                self.progress_tracker.progress_data['total_restaurants'] = len(restaurant_data)
                self.progress_tracker.save_progress()
            
            # Process each restaurant
            scraped_count = 0
            failed_count = 0
            
            for i, data in enumerate(restaurant_data):
                restaurant_name = data.get('name', 'Unknown')
                
                # Skip if already scraped (resume functionality)
                if resume and self.progress_tracker and self.progress_tracker.is_restaurant_scraped(restaurant_name):
                    self.logger.info(f"Skipping already scraped restaurant: {restaurant_name}")
                    continue
                
                self.logger.info(f"Processing restaurant {i+1}/{len(restaurant_data)}: {restaurant_name}")
                
                try:
                    # Get detailed information if URL is available
                    if data.get('url'):
                        details = self.scrape_restaurant_details(data['url'])
                        data.update(details)
                    
                    # Parse and create Restaurant object
                    restaurant = self.parse_restaurant_data(data)
                    if restaurant:
                        restaurants.append(restaurant)
                        scraped_count += 1
                        
                        # Update progress tracker
                        if self.progress_tracker:
                            self.progress_tracker.add_scraped_restaurant(restaurant_name)
                            self.progress_tracker.update_progress(scraped_count, failed_count)
                    else:
                        failed_count += 1
                        self.logger.warning(f"Failed to parse restaurant: {restaurant_name}")
                        
                except Exception as e:
                    failed_count += 1
                    self.logger.error(f"Error processing restaurant {restaurant_name}: {e}")
            
            # Mark as completed
            if self.progress_tracker:
                self.progress_tracker.mark_completed()
            
            self.logger.info(f"Successfully scraped {len(restaurants)} restaurants")
            self.logger.info(f"Failed to scrape {failed_count} restaurants")
            
        except Exception as e:
            self.logger.error(f"Error scraping restaurants: {e}")
        
        return restaurants
    
    def scrape_with_requests(self) -> List[Dict]:
        """Scrape using traditional HTTP requests (for static content)"""
        try:
            response = self.make_request(Config.SEARCH_URL, Config.SINGAPORE_PARAMS)
            if not response:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            restaurant_data = []
            
            # Look for restaurant data in script tags
            script_tags = soup.find_all('script', type='text/javascript')
            for script in script_tags:
                if script.string and 'restaurants' in script.string:
                    try:
                        json_match = re.search(r'var\s+restaurants\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(1)
                            restaurant_data = json.loads(json_str)
                            break
                    except (json.JSONDecodeError, AttributeError):
                        continue
            
            return restaurant_data
            
        except Exception as e:
            self.logger.error(f"Error in requests scraping: {e}")
            return []
    
    def save_to_json(self, restaurants: List[Restaurant], filename: str = 'logs/singapore_restaurants.json', append: bool = True):
        """Save restaurants to JSON file with duplicate handling"""
        try:
            # Ensure logs directory exists
            os.makedirs('logs', exist_ok=True)
            existing_restaurants = []
            
            # Load existing data if appending
            if append and os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                        existing_restaurants = [Restaurant(**item) for item in existing_data]
                except Exception as e:
                    self.logger.warning(f"Could not load existing JSON file: {e}")
                    existing_restaurants = []
            
            # Merge with existing data, avoiding duplicates
            all_restaurants = existing_restaurants.copy()
            existing_names = {r.name for r in existing_restaurants}
            
            new_count = 0
            duplicate_count = 0
            
            for restaurant in restaurants:
                if restaurant.name not in existing_names:
                    all_restaurants.append(restaurant)
                    existing_names.add(restaurant.name)
                    new_count += 1
                else:
                    duplicate_count += 1
                    self.logger.info(f"Skipping duplicate in JSON: {restaurant.name}")
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump([restaurant.model_dump() for restaurant in all_restaurants], f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"JSON file updated: {new_count} new restaurants added, {duplicate_count} duplicates skipped")
            self.logger.info(f"Total restaurants in {filename}: {len(all_restaurants)}")
            
        except Exception as e:
            self.logger.error(f"Error saving to JSON: {e}")
