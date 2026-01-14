"""
Page Object Model for U-Ask chatbot interface.
Encapsulates all interactions with the chatbot UI elements.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from utils.wait_utils import WaitUtils
import time


class ChatPage:
    """Page Object for U-Ask chatbot interface."""
    
    # Locators - Adjust these based on actual chatbot implementation
    # Common patterns for chatbot widgets - using XPath for OR conditions
    CHAT_INPUT = (By.CSS_SELECTOR, "input[type='text'], textarea, [contenteditable='true']")
    CHAT_INPUT_ALT = (By.XPATH, "//input[@type='text'] | //textarea | //*[@contenteditable='true'] | //*[contains(@class, 'input')] | //*[contains(@id, 'input')]")
    SEND_BUTTON = (By.XPATH, "//button[@type='submit'] | //*[contains(@class, 'send')] | //*[contains(@aria-label, 'send') or contains(@aria-label, 'Send')]")
    USER_MESSAGE = (By.XPATH, "//*[contains(@class, 'user-message')] | //*[contains(@class, 'message') and contains(@class, 'user')]")
    AI_MESSAGE = (By.XPATH, "//*[contains(@class, 'ai-message')] | //*[contains(@class, 'bot-message')] | //*[contains(@class, 'assistant-message')] | //*[contains(@class, 'response')]")
    LOADING_INDICATOR = (By.XPATH, "//*[contains(@class, 'loading')] | //*[contains(@class, 'typing')] | //*[contains(@class, 'spinner')] | //*[contains(@aria-label, 'loading')]")
    ERROR_MESSAGE = (By.XPATH, "//*[contains(@class, 'error')] | //*[contains(@class, 'fallback')]")
    
    def __init__(self, driver: WebDriver, wait: WaitUtils):
        """
        Initialize ChatPage with driver and wait utilities.
        
        Args:
            driver: WebDriver instance
            wait: WaitUtils instance for explicit waits
        """
        self.driver = driver
        self.wait = wait
    
    def _find_element_with_fallback(self, primary_locator, fallback_locator=None, timeout=10):
        """
        Try to find element using primary locator, fallback to alternative if needed.
        
        Args:
            primary_locator: Primary locator tuple
            fallback_locator: Optional fallback locator tuple
            timeout: Timeout in seconds
        
        Returns:
            WebElement: Found element
        """
        try:
            return self.wait.wait_for_element_visible(primary_locator, timeout=timeout)
        except:
            if fallback_locator:
                return self.wait.wait_for_element_visible(fallback_locator, timeout=timeout)
            raise
    
    def navigate_to_chatbot(self, url: str):
        """
        Navigate to the chatbot URL.
        
        Args:
            url: Chatbot URL to navigate to
        """
        self.driver.get(url)
        # Wait for page to load
        self.wait_for_chat_widget()
    
    def wait_for_chat_widget(self, timeout=15):
        """
        Wait for chat widget to be visible and ready.
        
        Args:
            timeout: Maximum time to wait in seconds
        """
        # Try to find input field (primary indicator that chat widget is loaded)
        try:
            self.wait.wait_for_element_visible(self.CHAT_INPUT, timeout=timeout)
        except:
            # If primary selector fails, try alternative selector
            try:
                self.wait.wait_for_element_visible(self.CHAT_INPUT_ALT, timeout=timeout)
            except Exception as e:
                # If both fail, wait a bit more and try once more
                import time
                time.sleep(2)
                self.wait.wait_for_element_visible(self.CHAT_INPUT_ALT, timeout=timeout-2)
    
    def is_chat_widget_loaded(self) -> bool:
        """
        Check if chat widget is loaded and visible.
        
        Returns:
            bool: True if widget is loaded, False otherwise
        """
        # Try primary selector first
        if self.wait.is_element_visible(self.CHAT_INPUT, timeout=2):
            return True
        # Try alternative selector
        return self.wait.is_element_visible(self.CHAT_INPUT_ALT, timeout=2)
    
    def send_message(self, message: str):
        """
        Type and send a message in the chat input.
        
        Args:
            message: Message text to send
        """
        # Wait for input to be visible and clickable - try primary selector first
        try:
            input_element = self.wait.wait_for_element_clickable(self.CHAT_INPUT, timeout=5)
        except:
            # Fallback to alternative selector
            input_element = self.wait.wait_for_element_clickable(self.CHAT_INPUT_ALT, timeout=5)
        
        # Clear any existing text
        try:
            input_element.clear()
        except:
            # For contenteditable divs, clear differently
            input_element.send_keys(Keys.CONTROL + "a")
            input_element.send_keys(Keys.DELETE)
        
        # Type the message
        input_element.send_keys(message)
        
        # Try to click send button, or press Enter
        try:
            send_button = self.wait.wait_for_element_clickable(self.SEND_BUTTON, timeout=3)
            send_button.click()
        except:
            # Fallback: Press Enter if send button not found
            input_element.send_keys(Keys.RETURN)
        
        # Wait a moment for message to be sent
        time.sleep(0.5)
    
    def get_input_value(self) -> str:
        """
        Get current value of the input field.
        
        Returns:
            str: Input field value
        """
        try:
            input_element = self.wait.wait_for_element_present(self.CHAT_INPUT, timeout=2)
        except:
            input_element = self.wait.wait_for_element_present(self.CHAT_INPUT_ALT, timeout=2)
        
        # Try value attribute first (for input/textarea), then text (for contenteditable)
        value = input_element.get_attribute("value")
        if value:
            return value
        return input_element.text or ""
    
    def is_input_cleared(self) -> bool:
        """
        Check if input field is cleared after sending message.
        
        Returns:
            bool: True if input is empty, False otherwise
        """
        value = self.get_input_value()
        return not value or value.strip() == ""
    
    def wait_for_ai_response(self, timeout=30):
        """
        Wait for AI response to appear in the conversation.
        
        Args:
            timeout: Maximum time to wait for response
        
        Returns:
            WebElement: AI message element
        """
        # Wait for loading indicator to disappear (if present)
        try:
            if self.wait.is_element_visible(self.LOADING_INDICATOR, timeout=2):
                self.wait.wait_until_not_visible(self.LOADING_INDICATOR, timeout=timeout)
        except:
            pass  # Loading indicator may not always be present
        
        # Wait for AI message to appear
        return self.wait.wait_for_element_visible(self.AI_MESSAGE, timeout=timeout)
    
    def get_latest_ai_response(self) -> str:
        """
        Get the text content of the latest AI response.
        
        Returns:
            str: AI response text
        """
        ai_messages = self.driver.find_elements(*self.AI_MESSAGE)
        if ai_messages:
            # Get the last (most recent) AI message
            return ai_messages[-1].text
        return ""
    
    def get_all_ai_responses(self) -> list:
        """
        Get all AI responses in the conversation.
        
        Returns:
            list: List of AI response texts
        """
        ai_messages = self.driver.find_elements(*self.AI_MESSAGE)
        return [msg.text for msg in ai_messages]
    
    def get_all_user_messages(self) -> list:
        """
        Get all user messages in the conversation.
        
        Returns:
            list: List of user message texts
        """
        user_messages = self.driver.find_elements(*self.USER_MESSAGE)
        return [msg.text for msg in user_messages]
    
    def is_loading_indicator_visible(self) -> bool:
        """
        Check if loading/typing indicator is currently visible.
        
        Returns:
            bool: True if loading indicator is visible
        """
        return self.wait.is_element_visible(self.LOADING_INDICATOR, timeout=1)
    
    def wait_for_loading_to_complete(self, timeout=30):
        """
        Wait for loading indicator to disappear.
        
        Args:
            timeout: Maximum time to wait
        """
        if self.is_loading_indicator_visible():
            self.wait.wait_until_not_visible(self.LOADING_INDICATOR, timeout=timeout)
    
    def get_error_message(self) -> str:
        """
        Get error or fallback message if present.
        
        Returns:
            str: Error message text, empty string if not found
        """
        try:
            error_element = self.wait.wait_for_element_visible(self.ERROR_MESSAGE, timeout=2)
            return error_element.text
        except:
            return ""
    
    def check_direction(self) -> str:
        """
        Check text direction of the page (LTR or RTL).
        
        Returns:
            str: 'ltr' or 'rtl'
        """
        direction = self.driver.execute_script("return document.documentElement.dir || 'ltr'")
        if not direction:
            # Fallback: check computed style
            direction = self.driver.execute_script(
                "return window.getComputedStyle(document.documentElement).direction || 'ltr'"
            )
        return direction.lower()
    
    def scroll_to_bottom(self):
        """Scroll conversation to bottom to see latest messages."""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)  # Brief pause for scroll to complete
    
    def is_element_visible_and_enabled(self, locator) -> bool:
        """
        Check if element is both visible and enabled (accessibility check).
        
        Args:
            locator: Tuple of (By strategy, value)
        
        Returns:
            bool: True if element is visible and enabled
        """
        try:
            element = self.wait.wait_for_element_visible(locator, timeout=2)
            return element.is_enabled()
        except:
            return False
    
    def get_page_source_snippet(self, length=500) -> str:
        """
        Get a snippet of page source for debugging.
        
        Args:
            length: Maximum length of snippet
        
        Returns:
            str: Page source snippet
        """
        return self.driver.page_source[:length]
