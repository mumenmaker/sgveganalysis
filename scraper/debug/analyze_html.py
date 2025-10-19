#!/usr/bin/env python3
"""
Analyze the HTML structure to find restaurant data
"""

import requests
from bs4 import BeautifulSoup
import json
import re

def analyze_html_structure():
    """Analyze the HTML structure to find restaurant data"""
    print("=== Analyzing HTML Structure ===\n")
    
    url = 'https://www.happycow.net/searchmap'
    params = {
        's': '3',
        'location': 'Central Singapore, Singapore',
        'lat': '1.34183',
        'lng': '103.861',
        'page': '1',
        'zoom': '11',
        'metric': 'mi',
        'limit': '81',
        'order': 'default'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Cache-Control': 'max-age=0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.happycow.net/asia/singapore/central_singapore/'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for any elements that might contain restaurant data
            print("=== Looking for restaurant-related elements ===")
            
            # Check for data attributes
            data_elements = soup.find_all(attrs={'data-venue': True})
            print(f"Elements with data-venue: {len(data_elements)}")
            
            # Check for specific classes
            classes_to_check = [
                'restaurant', 'venue', 'listing', 'search-result', 'item',
                'business', 'place', 'location', 'result'
            ]
            
            for class_name in classes_to_check:
                elements = soup.find_all(class_=lambda x: x and class_name in x.lower())
                if elements:
                    print(f"Elements with class containing '{class_name}': {len(elements)}")
                    for i, elem in enumerate(elements[:2]):
                        text = elem.get_text(strip=True)[:100]
                        print(f"  {class_name} {i+1}: {text}...")
            
            # Look for any divs with restaurant-like content
            print("\n=== Looking for divs with restaurant-like content ===")
            all_divs = soup.find_all('div')
            restaurant_like_divs = []
            
            for div in all_divs:
                text = div.get_text(strip=True).lower()
                if any(word in text for word in ['restaurant', 'cafe', 'food', 'dining', 'vegan', 'vegetarian']):
                    if len(text) > 10 and len(text) < 200:  # Reasonable length
                        restaurant_like_divs.append(div)
            
            print(f"Found {len(restaurant_like_divs)} divs with restaurant-like content")
            for i, div in enumerate(restaurant_like_divs[:5]):
                text = div.get_text(strip=True)
                print(f"  Restaurant-like div {i+1}: {text[:150]}...")
            
            # Look for any JSON data in script tags
            print("\n=== Looking for JSON data in script tags ===")
            script_tags = soup.find_all('script', type='text/javascript')
            for i, script in enumerate(script_tags):
                if script.string:
                    # Look for JSON-like data
                    if '{' in script.string and '}' in script.string:
                        print(f"Script {i} contains JSON-like data (length: {len(script.string)})")
                        # Try to find restaurant data
                        if 'restaurant' in script.string.lower() or 'venue' in script.string.lower():
                            print(f"  Script {i} contains restaurant/venue data")
                            # Show first 500 chars
                            print(f"  Preview: {script.string[:500]}...")
            
            # Look for any elements with coordinates or addresses
            print("\n=== Looking for elements with coordinates or addresses ===")
            coord_elements = soup.find_all(attrs={'data-lat': True}) + soup.find_all(attrs={'data-lng': True})
            print(f"Elements with coordinates: {len(coord_elements)}")
            
            # Look for any elements with restaurant names
            print("\n=== Looking for elements that might contain restaurant names ===")
            name_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            restaurant_names = []
            for elem in name_elements:
                text = elem.get_text(strip=True)
                if len(text) > 3 and len(text) < 100:  # Reasonable name length
                    if any(word in text.lower() for word in ['restaurant', 'cafe', 'food', 'dining', 'vegan', 'vegetarian']):
                        restaurant_names.append(text)
            
            print(f"Found {len(restaurant_names)} potential restaurant names")
            for i, name in enumerate(restaurant_names[:10]):
                print(f"  Name {i+1}: {name}")
            
            # If we still haven't found anything, show the page structure
            if not restaurant_like_divs and not restaurant_names:
                print("\n=== Page structure analysis ===")
                print(f"Total elements: {len(soup.find_all())}")
                print(f"Total divs: {len(soup.find_all('div'))}")
                print(f"Total spans: {len(soup.find_all('span'))}")
                print(f"Total links: {len(soup.find_all('a'))}")
                
                # Show the main content area
                main_content = soup.find('main') or soup.find('div', class_='content') or soup.find('div', class_='main')
                if main_content:
                    print(f"Main content area found: {main_content.name}")
                    print(f"Main content text: {main_content.get_text(strip=True)[:200]}...")
                else:
                    print("No main content area found")
                    
                    # Show the body content
                    body = soup.find('body')
                    if body:
                        print(f"Body content preview: {body.get_text(strip=True)[:500]}...")
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    analyze_html_structure()
