import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import type { Restaurant } from '../types/restaurant';
import { fetchRestaurants, fetchRestaurantsWithFilters } from '../lib/supabase';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { ExternalLink, Phone, MapPin, Star, Clock } from 'lucide-react';

// Fix for default markers in react-leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom icons for different restaurant types
const createCustomIcon = (restaurant: Restaurant) => {
  let color = '#3b82f6'; // Default blue
  
  if (restaurant.is_vegan) {
    color = '#10b981'; // Green for vegan
  } else if (restaurant.is_vegetarian) {
    color = '#f59e0b'; // Orange for vegetarian
  } else if (restaurant.has_veg_options) {
    color = '#8b5cf6'; // Purple for veg options
  }

  return L.divIcon({
    className: 'custom-div-icon',
    html: `<div style="
      background-color: ${color};
      width: 20px;
      height: 20px;
      border-radius: 50%;
      border: 2px solid white;
      box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    "></div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });
};

interface RestaurantMapProps {
  filters?: {
    is_vegan?: boolean;
    is_vegetarian?: boolean;
    has_veg_options?: boolean;
    category?: string;
    price_range?: string;
    min_rating?: number;
  };
}

const RestaurantMap: React.FC<RestaurantMapProps> = ({ filters }) => {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadRestaurants = async () => {
      try {
        setLoading(true);
        setError(null);
        
        
        const data = filters 
          ? await fetchRestaurantsWithFilters(filters)
          : await fetchRestaurants();
        
        setRestaurants(data);
      } catch (err) {
        setError('Failed to load restaurants');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadRestaurants();
  }, [filters]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading restaurants...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={() => window.location.reload()}>
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full w-full">
      <MapContainer
        center={[1.3521, 103.8198]} // Singapore center
        zoom={11}
        className="h-full w-full"
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {restaurants.map((restaurant) => (
          <Marker
            key={restaurant.id}
            position={[restaurant.latitude!, restaurant.longitude!]}
            icon={createCustomIcon(restaurant)}
          >
            <Popup>
              <div className="w-80 p-2">
                <Card className="bg-white/95 backdrop-blur-sm border-green-200 shadow-lg">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg text-green-800">{restaurant.name}</CardTitle>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {restaurant.is_vegan && (
                        <Badge variant="default" className="bg-green-500 text-white border-green-600">🌱 Vegan</Badge>
                      )}
                      {restaurant.is_vegetarian && (
                        <Badge variant="default" className="bg-orange-500 text-white border-orange-600">🥗 Vegetarian</Badge>
                      )}
                      {restaurant.has_veg_options && (
                        <Badge variant="outline" className="border-green-300 text-green-700">🍃 Veg Options</Badge>
                      )}
                    </div>
                  </CardHeader>
                  
                  <CardContent className="space-y-2">
                    {restaurant.address && (
                      <div className="flex items-start gap-2 text-sm text-gray-600">
                        <MapPin className="h-4 w-4 mt-0.5 flex-shrink-0" />
                        <span>{restaurant.address}</span>
                      </div>
                    )}
                    
                    {restaurant.phone && (
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Phone className="h-4 w-4" />
                        <span>{restaurant.phone}</span>
                      </div>
                    )}
                    
                    {restaurant.rating && (
                      <div className="flex items-center gap-2 text-sm">
                        <Star className="h-4 w-4 text-yellow-500 fill-current" />
                        <span>{restaurant.rating.toFixed(1)}</span>
                        {restaurant.review_count && (
                          <span className="text-gray-500">({restaurant.review_count} reviews)</span>
                        )}
                      </div>
                    )}
                    
                    {restaurant.category && (
                      <div className="text-sm text-gray-600">
                        <strong>Category:</strong> {restaurant.category}
                      </div>
                    )}
                    
                    {restaurant.price_range && (
                      <div className="text-sm text-gray-600">
                        <strong>Price:</strong> {restaurant.price_range}
                      </div>
                    )}
                    
                    {restaurant.hours && (
                      <div className="flex items-start gap-2 text-sm text-gray-600">
                        <Clock className="h-4 w-4 mt-0.5 flex-shrink-0" />
                        <span>{restaurant.hours}</span>
                      </div>
                    )}
                    
                    {restaurant.description && (
                      <p className="text-sm text-gray-700 mt-2 line-clamp-3">
                        {restaurant.description}
                      </p>
                    )}
                    
                    <div className="flex gap-2 mt-4">
                      {restaurant.website && (
                        <Button size="sm" variant="outline" asChild className="border-green-300 text-green-700 hover:bg-green-50 hover:border-green-400">
                          <a href={restaurant.website} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="h-4 w-4 mr-1" />
                            Website
                          </a>
                        </Button>
                      )}
                      
                      {restaurant.cow_reviews && (
                        <Button size="sm" variant="outline" asChild className="border-green-300 text-green-700 hover:bg-green-50 hover:border-green-400">
                          <a href={restaurant.cow_reviews} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="h-4 w-4 mr-1" />
                            Reviews
                          </a>
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};

export default RestaurantMap;
