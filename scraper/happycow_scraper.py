import requests
import time
import logging
import json
import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from config import Config
from models import Restaurant

class HappyCowScraper:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
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
            # Extract basic information
            name = restaurant_data.get('name', '')
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
    
    def scrape_singapore_restaurants(self) -> List[Restaurant]:
        """Scrape all restaurants from Singapore search results"""
        restaurants = []
        
        try:
            # Get initial search results
            response = self.make_request(Config.SEARCH_URL, Config.SINGAPORE_PARAMS)
            if not response:
                self.logger.error("Failed to get initial search results")
                return restaurants
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for restaurant data in script tags (common pattern for dynamic content)
            script_tags = soup.find_all('script', type='text/javascript')
            restaurant_data = []
            
            for script in script_tags:
                if script.string and 'restaurants' in script.string:
                    try:
                        # Extract JSON data from script
                        json_match = re.search(r'var\s+restaurants\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(1)
                            restaurant_data = json.loads(json_str)
                            break
                    except (json.JSONDecodeError, AttributeError):
                        continue
            
            # If no JSON data found, try to parse HTML elements
            if not restaurant_data:
                restaurant_elements = soup.find_all('div', class_='restaurant-item')
                for elem in restaurant_elements:
                    restaurant_info = {}
                    
                    # Extract name
                    name_elem = elem.find('h3', class_='name')
                    if name_elem:
                        restaurant_info['name'] = name_elem.get_text(strip=True)
                    
                    # Extract address
                    address_elem = elem.find('div', class_='address')
                    if address_elem:
                        restaurant_info['address'] = address_elem.get_text(strip=True)
                    
                    # Extract rating
                    rating_elem = elem.find('span', class_='rating')
                    if rating_elem:
                        try:
                            restaurant_info['rating'] = float(rating_elem.get_text(strip=True))
                        except ValueError:
                            pass
                    
                    # Extract type
                    type_elem = elem.find('span', class_='type')
                    if type_elem:
                        restaurant_info['type'] = type_elem.get_text(strip=True)
                    
                    # Extract URL
                    link_elem = elem.find('a')
                    if link_elem:
                        href = link_elem.get('href')
                        if href:
                            restaurant_info['url'] = Config.BASE_URL + href
                    
                    if restaurant_info:
                        restaurant_data.append(restaurant_info)
            
            self.logger.info(f"Found {len(restaurant_data)} restaurants")
            
            # Process each restaurant
            for i, data in enumerate(restaurant_data):
                self.logger.info(f"Processing restaurant {i+1}/{len(restaurant_data)}: {data.get('name', 'Unknown')}")
                
                # Get detailed information if URL is available
                if data.get('url'):
                    details = self.scrape_restaurant_details(data['url'])
                    data.update(details)
                
                # Parse and create Restaurant object
                restaurant = self.parse_restaurant_data(data)
                if restaurant:
                    restaurants.append(restaurant)
            
            self.logger.info(f"Successfully scraped {len(restaurants)} restaurants")
            
        except Exception as e:
            self.logger.error(f"Error scraping restaurants: {e}")
        
        return restaurants
    
    def save_to_json(self, restaurants: List[Restaurant], filename: str = 'singapore_restaurants.json'):
        """Save restaurants to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump([restaurant.dict() for restaurant in restaurants], f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved {len(restaurants)} restaurants to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving to JSON: {e}")
