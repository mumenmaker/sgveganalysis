import { useState, useEffect } from 'react';
import RestaurantMap from './components/RestaurantMap';
import RestaurantFilters from './components/RestaurantFilters';
import DraggableLegend from './components/DraggableLegend';
import type { RestaurantFilters as FilterType } from './types/restaurant';
import { Badge } from './components/ui/badge';
import { Utensils, Star, Sun, Moon } from 'lucide-react';

function App() {
  const [filters, setFilters] = useState<FilterType>({});
  const [showFilters, setShowFilters] = useState(true);
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Handle dark mode toggle
  useEffect(() => {
    const html = document.documentElement;
    if (isDarkMode) {
      html.classList.add('dark');
    } else {
      html.classList.remove('dark');
    }
  }, [isDarkMode]);

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
  };

  return (
    <div className="h-screen w-full flex flex-col bg-gradient-to-br from-green-50 to-emerald-50">
      {/* Header */}
      <header className="bg-white/90 backdrop-blur-sm shadow-sm border-b border-green-200">
        <div className="px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <Utensils className="h-8 w-8 text-green-600" />
                <h1 className="text-xl sm:text-2xl font-bold text-gray-900">
                  Singapore Vegan Map
                </h1>
              </div>
              <Badge variant="outline" className="text-green-600 border-green-600 bg-green-50">
                HappyCow Data
              </Badge>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={toggleDarkMode}
                className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
                title={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {isDarkMode ? <Sun className="h-5 w-5 text-yellow-600" /> : <Moon className="h-5 w-5 text-gray-600" />}
              </button>
              
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors shadow-sm"
              >
                {showFilters ? 'Hide Filters' : 'Show Filters'}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex w-full overflow-hidden">
        {/* Filters Sidebar */}
        {showFilters && (
          <div className="w-full sm:w-80 bg-white/95 backdrop-blur-sm border-r border-green-200 overflow-y-auto">
            <div className="p-4">
              <RestaurantFilters
                filters={filters}
                onFiltersChange={setFilters}
              />
            </div>
          </div>
        )}

        {/* Map Container */}
        <div className="flex-1 relative">
          <RestaurantMap filters={filters} />
          
          {/* Draggable Legend */}
          <DraggableLegend />
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white/90 backdrop-blur-sm border-t border-green-200 px-4 sm:px-6 py-3">
        <div className="flex flex-col sm:flex-row items-center justify-between text-sm text-gray-600 space-y-2 sm:space-y-0">
          <div className="flex items-center space-x-4">
            <span>Data from HappyCow Singapore</span>
            <span className="hidden sm:inline">•</span>
            <span>Powered by Supabase</span>
          </div>
          <div className="flex items-center space-x-2">
            <Star className="h-4 w-4 text-green-500" />
            <span>Singapore Vegan & Vegetarian Restaurants</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;