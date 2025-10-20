#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Marker Extractor for HappyCow Veggiemap
Handles extraction of restaurant markers and coordinates from the map interface
"""

import time
import re
import logging
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from .cluster_handler import ClusterHandler

class MarkerExtractor:
    """Extract restaurant markers and coordinates from HappyCow veggiemap"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome WebDriver for marker extraction"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            
            self.logger.info("Chrome WebDriver setup successful")
            return self.driver
            
        except Exception as e:
            self.logger.error(f"Failed to setup Chrome WebDriver: {e}")
            return None
    
    def load_veggiemap_page(self, url: str) -> bool:
        """Load the HappyCow veggiemap page"""
        try:
            if not self.driver:
                self.driver = self.setup_driver()
                if not self.driver:
                    return False
            
            self.logger.info(f"Loading veggiemap page: {url}")
            self.driver.get(url)
            
            # Wait for map to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "leaflet-container"))
            )
            
            # Additional wait for markers to load
            time.sleep(5)
            
            self.logger.info("Veggiemap page loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load veggiemap page: {e}")
            return False
    
    def extract_markers_by_attributes(self) -> List[Dict]:
        """Extract markers using data attributes (Method A)"""
        try:
            # Try multiple selectors for markers with coordinates
            selectors = [
                ".leaflet-marker-icon[data-lat][data-lng]",
                "[data-lat][data-lng]",
                ".leaflet-marker-icon"
            ]
            
            coordinates = []
            
            for selector in selectors:
                markers = self.driver.find_elements(By.CSS_SELECTOR, selector)
                self.logger.debug(f"Found {len(markers)} elements with selector: {selector}")
                
                for marker in markers:
                    try:
                        lat = marker.get_attribute('data-lat')
                        lng = marker.get_attribute('data-lng')
                        if lat and lng:
                            coordinates.append({
                                'latitude': float(lat),
                                'longitude': float(lng),
                                'method': 'attributes'
                            })
                    except Exception as e:
                        self.logger.warning(f"Error extracting marker attributes: {e}")
                        continue
            
            self.logger.info(f"Extracted {len(coordinates)} markers via attributes")
            return coordinates
            
        except Exception as e:
            self.logger.error(f"Failed to extract markers by attributes: {e}")
            return []
    
    def extract_markers_by_page_source(self) -> List[Dict]:
        """Extract markers using regex on page source (Method B)"""
        try:
            page_source = self.driver.page_source
            coordinates = []
            
            # Regex patterns for coordinates
            lat_patterns = [
                r'data-lat="([^"]+)"',
                r'lat["\']?\s*[:=]\s*["\']?([0-9.-]+)',
                r'latitude["\']?\s*[:=]\s*["\']?([0-9.-]+)'
            ]
            
            lng_patterns = [
                r'data-lng="([^"]+)"',
                r'lng["\']?\s*[:=]\s*["\']?([0-9.-]+)',
                r'longitude["\']?\s*[:=]\s*["\']?([0-9.-]+)'
            ]
            
            # Extract latitudes
            latitudes = []
            for pattern in lat_patterns:
                matches = re.findall(pattern, page_source)
                latitudes.extend([float(match) for match in matches if match])
            
            # Extract longitudes
            longitudes = []
            for pattern in lng_patterns:
                matches = re.findall(pattern, page_source)
                longitudes.extend([float(match) for match in matches if match])
            
            # Pair up coordinates (assuming they're in order)
            min_length = min(len(latitudes), len(longitudes))
            for i in range(min_length):
                try:
                    lat = float(latitudes[i])
                    lng = float(longitudes[i])
                    
                    # Basic validation (Singapore coordinates)
                    if 1.0 <= lat <= 2.0 and 103.0 <= lng <= 105.0:
                        coordinates.append({
                            'latitude': lat,
                            'longitude': lng,
                            'method': 'page_source'
                        })
                except (ValueError, IndexError):
                    continue
            
            self.logger.info(f"Extracted {len(coordinates)} markers via page source")
            return coordinates
            
        except Exception as e:
            self.logger.error(f"Failed to extract markers by page source: {e}")
            return []
    
    def extract_markers_by_javascript(self) -> List[Dict]:
        """Extract markers using JavaScript access to Leaflet layers (Method B)"""
        try:
            marker_data = self.driver.execute_script("""
                const markers = [];
                try {
                    // Try to access the Leaflet map instance
                    if (window.map && window.map._layers) {
                        for (let layerId in window.map._layers) {
                            const layer = window.map._layers[layerId];
                            if (layer.getLatLng && typeof layer.getLatLng === 'function') {
                                const latLng = layer.getLatLng();
                                if (latLng && latLng.lat && latLng.lng) {
                                    markers.push({
                                        lat: latLng.lat,
                                        lng: latLng.lng
                                    });
                                }
                            }
                        }
                    }
                } catch (e) {
                    console.log('Error accessing Leaflet layers:', e);
                }
                return markers;
            """)
            
            coordinates = []
            for marker in marker_data:
                try:
                    coordinates.append({
                        'latitude': float(marker['lat']),
                        'longitude': float(marker['lng']),
                        'method': 'javascript'
                    })
                except Exception as e:
                    self.logger.warning(f"Error processing JavaScript marker: {e}")
                    continue
            
            self.logger.info(f"Extracted {len(coordinates)} markers via JavaScript")
            return coordinates
            
        except Exception as e:
            self.logger.error(f"Failed to extract markers by JavaScript: {e}")
            return []
    
    def extract_markers_by_clicking(self) -> List[Dict]:
        """Extract markers by clicking them to get popup data (Method C)"""
        try:
            # Find all clickable markers
            markers = self.driver.find_elements(
                By.CSS_SELECTOR, 
                ".leaflet-marker-icon"
            )
            
            coordinates = []
            for i, marker in enumerate(markers):
                try:
                    # Click the marker
                    self.driver.execute_script("arguments[0].click();", marker)
                    time.sleep(1)  # Wait for popup
                    
                    # Extract popup data
                    popup_data = self._extract_popup_data()
                    if popup_data:
                        coordinates.append(popup_data)
                    
                    # Close popup if it exists
                    self._close_popup()
                    
                except Exception as e:
                    self.logger.warning(f"Error clicking marker {i}: {e}")
                    continue
            
            self.logger.info(f"Extracted {len(coordinates)} markers via clicking")
            return coordinates
            
        except Exception as e:
            self.logger.error(f"Failed to extract markers by clicking: {e}")
            return []
    
    def _extract_popup_data(self) -> Optional[Dict]:
        """Extract data from marker popup"""
        try:
            # Look for popup content
            popup_selectors = [
                ".leaflet-popup-content",
                ".leaflet-popup-content-wrapper",
                "[class*='popup']"
            ]
            
            for selector in popup_selectors:
                popup = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if popup:
                    popup_text = popup[0].text
                    if popup_text:
                        return {
                            'popup_text': popup_text,
                            'method': 'clicking'
                        }
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error extracting popup data: {e}")
            return None
    
    def _close_popup(self):
        """Close any open popup"""
        try:
            # Look for close button or click outside popup
            close_selectors = [
                ".leaflet-popup-close-button",
                ".leaflet-popup-close",
                "[class*='close']"
            ]
            
            for selector in close_selectors:
                close_btn = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if close_btn:
                    close_btn[0].click()
                    break
                    
        except Exception as e:
            self.logger.warning(f"Error closing popup: {e}")
    
    def extract_markers_with_cluster_expansion(self, url: str, max_zoom: int = 16) -> List[Dict]:
        """Extract markers with cluster expansion and zooming"""
        try:
            if not self.load_veggiemap_page(url):
                return []
            
            # Initialize cluster handler
            cluster_handler = ClusterHandler(self.driver)
            
            # Step 1: Try to expand clusters
            self.logger.info("Step 1: Expanding clusters and zooming in...")
            expansion_log = cluster_handler.expand_all_clusters(max_zoom)
            self.logger.info(f"Cluster expansion completed: {len(expansion_log)} actions")
            
            # Step 2: Get individual markers after expansion
            self.logger.info("Step 2: Extracting individual markers...")
            individual_markers = cluster_handler.get_individual_markers()
            
            # Step 3: Fallback to other methods if needed
            all_coordinates = []
            
            if individual_markers:
                all_coordinates.extend(individual_markers)
                self.logger.info(f"Found {len(individual_markers)} individual markers")
            else:
                self.logger.info("No individual markers found, trying fallback methods...")
                
                # Fallback methods
                coords_1 = self.extract_markers_by_attributes()
                all_coordinates.extend(coords_1)
                
                coords_2 = self.extract_markers_by_page_source()
                all_coordinates.extend(coords_2)
                
                coords_3 = self.extract_markers_by_javascript()
                all_coordinates.extend(coords_3)
            
            # Remove duplicates based on coordinates
            unique_coordinates = self._remove_duplicate_coordinates(all_coordinates)
            
            self.logger.info(f"Total unique coordinates extracted: {len(unique_coordinates)}")
            return unique_coordinates
            
        except Exception as e:
            self.logger.error(f"Failed to extract markers with cluster expansion: {e}")
            return []
    
    def extract_all_markers(self, url: str) -> List[Dict]:
        """Extract all markers using multiple methods"""
        try:
            if not self.load_veggiemap_page(url):
                return []
            
            all_coordinates = []
            
            # Method 1: Direct attributes
            self.logger.info("Trying Method 1: Direct marker attributes")
            coords_1 = self.extract_markers_by_attributes()
            all_coordinates.extend(coords_1)
            
            # Method 2: Page source regex
            self.logger.info("Trying Method 2: Page source regex")
            coords_2 = self.extract_markers_by_page_source()
            all_coordinates.extend(coords_2)
            
            # Method 3: JavaScript access
            self.logger.info("Trying Method 3: JavaScript access")
            coords_3 = self.extract_markers_by_javascript()
            all_coordinates.extend(coords_3)
            
            # Method 4: Clicking markers
            self.logger.info("Trying Method 4: Clicking markers")
            coords_4 = self.extract_markers_by_clicking()
            all_coordinates.extend(coords_4)
            
            # Remove duplicates based on coordinates
            unique_coordinates = self._remove_duplicate_coordinates(all_coordinates)
            
            self.logger.info(f"Total unique coordinates extracted: {len(unique_coordinates)}")
            return unique_coordinates
            
        except Exception as e:
            self.logger.error(f"Failed to extract all markers: {e}")
            return []
    
    def _remove_duplicate_coordinates(self, coordinates: List[Dict]) -> List[Dict]:
        """Remove duplicate coordinates"""
        seen = set()
        unique = []
        
        for coord in coordinates:
            lat = coord.get('latitude')
            lng = coord.get('longitude')
            if lat is not None and lng is not None:
                key = (round(lat, 6), round(lng, 6))  # Round to avoid floating point issues
                if key not in seen:
                    seen.add(key)
                    unique.append(coord)
        
        return unique
    
    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver closed successfully")
            except Exception as e:
                self.logger.warning(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None
