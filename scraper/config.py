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
    VEGGIEMAP_URL = "https://www.happycow.net/veggiemap"
    
    # Singapore veggiemap parameters
    SINGAPORE_VEGGIEMAP_PARAMS = {
        'location': 'singapore',
        'zoom': '11',
        'clat': '1.351188231529612',
        'clng': '103.8091278076172'
    }
