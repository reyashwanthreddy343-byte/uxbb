import pytest
import inspect
from app.driver.browser import BlackBoxBrowserDriver

def test_driver_strictly_has_no_dom_or_selector_methods():
    """
    CRITICAL CONSTRAINT VERIFICATION:
    Asserts that BlackBoxBrowserDriver has NO methods accepting CSS selectors,
    XPath, or DOM queries. Only pixel coordinates are supported.
    """
    driver_methods = [m for m in dir(BlackBoxBrowserDriver) if not m.startswith("_")]
    
    forbidden_terms = ["selector", "xpath", "locator", "by_id", "by_class", "query_selector"]
    for method_name in driver_methods:
        for term in forbidden_terms:
            assert term not in method_name.lower(), f"Forbidden DOM selector method found: {method_name}"
            
    # Verify parameter signatures of action methods
    sig_click = inspect.signature(BlackBoxBrowserDriver.click_at_coordinate)
    params_click = list(sig_click.parameters.keys())
    assert "x" in params_click and "y" in params_click
    assert "selector" not in params_click
