"""
Healthcare Data QA Automation - Test Configuration

This module provides pytest fixtures and configuration for:
1. Data ingestion and validation testing
2. Data quality check testing
3. API endpoint testing
4. Web UI automation testing

Author: Robert Torres
"""

import os
import json
import sqlite3
import pytest
import pandas as pd
import numpy as np
import requests
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# Add project root to Python path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test Constants
TEST_DATA_DIR = Path("tests/data")
TEST_DB_PATH = Path("tests/data/test_healthcare.db")
TEST_CONFIG_PATH = Path("tests/data/test_config.json")
API_BASE_URL = "http://localhost:5001"

@pytest.fixture(scope="session")
def test_config():
    """Create test configuration."""
    config = {
        "data_dir": str(TEST_DATA_DIR),
        "db_path": str(TEST_DB_PATH),
        "reports_dir": str(TEST_DATA_DIR / "reports"),
        "table_name": "insurance_data",
        "thresholds": {
            "null_percentage": 5.0,
            "outlier_threshold": 3.0,
            "distribution_p_value": 0.05,
            "correlation_threshold": 0.1,
            "min_row_count": 10,
            "max_duplicates": 5.0,
            "cardinality_threshold": 0.2
        }
    }
    
    # Create test directories
    TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
    (TEST_DATA_DIR / "reports").mkdir(parents=True, exist_ok=True)
    
    # Save config
    with open(TEST_CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    
    return config

@pytest.fixture(scope="session")
def test_data():
    """Create sample healthcare data for testing."""
    return pd.DataFrame({
        "age": [19, 18, 28, 33, 32],
        "sex": ["female", "male", "male", "male", "male"],
        "bmi": [27.9, 33.77, 33.0, 22.71, 28.88],
        "children": [0, 1, 3, 0, 0],
        "smoker": ["yes", "no", "no", "no", "no"],
        "region": ["southwest", "southeast", "southeast", "northwest", "northwest"],
        "charges": [16884.92, 1725.55, 4449.46, 21984.47, 3866.86]
    })

@pytest.fixture(scope="session")
def test_db(test_config, test_data):
    """Create test database with sample data."""
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    
    conn = sqlite3.connect(TEST_DB_PATH)
    
    # Create tables
    conn.execute('''
    CREATE TABLE IF NOT EXISTS insurance_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        age INTEGER NOT NULL,
        sex TEXT NOT NULL,
        bmi REAL NOT NULL,
        children INTEGER NOT NULL,
        smoker TEXT NOT NULL,
        region TEXT NOT NULL,
        charges REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.execute('''
    CREATE TABLE IF NOT EXISTS quality_issues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        issue_type TEXT NOT NULL,
        column_name TEXT,
        description TEXT NOT NULL,
        severity TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Insert test data
    test_data.to_sql("insurance_data", conn, if_exists="replace", index=False)
    
    conn.commit()
    conn.close()
    
    return TEST_DB_PATH

@pytest.fixture(scope="function")
def temp_db():
    """Create temporary database for isolated tests."""
    temp_dir = tempfile.mkdtemp()
    temp_db_path = Path(temp_dir) / "temp_test.db"
    
    conn = sqlite3.connect(temp_db_path)
    conn.execute('''
    CREATE TABLE IF NOT EXISTS insurance_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        age INTEGER NOT NULL,
        sex TEXT NOT NULL,
        bmi REAL NOT NULL,
        children INTEGER NOT NULL,
        smoker TEXT NOT NULL,
        region TEXT NOT NULL,
        charges REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.close()
    
    yield temp_db_path
    
    # Cleanup
    shutil.rmtree(temp_dir)

@pytest.fixture(scope="session")
def api_client():
    """Create API client for testing endpoints."""
    class APIClient:
        def __init__(self, base_url):
            self.base_url = base_url
        
        def get(self, endpoint, params=None):
            return requests.get(f"{self.base_url}{endpoint}", params=params)
        
        def post(self, endpoint, json_data=None):
            return requests.post(f"{self.base_url}{endpoint}", json=json_data)
    
    return APIClient(API_BASE_URL)

@pytest.fixture(scope="function")
def selenium_driver():
    """Create Selenium WebDriver for UI testing."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.webdriver import WebDriver
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        # Let Selenium handle driver installation and configuration
        driver = WebDriver(options=chrome_options)
        yield driver
    finally:
        if 'driver' in locals():
            driver.quit()