import logging
import requests
import re
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_coordinates_from_source():
    """Extract coordinates from page source using regex patterns"""
    logger.info("🔍 Extracting coordinates from page source...")

    # Use the same URL as the scraper
    url = "https://www.happycow.net/searchmap?s=3&location=Central Singapore, Singapore&lat=1.34183&lng=103.861&page=1&zoom=11&metric=mi&order=default"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
    }

    try:
        logger.info(f"Fetching page: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        page_source = response.text
        
        # Look for coordinate patterns in the page source
        coord_patterns = [
            (r'data-lat="([^"]+)"', 'data-lat attributes'),
            (r'data-lng="([^"]+)"', 'data-lng attributes'),
            (r'"lat":\s*([0-9.]+)', 'lat in JSON'),
            (r'"lng":\s*([0-9.]+)', 'lng in JSON'),
            (r'"latitude":\s*([0-9.]+)', 'latitude in JSON'),
            (r'"longitude":\s*([0-9.]+)', 'longitude in JSON'),
            (r'lat:\s*([0-9.]+)', 'lat in JS'),
            (r'lng:\s*([0-9.]+)', 'lng in JS')
        ]
        
        all_coords = {}
        for pattern, description in coord_patterns:
            matches = re.findall(pattern, page_source)
            if matches:
                all_coords[description] = matches
                logger.info(f"✅ Found {len(matches)} {description}")
            else:
                logger.info(f"❌ No {description} found")
        
        # Look for data-id patterns to match with coordinates
        data_id_pattern = r'data-id="([^"]+)"'
        data_ids = re.findall(data_id_pattern, page_source)
        logger.info(f"Found {len(data_ids)} data-id attributes")
        
        # Try to find the relationship between data-id and coordinates
        if 'data-lat attributes' in all_coords and 'data-lng attributes' in all_coords:
            lats = all_coords['data-lat attributes']
            lngs = all_coords['data-lng attributes']
            
            logger.info(f"Found {len(lats)} latitude values and {len(lngs)} longitude values")
            
            # Show first few coordinate pairs
            for i in range(min(5, len(lats), len(lngs))):
                logger.info(f"Coordinate pair {i+1}: lat={lats[i]}, lng={lngs[i]}")
        
        # Look for JavaScript data structures that might contain coordinates
        js_patterns = [
            r'venues\s*:\s*\[(.*?)\]',
            r'restaurants\s*:\s*\[(.*?)\]',
            r'locations\s*:\s*\[(.*?)\]',
            r'markers\s*:\s*\[(.*?)\]',
            r'data\s*:\s*\[(.*?)\]'
        ]
        
        logger.info("\n🔍 Looking for JavaScript data structures...")
        for pattern in js_patterns:
            matches = re.findall(pattern, page_source, re.DOTALL)
            if matches:
                logger.info(f"✅ Found JavaScript data pattern: {pattern}")
                for i, match in enumerate(matches[:2]):  # First 2 matches
                    logger.info(f"  Match {i+1}: {match[:200]}...")
        
        # Look for specific coordinate patterns that might be in JavaScript
        js_coord_patterns = [
            r'\{[^}]*"lat"[^}]*"lng"[^}]*\}',
            r'\{[^}]*"lng"[^}]*"lat"[^}]*\}',
            r'\{[^}]*"latitude"[^}]*"longitude"[^}]*\}',
            r'\{[^}]*"longitude"[^}]*"latitude"[^}]*\}'
        ]
        
        logger.info("\n🔍 Looking for coordinate objects in JavaScript...")
        for pattern in js_coord_patterns:
            matches = re.findall(pattern, page_source)
            if matches:
                logger.info(f"✅ Found coordinate objects: {pattern}")
                for i, match in enumerate(matches[:3]):  # First 3 matches
                    logger.info(f"  Object {i+1}: {match}")
        
        return True

    except Exception as e:
        logger.error(f"Error extracting coordinates: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Extracting Coordinates from Page Source")
    print("=" * 50)
    if extract_coordinates_from_source():
        print("\n✅ Test completed successfully")
    else:
        print("\n❌ Test failed")
