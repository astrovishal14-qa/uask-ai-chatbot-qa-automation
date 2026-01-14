"""
WebDriver factory for creating and configuring browser instances.
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class DriverFactory:
    """Factory class for creating WebDriver instances with consistent configuration."""
    
    @staticmethod
    def create_driver(headless=False, page_load_timeout=30):
        """
        Create and configure Chrome WebDriver instance.
        
        Args:
            headless (bool): Run browser in headless mode
            page_load_timeout (int): Maximum time to wait for page load (seconds)
        
        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance
        """
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument("--headless")
        
        # Standard Chrome options for stability
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Set window size for consistent testing
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Initialize service with webdriver-manager for automatic driver management
        service = Service(ChromeDriverManager().install())
        
        # Create driver instance
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(page_load_timeout)
        
        # Remove webdriver property to avoid detection
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })
        
        return driver
