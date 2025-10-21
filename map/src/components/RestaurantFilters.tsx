import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Checkbox } from './ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Slider } from './ui/slider';
import ReactSelect from 'react-select';
import type { RestaurantFilters as FilterType } from '../types/restaurant';

interface RestaurantFiltersProps {
  filters: FilterType;
  onFiltersChange: (filters: FilterType) => void;
}

const RestaurantFilters: React.FC<RestaurantFiltersProps> = ({ filters, onFiltersChange }) => {
  const handleBooleanChange = (key: keyof FilterType, value: boolean) => {
    onFiltersChange({
      ...filters,
      [key]: value,
    });
  };

  const handleStringChange = (key: keyof FilterType, value: string) => {
    onFiltersChange({
      ...filters,
      [key]: value === 'all' ? undefined : value,
    });
  };

  const handleRatingChange = (value: number[]) => {
    onFiltersChange({
      ...filters,
      min_rating: value[0] > 0 ? value[0] : undefined,
    });
  };

  return (
    <Card className="w-full bg-white/95 backdrop-blur-sm border-green-200 shadow-sm dark:bg-slate-800/95 dark:border-slate-700 transition-colors duration-300">
      <CardHeader className="pb-4">
        <CardTitle className="text-lg font-semibold text-green-800 dark:text-green-400 flex items-center space-x-2 transition-colors duration-300">
          <div className="w-2 h-2 bg-green-500 dark:bg-green-400 rounded-full transition-colors duration-300"></div>
          <span>Filter Restaurants</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Restaurant Type Filters */}
        <div className="space-y-4">
          <h4 className="font-semibold text-green-700 dark:text-green-400 text-sm uppercase tracking-wide transition-colors duration-300">Restaurant Type</h4>
          <div className="space-y-3">
            <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-green-50 dark:hover:bg-slate-700 transition-colors duration-300">
              <Checkbox
                id="vegan"
                checked={filters.is_vegan || false}
                onCheckedChange={(checked) => handleBooleanChange('is_vegan', !!checked)}
                className="border-green-300 data-[state=checked]:bg-green-500 data-[state=checked]:border-green-500"
              />
                      <label htmlFor="vegan" className="text-sm font-medium text-gray-700 dark:text-white cursor-pointer transition-colors duration-300">
                        🌱 Vegan Only
                      </label>
            </div>
            <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-orange-50 dark:hover:bg-slate-700 transition-colors duration-300">
              <Checkbox
                id="vegetarian"
                checked={filters.is_vegetarian || false}
                onCheckedChange={(checked) => handleBooleanChange('is_vegetarian', !!checked)}
                className="border-orange-300 data-[state=checked]:bg-orange-500 data-[state=checked]:border-orange-500"
              />
                      <label htmlFor="vegetarian" className="text-sm font-medium text-gray-700 dark:text-white cursor-pointer transition-colors duration-300">
                        🥗 Vegetarian
                      </label>
            </div>
            <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-purple-50 dark:hover:bg-slate-700 transition-colors duration-300">
              <Checkbox
                id="veg-options"
                checked={filters.has_veg_options || false}
                onCheckedChange={(checked) => handleBooleanChange('has_veg_options', !!checked)}
                className="border-purple-300 data-[state=checked]:bg-purple-500 data-[state=checked]:border-purple-500"
              />
                      <label htmlFor="veg-options" className="text-sm font-medium text-gray-700 dark:text-white cursor-pointer transition-colors duration-300">
                        🍃 Has Veg Options
                      </label>
            </div>
            <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-blue-50 dark:hover:bg-slate-700 transition-colors duration-300">
              <Checkbox
                id="other"
                checked={filters.is_other || false}
                onCheckedChange={(checked) => handleBooleanChange('is_other', !!checked)}
                className="border-blue-300 data-[state=checked]:bg-blue-500 data-[state=checked]:border-blue-500"
              />
                      <label htmlFor="other" className="text-sm font-medium text-gray-700 dark:text-white cursor-pointer transition-colors duration-300">
                        🔵 Other Restaurants
                      </label>
            </div>
          </div>
        </div>

        {/* Category Filter */}
        <div className="space-y-3">
                  <label className="text-sm font-semibold text-green-700 dark:text-green-400 uppercase tracking-wide transition-colors duration-300">Category</label>
          <Select
            value={filters.category || 'all'}
            onValueChange={(value) => handleStringChange('category', value)}
          >
            <SelectTrigger className="border-green-300 focus:border-green-500 focus:ring-green-500 bg-white">
              <SelectValue placeholder="All Categories" />
            </SelectTrigger>
            <SelectContent className="bg-white border-green-200">
              <SelectItem value="all">All Categories</SelectItem>
              <SelectItem value="vegetarian">🥗 Vegetarian</SelectItem>
              <SelectItem value="vegan">🌱 Vegan</SelectItem>
              <SelectItem value="veg-options">🍃 Veg Options</SelectItem>
              <SelectItem value="other">🍴 Other</SelectItem>
              <SelectItem value="ice-cream">🍦 Ice Cream</SelectItem>
              <SelectItem value="health-food-store">🏪 Health Food Store</SelectItem>
              <SelectItem value="vegan-store">🛒 Vegan Store</SelectItem>
              <SelectItem value="juice-bar">🥤 Juice Bar</SelectItem>
              <SelectItem value="market-vendor">🏪 Market Vendor</SelectItem>
              <SelectItem value="delivery">🚚 Delivery</SelectItem>
              <SelectItem value="bakery">🥖 Bakery</SelectItem>
              <SelectItem value="coffee-tea">☕ Coffee & Tea</SelectItem>
              <SelectItem value="food-truck">🚚 Food Truck</SelectItem>
              <SelectItem value="farmers-market">🌾 Farmers Market</SelectItem>
              <SelectItem value="catering">🍽️ Catering</SelectItem>
              <SelectItem value="spa">🧘 Spa</SelectItem>
              <SelectItem value="hotel">🏨 Hotel</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Price Range Filter */}
        <div className="space-y-3">
                  <label className="text-sm font-semibold text-green-700 dark:text-green-400 uppercase tracking-wide transition-colors duration-300">Price Range</label>
          <Select
            value={filters.price_range || 'all'}
            onValueChange={(value) => handleStringChange('price_range', value)}
          >
            <SelectTrigger className="border-green-300 focus:border-green-500 focus:ring-green-500 bg-white">
              <SelectValue placeholder="All Price Ranges" />
            </SelectTrigger>
            <SelectContent className="bg-white border-green-200">
              <SelectItem value="all">All Price Ranges</SelectItem>
              <SelectItem value="Inexpensive">💰 Inexpensive</SelectItem>
              <SelectItem value="Moderate">💵 Moderate</SelectItem>
              <SelectItem value="Expensive">💎 Expensive</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Rating Filter */}
        <div className="space-y-3">
          <label className="text-sm font-semibold text-green-700 dark:text-green-400 uppercase tracking-wide transition-colors duration-300">
            ⭐ Minimum Rating
          </label>
          <div className="flex items-center space-x-2">
            {[0, 1, 2, 3, 4, 5].map((rating) => (
              <button
                key={rating}
                onClick={() => handleRatingChange([rating])}
                className={`flex items-center justify-center w-8 h-8 rounded border-2 transition-colors ${
                  (filters.min_rating || 0) >= rating
                    ? 'bg-yellow-100 border-yellow-400 text-yellow-600'
                    : 'bg-gray-100 border-gray-300 text-gray-400 hover:bg-gray-200'
                }`}
                title={`${rating} star${rating !== 1 ? 's' : ''} and above`}
              >
                <span className="text-sm font-medium">
                  {rating}
                </span>
              </button>
            ))}
          </div>
          <div className="text-xs text-gray-500">
            {filters.min_rating === 0 
              ? 'Show all restaurants' 
              : `Show ${filters.min_rating}+ star restaurants`
            }
          </div>
        </div>

        {/* Features Filter */}
        <div className="space-y-3">
          <label className="text-sm font-semibold text-green-700 dark:text-green-400 uppercase tracking-wide transition-colors duration-300">
            🏷️ Features
          </label>
          <ReactSelect
            isMulti
            options={[
              // Dietary preferences
              { value: 'Vegan-friendly', label: '🌱 Vegan-friendly' },
              { value: 'Vegan', label: '🌱 Vegan' },
              { value: 'Lacto', label: '🥛 Lacto' },
              { value: 'Ovo', label: '🥚 Ovo' },
              { value: 'Gluten-free', label: '🌾 Gluten-free' },
              { value: 'Organic', label: '🌿 Organic' },
              { value: 'Raw', label: '🥗 Raw' },
              { value: 'Macrobiotic', label: '🍚 Macrobiotic' },
              // Cuisine types
              { value: 'Chinese', label: '🥢 Chinese' },
              { value: 'Japanese', label: '🍣 Japanese' },
              { value: 'Korean', label: '🍲 Korean' },
              { value: 'Thai', label: '🌶️ Thai' },
              { value: 'Indian', label: '🍛 Indian' },
              { value: 'Vietnamese', label: '🍜 Vietnamese' },
              { value: 'Indonesian', label: '🍛 Indonesian' },
              { value: 'Malaysian', label: '🍜 Malaysian' },
              { value: 'Singaporean', label: '🇸🇬 Singaporean' },
              // Service types
              { value: 'Fast food', label: '⚡ Fast food' },
              { value: 'Take-out', label: '📦 Take-out' },
              { value: 'Delivery', label: '🚚 Delivery' },
              { value: 'Buffet', label: '🍽️ Buffet' },
              { value: 'Breakfast', label: '🌅 Breakfast' },
              { value: 'Catering', label: '🎉 Catering' },
              // Other features
              { value: 'Salad bar', label: '🥗 Salad bar' },
              { value: 'Juice bar', label: '🥤 Juice bar' },
              { value: 'Bakery', label: '🥖 Bakery' },
              { value: 'Pizza', label: '🍕 Pizza' },
              { value: 'Beer/Wine', label: '🍺 Beer/Wine' },
              { value: 'Fusion', label: '🌍 Fusion' },
              { value: 'International', label: '🌐 International' }
            ]}
            value={filters.features?.map(feature => ({ value: feature, label: feature })) || []}
            onChange={(selectedOptions) => {
              const selectedFeatures = selectedOptions?.map(option => option.value) || [];
              onFiltersChange({ ...filters, features: selectedFeatures });
            }}
            placeholder="Select features..."
            className="text-sm"
            styles={{
              control: (base) => ({
                ...base,
                borderColor: '#86efac',
                '&:hover': {
                  borderColor: '#22c55e'
                },
                '&:focus': {
                  borderColor: '#22c55e',
                  boxShadow: '0 0 0 2px rgba(34, 197, 94, 0.2)'
                }
              }),
              multiValue: (base) => ({
                ...base,
                backgroundColor: '#dcfce7',
                borderRadius: '6px'
              }),
              multiValueLabel: (base) => ({
                ...base,
                color: '#166534',
                fontSize: '12px'
              }),
              multiValueRemove: (base) => ({
                ...base,
                color: '#166534',
                '&:hover': {
                  backgroundColor: '#22c55e',
                  color: 'white'
                }
              })
            }}
          />
        </div>

        {/* Clear Filters */}
        <div className="pt-4 border-t border-green-200">
          <button
            onClick={() => onFiltersChange({})}
            className="w-full px-4 py-2 text-sm font-medium text-green-600 hover:text-green-700 hover:bg-green-50 rounded-lg transition-colors border border-green-300 hover:border-green-400"
          >
            🗑️ Clear All Filters
          </button>
        </div>
      </CardContent>
    </Card>
  );
};

export default RestaurantFilters;
