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

            # Price range
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


