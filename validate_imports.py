"""
Simple script to validate Python imports and syntax.
Run this to check if all dependencies are available and code is syntactically correct.
"""
import sys

def validate_imports():
    """Check if all required imports work."""
    errors = []
    
    # Check standard library imports
    try:
        import json
        import os
        from pathlib import Path
        import re
        import time
        print("✓ Standard library imports: OK")
    except ImportError as e:
        errors.append(f"Standard library import error: {e}")
        print(f"✗ Standard library imports: FAILED - {e}")
    
    # Check third-party imports
    try:
        import pytest
        print("✓ PyTest: OK")
    except ImportError:
        errors.append("pytest not installed")
        print("✗ PyTest: NOT INSTALLED (run: pip install pytest)")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        print("✓ Selenium: OK")
    except ImportError:
        errors.append("selenium not installed")
        print("✗ Selenium: NOT INSTALLED (run: pip install selenium)")
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("✓ webdriver-manager: OK")
    except ImportError:
        errors.append("webdriver-manager not installed")
        print("✗ webdriver-manager: NOT INSTALLED (run: pip install webdriver-manager)")
    
    # Check project imports
    try:
        from utils.driver_factory import DriverFactory
        print("✓ utils.driver_factory: OK")
    except ImportError as e:
        errors.append(f"utils.driver_factory import error: {e}")
        print(f"✗ utils.driver_factory: FAILED - {e}")
    
    try:
        from utils.wait_utils import WaitUtils
        print("✓ utils.wait_utils: OK")
    except ImportError as e:
        errors.append(f"utils.wait_utils import error: {e}")
        print(f"✗ utils.wait_utils: FAILED - {e}")
    
    try:
        from pages.chat_page import ChatPage
        print("✓ pages.chat_page: OK")
    except ImportError as e:
        errors.append(f"pages.chat_page import error: {e}")
        print(f"✗ pages.chat_page: FAILED - {e}")
    
    # Check test files
    try:
        import tests.test_chat_ui
        print("✓ tests.test_chat_ui: OK")
    except ImportError as e:
        errors.append(f"tests.test_chat_ui import error: {e}")
        print(f"✗ tests.test_chat_ui: FAILED - {e}")
    
    try:
        import tests.test_ai_responses
        print("✓ tests.test_ai_responses: OK")
    except ImportError as e:
        errors.append(f"tests.test_ai_responses import error: {e}")
        print(f"✗ tests.test_ai_responses: FAILED - {e}")
    
    try:
        import tests.test_security
        print("✓ tests.test_security: OK")
    except ImportError as e:
        errors.append(f"tests.test_security import error: {e}")
        print(f"✗ tests.test_security: FAILED - {e}")
    
    # Check data file
    try:
        import json
        from pathlib import Path
        data_path = Path("data") / "test_data.json"
        if data_path.exists():
            with open(data_path, "r", encoding="utf-8") as f:
                json.load(f)
            print("✓ test_data.json: OK (valid JSON)")
        else:
            errors.append("test_data.json not found")
            print("✗ test_data.json: NOT FOUND")
    except json.JSONDecodeError as e:
        errors.append(f"test_data.json invalid JSON: {e}")
        print(f"✗ test_data.json: INVALID JSON - {e}")
    except Exception as e:
        errors.append(f"test_data.json error: {e}")
        print(f"✗ test_data.json: ERROR - {e}")
    
    print("\n" + "="*50)
    if errors:
        print(f"Validation FAILED with {len(errors)} error(s):")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("Validation PASSED: All imports and files are OK!")
        return True

if __name__ == "__main__":
    success = validate_imports()
    sys.exit(0 if success else 1)
