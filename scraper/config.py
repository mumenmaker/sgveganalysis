import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Supabase Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL', '')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
    
    # Scraper Configuration
    DELAY_BETWEEN_REQUESTS = int(os.getenv('DELAY_BETWEEN_REQUESTS', '2'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    USER_AGENT_ROTATION = os.getenv('USER_AGENT_ROTATION', 'True').lower() == 'true'
    
    # HappyCow URLs
    BASE_URL = "https://www.happycow.net"
    SEARCH_URL = "https://www.happycow.net/searchmap"
    
    # Singapore specific parameters
    SINGAPORE_PARAMS = {
        's': '3',
        'location': 'Central Singapore, Singapore',
        'lat': '1.34183',
        'lng': '103.861',
        'page': '1',
        'zoom': '11',
        'metric': 'mi',
        'limit': '81',
        'order': 'default'
    }
