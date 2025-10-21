import { createClient } from '@supabase/supabase-js';
import type { Restaurant } from '../types/restaurant';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseKey) {
  throw new Error('Missing Supabase environment variables');
}

export const supabase = createClient(supabaseUrl, supabaseKey);

export const fetchRestaurants = async (): Promise<Restaurant[]> => {
  const { data, error } = await supabase
    .from('restaurants')
    .select('*')
    .not('latitude', 'is', null)
    .not('longitude', 'is', null)
    .order('name');

  if (error) {
    console.error('Error fetching restaurants:', error);
    throw error;
  }

  return data || [];
};

// Debug function to see what price ranges exist in the database
export const getAvailablePriceRanges = async (): Promise<string[]> => {
  const { data, error } = await supabase
    .from('restaurants')
    .select('price_range')
    .not('price_range', 'is', null)
    .not('price_range', 'eq', '');

  if (error) {
    console.error('Error fetching price ranges:', error);
    return [];
  }

  const priceRanges = [...new Set(data?.map(r => r.price_range) || [])];
  return priceRanges;
};

export const fetchRestaurantsWithFilters = async (filters: {
  is_vegan?: boolean;
  is_vegetarian?: boolean;
  has_veg_options?: boolean;
  is_other?: boolean;
  category?: string;
  price_range?: string;
  min_rating?: number;
}): Promise<Restaurant[]> => {
  let query = supabase
    .from('restaurants')
    .select('*')
    .not('latitude', 'is', null)
    .not('longitude', 'is', null);

  // Handle multiple checkbox filters with OR logic
  const checkboxFilters = [];
  
  if (filters.is_vegan) {
    checkboxFilters.push('is_vegan.eq.true');
  }
  
  if (filters.is_vegetarian) {
    checkboxFilters.push('is_vegetarian.eq.true');
  }
  
  if (filters.has_veg_options) {
    checkboxFilters.push('has_veg_options.eq.true');
  }
  
  if (filters.is_other) {
    // Other restaurants: NOT vegan, NOT vegetarian, and do NOT have veg options
    checkboxFilters.push('and(is_vegan.eq.false,is_vegetarian.eq.false,has_veg_options.eq.false)');
  }

  // Apply OR logic for checkbox filters
  if (checkboxFilters.length > 0) {
    query = query.or(checkboxFilters.join(','));
  }

  // Apply category filter (works with checkbox filters)
  if (filters.category && filters.category !== 'all') {
    query = query.eq('category', filters.category);
  }

  if (filters.price_range) {
    query = query.eq('price_range', filters.price_range);
  }

  if (filters.min_rating) {
    query = query.gte('rating', filters.min_rating);
  }

  const { data, error } = await query.order('name');

  if (error) {
    console.error('Error fetching filtered restaurants:', error);
    throw error;
  }

  return data || [];
};
