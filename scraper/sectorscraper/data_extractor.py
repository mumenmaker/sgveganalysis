"""
Data Extractor for HappyCow SearchMap
Extracts restaurant data from loaded pages
"""

import re
import json
import time
import logging
from typing import List, Dict, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class HappyCowDataExtractor:
    """Extracts restaurant data from HappyCow searchmap pages"""
    
    def __init__(self, driver):
        self.driver = driver
        self.logger = logging.getLogger(__name__)
    
    def extract_restaurants_from_page(self) -> List[Dict]:
        """Extract all restaurant data from the current page"""
        try:
            self.logger.info("Starting restaurant data extraction")
            
            # Try multiple extraction methods
            restaurants = []
            
            # Method 1: Extract from JavaScript variables
            js_restaurants = self._extract_from_javascript()
            if js_restaurants:
                restaurants.extend(js_restaurants)
                self.logger.info(f"Extracted {len(js_restaurants)} restaurants from JavaScript")
            
            # Method 2: Extract from page source
            source_restaurants = self._extract_from_page_source()
            if source_restaurants:
                restaurants.extend(source_restaurants)
                self.logger.info(f"Extracted {len(source_restaurants)} restaurants from page source")
            
            # Method 3: Extract from DOM elements (basic coordinates)
            dom_restaurants = self._extract_from_dom()
            if dom_restaurants:
                restaurants.extend(dom_restaurants)
                self.logger.info(f"Extracted {len(dom_restaurants)} restaurants from DOM")
            
            # Method 4: Try to get detailed info by clicking markers
            detailed_restaurants = self._extract_detailed_info_by_clicking()
            if detailed_restaurants:
                # Replace basic restaurants with detailed ones where possible
                restaurants = self._merge_restaurant_data(restaurants, detailed_restaurants)
                self.logger.info(f"Enhanced {len(detailed_restaurants)} restaurants with detailed info")
            
            # Remove duplicates based on coordinates
            unique_restaurants = self._remove_duplicates(restaurants)
            
            self.logger.info(f"Total unique restaurants extracted: {len(unique_restaurants)}")
            return unique_restaurants
            
        except Exception as e:
            self.logger.error(f"Error extracting restaurant data: {e}")
            return []
    
    def _extract_from_javascript(self) -> List[Dict]:
        """Extract restaurant data from JavaScript variables"""
        try:
            # Common JavaScript variable names that might contain restaurant data
            js_vars = [
                'window.restaurants',
                'window.markers',
                'window.data',
                'window.restaurantData',
                'window.mapData',
                'window.searchResults',
                'window.venues'
            ]
            
            restaurants = []
            
            for var_name in js_vars:
                try:
                    data = self.driver.execute_script(f"return {var_name};")
                    if data and isinstance(data, (list, dict)):
                        if isinstance(data, list):
                            for item in data:
                                if self._is_valid_restaurant_data(item):
                                    restaurants.append(self._normalize_restaurant_data(item))
                        elif isinstance(data, dict):
                            if self._is_valid_restaurant_data(data):
                                restaurants.append(self._normalize_restaurant_data(data))
                except Exception:
                    continue
            
            return restaurants
            
        except Exception as e:
            self.logger.error(f"Error extracting from JavaScript: {e}")
            return []
    
    def _extract_from_page_source(self) -> List[Dict]:
        """Extract restaurant data from page source using regex"""
        try:
            page_source = self.driver.page_source
            restaurants = []
            
            # Pattern 1: Look for JSON data structures
            json_patterns = [
                r'\[\{.*?"name".*?\}\]',  # Array of objects with name
                r'\[\{.*?"lat".*?"lng".*?\}\]',  # Array of objects with coordinates
                r'\[\{.*?"restaurant".*?\}\]'  # Array of restaurant objects
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, page_source, re.DOTALL)
                for match in matches:
                    try:
                        data = json.loads(match)
                        if isinstance(data, list):
                            for item in data:
                                if self._is_valid_restaurant_data(item):
                                    restaurants.append(self._normalize_restaurant_data(item))
                    except json.JSONDecodeError:
                        continue
            
            # Pattern 2: Look for data attributes
            data_attr_pattern = r'data-lat="([^"]+)"[^>]*data-lng="([^"]+)"[^>]*title="([^"]+)"'
            matches = re.findall(data_attr_pattern, page_source)
            for lat, lng, title in matches:
                try:
                    restaurant = {
                        'name': title,
                        'latitude': float(lat),
                        'longitude': float(lng),
                        'address': 'Address not available',
                        'is_vegan': False,
                        'is_vegetarian': False,
                        'has_veg_options': False
                    }
                    restaurants.append(restaurant)
                except ValueError:
                    continue
            
            return restaurants
            
        except Exception as e:
            self.logger.error(f"Error extracting from page source: {e}")
            return []
    
    def _extract_from_dom(self) -> List[Dict]:
        """Extract restaurant data from DOM elements using data-marker-id divs"""
        try:
            restaurants = []
            
            # Look for restaurant cards with data-marker-id attribute
            restaurant_cards = self.driver.find_elements(By.CSS_SELECTOR, "[data-marker-id]")
            
            self.logger.info(f"Found {len(restaurant_cards)} restaurant cards with data-marker-id")
            
            for i, card in enumerate(restaurant_cards):
                try:
                    # Get marker ID
                    marker_id = card.get_attribute('data-marker-id')
                    
                    # Look for coordinates in child div with class "details hidden"
                    details_div = card.find_element(By.CSS_SELECTOR, ".details.hidden")
                    
                    if details_div:
                        # Get coordinates from the details div
                        lat = details_div.get_attribute('data-lat')
                        lng = details_div.get_attribute('data-lng')
                        
                        if lat and lng:
                            # Extract restaurant information from the card
                            restaurant = self._extract_restaurant_info_from_card(card, marker_id, lat, lng)
                            
                            if restaurant:
                                restaurants.append(restaurant)
                                self.logger.debug(f"Extracted restaurant {i+1}: {restaurant['name']} at ({lat}, {lng})")
                        else:
                            self.logger.warning(f"Restaurant card {i+1} (ID: {marker_id}) has no coordinates")
                    else:
                        self.logger.warning(f"Restaurant card {i+1} (ID: {marker_id}) has no details div")
                        
                except Exception as e:
                    self.logger.warning(f"Error processing restaurant card {i+1}: {e}")
                    continue
            
            self.logger.info(f"Successfully extracted {len(restaurants)} restaurants from DOM")
            return restaurants
            
        except Exception as e:
            self.logger.error(f"Error extracting from DOM: {e}")
            return []
    
    def _extract_restaurant_info_from_card(self, card, marker_id: str, lat: str, lng: str) -> Optional[Dict]:
        """Extract detailed restaurant information from a restaurant card"""
        try:
            # Extract restaurant name
            name = self._extract_restaurant_name(card)
            
            # Extract address
            address = self._extract_restaurant_address(card)
            
            # Extract phone
            phone = self._extract_restaurant_phone(card)
            
            # Extract website and HappyCow reviews link
            website = self._extract_restaurant_website(card)
            cow_reviews = self._extract_happycow_reviews_link(card)
            
            # Extract rating
            rating = self._extract_restaurant_rating(card)
            
            # Extract restaurant type (vegan, vegetarian, veg-friendly)
            is_vegan, is_vegetarian, has_veg_options = self._extract_restaurant_type(card)
            
            # Extract additional info
            cuisine_type = self._extract_cuisine_type(card)
            price_range = self._extract_price_range(card)
            hours = self._extract_hours(card)
            description = self._extract_description(card)
            
            restaurant = {
                'name': name,
                'latitude': float(lat),
                'longitude': float(lng),
                'address': address,
                'phone': phone,
                'website': website,
                'rating': rating,
                'price_range': price_range,
                'category': cuisine_type,
                'hours': hours,
                'description': description,
                'cow_reviews': cow_reviews,
                'is_vegan': is_vegan,
                'is_vegetarian': is_vegetarian,
                'has_veg_options': has_veg_options,
                'marker_id': marker_id
            }
            
            return restaurant
            
        except Exception as e:
            self.logger.warning(f"Error extracting restaurant info from card: {e}")
            return None
    
    def _extract_restaurant_name(self, card) -> str:
        """Extract restaurant name from card"""
        try:
            # Try various selectors for restaurant name
            name_selectors = [
                "h1", "h2", "h3", ".name", ".title", ".restaurant-name", 
                ".venue-name", ".business-name", ".establishment-name"
            ]
            
            for selector in name_selectors:
                elements = card.find_elements(By.CSS_SELECTOR, selector)
                if elements and elements[0].text.strip():
                    return elements[0].text.strip()
            
            # Fallback: look for any text content in the card
            card_text = card.text.strip()
            if card_text:
                # Take the first line as the name
                first_line = card_text.split('\n')[0].strip()
                if first_line and len(first_line) < 100:  # Reasonable name length
                    return first_line
            
            return "Unknown Restaurant"
            
        except Exception:
            return "Unknown Restaurant"
    
    def _extract_restaurant_address(self, card) -> str:
        """Extract restaurant address from card"""
        try:
            address_selectors = [
                ".address", ".location", ".venue-address", ".business-address",
                "[data-address]", ".street-address"
            ]
            
            for selector in address_selectors:
                elements = card.find_elements(By.CSS_SELECTOR, selector)
                if elements and elements[0].text.strip():
                    return elements[0].text.strip()
            
            return "Address not available"
            
        except Exception:
            return "Address not available"
    
    def _extract_restaurant_phone(self, card) -> str:
        """Extract restaurant phone from card"""
        try:
            phone_selectors = [
                ".phone", ".tel", "[href^='tel:']", ".contact-phone",
                "[data-phone]"
            ]
            
            for selector in phone_selectors:
                elements = card.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    phone_text = elements[0].text.strip() or elements[0].get_attribute('href')
                    if phone_text:
                        return phone_text
            
            return ""
            
        except Exception:
            return ""
    
    def _extract_restaurant_website(self, card) -> str:
        """Extract restaurant website from card"""
        try:
            website_elements = card.find_elements(By.CSS_SELECTOR, "a[href^='http']")
            if website_elements:
                return website_elements[0].get_attribute('href')
            return ""
            
        except Exception:
            return ""

    def _extract_happycow_reviews_link(self, card) -> str:
        """Extract the HappyCow reviews/details link.
        Accepts either relative '/reviews/...' or absolute 'https://www.happycow.net/reviews/...'.
        Filters out Google Maps links and strips trailing '#' anchors.
        """
        try:
            anchors = card.find_elements(By.CSS_SELECTOR, "a[href]")
            for a in anchors:
                href = (a.get_attribute('href') or '').strip()
                if not href:
                    continue
                # Skip Google Maps or other non-HappyCow links
                if 'google.com/maps' in href:
                    continue
                # Normalize to absolute HappyCow URL
                if href.startswith('/reviews/'):
                    url = f"https://www.happycow.net{href}"
                elif href.startswith('https://www.happycow.net/reviews/') or href.startswith('http://www.happycow.net/reviews/'):
                    url = href
                else:
                    continue
                # Drop a single trailing '#'
                if url.endswith('#'):
                    url = url[:-1]
                return url
            return ""
        except Exception:
            return ""
    
    def _extract_restaurant_rating(self, card) -> float:
        """Extract restaurant rating from card"""
        try:
            rating_selectors = [
                ".rating", ".stars", ".score", ".review-rating",
                "[data-rating]", ".avg-rating"
            ]
            
            for selector in rating_selectors:
                elements = card.find_elements(By.CSS_SELECTOR, selector)
                if elements and elements[0].text.strip():
                    try:
                        # Extract number from text
                        import re
                        numbers = re.findall(r'\d+\.?\d*', elements[0].text.strip())
                        if numbers:
                            return float(numbers[0])
                    except ValueError:
                        continue
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _extract_restaurant_type(self, card) -> tuple:
        """Extract restaurant type (vegan, vegetarian, veg-friendly) from card"""
        try:
            card_text = card.text.lower()
            class_name = card.get_attribute('class') or ''
            all_text = (card_text + ' ' + class_name).lower()
            
            is_vegan = 'vegan' in all_text and 'vegetarian' not in all_text
            is_vegetarian = 'vegetarian' in all_text and not is_vegan
            has_veg_options = ('veg' in all_text or 'vegetarian-friendly' in all_text) and not is_vegan and not is_vegetarian
            
            return is_vegan, is_vegetarian, has_veg_options
            
        except Exception:
            return False, False, False
    
    def _extract_cuisine_type(self, card) -> str:
        """Extract cuisine type from card"""
        try:
            cuisine_selectors = [
                ".cuisine", ".cuisine-type", ".food-type", ".category"
            ]
            
            for selector in cuisine_selectors:
                elements = card.find_elements(By.CSS_SELECTOR, selector)
                if elements and elements[0].text.strip():
                    return elements[0].text.strip()
            
            return ""
            
        except Exception:
            return ""
    
    def _extract_price_range(self, card) -> str:
        """Extract price range from card"""
        try:
            price_selectors = [
                ".price", ".price-range", ".cost", ".budget"
            ]
            
            for selector in price_selectors:
                elements = card.find_elements(By.CSS_SELECTOR, selector)
                if elements and elements[0].text.strip():
                    return elements[0].text.strip()
            
            return ""
            
        except Exception:
            return ""
    
    def _extract_hours(self, card) -> str:
        """Extract opening hours from card"""
        try:
            hours_selectors = [
                ".hours", ".opening-hours", ".schedule", ".time"
            ]
            
            for selector in hours_selectors:
                elements = card.find_elements(By.CSS_SELECTOR, selector)
                if elements and elements[0].text.strip():
                    return elements[0].text.strip()
            
            return ""
            
        except Exception:
            return ""
    
    def _extract_description(self, card) -> str:
        """Extract description from card"""
        try:
            desc_selectors = [
                ".description", ".summary", ".about", ".details"
            ]
            
            for selector in desc_selectors:
                elements = card.find_elements(By.CSS_SELECTOR, selector)
                if elements and elements[0].text.strip():
                    return elements[0].text.strip()
            
            return ""
            
        except Exception:
            return ""
    
    def _is_valid_restaurant_data(self, data: Dict) -> bool:
        """Check if data contains valid restaurant information"""
        if not isinstance(data, dict):
            return False
        
        # Must have coordinates
        has_coords = ('lat' in data or 'latitude' in data) and ('lng' in data or 'longitude' in data)
        
        # Must have some identifying information
        has_identifier = any(key in data for key in ['name', 'title', 'restaurant', 'venue'])
        
        return has_coords and has_identifier
    
    def _normalize_restaurant_data(self, data: Dict) -> Dict:
        """Normalize restaurant data to standard format"""
        try:
            # Extract coordinates
            lat = data.get('lat') or data.get('latitude')
            lng = data.get('lng') or data.get('longitude')
            
            if lat is None or lng is None:
                return None
            
            # Extract name
            name = (data.get('name') or 
                   data.get('title') or 
                   data.get('restaurant') or 
                   data.get('venue') or 
                   'Unknown Restaurant')
            
            # Extract address
            address = (data.get('address') or 
                      data.get('location') or 
                      data.get('full_address') or 
                      'Address not available')
            
            # Extract restaurant type
            is_vegan = 'vegan' in str(data.get('type', '')).lower()
            is_vegetarian = 'vegetarian' in str(data.get('type', '')).lower()
            has_veg_options = 'veg' in str(data.get('type', '')).lower() and not is_vegan and not is_vegetarian
            
            return {
                'name': str(name).strip(),
                'latitude': float(lat),
                'longitude': float(lng),
                'address': str(address).strip(),
                'is_vegan': is_vegan,
                'is_vegetarian': is_vegetarian,
                'has_veg_options': has_veg_options,
                'phone': data.get('phone', ''),
                'website': data.get('website', ''),
                'rating': data.get('rating', 0.0),
                'price_range': data.get('price_range', ''),
                'cuisine_type': data.get('cuisine_type', ''),
                'hours': data.get('hours', ''),
                'description': data.get('description', '')
            }
            
        except Exception as e:
            self.logger.error(f"Error normalizing restaurant data: {e}")
            return None
    
    def _extract_detailed_info_by_clicking(self) -> List[Dict]:
        """Try to get detailed restaurant info by clicking on markers"""
        try:
            self.logger.info("Attempting to extract detailed info by clicking markers")
            
            # Find all clickable markers
            markers = self.driver.find_elements(By.CSS_SELECTOR, "[data-lat][data-lng]")
            detailed_restaurants = []
            
            # Limit to first 10 markers to avoid overwhelming the page
            max_markers = min(10, len(markers))
            
            for i in range(max_markers):
                try:
                    marker = markers[i]
                    
                    # Get basic coordinates first
                    lat = marker.get_attribute('data-lat')
                    lng = marker.get_attribute('data-lng')
                    
                    if not lat or not lng:
                        continue
                    
                    # Click the marker
                    self.driver.execute_script("arguments[0].click();", marker)
                    time.sleep(1)  # Wait for popup to appear
                    
                    # Look for popup content
                    popup_content = self._extract_popup_content()
                    
                    if popup_content:
                        restaurant = {
                            'name': popup_content.get('name', f'Restaurant {i+1}'),
                            'latitude': float(lat),
                            'longitude': float(lng),
                            'address': popup_content.get('address', 'Address not available'),
                            'phone': popup_content.get('phone', ''),
                            'website': popup_content.get('website', ''),
                            'rating': popup_content.get('rating', 0.0),
                            'price_range': popup_content.get('price_range', ''),
                            'cuisine_type': popup_content.get('cuisine_type', ''),
                            'hours': popup_content.get('hours', ''),
                            'description': popup_content.get('description', ''),
                            'is_vegan': popup_content.get('is_vegan', False),
                            'is_vegetarian': popup_content.get('is_vegetarian', False),
                            'has_veg_options': popup_content.get('has_veg_options', False)
                        }
                        detailed_restaurants.append(restaurant)
                        self.logger.debug(f"Extracted detailed info for restaurant {i+1}: {restaurant['name']}")
                    
                    # Close popup if it exists
                    self._close_popup()
                    time.sleep(0.5)
                    
                except Exception as e:
                    self.logger.warning(f"Error clicking marker {i+1}: {e}")
                    self._close_popup()  # Try to close any open popup
                    continue
            
            self.logger.info(f"Successfully extracted detailed info for {len(detailed_restaurants)} restaurants")
            return detailed_restaurants
            
        except Exception as e:
            self.logger.error(f"Error extracting detailed info by clicking: {e}")
            return []
    
    def _extract_popup_content(self) -> Optional[Dict]:
        """Extract content from any open popup"""
        try:
            # Look for various popup selectors
            popup_selectors = [
                ".leaflet-popup-content",
                ".popup-content",
                ".marker-popup",
                ".restaurant-popup"
            ]
            
            for selector in popup_selectors:
                popups = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if popups:
                    popup = popups[0]
                    return self._parse_popup_content(popup)
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error extracting popup content: {e}")
            return None
    
    def _parse_popup_content(self, popup_element) -> Dict:
        """Parse content from a popup element"""
        try:
            content = {}
            
            # Try to find restaurant name
            name_selectors = ["h1", "h2", "h3", ".name", ".title", ".restaurant-name"]
            for selector in name_selectors:
                name_elements = popup_element.find_elements(By.CSS_SELECTOR, selector)
                if name_elements and name_elements[0].text.strip():
                    content['name'] = name_elements[0].text.strip()
                    break
            
            # Try to find address
            address_selectors = [".address", ".location", ".venue-address"]
            for selector in address_selectors:
                address_elements = popup_element.find_elements(By.CSS_SELECTOR, selector)
                if address_elements and address_elements[0].text.strip():
                    content['address'] = address_elements[0].text.strip()
                    break
            
            # Try to find phone
            phone_selectors = [".phone", ".tel", "[href^='tel:']"]
            for selector in phone_selectors:
                phone_elements = popup_element.find_elements(By.CSS_SELECTOR, selector)
                if phone_elements:
                    phone_text = phone_elements[0].text.strip() or phone_elements[0].get_attribute('href')
                    if phone_text:
                        content['phone'] = phone_text
                        break
            
            # Try to find website
            website_elements = popup_element.find_elements(By.CSS_SELECTOR, "a[href^='http']")
            if website_elements:
                content['website'] = website_elements[0].get_attribute('href')
            
            # Try to find rating
            rating_selectors = [".rating", ".stars", ".score"]
            for selector in rating_selectors:
                rating_elements = popup_element.find_elements(By.CSS_SELECTOR, selector)
                if rating_elements and rating_elements[0].text.strip():
                    try:
                        content['rating'] = float(rating_elements[0].text.strip())
                        break
                    except ValueError:
                        continue
            
            # Determine restaurant type from text content
            popup_text = popup_element.text.lower()
            content['is_vegan'] = 'vegan' in popup_text and 'vegetarian' not in popup_text
            content['is_vegetarian'] = 'vegetarian' in popup_text and not content['is_vegan']
            content['has_veg_options'] = 'veg' in popup_text and not content['is_vegan'] and not content['is_vegetarian']
            
            return content
            
        except Exception as e:
            self.logger.warning(f"Error parsing popup content: {e}")
            return {}
    
    def _close_popup(self):
        """Close any open popup"""
        try:
            close_selectors = [
                ".leaflet-popup-close-button",
                ".popup-close",
                ".close-button",
                "[aria-label='Close']"
            ]
            
            for selector in close_selectors:
                close_buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if close_buttons:
                    close_buttons[0].click()
                    time.sleep(0.5)
                    break
                    
        except Exception as e:
            self.logger.debug(f"Error closing popup: {e}")
    
    def _merge_restaurant_data(self, basic_restaurants: List[Dict], detailed_restaurants: List[Dict]) -> List[Dict]:
        """Merge basic restaurant data with detailed information"""
        try:
            # Create a map of detailed restaurants by coordinates
            detailed_map = {}
            for detailed in detailed_restaurants:
                if 'latitude' in detailed and 'longitude' in detailed:
                    coord_key = (detailed['latitude'], detailed['longitude'])
                    detailed_map[coord_key] = detailed
            
            # Merge with basic restaurants
            merged_restaurants = []
            for basic in basic_restaurants:
                if 'latitude' in basic and 'longitude' in basic:
                    coord_key = (basic['latitude'], basic['longitude'])
                    if coord_key in detailed_map:
                        # Use detailed info if available
                        merged_restaurants.append(detailed_map[coord_key])
                    else:
                        # Use basic info
                        merged_restaurants.append(basic)
                else:
                    merged_restaurants.append(basic)
            
            return merged_restaurants
            
        except Exception as e:
            self.logger.error(f"Error merging restaurant data: {e}")
            return basic_restaurants
    
    def _remove_duplicates(self, restaurants: List[Dict]) -> List[Dict]:
        """Remove duplicate restaurants based on coordinates"""
        seen_coords = set()
        unique_restaurants = []
        
        for restaurant in restaurants:
            if restaurant and 'latitude' in restaurant and 'longitude' in restaurant:
                coord_key = (restaurant['latitude'], restaurant['longitude'])
                if coord_key not in seen_coords:
                    seen_coords.add(coord_key)
                    unique_restaurants.append(restaurant)
        
        return unique_restaurants
    
    def get_extraction_summary(self, restaurants: List[Dict]) -> Dict:
        """Get a summary of the extraction results"""
        if not restaurants:
            return {
                'total_restaurants': 0,
                'with_coordinates': 0,
                'with_names': 0,
                'vegan_count': 0,
                'vegetarian_count': 0,
                'veg_options_count': 0
            }
        
        with_coords = sum(1 for r in restaurants if r.get('latitude') and r.get('longitude'))
        with_names = sum(1 for r in restaurants if r.get('name') and r.get('name') != 'Unknown Restaurant')
        vegan_count = sum(1 for r in restaurants if r.get('is_vegan'))
        vegetarian_count = sum(1 for r in restaurants if r.get('is_vegetarian'))
        veg_options_count = sum(1 for r in restaurants if r.get('has_veg_options'))
        
        return {
            'total_restaurants': len(restaurants),
            'with_coordinates': with_coords,
            'with_names': with_names,
            'vegan_count': vegan_count,
            'vegetarian_count': vegetarian_count,
            'veg_options_count': veg_options_count
        }


if __name__ == "__main__":
    # Test the data extractor
    from .sector_grid import SingaporeSectorGrid
    from .url_generator import HappyCowURLGenerator
    from .page_loader import HappyCowPageLoader
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Generate test sector and URL
    grid = SingaporeSectorGrid()
    sectors = grid.generate_sectors()
    url_gen = HappyCowURLGenerator()
    
    test_sector = sectors[0]
    test_url = url_gen.generate_sector_url(test_sector)
    
    print(f"Testing data extractor with sector: {test_sector['name']}")
    print(f"URL: {test_url}")
    
    # Test data extraction
    loader = HappyCowPageLoader(headless=False)  # Set to False for visual testing
    
    try:
        if loader.load_sector_page(test_url):
            extractor = HappyCowDataExtractor(loader.driver)
            restaurants = extractor.extract_restaurants_from_page()
            
            if restaurants:
                print(f"✅ Extracted {len(restaurants)} restaurants")
                summary = extractor.get_extraction_summary(restaurants)
                print(f"Summary: {summary}")
                
                # Show first few restaurants
                for i, restaurant in enumerate(restaurants[:3]):
                    print(f"\nRestaurant {i+1}:")
                    for key, value in restaurant.items():
                        print(f"  {key}: {value}")
            else:
                print("❌ No restaurants extracted")
        else:
            print("❌ Failed to load page")
    finally:
        loader.close_driver()
