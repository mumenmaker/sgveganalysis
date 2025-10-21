# Singapore Vegan Map

A React-based interactive map showing vegan and vegetarian restaurants in Singapore, powered by data from HappyCow.

## Features

- 🗺️ **Interactive Map**: Leaflet-based map with custom markers
- 🍃 **Restaurant Types**: Color-coded markers for vegan, vegetarian, and veg-option restaurants
- 🔍 **Advanced Filtering**: Filter by restaurant type, category, price range, and rating
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 🎨 **Modern UI**: Built with Tailwind CSS and shadcn/ui components

## Setup

### 1. Install Dependencies
```bash
pnpm install
```

### 2. Environment Variables
Create a `.env` file in the map directory:
```env
VITE_SUPABASE_URL=your_supabase_url_here
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

### 3. Run Development Server
```bash
pnpm dev
```

## Data Source

This app connects to the Supabase database populated by the `scraper/` module, which collects restaurant data from HappyCow's Singapore search map.

## Map Features

### Restaurant Markers
- 🟢 **Green**: Vegan restaurants
- 🟠 **Orange**: Vegetarian restaurants  
- 🟣 **Purple**: Restaurants with vegetarian options
- 🔵 **Blue**: Other restaurants

### Filtering Options
- **Restaurant Type**: Vegan only, vegetarian, has veg options
- **Category**: Asian, Western, Indian, Chinese, Japanese, etc.
- **Price Range**: Inexpensive, Moderate, Expensive
- **Rating**: Minimum rating filter with slider

### Popup Information
Each marker shows:
- Restaurant name and type badges
- Address and phone number
- Rating and review count
- Category and price range
- Opening hours
- Description
- Links to website and HappyCow reviews

## Technology Stack

- **React 18** with TypeScript
- **Vite** for build tooling
- **Leaflet** for map functionality
- **React-Leaflet** for React integration
- **Tailwind CSS** for styling
- **shadcn/ui** for UI components
- **Supabase** for data management
- **Lucide React** for icons

## Development

### Project Structure
```
src/
├── components/
│   ├── RestaurantMap.tsx      # Main map component
│   ├── RestaurantFilters.tsx  # Filter sidebar
│   └── ui/                    # shadcn/ui components
├── lib/
│   └── supabase.ts           # Supabase client and queries
├── types/
│   └── restaurant.ts         # TypeScript interfaces
└── App.tsx                   # Main application
```

### Available Scripts
- `pnpm dev` - Start development server
- `pnpm build` - Build for production
- `pnpm preview` - Preview production build
- `pnpm lint` - Run ESLint

## Deployment

The app can be deployed to any static hosting service:
- Vercel
- Netlify
- GitHub Pages
- AWS S3 + CloudFront

Make sure to set the environment variables in your deployment platform.