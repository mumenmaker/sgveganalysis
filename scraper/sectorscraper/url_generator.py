"""
URL Generator for HappyCow SearchMap
Generates search URLs for each sector with proper parameters
"""

from typing import Dict, List
import logging

class HappyCowURLGenerator:
    """Generates HappyCow searchmap URLs for each sector"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Base URL for HappyCow searchmap
        self.base_url = "https://www.happycow.net/searchmap/"
        
        # Default parameters for Singapore search
        self.default_params = {
            's': '3',  # Search type
            'location': '',  # Empty for coordinate-based search
            'page': '1',  # Always page 1 for each sector
            'zoom': '11',  # Consistent zoom level
            'metric': 'mi',  # Distance metric
            'limit': '81',  # Maximum results per sector
            'order': 'default'  # Sort order
        }
    
    def generate_sector_url(self, sector: Dict) -> str:
        """Generate search URL for a specific sector"""
        try:
            # Build URL with sector coordinates
            url = f"{self.base_url}?s={self.default_params['s']}&location={self.default_params['location']}&lat={sector['lat_center']}&lng={sector['lng_center']}&page={self.default_params['page']}&zoom={self.default_params['zoom']}&metric={self.default_params['metric']}&limit={self.default_params['limit']}&order={self.default_params['order']}"
            
            self.logger.debug(f"Generated URL for {sector['name']}: {url}")
            return url
            
        except Exception as e:
            self.logger.error(f"Error generating URL for sector {sector.get('name', 'unknown')}: {e}")
            return None
    
    def generate_all_sector_urls(self, sectors: List[Dict]) -> List[Dict]:
        """Generate URLs for all sectors"""
        sector_urls = []
        
        for sector in sectors:
            url = self.generate_sector_url(sector)
            if url:
                sector_data = {
                    'sector': sector,
                    'url': url,
                    'status': 'pending'
                }
                sector_urls.append(sector_data)
            else:
                self.logger.error(f"Failed to generate URL for sector {sector['name']}")
        
        self.logger.info(f"Generated {len(sector_urls)} sector URLs")
        return sector_urls
    
    def validate_url(self, url: str) -> bool:
        """Validate that a URL has all required parameters"""
        required_params = ['s=', 'lat=', 'lng=', 'page=', 'zoom=', 'metric=', 'limit=', 'order=']
        
        for param in required_params:
            if param not in url:
                self.logger.warning(f"Missing parameter {param} in URL: {url}")
                return False
        
        return True
    
    def get_url_parameters(self, url: str) -> Dict:
        """Extract parameters from a URL"""
        try:
            # Split URL and extract query parameters
            if '?' in url:
                query_string = url.split('?')[1]
                params = {}
                
                for param in query_string.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        params[key] = value
                
                return params
            else:
                return {}
                
        except Exception as e:
            self.logger.error(f"Error parsing URL parameters: {e}")
            return {}
    
    def print_url_examples(self, sectors: List[Dict], max_examples: int = 5):
        """Print example URLs for the first few sectors"""
        print("HappyCow SearchMap URL Examples")
        print("=" * 50)
        
        for i, sector in enumerate(sectors[:max_examples]):
            url = self.generate_sector_url(sector)
            if url:
                print(f"\nSector {i+1}: {sector['name']}")
                print(f"  Center: ({sector['lat_center']}, {sector['lng_center']})")
                print(f"  URL: {url}")
                print(f"  Valid: {self.validate_url(url)}")
        
        if len(sectors) > max_examples:
            print(f"\n... and {len(sectors) - max_examples} more sectors")


if __name__ == "__main__":
    # Test the URL generator
    from .sector_grid import SingaporeSectorGrid
    
    # Generate sectors
    grid = SingaporeSectorGrid()
    sectors = grid.generate_sectors()
    
    # Generate URLs
    url_gen = HappyCowURLGenerator()
    url_gen.print_url_examples(sectors)
    
    # Test URL validation
    test_url = url_gen.generate_sector_url(sectors[0])
    print(f"\nURL Validation Test:")
    print(f"URL: {test_url}")
    print(f"Valid: {url_gen.validate_url(test_url)}")
    
    # Test parameter extraction
    params = url_gen.get_url_parameters(test_url)
    print(f"Extracted Parameters: {params}")
