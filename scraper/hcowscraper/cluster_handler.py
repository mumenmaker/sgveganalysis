#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cluster Handler for HappyCow Veggiemap
Handles marker clustering and zooming to extract individual restaurant records
"""

import time
import logging
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ClusterHandler:
    """Handle marker clustering and zooming to extract individual restaurants"""
    
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.logger = logging.getLogger(__name__)
        self.actions = ActionChains(driver)
        
    def zoom_to_level(self, zoom_level: int) -> bool:
        """Zoom the map to a specific level"""
        try:
            self.logger.info(f"Zooming to level {zoom_level}")
            
            # Try multiple zoom methods
            success = False
            
            # Method 1: Use JavaScript to set zoom level
            try:
                self.driver.execute_script(f"""
                    if (window.map) {{
                        window.map.setZoom({zoom_level});
                    }}
                """)
                time.sleep(2)
                success = True
                self.logger.info(f"Zoomed to level {zoom_level} via JavaScript")
            except Exception as e:
                self.logger.warning(f"JavaScript zoom failed: {e}")
            
            # Method 2: Use zoom controls if available
            try:
                zoom_controls = self.driver.find_elements(By.CSS_SELECTOR, 
                    ".leaflet-control-zoom-in, .leaflet-control-zoom-out, [class*='zoom']")
                
                if zoom_controls:
                    # Calculate how many clicks needed
                    current_zoom = self.get_current_zoom_level()
                    clicks_needed = zoom_level - current_zoom
                    
                    if clicks_needed > 0:
                        # Zoom in
                        zoom_in_btn = self.driver.find_elements(By.CSS_SELECTOR, 
                            ".leaflet-control-zoom-in")
                        for _ in range(min(clicks_needed, 10)):  # Limit to 10 clicks
                            if zoom_in_btn:
                                zoom_in_btn[0].click()
                                time.sleep(0.5)
                    elif clicks_needed < 0:
                        # Zoom out
                        zoom_out_btn = self.driver.find_elements(By.CSS_SELECTOR, 
                            ".leaflet-control-zoom-out")
                        for _ in range(min(abs(clicks_needed), 10)):  # Limit to 10 clicks
                            if zoom_out_btn:
                                zoom_out_btn[0].click()
                                time.sleep(0.5)
                    
                    success = True
                    self.logger.info(f"Zoomed via controls to level {zoom_level}")
            except Exception as e:
                self.logger.warning(f"Control zoom failed: {e}")
            
            # Method 3: Mouse wheel zoom
            try:
                map_container = self.driver.find_element(By.CLASS_NAME, "leaflet-container")
                
                # Calculate wheel delta for zoom level
                current_zoom = self.get_current_zoom_level()
                zoom_delta = zoom_level - current_zoom
                
                if zoom_delta != 0:
                    # Simulate mouse wheel events
                    for _ in range(abs(zoom_delta)):
                        if zoom_delta > 0:
                            # Zoom in (positive delta)
                            self.actions.move_to_element(map_container).scroll_by_amount(0, -100).perform()
                        else:
                            # Zoom out (negative delta)
                            self.actions.move_to_element(map_container).scroll_by_amount(0, 100).perform()
                        time.sleep(0.5)
                    
                    success = True
                    self.logger.info(f"Zoomed via mouse wheel to level {zoom_level}")
            except Exception as e:
                self.logger.warning(f"Mouse wheel zoom failed: {e}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to zoom to level {zoom_level}: {e}")
            return False
    
    def get_current_zoom_level(self) -> int:
        """Get the current zoom level of the map"""
        try:
            zoom_level = self.driver.execute_script("""
                if (window.map) {
                    return window.map.getZoom();
                }
                return null;
            """)
            
            if zoom_level is not None:
                return int(zoom_level)
            else:
                # Fallback: try to extract from URL or other sources
                current_url = self.driver.current_url
                if 'zoom=' in current_url:
                    import re
                    match = re.search(r'zoom=(\d+)', current_url)
                    if match:
                        return int(match.group(1))
                
                return 11  # Default fallback
                
        except Exception as e:
            self.logger.warning(f"Could not get current zoom level: {e}")
            return 11
    
    def click_cluster_markers(self) -> List[Dict]:
        """Click on cluster markers to expand them"""
        try:
            self.logger.info("Looking for cluster markers to click...")
            
            # Find cluster markers (usually have different styling)
            cluster_selectors = [
                ".leaflet-marker-icon[class*='cluster']",
                ".leaflet-marker-icon[class*='marker-cluster']",
                ".leaflet-marker-icon[title*='cluster']",
                ".leaflet-marker-icon[title*='markers']",
                ".leaflet-marker-icon"  # Fallback to all markers
            ]
            
            clicked_markers = []
            
            for selector in cluster_selectors:
                markers = self.driver.find_elements(By.CSS_SELECTOR, selector)
                self.logger.info(f"Found {len(markers)} markers with selector: {selector}")
                
                for i, marker in enumerate(markers):
                    try:
                        # Check if marker looks like a cluster
                        marker_text = marker.get_attribute('title') or ''
                        marker_class = marker.get_attribute('class') or ''
                        
                        # Skip if already processed or not a cluster
                        if 'cluster' not in marker_class.lower() and 'markers' not in marker_text.lower():
                            continue
                        
                        self.logger.info(f"Clicking cluster marker {i+1}: {marker_text}")
                        
                        # Click the marker
                        self.driver.execute_script("arguments[0].click();", marker)
                        time.sleep(2)  # Wait for cluster to expand
                        
                        # Check if new markers appeared
                        new_markers = self.driver.find_elements(By.CSS_SELECTOR, ".leaflet-marker-icon")
                        self.logger.info(f"Found {len(new_markers)} markers after clicking cluster")
                        
                        clicked_markers.append({
                            'marker_index': i,
                            'marker_text': marker_text,
                            'new_marker_count': len(new_markers)
                        })
                        
                    except Exception as e:
                        self.logger.warning(f"Error clicking cluster marker {i+1}: {e}")
                        continue
            
            return clicked_markers
            
        except Exception as e:
            self.logger.error(f"Failed to click cluster markers: {e}")
            return []
    
    def pan_to_area(self, lat: float, lng: float) -> bool:
        """Pan the map to a specific area"""
        try:
            self.logger.info(f"Panning to coordinates: {lat}, {lng}")
            
            # Method 1: Use JavaScript to pan
            try:
                self.driver.execute_script(f"""
                    if (window.map) {{
                        window.map.panTo([{lat}, {lng}]);
                    }}
                """)
                time.sleep(2)
                self.logger.info("Panned via JavaScript")
                return True
            except Exception as e:
                self.logger.warning(f"JavaScript pan failed: {e}")
            
            # Method 2: Use map controls if available
            try:
                # Look for pan controls or drag the map
                map_container = self.driver.find_element(By.CLASS_NAME, "leaflet-container")
                
                # Simulate drag to pan (this is complex, so we'll use JavaScript)
                self.driver.execute_script(f"""
                    if (window.map) {{
                        window.map.setView([{lat}, {lng}], window.map.getZoom());
                    }}
                """)
                time.sleep(2)
                self.logger.info("Panned via setView")
                return True
                
            except Exception as e:
                self.logger.warning(f"Control pan failed: {e}")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to pan to area: {e}")
            return False
    
    def expand_all_clusters(self, max_zoom: int = 16) -> List[Dict]:
        """Systematically expand all clusters by zooming and clicking"""
        try:
            self.logger.info("Starting systematic cluster expansion...")
            
            expansion_log = []
            current_zoom = self.get_current_zoom_level()
            
            # Zoom in gradually
            for zoom_level in range(current_zoom + 1, max_zoom + 1):
                self.logger.info(f"Zooming to level {zoom_level}")
                
                if self.zoom_to_level(zoom_level):
                    time.sleep(3)  # Wait for map to update
                    
                    # Click any visible cluster markers
                    clicked_markers = self.click_cluster_markers()
                    expansion_log.extend(clicked_markers)
                    
                    # Check if we have individual markers now
                    individual_markers = self.driver.find_elements(By.CSS_SELECTOR, 
                        ".leaflet-marker-icon:not([class*='cluster'])")
                    
                    self.logger.info(f"Found {len(individual_markers)} individual markers at zoom {zoom_level}")
                    
                    # If we have many individual markers, we might be done
                    if len(individual_markers) > 10:
                        self.logger.info(f"Found sufficient individual markers at zoom {zoom_level}")
                        break
            
            return expansion_log
            
        except Exception as e:
            self.logger.error(f"Failed to expand clusters: {e}")
            return []
    
    def get_individual_markers(self) -> List[Dict]:
        """Get individual restaurant markers (not clusters)"""
        try:
            # Look for individual markers (not clusters)
            individual_selectors = [
                ".leaflet-marker-icon:not([class*='cluster'])",
                ".leaflet-marker-icon:not([title*='markers'])",
                ".leaflet-marker-icon[data-lat][data-lng]"
            ]
            
            individual_markers = []
            
            for selector in individual_selectors:
                markers = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                for marker in markers:
                    try:
                        # Extract marker data
                        lat = marker.get_attribute('data-lat')
                        lng = marker.get_attribute('data-lng')
                        title = marker.get_attribute('title') or ''
                        marker_class = marker.get_attribute('class') or ''
                        
                        # Skip if it's still a cluster
                        if 'cluster' in marker_class.lower() or 'markers' in title.lower():
                            continue
                        
                        if lat and lng:
                            individual_markers.append({
                                'latitude': float(lat),
                                'longitude': float(lng),
                                'title': title,
                                'class': marker_class
                            })
                            
                    except Exception as e:
                        self.logger.warning(f"Error processing individual marker: {e}")
                        continue
            
            self.logger.info(f"Found {len(individual_markers)} individual markers")
            return individual_markers
            
        except Exception as e:
            self.logger.error(f"Failed to get individual markers: {e}")
            return []
