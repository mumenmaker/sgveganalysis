#!/usr/bin/env python3
"""
Test script to check for pagination controls on HappyCow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from happycow_scraper import HappyCowScraper
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_pagination():
    """Test for pagination controls on HappyCow"""
    try:
        logger.info("🔍 Testing for pagination controls...")
        
        # Initialize scraper with Selenium
        scraper = HappyCowScraper(use_selenium=True, enable_resume=False)
        
        # Setup Selenium
        driver = scraper.setup_selenium()
        if not driver:
            logger.error("Failed to setup Selenium")
            return False
        
        # Load the page
        from config import Config
        params = Config.SINGAPORE_PARAMS.copy()
        url = f"{Config.SEARCH_URL}?" + "&".join([f"{k}={v}" for k, v in params.items()])
        
        logger.info(f"Loading page: {url}")
        driver.get(url)
        
        # Wait for page to load
        import time
        time.sleep(10)
        
        # Check for pagination controls
        from selenium.webdriver.common.by import By
        
        # Look for common pagination elements
        pagination_selectors = [
            '.pagination',
            '.pager',
            '.page-numbers',
            '.pagination-controls',
            '[class*="pagination"]',
            '[class*="pager"]',
            '[class*="page"]',
            'button[class*="next"]',
            'button[class*="more"]',
            'a[class*="next"]',
            'a[class*="more"]',
            'button:contains("Next")',
            'button:contains("More")',
            'button:contains("Load")',
            'button:contains("Show")'
        ]
        
        logger.info("🔍 Looking for pagination controls...")
        found_pagination = False
        
        for selector in pagination_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"✅ Found pagination elements with selector '{selector}': {len(elements)} elements")
                    for i, elem in enumerate(elements[:3]):  # Show first 3
                        try:
                            text = elem.text.strip()
                            if text:
                                logger.info(f"  Element {i+1}: '{text}'")
                        except:
                            pass
                    found_pagination = True
            except Exception as e:
                pass
        
        if not found_pagination:
            logger.warning("❌ No pagination controls found")
        
        # Check for "Load More" or "Show More" buttons
        logger.info("🔍 Looking for 'Load More' or 'Show More' buttons...")
        load_more_selectors = [
            'button:contains("Load More")',
            'button:contains("Show More")',
            'button:contains("More Results")',
            'button:contains("View All")',
            'a:contains("Load More")',
            'a:contains("Show More")'
        ]
        
        for selector in load_more_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"✅ Found 'Load More' elements with selector '{selector}': {len(elements)} elements")
                    for i, elem in enumerate(elements):
                        try:
                            text = elem.text.strip()
                            logger.info(f"  Element {i+1}: '{text}'")
                        except:
                            pass
            except Exception as e:
                pass
        
        # Check page source for pagination-related text
        logger.info("🔍 Checking page source for pagination-related text...")
        page_source = driver.page_source.lower()
        
        pagination_keywords = [
            'pagination', 'pager', 'next page', 'load more', 'show more', 
            'view all', 'more results', 'page 2', 'page 3', 'next', 'previous'
        ]
        
        found_keywords = []
        for keyword in pagination_keywords:
            if keyword in page_source:
                found_keywords.append(keyword)
        
        if found_keywords:
            logger.info(f"✅ Found pagination-related keywords in page source: {found_keywords}")
        else:
            logger.warning("❌ No pagination-related keywords found in page source")
        
        # Check if there are any JavaScript functions that might load more data
        logger.info("🔍 Checking for JavaScript functions that might load more data...")
        js_functions = [
            'loadMore', 'showMore', 'loadResults', 'getMoreResults', 
            'loadPage', 'nextPage', 'loadAll'
        ]
        
        found_js = []
        for func in js_functions:
            if func in page_source:
                found_js.append(func)
        
        if found_js:
            logger.info(f"✅ Found JavaScript functions: {found_js}")
        else:
            logger.warning("❌ No relevant JavaScript functions found")
        
        # Close Selenium
        scraper.close_selenium()
        
        return True
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Pagination Controls")
    print("=" * 50)
    
    success = test_pagination()
    
    if success:
        print("\n✅ Test completed successfully")
    else:
        print("\n❌ Test failed")
