#!/usr/bin/env python3
"""
Test script to examine the actual HTML response from HappyCow
"""

import requests
from bs4 import BeautifulSoup
import json
import re

def test_happycow_response():
    """Test the actual response from HappyCow"""
    print("=== Testing HappyCow Response ===\n")
    
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
        print(f"Making request to: {url}")
        print(f"Params: {params}")
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Content Length: {len(response.content)}")
        
        if response.status_code == 200:
            print("✅ Request successful!")
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for restaurant data in script tags
            script_tags = soup.find_all('script', type='text/javascript')
            print(f"\nFound {len(script_tags)} script tags")
            
            restaurant_data = []
            for i, script in enumerate(script_tags):
                if script.string and 'restaurant' in script.string.lower():
                    print(f"Script {i} contains restaurant data (length: {len(script.string)})")
                    
                    # Try to extract JSON data
                    try:
                        json_match = re.search(r'var\s+restaurants\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(1)
                            restaurant_data = json.loads(json_str)
                            print(f"✅ Found {len(restaurant_data)} restaurants in JSON data")
                            break
                    except (json.JSONDecodeError, AttributeError) as e:
                        print(f"❌ Error parsing JSON: {e}")
                        continue
            
            if not restaurant_data:
                print("❌ No restaurant data found in script tags")
                
                # Try to find restaurant elements in HTML
                restaurant_elements = soup.find_all('div', class_='restaurant-item')
                print(f"Found {len(restaurant_elements)} restaurant elements in HTML")
                
                if restaurant_elements:
                    print("✅ Found restaurant elements in HTML")
                    for i, elem in enumerate(restaurant_elements[:3]):
                        name_elem = elem.find('h3', class_='name')
                        if name_elem:
                            print(f"  Restaurant {i+1}: {name_elem.get_text(strip=True)}")
                else:
                    print("❌ No restaurant elements found in HTML")
                    
                    # Show page title and some content
                    title = soup.find('title')
                    if title:
                        print(f"Page title: {title.get_text()}")
                    
                    # Look for any divs that might contain restaurant data
                    all_divs = soup.find_all('div')
                    print(f"Total divs found: {len(all_divs)}")
                    
                    # Look for divs with restaurant-related classes
                    restaurant_classes = ['restaurant', 'venue', 'listing', 'search-result', 'item']
                    for class_name in restaurant_classes:
                        elements = soup.find_all('div', class_=lambda x: x and class_name in x.lower())
                        if elements:
                            print(f"Found {len(elements)} divs with class containing '{class_name}'")
                            for i, elem in enumerate(elements[:3]):
                                text = elem.get_text(strip=True)[:100]
                                print(f"  {class_name} {i+1}: {text}...")
                    
                    # Show first 1000 chars of content
                    print(f"\nPage content preview (first 1000 chars):")
                    print(response.text[:1000])
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response content: {response.text[:500]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_happycow_response()
