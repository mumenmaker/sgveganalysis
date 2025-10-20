"""
HappyCow Scraper Library
A modular library for scraping restaurant data from HappyCow veggiemap
"""

from .veggiemap_scraper import VeggiemapScraper
from .marker_extractor import MarkerExtractor
from .restaurant_parser import RestaurantParser

__version__ = "1.0.0"
__author__ = "HappyCow Scraper Team"

__all__ = [
    'VeggiemapScraper',
    'MarkerExtractor', 
    'RestaurantParser'
]
