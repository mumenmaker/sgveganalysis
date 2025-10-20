"""
Page Loader for HappyCow SearchMap
Handles loading and waiting for content on each sector page
"""

import time
import logging
from typing import Optional, Dict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

class HappyCowPageLoader:
    """Handles loading HappyCow searchmap pages and waiting for content"""
    
    def __init__(self, headless: bool = True, wait_timeout: int = 30):
        self.logger = logging.getLogger(__name__)
        self.headless = headless
        self.wait_timeout = wait_timeout
        self.driver = None
        
    def setup_driver(self) -> bool:
        """Setup Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Performance and stability options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-javascript")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Window size
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            
            self.logger.info("Chrome WebDriver setup successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup Chrome WebDriver: {e}")
            return False
    
    def load_sector_page(self, url: str) -> bool:
        """Load a specific sector page and wait for content"""
        try:
            if not self.driver:
                if not self.setup_driver():
                    return False
            
            self.logger.info(f"Loading sector page: {url}")
            
            # Navigate to the page
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Wait for specific elements that indicate content is loaded
            if self._wait_for_content():
                self.logger.info("Page content loaded successfully")
                return True
            else:
                self.logger.warning("Page content may not be fully loaded")
                return False
                
        except TimeoutException:
            self.logger.error(f"Timeout loading page: {url}")
            return False
        except WebDriverException as e:
            self.logger.error(f"WebDriver error loading page: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error loading page: {e}")
            return False
    
    def _wait_for_content(self) -> bool:
        """Wait for specific content elements to appear"""
        try:
            # Wait for the map container
            WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".leaflet-container"))
            )
            
            # Wait for markers or results
            WebDriverWait(self.driver, 10).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".leaflet-marker-icon")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".search-results")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".no-results"))
                )
            )
            
            return True
            
        except TimeoutException:
            self.logger.warning("Timeout waiting for content elements")
            return False
        except Exception as e:
            self.logger.warning(f"Error waiting for content: {e}")
            return False
    
    def get_page_source(self) -> Optional[str]:
        """Get the current page source"""
        try:
            if self.driver:
                return self.driver.page_source
            return None
        except Exception as e:
            self.logger.error(f"Error getting page source: {e}")
            return None
    
    def get_page_title(self) -> Optional[str]:
        """Get the current page title"""
        try:
            if self.driver:
                return self.driver.title
            return None
        except Exception as e:
            self.logger.error(f"Error getting page title: {e}")
            return None
    
    def check_for_errors(self) -> bool:
        """Check if the page shows any error messages"""
        try:
            if not self.driver:
                return True
            
            # Check for common error indicators
            error_selectors = [
                ".error-message",
                ".no-results",
                ".search-error",
                "[class*='error']"
            ]
            
            for selector in error_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    error_text = elements[0].text.strip()
                    if error_text:
                        self.logger.warning(f"Error detected on page: {error_text}")
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking for page errors: {e}")
            return False
    
    def get_marker_count(self) -> int:
        """Get the number of markers visible on the page"""
        try:
            if not self.driver:
                return 0
            
            markers = self.driver.find_elements(By.CSS_SELECTOR, ".leaflet-marker-icon")
            count = len(markers)
            self.logger.debug(f"Found {count} markers on page")
            return count
            
        except Exception as e:
            self.logger.error(f"Error counting markers: {e}")
            return 0
    
    def get_results_count(self) -> int:
        """Get the number of results shown on the page"""
        try:
            if not self.driver:
                return 0
            
            # Look for results count in various places
            count_selectors = [
                ".results-count",
                ".search-results-count",
                "[class*='count']",
                ".total-results"
            ]
            
            for selector in count_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    text = elements[0].text.strip()
                    # Extract number from text
                    import re
                    numbers = re.findall(r'\d+', text)
                    if numbers:
                        return int(numbers[0])
            
            # Fallback to marker count
            return self.get_marker_count()
            
        except Exception as e:
            self.logger.error(f"Error getting results count: {e}")
            return 0
    
    def close_driver(self):
        """Close the WebDriver"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.logger.info("WebDriver closed")
        except Exception as e:
            self.logger.error(f"Error closing WebDriver: {e}")
    
    def __del__(self):
        """Ensure driver is closed when object is destroyed"""
        self.close_driver()


if __name__ == "__main__":
    # Test the page loader
    from .sector_grid import SingaporeSectorGrid
    from .url_generator import HappyCowURLGenerator
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Generate test sector and URL
    grid = SingaporeSectorGrid()
    sectors = grid.generate_sectors()
    url_gen = HappyCowURLGenerator()
    
    test_sector = sectors[0]
    test_url = url_gen.generate_sector_url(test_sector)
    
    print(f"Testing page loader with sector: {test_sector['name']}")
    print(f"URL: {test_url}")
    
    # Test page loading
    loader = HappyCowPageLoader(headless=False)  # Set to False for visual testing
    
    try:
        if loader.load_sector_page(test_url):
            print("✅ Page loaded successfully")
            print(f"Page title: {loader.get_page_title()}")
            print(f"Markers found: {loader.get_marker_count()}")
            print(f"Results count: {loader.get_results_count()}")
            print(f"Has errors: {loader.check_for_errors()}")
        else:
            print("❌ Failed to load page")
    finally:
        loader.close_driver()
