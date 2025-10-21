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

// Debug function to see what features exist in the database
export const getAvailableFeatures = async (): Promise<string[]> => {
  const { data, error } = await supabase
    .from('restaurants')
    .select('features')
    .not('features', 'is', null);

  if (error) {
    console.error('Error fetching features:', error);
    return [];
  }

  // Flatten all features arrays and get unique values
  const allFeatures = data?.flatMap(r => r.features || []) || [];
  const uniqueFeatures = [...new Set(allFeatures)].filter(Boolean);
  return uniqueFeatures;
};

export const fetchRestaurantsWithFilters = async (filters: {
  is_vegan?: boolean;
  is_vegetarian?: boolean;
  has_veg_options?: boolean;
  is_other?: boolean;
  category?: string;
  price_range?: string;
  min_rating?: number;
  features?: string[];
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

  // Handle features filtering (array contains any of the selected features)
  if (filters.features && filters.features.length > 0) {
    // Use OR logic for features - restaurant must have at least one of the selected features
    const featureConditions = filters.features.map(feature => `features.cs.{${feature}}`);
    query = query.or(featureConditions.join(','));
  }

  const { data, error } = await query.order('name');

  if (error) {
    console.error('Error fetching filtered restaurants:', error);
    throw error;
  }

  return data || [];
};
