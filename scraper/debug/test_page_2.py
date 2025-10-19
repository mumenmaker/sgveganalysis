# -*- coding: utf-8 -*-
import logging
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_page_2():
    """Test if page 2 has restaurant elements"""
    logger.info("Testing page 2 for restaurant elements...")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)

    try:
        # Test page 1 first
        params = Config.SINGAPORE_PARAMS.copy()
        params['page'] = str(1)
        url = "{}?".format(Config.SEARCH_URL) + "&".join(["{}={}".format(k, v) for k, v in params.items()])
        
        logger.info("Loading page 1: {}".format(url))
        driver.get(url)
        time.sleep(15)
        
        elements_page_1 = driver.find_elements(By.CSS_SELECTOR, '.venue-item')
        logger.info("Page 1: Found {} restaurant elements".format(len(elements_page_1)))
        
        # Test page 2
        params['page'] = str(2)
        url = "{}?".format(Config.SEARCH_URL) + "&".join(["{}={}".format(k, v) for k, v in params.items()])
        
        logger.info("Loading page 2: {}".format(url))
        driver.get(url)
        time.sleep(15)
        
        elements_page_2 = driver.find_elements(By.CSS_SELECTOR, '.venue-item')
        logger.info("Page 2: Found {} restaurant elements".format(len(elements_page_2)))
        
        if elements_page_2:
            logger.info("Page 2 has restaurant elements!")
            # Show first few elements
            for i, element in enumerate(elements_page_2[:3]):
                logger.info("  Element {}: {}".format(i+1, element.text.strip()[:50]))
        else:
            logger.warning("Page 2 has no restaurant elements")
            
        # Test page 3
        params['page'] = str(3)
        url = "{}?".format(Config.SEARCH_URL) + "&".join(["{}={}".format(k, v) for k, v in params.items()])
        
        logger.info("Loading page 3: {}".format(url))
        driver.get(url)
        time.sleep(15)
        
        elements_page_3 = driver.find_elements(By.CSS_SELECTOR, '.venue-item')
        logger.info("Page 3: Found {} restaurant elements".format(len(elements_page_3)))
        
        return len(elements_page_1), len(elements_page_2), len(elements_page_3)

    except Exception as e:
        logger.error("Error during page 2 test: {}".format(e))
        return 0, 0, 0
    finally:
        driver.quit()

if __name__ == "__main__":
    print("Testing Page 2 for Restaurant Elements")
    print("=" * 50)
    page_1_count, page_2_count, page_3_count = test_page_2()
    print("\nResults:")
    print("  Page 1: {} restaurants".format(page_1_count))
    print("  Page 2: {} restaurants".format(page_2_count))
    print("  Page 3: {} restaurants".format(page_3_count))
    
    if page_2_count > 0:
        print("\n✅ Page 2 has restaurants - pagination should work!")
    else:
        print("\n❌ Page 2 has no restaurants - pagination issue!")
