"""
PyTest configuration and fixtures for U-Ask chatbot automation.
"""
import pytest
import json
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from utils.driver_factory import DriverFactory
from utils.wait_utils import WaitUtils


# Configuration: Chatbot URL - can be overridden via environment variable
CHATBOT_URL = os.getenv("CHATBOT_URL", "https://uask.gov.ae")


@pytest.fixture(scope="session")
def config():
    """Load test configuration from environment or defaults."""
    return {
        "chatbot_url": CHATBOT_URL,
        "headless": os.getenv("HEADLESS", "false").lower() == "true",
        "implicit_wait": 0,  # We use explicit waits only
        "page_load_timeout": 30,
        "screenshot_on_failure": True
    }


@pytest.fixture(scope="function")
def driver(config, request):
    """Create and configure WebDriver instance for each test."""
    driver_instance = DriverFactory.create_driver(
        headless=config["headless"],
        page_load_timeout=config["page_load_timeout"]
    )
    yield driver_instance
    
    # Cleanup: Take screenshot on failure
    if config["screenshot_on_failure"]:
        # Check test outcome using pytest hook
        if hasattr(request.node, 'rep_call') and request.node.rep_call.outcome == "failed":
            screenshot_path = Path("screenshots") / f"{request.node.name}.png"
            screenshot_path.parent.mkdir(exist_ok=True)
            try:
                driver_instance.save_screenshot(str(screenshot_path))
            except:
                pass  # Continue even if screenshot fails
    
    driver_instance.quit()


@pytest.fixture(scope="function")
def wait(driver):
    """Provide WaitUtils instance for explicit waits."""
    return WaitUtils(driver)


@pytest.fixture(scope="function")
def test_data():
    """Load test data from JSON file."""
    data_path = Path("data") / "test_data.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="function")
def chat_page(driver, wait, config):
    """Initialize ChatPage with driver and navigate to chatbot."""
    from pages.chat_page import ChatPage
    page = ChatPage(driver, wait)
    page.navigate_to_chatbot(config["chatbot_url"])
    return page


# Hook to capture test outcome for screenshot on failure
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture test outcome for screenshot on failure."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


