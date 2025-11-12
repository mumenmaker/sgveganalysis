#!/usr/bin/env python3
"""
Export restaurants table from Supabase to CSV file.
"""
import os
import csv
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def export_restaurants_to_csv():
    """Export all restaurants from Supabase to a CSV file."""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    
    # Create Supabase client
    supabase: Client = create_client(supabase_url, supabase_key)
    
    print("Fetching restaurants from Supabase...")
    
    # Fetch all restaurants (handle pagination if needed)
    response = supabase.table("restaurants").select("*").execute()
    restaurants = response.data
    
    if not restaurants:
        print("No restaurants found in the database.")
        return
    
    print(f"Found {len(restaurants)} restaurants. Exporting to CSV...")
    
    # Get all column names from the first restaurant
    if restaurants:
        fieldnames = list(restaurants[0].keys())
        
        # Write to CSV file
        output_file = "restaurants_export.csv"
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(restaurants)
        
        print(f"✅ Successfully exported {len(restaurants)} restaurants to '{output_file}'")
        print(f"📁 File location: {os.path.abspath(output_file)}")
    else:
        print("No data to export.")

if __name__ == "__main__":
    try:
        export_restaurants_to_csv()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

