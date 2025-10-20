"""
Singapore Sector Grid Generator
Divides Singapore into 48 sectors (6x8 grid) for systematic scraping
"""

from typing import List, Dict, Tuple
import logging

class SingaporeSectorGrid:
    """Generates a grid of sectors covering Singapore for systematic scraping"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Singapore bounds
        self.singapore_bounds = {
            'min_lat': 1.2,
            'max_lat': 1.5,
            'min_lng': 103.6,
            'max_lng': 104.0
        }
        
        # Grid dimensions
        self.lat_sectors = 6  # 6 sectors vertically
        self.lng_sectors = 8  # 8 sectors horizontally
        
        # Calculate sector size
        self.lat_step = (self.singapore_bounds['max_lat'] - self.singapore_bounds['min_lat']) / self.lat_sectors
        self.lng_step = (self.singapore_bounds['max_lng'] - self.singapore_bounds['min_lng']) / self.lng_sectors
    
    def generate_sectors(self) -> List[Dict]:
        """Generate all 48 sectors with their coordinates and metadata"""
        sectors = []
        
        for lat_idx in range(self.lat_sectors):
            for lng_idx in range(self.lng_sectors):
                # Calculate sector center
                lat_center = self.singapore_bounds['min_lat'] + (lat_idx + 0.5) * self.lat_step
                lng_center = self.singapore_bounds['min_lng'] + (lng_idx + 0.5) * self.lng_step
                
                # Calculate sector bounds
                lat_min = self.singapore_bounds['min_lat'] + lat_idx * self.lat_step
                lat_max = lat_min + self.lat_step
                lng_min = self.singapore_bounds['min_lng'] + lng_idx * self.lng_step
                lng_max = lng_min + self.lng_step
                
                # Generate sector name
                sector_name = f"Sector_{lat_idx+1}_{lng_idx+1}"
                
                # Create sector data
                sector = {
                    'id': f"{lat_idx+1}_{lng_idx+1}",
                    'name': sector_name,
                    'lat_center': round(lat_center, 6),
                    'lng_center': round(lng_center, 6),
                    'lat_min': round(lat_min, 6),
                    'lat_max': round(lat_max, 6),
                    'lng_min': round(lng_min, 6),
                    'lng_max': round(lng_max, 6),
                    'grid_position': (lat_idx + 1, lng_idx + 1),
                    'area_km2': self._calculate_sector_area(lat_min, lat_max, lng_min, lng_max)
                }
                
                sectors.append(sector)
        
        self.logger.info(f"Generated {len(sectors)} sectors covering Singapore")
        return sectors
    
    def _calculate_sector_area(self, lat_min: float, lat_max: float, lng_min: float, lng_max: float) -> float:
        """Calculate approximate area of a sector in km²"""
        # Rough calculation for Singapore's latitude
        lat_km_per_degree = 111.32  # km per degree latitude
        lng_km_per_degree = 111.32 * 0.866  # km per degree longitude at Singapore's latitude
        
        lat_km = (lat_max - lat_min) * lat_km_per_degree
        lng_km = (lng_max - lng_min) * lng_km_per_degree
        
        return round(lat_km * lng_km, 2)
    
    def get_sector_by_id(self, sector_id: str) -> Dict:
        """Get a specific sector by its ID"""
        sectors = self.generate_sectors()
        for sector in sectors:
            if sector['id'] == sector_id:
                return sector
        return None
    
    def get_sectors_by_region(self, region: str) -> List[Dict]:
        """Get sectors by region (Central, East, West, North, Northeast, South)"""
        sectors = self.generate_sectors()
        
        if region.lower() == 'central':
            # Central Singapore (sectors 2-4, columns 3-6)
            return [s for s in sectors if 2 <= s['grid_position'][0] <= 4 and 3 <= s['grid_position'][1] <= 6]
        elif region.lower() == 'east':
            # East Singapore (sectors 1-6, columns 7-8)
            return [s for s in sectors if 7 <= s['grid_position'][1] <= 8]
        elif region.lower() == 'west':
            # West Singapore (sectors 1-6, columns 1-2)
            return [s for s in sectors if 1 <= s['grid_position'][1] <= 2]
        elif region.lower() == 'north':
            # North Singapore (sectors 5-6, columns 1-8)
            return [s for s in sectors if 5 <= s['grid_position'][0] <= 6]
        elif region.lower() == 'northeast':
            # Northeast Singapore (sectors 4-6, columns 5-8)
            return [s for s in sectors if 4 <= s['grid_position'][0] <= 6 and 5 <= s['grid_position'][1] <= 8]
        elif region.lower() == 'south':
            # South Singapore (sectors 1-2, columns 1-8)
            return [s for s in sectors if 1 <= s['grid_position'][0] <= 2]
        else:
            return sectors
    
    def print_sector_summary(self):
        """Print a summary of all sectors"""
        sectors = self.generate_sectors()
        
        print("Singapore Sector Grid Summary")
        print("=" * 50)
        print(f"Total Sectors: {len(sectors)}")
        print(f"Grid Size: {self.lat_sectors} × {self.lng_sectors}")
        print(f"Latitude Range: {self.singapore_bounds['min_lat']}° to {self.singapore_bounds['max_lat']}°")
        print(f"Longitude Range: {self.singapore_bounds['min_lng']}° to {self.singapore_bounds['max_lng']}°")
        print(f"Sector Size: {self.lat_step:.3f}° × {self.lng_step:.3f}°")
        print()
        
        # Print grid layout
        print("Sector Grid Layout:")
        print("(Row, Column) format")
        for lat_idx in range(self.lat_sectors):
            row_sectors = []
            for lng_idx in range(self.lng_sectors):
                sector_id = f"{lat_idx+1}_{lng_idx+1}"
                row_sectors.append(sector_id)
            print(f"Row {lat_idx+1}: {' '.join(row_sectors)}")
        print()
        
        # Print first few sectors as examples
        print("Sample Sectors:")
        for i, sector in enumerate(sectors[:5]):
            print(f"  {sector['name']}: Center({sector['lat_center']}, {sector['lng_center']}) - Area: {sector['area_km2']} km²")
        print(f"  ... and {len(sectors)-5} more sectors")


if __name__ == "__main__":
    # Test the sector grid generator
    grid = SingaporeSectorGrid()
    grid.print_sector_summary()
    
    # Test getting specific sectors
    print("\nTesting specific sector retrieval:")
    test_sector = grid.get_sector_by_id("3_4")
    if test_sector:
        print(f"Sector 3_4: {test_sector}")
    
    # Test regional sectors
    central_sectors = grid.get_sectors_by_region("central")
    print(f"\nCentral Singapore sectors: {len(central_sectors)}")
    for sector in central_sectors[:3]:
        print(f"  {sector['name']}: ({sector['lat_center']}, {sector['lng_center']})")
