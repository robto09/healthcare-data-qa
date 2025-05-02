"""
Healthcare Data QA Automation - Web UI Tests

This module provides automated UI tests for:
1. Dashboard navigation and functionality
2. Data visualization components
3. Quality metrics display
4. Interactive features

Uses Selenium WebDriver for browser automation.

Author: Robert Torres
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class TestDashboardUI:
    """Test suite for web dashboard UI automation."""
    
    @pytest.fixture(autouse=True)
    def setup(self, selenium_driver):
        """Setup test environment before each test."""
        self.driver = selenium_driver
        self.wait = WebDriverWait(self.driver, 10)
        self.base_url = "http://localhost:5001"
        
        # Configure Chrome
        self.driver.set_window_size(1366, 768)
        self.driver.implicitly_wait(5)
    
    def test_dashboard_loads(self):
        """Test that the dashboard loads successfully."""
        self.driver.get(self.base_url)
        
        # Check title
        title = self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        assert "Dashboard" in title.text
        
        # Check navigation menu
        nav = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "navbar"))
        )
        assert nav.is_displayed()
    
    def test_navigation(self):
        """Test navigation between dashboard pages."""
        self.driver.get(self.base_url)
        
        # Test each navigation option
        pages = {
            "Dashboard": "/",
            "Tables": "/tables",
            "Quality Checks": "/quality",
            "API Docs": "/api-docs"
        }
        
        for page_name, path in pages.items():
            # Click navigation link
            nav_link = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{page_name}')]"))
            )
            nav_link.click()
            
            # Verify URL changed
            assert path in self.driver.current_url
            
            # Verify page loaded
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
    
    def test_data_visualization(self):
        """Test data visualization functionality."""
        self.driver.get(self.base_url)
        
        # Check if chart is displayed
        chart_canvas = self.wait.until(
            EC.presence_of_element_located((By.ID, "tableDistributionChart"))
        )
        assert chart_canvas.is_displayed()
        
        # Check table records section
        records_container = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "card-body"))
        )
        assert "Table Records" in records_container.text
    def test_quality_checks(self):
        """Test quality checks page."""
        self.driver.get(f"{self.base_url}/quality")
        
        # Check page title
        title = self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        assert "Quality Checks" in title.text
        
        # Check run check button
        run_button = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "btn-success"))
        )
        assert "Run Quality Check" in run_button.text
        
        # Check results table if exists
        try:
            table = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "table"))
            )
            assert table.is_displayed()
            
            # Verify table headers
            headers = table.find_elements(By.TAG_NAME, "th")
            # Check if table has headers
            assert len(headers) > 0
            # Verify at least one header contains text
            assert any(h.text.strip() for h in headers)
        except TimeoutException:
            # Table might not exist if no checks have been run
            no_data = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "text-muted"))
            )
            assert "No quality checks" in no_data.text
    
    def test_tables_page(self):
        """Test tables page functionality."""
        self.driver.get(f"{self.base_url}/tables")
        
        # Check page title
        title = self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        assert "Tables" in title.text
        
        # Check database statistics
        stats_card = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "card"))
        )
        assert "Total Records" in stats_card.text
        
        # Check table is displayed
        table = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "table"))
        )
        assert table.is_displayed()
        
        # Verify table has content
        rows = table.find_elements(By.TAG_NAME, "tr")
        assert len(rows) > 0
    
    def test_responsive_layout(self):
        """Test dashboard responsiveness."""
        self.driver.get(self.base_url)
        
        # Test different viewport sizes
        viewports = [
            (1920, 1080),  # Desktop
            (1366, 768),   # Laptop
            (768, 1024),   # Tablet
            (375, 812)     # Mobile
        ]
        
        for width, height in viewports:
            self.driver.set_window_size(width, height)
            
            # Check navbar visibility
            navbar = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "navbar"))
            )
            assert navbar.is_displayed()
            
            # Check main content area
            content = self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "main"))
            )
            assert content.is_displayed()
            
            # Check footer
            footer = self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "footer"))
            )
            assert footer.is_displayed()
    
    def test_error_handling(self):
        """Test error handling."""
        # Test non-existent page
        self.driver.get(f"{self.base_url}/nonexistent")
        
        try:
            error_message = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
            )
            assert "Page not found" in error_message.text
        except TimeoutException:
            pytest.fail("Error message not displayed for invalid route")
        
        # Verify navbar remains functional
        navbar = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "navbar"))
        )
        assert navbar.is_displayed()