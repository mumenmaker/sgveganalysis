#!/usr/bin/env python3
"""
Simple test to check if Selenium works
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def test_selenium():
    """Test Selenium setup"""
    print("Testing Selenium setup...")
    
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        print("Creating Chrome WebDriver...")
        driver = webdriver.Chrome(options=chrome_options)
        
        print("Loading Google...")
        driver.get("https://www.google.com")
        
        print(f"Page title: {driver.title}")
        
        driver.quit()
        print("✅ Selenium test successful!")
        
    except Exception as e:
        print(f"❌ Selenium test failed: {e}")

if __name__ == "__main__":
    test_selenium()
