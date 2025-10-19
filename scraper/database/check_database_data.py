#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check database data for coordinates and duplicates
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

def check_database_data():
    """Check what data is in the database"""
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ No database credentials found")
        return
    
    supabase = create_client(supabase_url, supabase_key)
    
    print("=== Database Data Check ===")
    
    # Check total count
    result = supabase.table('restaurants').select('id', count='exact').execute()
    print("Total restaurants: {}".format(result.count))
    
    # Check for coordinates
    result = supabase.table('restaurants').select('name, latitude, longitude, address').limit(10).execute()
    print("\nSample data (first 10 restaurants):")
    for i, r in enumerate(result.data):
        print("{}. {}".format(i+1, r.get('name')))
        print("   Address: {}".format(r.get('address')))
        print("   Lat: {}".format(r.get('latitude')))
        print("   Lng: {}".format(r.get('longitude')))
        print()
    
    # Check for duplicates by name
    print("=== Duplicate Check ===")
    result = supabase.table('restaurants').select('name').execute()
    names = [r['name'] for r in result.data]
    unique_names = set(names)
    duplicates = len(names) - len(unique_names)
    print("Total records: {}".format(len(names)))
    print("Unique names: {}".format(len(unique_names)))
    print("Duplicates: {}".format(duplicates))
    
    # Find actual duplicates
    from collections import Counter
    name_counts = Counter(names)
    duplicate_names = {name: count for name, count in name_counts.items() if count > 1}
    if duplicate_names:
        print("\nDuplicate restaurant names:")
        for name, count in duplicate_names.items():
            print("  {}: {} times".format(name, count))

if __name__ == "__main__":
    check_database_data()
