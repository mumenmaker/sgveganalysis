#!/usr/bin/env python3
"""
Test runner script for HappyCow scraper
"""

import subprocess
import sys
import os

def run_tests():
    """Run tests with different configurations"""
    
    print("🧪 HappyCow Scraper Test Suite")
    print("=" * 50)
    
    # Change to the scraper directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Test configurations
    test_configs = [
        {
            "name": "Unit Tests Only",
            "command": ["python", "-m", "pytest", "tests/", "-v", "-m", "not slow and not integration and not selenium and not database"]
        },
        {
            "name": "Unit Tests with Coverage",
            "command": ["python", "-m", "pytest", "tests/", "-v", "--cov=.", "--cov-report=html", "--cov-report=term", "-m", "not slow and not integration and not selenium and not database"]
        },
        {
            "name": "All Tests (if database available)",
            "command": ["python", "-m", "pytest", "tests/", "-v", "-m", "not slow"]
        }
    ]
    
    for config in test_configs:
        print(f"\n🔍 Running: {config['name']}")
        print("-" * 30)
        
        try:
            result = subprocess.run(config["command"], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Tests passed!")
                if result.stdout:
                    print(result.stdout)
            else:
                print("❌ Tests failed!")
                if result.stderr:
                    print(result.stderr)
                if result.stdout:
                    print(result.stdout)
                    
        except Exception as e:
            print(f"❌ Error running tests: {e}")
    
    print("\n📊 Test Summary")
    print("=" * 50)
    print("To run specific test categories:")
    print("  pytest tests/ -m unit          # Unit tests only")
    print("  pytest tests/ -m database      # Database tests")
    print("  pytest tests/ -m selenium      # Selenium tests")
    print("  pytest tests/ -m integration   # Integration tests")
    print("  pytest tests/ --cov=.          # With coverage report")

if __name__ == "__main__":
    run_tests()
