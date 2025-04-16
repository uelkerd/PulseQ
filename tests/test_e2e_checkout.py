# tests/test_e2e_checkout.py

import pytest
import allure
import json
import os
from datetime import datetime

from framework.utilities.driver_manager import initialize_driver, quit_driver
from framework.utilities.wait_utils import WaitUtils
from framework.utilities.elements_utils import ElementsUtils
from framework.utilities.data_handler import DataHandler
from framework.utilities.logger import setup_logger
from framework.utilities.performance_metrics import measure_performance, PerformanceMetrics
from framework.utilities.misc_utils import MiscUtils
from framework.config import load_config

from selenium.webdriver.common.by import By

# Set up logger
logger = setup_logger("test_e2e_checkout")

# Create metrics instance for performance measurement
metrics = PerformanceMetrics()

# Create or ensure test data directory exists
os.makedirs("test_data", exist_ok=True)

# Test data - we'll use a more complex data structure for this test
PRODUCTS = [
    {"id": 1, "name": "Laptop", "price": 999.99, "quantity": 1},
    {"id": 2, "name": "Smartphone", "price": 499.99, "quantity": 2},
    {"id": 3, "name": "Headphones", "price": 129.99, "quantity": 1}
]

SHIPPING_METHODS = [
    {"id": 1, "name": "Standard", "price": 5.99, "days": "3-5"},
    {"id": 2, "name": "Express", "price": 15.99, "days": "1-2"},
    {"id": 3, "name": "Next Day", "price": 29.99, "days": "1"}
]

USER_DATA = {
    "first_name": "Test",
    "last_name": "User",
    "email": "testuser@example.com",
    "address": "123 Test Street",
    "city": "Test City",
    "state": "TS",
    "zip": "12345",
    "country": "Test Country",
    "card_number": "4111111111111111",
    "card_expiry": "12/25",
    "card_cvv": "123"
}

# Save test data to file for later use if needed
with open("test_data/products.json", "w") as f:
    json.dump(PRODUCTS, f, indent=2)

with open("test_data/shipping.json", "w") as f:
    json.dump(SHIPPING_METHODS, f, indent=2)

with open("test_data/user.json", "w") as f:
    json.dump(USER_DATA, f, indent=2)

# Page objects as embedded classes for this example
# In a real project, these would be in separate files
class HomePage:
    def __init__(self, driver):
        self.driver = driver
        self.elements_utils = ElementsUtils(driver)
        self.wait_utils = WaitUtils(driver)
        
        # Locators
        self.product_cards = (By.CSS_SELECTOR, ".product-card")
        self.add_to_cart_buttons = (By.CSS_SELECTOR, ".add-to-cart-btn")
        self.cart_icon = (By.ID, "cart-icon")
        self.cart_count = (By.CSS_SELECTOR, ".cart-count")
    
    def open(self):
        """Navigate to the home page."""
        self.driver.get("http://example.com")
        self.wait_utils.wait_for_element_visible((By.TAG_NAME, "h1"))
        logger.info("Opened home page")
        return self
    
    def add_product_to_cart(self, product_id):
        """Add a product to the cart by ID."""
        product_selector = (By.CSS_SELECTOR, f".product-card[data-product-id='{product_id}']")
        self.elements_utils.scroll_to_element(product_selector)
        
        add_button = (By.CSS_SELECTOR, f".product-card[data-product-id='{product_id}'] .add-to-cart-btn")
        self.elements_utils.click_element(add_button)
        
        # Wait for cart update
        self.wait_utils.wait_for_element_visible(self.cart_count)
        logger.info(f"Added product ID {product_id} to cart")
        return self
    
    def go_to_cart(self):
        """Navigate to the shopping cart."""
        self.elements_utils.click_element(self.cart_icon)
        self.wait_utils.wait_for_url_contains("cart")
        logger.info("Navigated to cart page")
        return CartPage(self.driver)

class CartPage:
    def __init__(self, driver):
        self.driver = driver
        self.elements_utils = ElementsUtils(driver)
        self.wait_utils = WaitUtils(driver)
        
        # Locators
        self.cart_items = (By.CSS_SELECTOR, ".cart-item")
        self.item_quantity_inputs = (By.CSS_SELECTOR, ".item-quantity")
        self.update_cart_button = (By.ID, "update-cart")
        self.checkout_button = (By.ID, "checkout-button")
        self.cart_total = (By.ID, "cart-total")
    
    def update_product_quantity(self, product_id, quantity):
        """Update the quantity for a product in the cart."""
        quantity_input = (By.CSS_SELECTOR, f".cart-item[data-product-id='{product_id}'] .item-quantity")
        self.elements_utils.send_keys(quantity_input, str(quantity), clear_first=True)
        
        self.elements_utils.click_element(self.update_cart_button)
        
        # Wait for cart update
        updated_price_locator = (By.CSS_SELECTOR, f".cart-item[data-product-id='{product_id}'] .item-total")
        self.wait_utils.wait_for_element_visible(updated_price_locator)
        logger.info(f"Updated quantity for product ID {product_id} to {quantity}")
        return self
    
    def get_cart_total(self):
        """Get the cart total price."""
        total_text = self.elements_utils.get_text(self.cart_total)
        # Extract numeric value from text (e.g., "$1,234.56" -> 1234.56)
        total = float(''.join(c for c in total_text if c.isdigit() or c == '.'))
        logger.info(f"Cart total: {total}")
        return total
    
    def proceed_to_checkout(self):
        """Proceed to checkout page."""
        self.elements_utils.click_element(self.checkout_button)
        self.wait_utils.wait_for_url_contains("checkout")
        logger.info("Proceeded to checkout page")
        return CheckoutPage(self.driver)

class CheckoutPage:
    def __init__(self, driver):
        self.driver = driver
        self.elements_utils = ElementsUtils(driver)
        self.wait_utils = WaitUtils(driver)
        
        # Locators - Shipping Information
        self.first_name = (By.ID, "first-name")
        self.last_name = (By.ID, "last-name")
        self.email = (By.ID, "email")
        self.address = (By.ID, "address")
        self.city = (By.ID, "city")
        self.state = (By.ID, "state")
        self.zip_code = (By.ID, "zip")
        self.country = (By.ID, "country")
        
        # Shipping Methods
        self.shipping_methods = (By.NAME, "shipping-method")
        
        # Payment Information
        self.card_number = (By.ID, "card-number")
        self.card_expiry = (By.ID, "card-expiry")
        self.card_cvv = (By.ID, "card-cvv")
        
        # Continue Buttons
        self.continue_to_shipping = (By.ID, "continue-shipping")
        self.continue_to_payment = (By.ID, "continue-payment")
        self.place_order_button = (By.ID, "place-order")
        
        # Order Summary
        self.order_summary = (By.ID, "order-summary")
        self.order_total = (By.ID, "order-total")
    
    def fill_shipping_information(self, user_data):
        """Fill the shipping information form."""
        self.elements_utils.send_keys(self.first_name, user_data["first_name"])
        self.elements_utils.send_keys(self.last_name, user_data["last_name"])
        self.elements_utils.send_keys(self.email, user_data["email"])
        self.elements_utils.send_keys(self.address, user_data["address"])
        self.elements_utils.send_keys(self.city, user_data["city"])
        self.elements_utils.send_keys(self.state, user_data["state"])
        self.elements_utils.send_keys(self.zip_code, user_data["zip"])
        self.elements_utils.send_keys(self.country, user_data["country"])
        
        self.elements_utils.click_element(self.continue_to_shipping)
        self.wait_utils.wait_for_element_visible(self.shipping_methods)
        logger.info("Filled shipping information form")
        return self
    
    def select_shipping_method(self, shipping_id):
        """Select a shipping method by ID."""
        shipping_method = (By.CSS_SELECTOR, f"input[name='shipping-method'][value='{shipping_id}']")
        self.elements_utils.click_element(shipping_method)
        
        self.elements_utils.click_element(self.continue_to_payment)
        self.wait_utils.wait_for_element_visible(self.card_number)
        logger.info(f"Selected shipping method ID {shipping_id}")
        return self
    
    def fill_payment_information(self, user_data):
        """Fill the payment information form."""
        self.elements_utils.send_keys(self.card_number, user_data["card_number"])
        self.elements_utils.send_keys(self.card_expiry, user_data["card_expiry"])
        self.elements_utils.send_keys(self.card_cvv, user_data["card_cvv"])
        logger.info("Filled payment information form")
        return self
    
    def place_order(self):
        """Place the order and proceed to confirmation."""
        self.elements_utils.click_element(self.place_order_button)
        self.wait_utils.wait_for_url_contains("confirmation")
        logger.info("Placed order successfully")
        return ConfirmationPage(self.driver)
    
    def get_order_total(self):
        """Get the order total from the summary."""
        total_text = self.elements_utils.get_text(self.order_total)
        # Extract numeric value from text
        total = float(''.join(c for c in total_text if c.isdigit() or c == '.'))
        logger.info(f"Order total: {total}")
        return total

class ConfirmationPage:
    def __init__(self, driver):
        self.driver = driver
        self.elements_utils = ElementsUtils(driver)
        self.wait_utils = WaitUtils(driver)
        
        # Locators
        self.confirmation_message = (By.CSS_SELECTOR, ".confirmation-message")
        self.order_number = (By.ID, "order-number")
        self.order_details = (By.ID, "order-details")
    
    def get_order_number(self):
        """Get the order number from confirmation page."""
        order_text = self.elements_utils.get_text(self.order_number)
        # Extract order number using regex
        import re
        match = re.search(r'#(\w+)', order_text)
        order_number = match.group(1) if match else None
        logger.info(f"Order number: {order_number}")
        return order_number
    
    def is_confirmation_displayed(self):
        """Check if confirmation message is displayed."""
        is_displayed = self.elements_utils.is_element_displayed(self.confirmation_message)
        logger.info(f"Confirmation message displayed: {is_displayed}")
        return is_displayed

@pytest.fixture(scope="function")
def driver():
    """Fixture to initialize and quit the WebDriver for each test."""
    driver = initialize_driver(headless=True)
    logger.info("WebDriver initialized")
    yield driver
    quit_driver(driver)
    logger.info("WebDriver closed")

@pytest.fixture(scope="module")
def config():
    """Fixture to load configuration."""
    return load_config()

@allure.feature("E-commerce Checkout")
@allure.story("End-to-End Checkout Process")
@allure.severity(allure.severity_level.CRITICAL)
@measure_performance(metrics)
def test_complete_checkout_flow(driver, config):
    """
    Test the complete checkout flow from product selection to order confirmation.
    
    This test demonstrates the full capabilities of the framework including:
    - Page object pattern
    - Data-driven testing
    - Allure reporting
    - Performance metrics
    - Modular utilities
    """
    try:
        # Initialize a data handler and load test data
        data_handler = DataHandler()
        products = data_handler.load_json_data("products.json")
        shipping_methods = data_handler.load_json_data("shipping.json")
        user_data = data_handler.load_json_data("user.json")
        
        # Step 1: Navigate to the home page and add products to cart
        with allure.step("Navigate to homepage and add products to cart"):
            home_page = HomePage(driver).open()
            
            # Add each product to the cart
            for product in products:
                home_page.add_product_to_cart(product["id"])
            
            # Take a screenshot for the report
            screenshot_path = MiscUtils.take_screenshot(driver, "products_added.png")
            allure.attach.file(screenshot_path, name="Products Added", attachment_type=allure.attachment_type.PNG)
        
        # Step 2: Go to cart and update quantities
        with allure.step("Review cart and update quantities"):
            cart_page = home_page.go_to_cart()
            
            # Update quantities for each product
            for product in products:
                cart_page.update_product_quantity(product["id"], product["quantity"])
            
            # Verify cart total
            expected_total = sum(p["price"] * p["quantity"] for p in products)
            actual_total = cart_page.get_cart_total()
            
            assert abs(actual_total - expected_total) < 0.01, \
                f"Cart total {actual_total} does not match expected {expected_total}"
            
            screenshot_path = MiscUtils.take_screenshot(driver, "cart_updated.png")
            allure.attach.file(screenshot_path, name="Cart Updated", attachment_type=allure.attachment_type.PNG)
        
        # Step 3: Proceed to checkout and fill shipping information
        with allure.step("Proceed to checkout and fill shipping information"):
            checkout_page = cart_page.proceed_to_checkout()
            checkout_page.fill_shipping_information(user_data)
            
            screenshot_path = MiscUtils.take_screenshot(driver, "shipping_info.png")
            allure.attach.file(screenshot_path, name="Shipping Information", attachment_type=allure.attachment_type.PNG)
        
        # Step 4: Select shipping method
        with allure.step("Select shipping method"):
            # Choose Express shipping (ID 2)
            shipping_id = 2
            selected_shipping = next((s for s in shipping_methods if s["id"] == shipping_id), None)
            checkout_page.select_shipping_method(shipping_id)
            
            screenshot_path = MiscUtils.take_screenshot(driver, "shipping_method.png")
            allure.attach.file(screenshot_path, name="Shipping Method Selected", attachment_type=allure.attachment_type.PNG)
        
        # Step 5: Fill payment information and place order
        with allure.step("Fill payment information and place order"):
            checkout_page.fill_payment_information(user_data)
            
            # Verify order total includes shipping
            expected_total = sum(p["price"] * p["quantity"] for p in products) + selected_shipping["price"]
            actual_total = checkout_page.get_order_total()
            
            assert abs(actual_total - expected_total) < 0.01, \
                f"Order total {actual_total} does not match expected {expected_total}"
            
            screenshot_path = MiscUtils.take_screenshot(driver, "payment_info.png")
            allure.attach.file(screenshot_path, name="Payment Information", attachment_type=allure.attachment_type.PNG)
            
            confirmation_page = checkout_page.place_order()
        
        # Step 6: Verify order confirmation
        with allure.step("Verify order confirmation"):
            assert confirmation_page.is_confirmation_displayed(), "Order confirmation message not displayed"
            
            order_number = confirmation_page.get_order_number()
            assert order_number, "Order number should be displayed"
            
            # Log order details for reference
            logger.info(f"Order completed successfully with order number: {order_number}")
            
            screenshot_path = MiscUtils.take_screenshot(driver, "order_confirmation.png")
            allure.attach.file(screenshot_path, name="Order Confirmation", attachment_type=allure.attachment_type.PNG)
        
        # Additional test assertions and validations can be added here
        
    except Exception as e:
        # Log and re-raise the exception
        logger.error(f"Test failed with error: {e}")
        # Take a screenshot on failure
        screenshot_path = MiscUtils.take_screenshot(driver, f"failure_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
        allure.attach.file(screenshot_path, name="Failure Screenshot", attachment_type=allure.attachment_type.PNG)
        raise

# Add more test variations to demonstrate data-driven testing
@allure.feature("E-commerce Checkout")
@allure.story("Different Shipping Methods")
@pytest.mark.parametrize("shipping_id", [1, 2, 3])
@measure_performance(metrics)
def test_different_shipping_methods(driver, shipping_id):
    """Test checkout with different shipping methods."""
    data_handler = DataHandler()
    products = data_handler.load_json_data("products.json")
    shipping_methods = data_handler.load_json_data("shipping.json")
    user_data = data_handler.load_json_data("user.json")
    
    # Get the selected shipping method
    selected_shipping = next((s for s in shipping_methods if s["id"] == shipping_id), None)
    assert selected_shipping, f"Shipping method with ID {shipping_id} not found"
    
    # Log test parameters
    logger.info(f"Testing with shipping method: {selected_shipping['name']}")
    
    # Execute abbreviated test flow focusing on shipping
    home_page = HomePage(driver).open()
    
    # Add just one product to simplify the test
    home_page.add_product_to_cart(products[0]["id"])
    
    cart_page = home_page.go_to_cart()
    checkout_page = cart_page.proceed_to_checkout()
    
    # Fill shipping information
    checkout_page.fill_shipping_information(user_data)
    
    # Select the specified shipping method
    checkout_page.select_shipping_method(shipping_id)
    
    # Verify shipping method affects the total
    product_total = products[0]["price"]
    expected_total = product_total + selected_shipping["price"]
    actual_total = checkout_page.get_order_total()
    
    assert abs(actual_total - expected_total) < 0.01, \
        f"Order total with {selected_shipping['name']} shipping does not match expected total"
    
    logger.info(f"Successfully verified shipping method: {selected_shipping['name']}")

# When all tests complete, save the metrics
def teardown_module(module):
    metrics.finalize_metrics()
    metrics.save_metrics()
    
    # Generate a performance report
    report = metrics.generate_report()
    logger.info(f"Test execution completed. Performance report generated.")
    
    # Try to compare with previous runs
    comparison = metrics.compare_with_history()
    if "error" not in comparison and "warning" not in comparison:
        improvement = comparison["overall_improvement"]["percent_diff"]
        logger.info(f"Performance improvement: {improvement:.2f}% compared to previous runs")