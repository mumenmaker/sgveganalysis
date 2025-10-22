import { useState, useEffect } from 'react';
import RestaurantMap from './components/RestaurantMap';
import RestaurantFilters from './components/RestaurantFilters';
import DraggableLegend from './components/DraggableLegend';
import type { RestaurantFilters as FilterType } from './types/restaurant';
import { Badge } from './components/ui/badge';
import { Utensils, Star, Sun, Moon, Menu, X } from 'lucide-react';

function App() {
  const [filters, setFilters] = useState<FilterType>({});
  const [showFilters, setShowFilters] = useState(true);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

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
    <div className={`h-screen w-full flex flex-col transition-colors duration-300 ${
      isDarkMode 
        ? 'bg-gradient-to-br from-slate-900 to-slate-800' 
        : 'bg-gradient-to-br from-green-50 to-emerald-50'
    }`}>
      {/* Header */}
      <header className={`backdrop-blur-sm shadow-sm border-b transition-colors duration-300 ${
        isDarkMode 
          ? 'bg-slate-800/90 border-slate-700' 
          : 'bg-white/90 border-green-200'
      }`}>
        <div className="px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <Utensils className={`h-4 w-4 sm:h-6 sm:w-6 md:h-8 md:w-8 transition-colors duration-300 ${
                  isDarkMode ? 'text-green-400' : 'text-green-600'
                }`} />
                <h1 className={`!text-xl sm:!text-xl md:!text-2xl lg:!text-3xl font-bold transition-colors duration-300 ${
                  isDarkMode ? 'text-white' : 'text-gray-900'
                }`}>
                  Singapore Vegan Map
                </h1>
              </div>
              <Badge variant="outline" className={`hidden sm:flex transition-colors duration-300 ${
                isDarkMode 
                  ? 'text-green-400 border-green-400 bg-slate-700' 
                  : 'text-green-600 border-green-600 bg-green-50'
              }`}>
                HappyCow Data
              </Badge>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Mobile menu button */}
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className={`p-2 rounded-lg transition-colors duration-300 sm:hidden ${
                  isDarkMode 
                    ? 'bg-slate-700 hover:bg-slate-600 text-slate-300' 
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
                }`}
                title="Toggle filters menu"
              >
                {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>
              
              <button
                onClick={toggleDarkMode}
                className={`p-2 rounded-lg transition-colors duration-300 ${
                  isDarkMode 
                    ? 'bg-slate-700 hover:bg-slate-600 text-slate-300' 
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
                }`}
                title={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {isDarkMode ? <Sun className="h-5 w-5 text-yellow-400" /> : <Moon className="h-5 w-5 text-gray-600" />}
              </button>
              
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`px-4 py-2 rounded-lg transition-colors duration-300 shadow-sm hidden sm:block ${
                  isDarkMode 
                    ? 'bg-green-600 hover:bg-green-700 text-white' 
                    : 'bg-green-600 hover:bg-green-700 text-white'
                }`}
              >
                {showFilters ? 'Hide Filters' : 'Show Filters'}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex w-full overflow-hidden">
        {/* Mobile Filters Overlay */}
        {isMobileMenuOpen && (
          <div className="fixed inset-0 z-[9999] sm:hidden">
            <div className="absolute inset-0 bg-black/50" onClick={() => setIsMobileMenuOpen(false)} />
            <div className={`absolute left-0 top-0 h-full w-80 max-w-[85vw] backdrop-blur-sm border-r overflow-y-auto transition-colors duration-300 z-[10000] ${
              isDarkMode 
                ? 'bg-slate-800/95 border-slate-700' 
                : 'bg-white/95 border-green-200'
            }`}>
              <div className="p-4">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold">Filters</h2>
                  <button
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
                <RestaurantFilters
                  filters={filters}
                  onFiltersChange={setFilters}
                />
              </div>
            </div>
          </div>
        )}

        {/* Desktop Filters Sidebar */}
        {showFilters && (
          <div className={`hidden sm:block w-80 backdrop-blur-sm border-r overflow-y-auto transition-colors duration-300 ${
            isDarkMode 
              ? 'bg-slate-800/95 border-slate-700' 
              : 'bg-white/95 border-green-200'
          }`}>
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
      <footer className={`backdrop-blur-sm border-t px-4 sm:px-6 py-3 transition-colors duration-300 ${
        isDarkMode 
          ? 'bg-slate-800/90 border-slate-700' 
          : 'bg-white/90 border-green-200'
      }`}>
        <div className={`flex flex-col sm:flex-row items-center justify-between text-sm space-y-2 sm:space-y-0 transition-colors duration-300 ${
          isDarkMode ? 'text-slate-300' : 'text-gray-600'
        }`}>
          <div className="flex items-center space-x-4">
            <span>Data from HappyCow Singapore</span>
            <span className="hidden sm:inline">•</span>
            <span>Powered by Supabase</span>
          </div>
          <div className="flex items-center space-x-2">
            <Star className={`h-4 w-4 transition-colors duration-300 ${
              isDarkMode ? 'text-green-400' : 'text-green-500'
            }`} />
            <span>Singapore Vegan & Vegetarian Restaurants</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;