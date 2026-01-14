"""
Utility class for explicit waits using Selenium WebDriverWait.
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement


class WaitUtils:
    """Wrapper class for common explicit wait operations."""
    
    def __init__(self, driver, timeout=10):
        """
        Initialize WaitUtils with driver and default timeout.
        
        Args:
            driver: WebDriver instance
            timeout (int): Default timeout in seconds
        """
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)
    
    def wait_for_element_visible(self, locator, timeout=None):
        """
        Wait for element to be visible on the page.
        
        Args:
            locator: Tuple of (By strategy, value)
            timeout: Optional custom timeout (uses default if None)
        
        Returns:
            WebElement: Visible element
        """
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        return wait.until(EC.visibility_of_element_located(locator))
    
    def wait_for_element_clickable(self, locator, timeout=None):
        """
        Wait for element to be clickable.
        
        Args:
            locator: Tuple of (By strategy, value)
            timeout: Optional custom timeout
        
        Returns:
            WebElement: Clickable element
        """
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        return wait.until(EC.element_to_be_clickable(locator))
    
    def wait_for_element_present(self, locator, timeout=None):
        """
        Wait for element to be present in DOM (may not be visible).
        
        Args:
            locator: Tuple of (By strategy, value)
            timeout: Optional custom timeout
        
        Returns:
            WebElement: Present element
        """
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located(locator))
    
    def wait_for_text_in_element(self, locator, text, timeout=None):
        """
        Wait for specific text to appear in element.
        
        Args:
            locator: Tuple of (By strategy, value)
            text: Expected text content
            timeout: Optional custom timeout
        
        Returns:
            WebElement: Element containing the text
        """
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        return wait.until(EC.text_to_be_present_in_element(locator, text))
    
    def wait_for_elements_present(self, locator, timeout=None, min_count=1):
        """
        Wait for multiple elements to be present.
        
        Args:
            locator: Tuple of (By strategy, value)
            timeout: Optional custom timeout
            min_count: Minimum number of elements expected
        
        Returns:
            list: List of WebElements
        """
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        elements = wait.until(lambda d: d.find_elements(*locator))
        assert len(elements) >= min_count, f"Expected at least {min_count} elements, found {len(elements)}"
        return elements
    
    def wait_until_not_visible(self, locator, timeout=None):
        """
        Wait for element to become invisible.
        
        Args:
            locator: Tuple of (By strategy, value)
            timeout: Optional custom timeout
        """
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        wait.until(EC.invisibility_of_element_located(locator))
    
    def is_element_visible(self, locator, timeout=2):
        """
        Check if element is visible without raising exception.
        
        Args:
            locator: Tuple of (By strategy, value)
            timeout: Short timeout for quick check
        
        Returns:
            bool: True if element is visible, False otherwise
        """
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False
