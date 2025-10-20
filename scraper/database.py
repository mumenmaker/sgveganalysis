from supabase import create_client, Client
from typing import List, Optional
import logging
from config import Config
from models import Restaurant

class DatabaseManager:
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.logger = logging.getLogger(__name__)
        self.setup_connection()
    
    def setup_connection(self):
        """Setup Supabase connection"""
        try:
            if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
                self.logger.error("Supabase URL and KEY must be set in environment variables")
                return
            
            self.supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
            self.logger.info("Successfully connected to Supabase")
        except Exception as e:
            self.logger.error(f"Failed to connect to Supabase: {e}")
    
    def test_connection(self) -> bool:
        """Test the database connection"""
        try:
            if not self.supabase:
                self.logger.error("No Supabase connection available")
                return False
            
            # Try a simple query to test the connection
            result = self.supabase.table('restaurants').select('id').limit(1).execute()
            self.logger.info("Database connection test successful")
            return True
        except Exception as e:
            self.logger.error(f"Database connection test failed: {e}")
            return False
    
    def create_tables(self):
        """Create necessary tables in Supabase"""
        if not self.supabase:
            self.logger.error("No Supabase connection available")
            return False
        
        try:
            # SQL to create restaurants table
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS restaurants (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                address TEXT,
                phone VARCHAR(50),
                website TEXT,
                cow_reviews TEXT,
                description TEXT,
                cuisine_type VARCHAR(100),
                price_range VARCHAR(50),
                rating DECIMAL(3,2),
                review_count INTEGER,
                latitude DECIMAL(10,8),
                longitude DECIMAL(11,8),
                is_vegan BOOLEAN DEFAULT FALSE,
                is_vegetarian BOOLEAN DEFAULT FALSE,
                has_veg_options BOOLEAN DEFAULT FALSE,
                features TEXT[], -- Array of features
                hours TEXT,
                happycow_url TEXT,
                scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Create indexes for better performance
            CREATE INDEX IF NOT EXISTS idx_restaurants_name ON restaurants(name);
            CREATE INDEX IF NOT EXISTS idx_restaurants_location ON restaurants(latitude, longitude);
            CREATE INDEX IF NOT EXISTS idx_restaurants_type ON restaurants(is_vegan, is_vegetarian, has_veg_options);
            CREATE INDEX IF NOT EXISTS idx_restaurants_rating ON restaurants(rating);
            
            -- Create updated_at trigger
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ language 'plpgsql';
            
            DROP TRIGGER IF EXISTS update_restaurants_updated_at ON restaurants;
            CREATE TRIGGER update_restaurants_updated_at
                BEFORE UPDATE ON restaurants
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
            """
            
            # Execute the SQL
            result = self.supabase.rpc('exec_sql', {'sql': create_table_sql})
            self.logger.info("Successfully created restaurants table and indexes")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating tables: {e}")
            return False
    
    def check_restaurant_exists(self, name: str, address: str = None, latitude: float = None, longitude: float = None) -> bool:
        """Check if a restaurant already exists in the database"""
        if not self.supabase:
            return False
        
        try:
            # First try to check by coordinates (most reliable)
            if latitude is not None and longitude is not None:
                query = self.supabase.table('restaurants').select('id').eq('latitude', latitude).eq('longitude', longitude)
                result = query.limit(1).execute()
                if len(result.data) > 0:
                    return True
            
            # Fallback to name and address check
            query = self.supabase.table('restaurants').select('id').eq('name', name)
            if address:
                query = query.eq('address', address)
            
            result = query.limit(1).execute()
            return len(result.data) > 0
        except Exception as e:
            self.logger.error(f"Error checking restaurant existence: {e}")
            return False
    
    def insert_restaurants(self, restaurants: List[Restaurant], skip_duplicates: bool = True) -> tuple:
        """Insert restaurants into Supabase database with duplicate detection
        
        Returns:
            tuple: (success: bool, inserted_count: int, skipped_count: int)
        """
        if not self.supabase:
            self.logger.error("No Supabase connection available")
            return False, 0, 0
        
        try:
            inserted_count = 0
            skipped_count = 0
            restaurant_data = []
            
            for restaurant in restaurants:
                # Check for duplicates if skip_duplicates is True
                if skip_duplicates and self.check_restaurant_exists(
                    restaurant.name, 
                    restaurant.address, 
                    restaurant.latitude, 
                    restaurant.longitude
                ):
                    self.logger.info(f"Skipping duplicate: {restaurant.name} at ({restaurant.latitude}, {restaurant.longitude})")
                    skipped_count += 1
                    continue
                
                data = restaurant.model_dump()
                # Convert datetime to string for JSON serialization
                data['scraped_at'] = data['scraped_at'].isoformat()
                restaurant_data.append(data)
            
            if not restaurant_data:
                self.logger.info("No new restaurants to insert (all were duplicates)")
                return True, 0, skipped_count
            
            # Insert into database
            try:
                result = self.supabase.table('restaurants').insert(restaurant_data).execute()
                
                if result.data:
                    inserted_count = len(result.data)
                    self.logger.info(f"Successfully inserted {inserted_count} restaurants, skipped {skipped_count} duplicates")
                    return True, inserted_count, skipped_count
                else:
                    self.logger.error("Failed to insert restaurants")
                    return False, 0, skipped_count
            except Exception as e:
                # Handle unique constraint violations (location-based duplicates)
                if "duplicate key value violates unique constraint" in str(e).lower():
                    self.logger.warning(f"Duplicate restaurant locations detected, skipping insertion: {e}")
                    return True, 0, len(restaurant_data)  # All were duplicates
                else:
                    self.logger.error(f"Database insertion error: {e}")
                    return False, 0, skipped_count
                
        except Exception as e:
            self.logger.error(f"Error inserting restaurants: {e}")
            return False, 0, skipped_count
    
    def get_restaurants(self, limit: int = 100, offset: int = 0) -> List[dict]:
        """Get restaurants from database"""
        if not self.supabase:
            self.logger.error("No Supabase connection available")
            return []
        
        try:
            result = self.supabase.table('restaurants').select('*').range(offset, offset + limit - 1).execute()
            return result.data if result.data else []
        except Exception as e:
            self.logger.error(f"Error getting restaurants: {e}")
            return []
    
    def search_restaurants(self, query: str, limit: int = 100) -> List[dict]:
        """Search restaurants by name or description"""
        if not self.supabase:
            self.logger.error("No Supabase connection available")
            return []
        
        try:
            result = self.supabase.table('restaurants').select('*').ilike('name', f'%{query}%').limit(limit).execute()
            return result.data if result.data else []
        except Exception as e:
            self.logger.error(f"Error searching restaurants: {e}")
            return []
    
    def get_vegan_restaurants(self, limit: int = 100) -> List[dict]:
        """Get vegan restaurants"""
        if not self.supabase:
            self.logger.error("No Supabase connection available")
            return []
        
        try:
            result = self.supabase.table('restaurants').select('*').eq('is_vegan', True).limit(limit).execute()
            return result.data if result.data else []
        except Exception as e:
            self.logger.error(f"Error getting vegan restaurants: {e}")
            return []
    
    def get_restaurants_by_location(self, lat: float, lng: float, radius_km: float = 5.0) -> List[dict]:
        """Get restaurants within a radius of given coordinates"""
        if not self.supabase:
            self.logger.error("No Supabase connection available")
            return []
        
        try:
            # Use PostGIS function for distance calculation
            # This requires the PostGIS extension to be enabled in Supabase
            sql = f"""
            SELECT *, 
                   ST_Distance(
                       ST_Point(longitude, latitude)::geography,
                       ST_Point({lng}, {lat})::geography
                   ) / 1000 as distance_km
            FROM restaurants 
            WHERE ST_DWithin(
                ST_Point(longitude, latitude)::geography,
                ST_Point({lng}, {lat})::geography,
                {radius_km * 1000}
            )
            ORDER BY distance_km
            """
            
            result = self.supabase.rpc('exec_sql', {'sql': sql})
            return result.data if result.data else []
        except Exception as e:
            self.logger.error(f"Error getting restaurants by location: {e}")
            return []
