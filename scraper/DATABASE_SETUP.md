# Database Setup Guide

## The Issue
The scraper is working perfectly and extracting restaurant data, but the database tables don't exist in your Supabase project. This is why you're not seeing any tables in the Supabase dashboard.

## Solution: Create Tables in Supabase

### Step 1: Go to Supabase Dashboard
1. Open your Supabase project dashboard
2. Go to the **SQL Editor** tab (in the left sidebar)

### Step 2: Run the SQL Script
1. Copy the contents of `create_tables.sql`
2. Paste it into the SQL Editor
3. Click **Run** to execute the script

### Step 3: Verify Tables Created
After running the SQL script, you should see:
- `restaurants` table in the **Table Editor**
- `scraping_progress` table in the **Table Editor**
- Both tables should be visible in your Supabase dashboard

### Step 4: Test Database Connection
Run the test script to verify everything is working:

```bash
cd /Users/zeldon/projects/mmaker/sgveganalysis/scraper
conda activate py3115
python test_database_insert.py
```

### Step 5: Run the Scraper Again
Once the tables are created, run the scraper:

```bash
python main.py
```

## What the SQL Script Creates

### `restaurants` table:
- Stores all restaurant information
- Includes fields for name, address, rating, cuisine type, etc.
- Has indexes for better performance

### `scraping_progress` table:
- Tracks scraping progress
- Stores session information
- Helps with resume functionality

## Troubleshooting

### If you get permission errors:
1. Make sure you're using the correct Supabase project
2. Check that your API key has the right permissions
3. Verify the table names match exactly

### If tables still don't appear:
1. Check the Supabase dashboard for any error messages
2. Try refreshing the page
3. Make sure you're in the correct project

## Next Steps

Once the tables are created:
1. The scraper will be able to save data to the database
2. You'll see the scraped restaurants in the Supabase dashboard
3. The resume functionality will work properly
4. You can query the data using Supabase's built-in tools

The scraper is already working perfectly - it just needs the database tables to exist!
