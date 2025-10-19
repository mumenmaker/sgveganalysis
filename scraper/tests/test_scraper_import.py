#!/usr/bin/env python3
"""
Test scraper import and basic functionality
"""

try:
    from happycow_scraper import HappyCowScraper
    print("✅ HappyCowScraper import successful")
    
    scraper = HappyCowScraper(use_selenium=True)
    print("✅ HappyCowScraper initialization successful")
    
    print(f"use_selenium: {scraper.use_selenium}")
    print(f"driver: {scraper.driver}")
    
    # Test Selenium setup
    driver = scraper.setup_selenium()
    if driver:
        print("✅ Selenium setup successful")
        scraper.close_selenium()
        print("✅ Selenium cleanup successful")
    else:
        print("❌ Selenium setup failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
