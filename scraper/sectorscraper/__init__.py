"""
HappyCow Sector Scraper Package
Scrapes Singapore restaurants by dividing the map into sectors
"""

from .sector_grid import SingaporeSectorGrid
from .url_generator import HappyCowURLGenerator
from .page_loader import HappyCowPageLoader
from .data_extractor import HappyCowDataExtractor
from .sector_scraper import HappyCowSectorScraper
from .session_manager import ScrapingSessionManager
from .reviews_enhancer import ReviewsEnhancer

__version__ = "1.0.0"
__author__ = "HappyCow Scraper Team"

__all__ = [
    'SingaporeSectorGrid',
    'HappyCowURLGenerator', 
    'HappyCowPageLoader',
    'HappyCowDataExtractor',
    'HappyCowSectorScraper',
    'ScrapingSessionManager',
    'ReviewsEnhancer'
]
