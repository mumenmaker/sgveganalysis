"""
ReviewsEnhancer: fetches details from HappyCow reviews page and parses fields
"""

import logging
import time
from typing import Optional, Dict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class ReviewsEnhancer:
    def __init__(self, headless: bool = True, timeout: int = 20):
        self.logger = logging.getLogger(__name__)
        self.timeout = timeout
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--log-level=3")
        self.driver = webdriver.Chrome(options=chrome_options)

    def close(self):
        try:
            self.driver.quit()
        except Exception:
            pass

    def fetch_details(self, url: str) -> Optional[Dict]:
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
            )
            time.sleep(1)
            return self._parse_page()
        except TimeoutException:
            self.logger.warning(f"Timeout loading reviews page: {url}")
            return None
        except Exception as e:
            self.logger.error(f"Error fetching details from {url}: {e}")
            return None

    def _parse_page(self) -> Dict:
        d: Dict[str, Optional[str]] = {
            'phone': None,
            'address': None,
            'description': None,
            'features': None,
            'cuisine_type': None,
            'price_range': None,
            'rating': None,
            'review_count': None,
            'hours': None,
            'category': None,
            'images_links': None,
        }

        try:
            # Common selectors on HappyCow venue pages
            # Phone
            tel = self._first_text([
                "a[href^='tel:']",
                ".phone, .tel",
            ])
            if tel:
                d['phone'] = tel

            # Address: concatenate itemprop streetAddress + postalCode if present
            try:
                street = self._first_text(["[itemprop='streetAddress']"]) or ""
                postal = self._first_text(["[itemprop='postalCode']"]) or ""
                if street or postal:
                    d['address'] = (street + (" " if street and postal else "") + postal).strip()
            except Exception:
                pass
            # Fallback generic address containers if itemprops missing
            if not d['address']:
                addr = self._first_text([
                    ".address, .venue-address, .business-address, .location",
                ])
                if addr:
                    d['address'] = addr

            # Description/About (prefer venue-description)
            desc = self._first_text([
                ".venue-description",
                ".description, .about, .summary, .details"
            ])
            if desc:
                d['description'] = desc

            # Category (from data-listing-type attribute or visible labels)
            try:
                cat_el = self.driver.find_element(By.CSS_SELECTOR, "[data-listing-type]")
                val = (cat_el.get_attribute('data-listing-type') or '').strip()
                if val:
                    d['category'] = val
            except Exception:
                pass
            if not d['category']:
                cuisine = self._first_text([
                    ".cuisine, .cuisine-type, .food-type, .category"
                ])
                if cuisine:
                    d['category'] = cuisine

            # Price range - check for colored SVG icons in title divs
            price_range = self._extract_price_range_from_icons()
            if price_range:
                d['price_range'] = price_range
            else:
                # Fallback to text-based extraction
                price = self._first_text([
                    ".price, .price-range, .cost, .budget"
                ])
                if price:
                    d['price_range'] = price

            # Rating and reviews
            # Rating: prefer itemprop content attribute
            rating_el = None
            try:
                rating_el = self.driver.find_element(By.CSS_SELECTOR, "[itemprop='ratingValue']")
            except Exception:
                rating_el = None
            if rating_el:
                content = (rating_el.get_attribute('content') or rating_el.text or '').strip()
                if content:
                    try:
                        d['rating'] = float(content)
                    except Exception:
                        pass
            if d['rating'] is None:
                rating_text = self._first_text([
                    ".rating, .avg-rating, .stars, .score"
                ])
                if rating_text:
                    import re
                    nums = re.findall(r"\d+\.?\d*", rating_text)
                    if nums:
                        d['rating'] = float(nums[0])

            # Review count: prefer itemprop content attribute
            count_el = None
            try:
                count_el = self.driver.find_element(By.CSS_SELECTOR, "[itemprop='reviewCount']")
            except Exception:
                count_el = None
            if count_el:
                content = (count_el.get_attribute('content') or count_el.text or '').strip()
                if content:
                    try:
                        d['review_count'] = int(''.join(ch for ch in content if ch.isdigit()))
                    except Exception:
                        pass
            if d['review_count'] is None:
                reviews_text = self._first_text([
                    ".review-count, .reviews-count, .reviews-total"
                ])
                if reviews_text:
                    import re
                    nums = re.findall(r"\d+", reviews_text)
                    if nums:
                        d['review_count'] = int(nums[0])

            # Hours - prioritize hours-summary class
            hours = self._first_text([
                ".hours-summary",  # Primary selector for hours
                ".hours, .opening-hours, .schedule, .time"  # Fallback selectors
            ])
            if hours:
                d['hours'] = hours

            # Images - extract restaurant image URLs
            images = self._extract_restaurant_images()
            if images:
                d['images_links'] = images

            # Features: prefer venue-info flex divs, fallback to previous badges
            features_vals = []
            try:
                venue_info = self.driver.find_elements(By.CSS_SELECTOR, ".venue-info")
                for block in venue_info:
                    items = block.find_elements(By.CSS_SELECTOR, "div, span")
                    for it in items:
                        # Skip if element or any ancestor is an excluded container
                        if self._has_excluded_ancestor(it, {"venue-info-container", "venue-description"}):
                            continue
                        txt = it.text.strip()
                        if txt:
                            features_vals.append(txt)
            except Exception:
                pass
            if not features_vals:
                features_els = self.driver.find_elements(By.CSS_SELECTOR, ".features .feature, .tags .tag, .amenities .amenity")
                if features_els:
                    features_vals = [e.text.strip() for e in features_els if e.text.strip()]
            if features_vals:
                # Deduplicate while preserving order
                seen = set()
                uniq = []
                for v in features_vals:
                    if v not in seen:
                        seen.add(v)
                        uniq.append(v)
                d['features'] = uniq

        except Exception as e:
            self.logger.debug(f"Parse page encountered issues: {e}")

        return d

    def _extract_restaurant_images(self):
        """Extract restaurant image URLs from the review page"""
        try:
            image_urls = []
            
            # Primary method: Look for images in the specific listing-images div
            try:
                listing_images_div = self.driver.find_element(By.ID, "listing-images")
                if listing_images_div:
                    # Look for images within venue-list-images divs
                    venue_image_divs = listing_images_div.find_elements(By.CSS_SELECTOR, ".venue-list-images")
                    
                    for venue_div in venue_image_divs:
                        # Look for img tags within each venue-list-images div
                        images = venue_div.find_elements(By.CSS_SELECTOR, "img")
                        for img in images:
                            src = img.get_attribute('src')
                            if src and self._is_valid_image_url(src):
                                # Convert relative URLs to absolute URLs
                                absolute_src = self._make_absolute_url(src)
                                if absolute_src and absolute_src not in image_urls:
                                    image_urls.append(absolute_src)
                    
                    # Also look for any other images within the listing-images div
                    all_images = listing_images_div.find_elements(By.CSS_SELECTOR, "img")
                    for img in all_images:
                        src = img.get_attribute('src')
                        if src and self._is_valid_image_url(src):
                            absolute_src = self._make_absolute_url(src)
                            if absolute_src and absolute_src not in image_urls:
                                image_urls.append(absolute_src)
                                
            except Exception as e:
                self.logger.debug(f"Could not find listing-images div: {e}")
            
            # Fallback method: Use broader selectors if listing-images div not found
            if not image_urls:
                fallback_selectors = [
                    "img[src*='restaurant']",  # Images with 'restaurant' in src
                    "img[src*='venue']",       # Images with 'venue' in src
                    "img[src*='food']",        # Images with 'food' in src
                    "img[src*='happycow']",    # Images from HappyCow CDN
                    ".venue-photo img",        # Venue photo images
                    ".restaurant-photo img",   # Restaurant photo images
                    ".gallery img",            # Gallery images
                    ".photos img",             # Photos section
                    ".images img",             # Images section
                    "img[alt*='restaurant']",  # Images with restaurant in alt text
                    "img[alt*='food']",        # Images with food in alt text
                    "img[alt*='venue']"        # Images with venue in alt text
                ]
                
                for selector in fallback_selectors:
                    try:
                        images = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for img in images:
                            src = img.get_attribute('src')
                            if src and self._is_valid_image_url(src):
                                absolute_src = self._make_absolute_url(src)
                                if absolute_src and absolute_src not in image_urls:
                                    image_urls.append(absolute_src)
                                    
                    except Exception:
                        continue
            
            # Limit to reasonable number of images (max 10)
            return image_urls[:10] if image_urls else []
            
        except Exception as e:
            self.logger.debug(f"Error extracting restaurant images: {e}")
            return []

    def _make_absolute_url(self, url):
        """Convert relative URL to absolute URL"""
        if not url:
            return None
        
        if url.startswith('http'):
            return url
        elif url.startswith('//'):
            return 'https:' + url
        elif url.startswith('/'):
            return 'https://www.happycow.net' + url
        else:
            return 'https://www.happycow.net/' + url

    def _is_valid_image_url(self, url):
        """Check if URL is a valid image URL"""
        if not url:
            return False
        
        # Check for common image extensions
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
        url_lower = url.lower()
        
        # Must have an image extension
        if not any(ext in url_lower for ext in image_extensions):
            return False
        
        # Exclude common non-restaurant images
        exclude_patterns = [
            'logo', 'icon', 'avatar', 'profile', 'banner', 'advertisement',
            'sponsor', 'partner', 'social', 'facebook', 'twitter', 'instagram',
            'youtube', 'linkedin', 'pinterest', 'tiktok', 'snapchat'
        ]
        
        for pattern in exclude_patterns:
            if pattern in url_lower:
                return False
        
        return True

    def _extract_price_range_from_icons(self):
        """Extract price range by checking for colored SVG icons in title divs"""
        try:
            # Look for divs with title attributes for price ranges
            price_titles = ["Inexpensive", "Moderate", "Expensive"]
            
            for title in price_titles:
                try:
                    # Find div with specific title attribute
                    divs = self.driver.find_elements(By.CSS_SELECTOR, f"div[title='{title}']")
                    
                    for div in divs:
                        # Look for SVG icon within this div
                        svg_icons = div.find_elements(By.CSS_SELECTOR, "svg")
                        
                        for svg in svg_icons:
                            # Check if SVG is colored yellow (indicating selected)
                            if self._is_svg_colored_yellow(svg):
                                self.logger.debug(f"Found price range: {title}")
                                return title
                                
                except Exception:
                    continue
            
            # Alternative approach: look for any div with price-related classes or attributes
            try:
                # Look for common price range indicators
                price_selectors = [
                    "div[class*='price']",
                    "div[class*='cost']", 
                    "div[class*='budget']",
                    ".price-range",
                    ".cost-range"
                ]
                
                for selector in price_selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        # Check if this element contains price range text
                        text = element.text.strip().lower()
                        if 'inexpensive' in text:
                            return 'Inexpensive'
                        elif 'moderate' in text:
                            return 'Moderate'
                        elif 'expensive' in text:
                            return 'Expensive'
                            
            except Exception:
                pass
                    
            return None
            
        except Exception as e:
            self.logger.debug(f"Error extracting price range from icons: {e}")
            return None

    def _is_svg_colored_yellow(self, svg_element):
        """Check if SVG element is colored yellow (indicating it's selected)"""
        try:
            # Check for yellow CSS classes (Tailwind CSS style)
            class_name = svg_element.get_attribute('class') or ''
            class_lower = class_name.lower()
            
            # Check for yellow color classes
            yellow_classes = [
                'text-yellow-500', 'text-yellow-400', 'text-yellow-600',
                'text-yellow-300', 'text-yellow-700', 'text-yellow-800',
                'text-yellow-900', 'text-yellow-100', 'text-yellow-200',
                'text-yellow', 'text-amber-500', 'text-amber-400',
                'text-amber-600', 'text-amber-300', 'text-amber-700',
                'text-amber-800', 'text-amber-900', 'text-amber-100',
                'text-amber-200', 'text-amber', 'text-orange-500',
                'text-orange-400', 'text-orange-600', 'text-orange-300',
                'text-orange-700', 'text-orange-800', 'text-orange-900',
                'text-orange-100', 'text-orange-200', 'text-orange'
            ]
            
            if any(yellow_class in class_lower for yellow_class in yellow_classes):
                return True
            
            # Check for non-gray classes (indicating it's selected vs gray/unselected)
            gray_classes = ['text-gray-500', 'text-gray-400', 'text-gray-600', 'text-gray-300', 'text-gray-700']
            if not any(gray_class in class_lower for gray_class in gray_classes):
                # If it's not gray, it might be selected
                if 'text-' in class_lower:
                    return True
            
            # Fallback: Check for yellow color variations in attributes
            yellow_colors = [
                'yellow', '#ffd700', '#ffff00', '#ffeb3b', '#ffc107', 
                '#ffd54f', '#fff176', '#ffeb3b', 'gold', '#gold'
            ]
            
            # 1. Check fill attribute
            fill = svg_element.get_attribute('fill')
            if fill:
                fill_lower = fill.lower()
                if any(color in fill_lower for color in yellow_colors):
                    return True
            
            # 2. Check style attribute
            style = svg_element.get_attribute('style')
            if style:
                style_lower = style.lower()
                if any(color in style_lower for color in yellow_colors):
                    return True
            
            # 3. Check computed style (more reliable)
            try:
                computed_style = self.driver.execute_script(
                    "return window.getComputedStyle(arguments[0]).fill;", 
                    svg_element
                )
                if computed_style:
                    computed_lower = computed_style.lower()
                    if any(color in computed_lower for color in yellow_colors):
                        return True
            except Exception:
                pass
            
            # 4. Check for yellow color in any child elements
            child_elements = svg_element.find_elements(By.CSS_SELECTOR, "*")
            for child in child_elements:
                child_fill = child.get_attribute('fill')
                if child_fill:
                    child_fill_lower = child_fill.lower()
                    if any(color in child_fill_lower for color in yellow_colors):
                        return True
                        
                # Also check child style
                child_style = child.get_attribute('style')
                if child_style:
                    child_style_lower = child_style.lower()
                    if any(color in child_style_lower for color in yellow_colors):
                        return True
            
            # 5. Check if element has a class that might indicate it's selected/active
            if any(keyword in class_lower for keyword in ['active', 'selected', 'current', 'highlighted']):
                return True
                    
            return False
            
        except Exception:
            return False

    def _first_text(self, selectors):
        for css in selectors:
            try:
                els = self.driver.find_elements(By.CSS_SELECTOR, css)
                for el in els:
                    t = el.text.strip()
                    if t:
                        return t
            except Exception:
                continue
        return None

    def _has_excluded_ancestor(self, element, excluded_classes: set) -> bool:
        try:
            current = element
            max_hops = 6
            hops = 0
            while current is not None and hops < max_hops:
                cls = (current.get_attribute('class') or '').split()
                if any(c in excluded_classes for c in cls):
                    return True
                try:
                    current = current.find_element(By.XPATH, "..")
                except Exception:
                    break
                hops += 1
            return False
        except Exception:
            return False


