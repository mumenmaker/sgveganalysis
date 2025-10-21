export interface Restaurant {
  id: number;
  name: string;
  address?: string;
  phone?: string;
  website?: string;
  cow_reviews?: string;
  description?: string;
  category?: string;
  price_range?: string;
  rating?: number;
  review_count?: number;
  latitude?: number;
  longitude?: number;
  is_vegan: boolean;
  is_vegetarian: boolean;
  has_veg_options: boolean;
  features: string[];
  hours?: string;
  images_links: string[];
  happycow_url?: string;
  scraped_at: string;
  created_at: string;
  updated_at: string;
}

export interface RestaurantFilters {
  is_vegan?: boolean;
  is_vegetarian?: boolean;
  has_veg_options?: boolean;
  is_other?: boolean;
  category?: string;
  price_range?: string;
  min_rating?: number;
}
