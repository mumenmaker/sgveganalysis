import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Checkbox } from './ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Slider } from './ui/slider';
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
    <Card className="w-full bg-white/95 backdrop-blur-sm border-green-200 shadow-sm">
      <CardHeader className="pb-4">
        <CardTitle className="text-lg font-semibold text-green-800 flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
          <span>Filter Restaurants</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Restaurant Type Filters */}
        <div className="space-y-4">
          <h4 className="font-semibold text-green-700 text-sm uppercase tracking-wide">Restaurant Type</h4>
          <div className="space-y-3">
            <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-green-50 transition-colors">
              <Checkbox
                id="vegan"
                checked={filters.is_vegan || false}
                onCheckedChange={(checked) => handleBooleanChange('is_vegan', !!checked)}
                className="border-green-300 data-[state=checked]:bg-green-500 data-[state=checked]:border-green-500"
              />
              <label htmlFor="vegan" className="text-sm font-medium text-gray-700 cursor-pointer">
                🌱 Vegan Only
              </label>
            </div>
            <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-orange-50 transition-colors">
              <Checkbox
                id="vegetarian"
                checked={filters.is_vegetarian || false}
                onCheckedChange={(checked) => handleBooleanChange('is_vegetarian', !!checked)}
                className="border-orange-300 data-[state=checked]:bg-orange-500 data-[state=checked]:border-orange-500"
              />
              <label htmlFor="vegetarian" className="text-sm font-medium text-gray-700 cursor-pointer">
                🥗 Vegetarian
              </label>
            </div>
            <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-purple-50 transition-colors">
              <Checkbox
                id="veg-options"
                checked={filters.has_veg_options || false}
                onCheckedChange={(checked) => handleBooleanChange('has_veg_options', !!checked)}
                className="border-purple-300 data-[state=checked]:bg-purple-500 data-[state=checked]:border-purple-500"
              />
              <label htmlFor="veg-options" className="text-sm font-medium text-gray-700 cursor-pointer">
                🍃 Has Veg Options
              </label>
            </div>
            <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-blue-50 transition-colors">
              <Checkbox
                id="other"
                checked={filters.is_other || false}
                onCheckedChange={(checked) => handleBooleanChange('is_other', !!checked)}
                className="border-blue-300 data-[state=checked]:bg-blue-500 data-[state=checked]:border-blue-500"
              />
              <label htmlFor="other" className="text-sm font-medium text-gray-700 cursor-pointer">
                🔵 Other Restaurants
              </label>
            </div>
          </div>
        </div>

        {/* Category Filter */}
        <div className="space-y-3">
          <label className="text-sm font-semibold text-green-700 uppercase tracking-wide">Category</label>
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
          <label className="text-sm font-semibold text-green-700 uppercase tracking-wide">Price Range</label>
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
          <label className="text-sm font-semibold text-green-700 uppercase tracking-wide">
            ⭐ Minimum Rating: {filters.min_rating || 0}
          </label>
          <Slider
            value={[filters.min_rating || 0]}
            onValueChange={handleRatingChange}
            max={5}
            min={0}
            step={0.1}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-gray-500">
            <span>0</span>
            <span>5</span>
          </div>
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
