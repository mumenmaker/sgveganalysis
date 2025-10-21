# Map Setup Guide

## Quick Setup

1. **Copy environment variables:**
   ```bash
   cp env.example .env
   ```

2. **Edit `.env` file with your Supabase credentials:**
   ```env
   VITE_SUPABASE_URL=your_supabase_url_here
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
   ```

3. **Start development server:**
   ```bash
   pnpm dev
   ```

## Getting Supabase Credentials

1. Go to your Supabase project dashboard
2. Navigate to Settings > API
3. Copy the "Project URL" and "anon public" key
4. Paste them into your `.env` file

## Troubleshooting

- **Map not loading**: Check that your Supabase credentials are correct
- **No restaurants showing**: Ensure the scraper has populated the database
- **Build errors**: Run `pnpm install` to ensure all dependencies are installed
