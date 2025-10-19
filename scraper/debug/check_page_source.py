import logging
import requests
from bs4 import BeautifulSoup
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_page_source_for_coordinates():
    """Check if coordinates are present in the page source"""
    logger.info("🔍 Checking page source for coordinates...")

    # Use the same URL as the scraper
    url = "https://www.happycow.net/searchmap?s=3&location=Central Singapore, Singapore&lat=1.34183&lng=103.861&page=1&zoom=11&metric=mi&order=default"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
    }

    try:
        logger.info(f"Fetching page: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for elements with data-lat attributes
        elements_with_lat = soup.find_all(attrs={'data-lat': True})
        logger.info(f"Found {len(elements_with_lat)} elements with data-lat attribute")
        
        if elements_with_lat:
            for i, elem in enumerate(elements_with_lat[:5]):  # Check first 5
                lat = elem.get('data-lat')
                lng = elem.get('data-lng')
                logger.info(f"Element {i+1}: data-lat={lat}, data-lng={lng}")
        
        # Look for venue-item elements specifically
        venue_items = soup.find_all(class_='venue-item')
        logger.info(f"Found {len(venue_items)} venue-item elements")
        
        if venue_items:
            for i, item in enumerate(venue_items[:3]):  # Check first 3
                lat = item.get('data-lat')
                lng = item.get('data-lng')
                data_id = item.get('data-id')
                logger.info(f"Venue item {i+1}: data-id={data_id}, data-lat={lat}, data-lng={lng}")
        
        # Look for hidden details elements
        hidden_details = soup.find_all('div', class_='details hidden')
        logger.info(f"Found {len(hidden_details)} hidden details elements")
        
        if hidden_details:
            for i, detail in enumerate(hidden_details[:3]):  # Check first 3
                lat = detail.get('data-lat')
                lng = detail.get('data-lng')
                data_id = detail.get('data-id')
                logger.info(f"Hidden detail {i+1}: data-id={data_id}, data-lat={lat}, data-lng={lng}")
        
        # Search for coordinate patterns in the HTML
        coord_patterns = [
            r'data-lat="([^"]+)"',
            r'data-lng="([^"]+)"',
            r'"lat":\s*([0-9.]+)',
            r'"lng":\s*([0-9.]+)',
            r'"latitude":\s*([0-9.]+)',
            r'"longitude":\s*([0-9.]+)'
        ]
        
        for pattern in coord_patterns:
            matches = re.findall(pattern, response.text)
            if matches:
                logger.info(f"Found coordinates with pattern {pattern}: {matches[:5]}")  # Show first 5 matches
        
        # Check if the page is dynamic (contains JavaScript that loads coordinates)
        if 'data-lat' in response.text:
            logger.info("✅ Found 'data-lat' in page source")
        else:
            logger.info("❌ No 'data-lat' found in page source")
            
        if 'venue-item' in response.text:
            logger.info("✅ Found 'venue-item' in page source")
        else:
            logger.info("❌ No 'venue-item' found in page source")
            
        return True

    except Exception as e:
        logger.error(f"Error checking page source: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Checking Page Source for Coordinates")
    print("=" * 50)
    if check_page_source_for_coordinates():
        print("\n✅ Test completed successfully")
    else:
        print("\n❌ Test failed")
