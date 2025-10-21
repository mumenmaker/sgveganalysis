import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import type { Restaurant } from '../types/restaurant';
import { fetchRestaurants, fetchRestaurantsWithFilters } from '../lib/supabase';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { ExternalLink, Phone, MapPin, Star, Clock } from 'lucide-react';

// Component for individual image with loading state
const RestaurantImage: React.FC<{ 
  imageUrl: string; 
  restaurantName: string; 
  index: number; 
}> = ({ imageUrl, restaurantName, index }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  return (
    <div className="relative group">
      {isLoading && !hasError && (
        <div className="w-20 h-20 bg-gray-100 rounded-lg border border-gray-200 flex items-center justify-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-green-500"></div>
        </div>
      )}
      
      {hasError ? (
        <div 
          className="w-20 h-20 bg-gradient-to-br from-green-100 to-green-200 rounded-lg border border-green-300 flex items-center justify-center cursor-pointer hover:bg-gradient-to-br hover:from-green-200 hover:to-green-300 transition-all duration-200"
          onClick={() => window.open(imageUrl, '_blank')}
          title="Click to view image"
        >
          <div className="text-center">
            <div className="text-lg">📷</div>
            <div className="text-xs text-green-700 font-medium">View Image</div>
          </div>
        </div>
      ) : (
        <img
          src={imageUrl}
          alt={`${restaurantName} photo ${index + 1}`}
          className={`w-20 h-20 object-cover rounded-lg border border-gray-200 hover:border-green-300 transition-colors cursor-pointer ${isLoading ? 'hidden' : 'block'}`}
          loading="lazy"
          onLoad={() => {
            setIsLoading(false);
            setHasError(false);
          }}
          onError={() => {
            setIsLoading(false);
            setHasError(true);
          }}
          onClick={() => window.open(imageUrl, '_blank')}
          crossOrigin="anonymous"
          referrerPolicy="no-referrer"
        />
      )}
      
      {!isLoading && !hasError && (
        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 rounded-lg transition-all duration-200 flex items-center justify-center">
          <div className="opacity-0 group-hover:opacity-100 transition-opacity">
            <div className="bg-white bg-opacity-90 rounded-full p-1">
              <svg className="w-4 h-4 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
              </svg>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

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
            eventHandlers={{
              mouseover: (e) => {
                e.target.openPopup();
              },
              mouseout: (e) => {
                e.target.closePopup();
              }
            }}
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
                    
                    {restaurant.features && restaurant.features.length > 0 && (
                      <div className="mt-3">
                        <div className="text-sm font-medium text-gray-700 mb-2">Features:</div>
                        <div className="flex flex-wrap gap-1">
                          {restaurant.features.slice(0, 8).map((feature, index) => (
                            <Badge 
                              key={index} 
                              variant="outline" 
                              className="text-xs bg-green-50 border-green-200 text-green-700 hover:bg-green-100"
                            >
                              {feature}
                            </Badge>
                          ))}
                          {restaurant.features.length > 8 && (
                            <Badge 
                              variant="outline" 
                              className="text-xs bg-gray-50 border-gray-200 text-gray-600"
                            >
                              +{restaurant.features.length - 8} more
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}
                    
                    {restaurant.images_links && restaurant.images_links.length > 0 && (
                      <div className="mt-3">
                        <div className="text-sm font-medium text-gray-700 mb-2">Photos:</div>
                        <div className="flex gap-2">
                          {restaurant.images_links.slice(0, 2).map((imageUrl, index) => (
                            <RestaurantImage
                              key={index}
                              imageUrl={imageUrl}
                              restaurantName={restaurant.name}
                              index={index}
                            />
                          ))}
                          {restaurant.images_links.length > 2 && (
                            <div className="w-20 h-20 bg-gray-100 rounded-lg border border-gray-200 flex items-center justify-center cursor-pointer hover:bg-gray-200 transition-colors">
                              <div className="text-center">
                                <div className="text-xs font-medium text-gray-600">+{restaurant.images_links.length - 2}</div>
                                <div className="text-xs text-gray-500">more</div>
                              </div>
                            </div>
                          )}
                        </div>
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
