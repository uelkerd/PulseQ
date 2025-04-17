# tests/test_e2e_checkout.py

import json
import os
import tempfile
from datetime import datetime

import allure
import pytest
from selenium.webdriver.common.by import By

from pulseq.config import load_config
from pulseq.page_objects.login_page import LoginPage
from pulseq.utilities.data_handler import DataHandler
from pulseq.utilities.driver_manager import initialize_driver, quit_driver
from pulseq.utilities.elements_utils import ElementsUtils
from pulseq.utilities.logger import setup_logger
from pulseq.utilities.misc_utils import MiscUtils
from pulseq.utilities.performance_metrics import PerformanceMetrics, measure_performance
from pulseq.utilities.wait_utils import WaitUtils

# Set up logger
logger = setup_logger("test_e2e_checkout")

# Initialize performance metrics
metrics = PerformanceMetrics()

# Create or ensure test data directory exists
os.makedirs("test_data", exist_ok=True)

# Test data - we'll use a more complex data structure for this test
PRODUCTS = [
    {"id": 1, "name": "Laptop", "price": 999.99, "quantity": 1},
    {"id": 2, "name": "Smartphone", "price": 499.99, "quantity": 2},
    {"id": 3, "name": "Headphones", "price": 129.99, "quantity": 1},
]

SHIPPING_METHODS = [
    {"id": 1, "name": "Standard", "price": 5.99, "days": "3-5"},
    {"id": 2, "name": "Express", "price": 15.99, "days": "1-2"},
    {"id": 3, "name": "Next Day", "price": 29.99, "days": "1"},
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
    "card_cvv": "123",
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
    """Home page object containing product listing and cart functionality."""

    def __init__(self, driver):
        self.driver = driver
        self.elements_utils = ElementsUtils(driver)
        self.wait_utils = WaitUtils(driver)

        # Locators
        self.product_cards = (By.CSS_SELECTOR, ".product-card")
        self.add_to_cart_buttons = (By.CSS_SELECTOR, ".add-to-cart-btn")
        self.cart_icon = (By.ID, "cart-icon")
        self.cart_count = (By.CSS_SELECTOR, ".cart-count")

    def open(self, base_url):
        """Navigate to the home page."""
        self.driver.get(base_url + "index.html")
        self.wait_utils.wait_for_element_visible((By.TAG_NAME, "h1"))
        logger.info("Opened home page")
        return self

    def add_product_to_cart(self, product_id):
        """Add a product to the cart by its ID."""
        product_selector = (
            By.CSS_SELECTOR,
            f".product-card[data-product-id='{product_id}']",
        )

        # First wait for the element to be present before scrolling
        self.wait_utils.wait_for_element_visible(product_selector)

        # Now scroll to the element
        self.elements_utils.scroll_to_element(product_selector)

        # Find the add to cart button within this product card
        add_button = self.driver.find_element(*product_selector).find_element(
            By.CSS_SELECTOR, ".add-to-cart-btn"
        )
        self.elements_utils.click_element(add_button)
        logger.info(f"Added product {product_id} to cart")

    def go_to_cart(self):
        """Navigate to the cart page."""
        self.elements_utils.click_element(self.cart_icon)
        self.wait_utils.wait_for_title_contains("Shopping Cart")
        logger.info("Navigated to cart page")
        return CartPage(self.driver)


class CartPage:
    """Cart page object for managing shopping cart."""

    def __init__(self, driver):
        self.driver = driver
        self.elements_utils = ElementsUtils(driver)
        self.wait_utils = WaitUtils(driver)

        # Locators
        self.cart_items = (By.CSS_SELECTOR, ".cart-item")
        self.quantity_inputs = (By.CSS_SELECTOR, ".item-quantity")
        self.update_cart_button = (By.ID, "update-cart")
        self.checkout_button = (By.ID, "checkout-button")
        self.cart_total = (By.ID, "cart-total")

    def update_product_quantity(self, product_id, quantity):
        """Update the quantity of a product in the cart."""
        item_selector = (
            By.CSS_SELECTOR,
            f".cart-item[data-product-id='{product_id}']",
        )
        quantity_input = self.driver.find_element(*item_selector).find_element(
            By.CSS_SELECTOR, ".item-quantity"
        )
        self.elements_utils.fill_input(quantity_input, str(quantity))
        self.elements_utils.click_element(self.update_cart_button)
        logger.info(f"Updated quantity for product {product_id} to {quantity}")

    def get_cart_total(self):
        """Get the current cart total as a float."""
        total_text = self.elements_utils.get_text(self.cart_total)
        return float(total_text.replace("$", "").strip())

    def proceed_to_checkout(self):
        """Navigate to the checkout page."""
        self.elements_utils.click_element(self.checkout_button)
        self.wait_utils.wait_for_title_contains("Checkout")
        logger.info("Proceeded to checkout page")
        return CheckoutPage(self.driver)


class CheckoutPage:
    """Checkout page object for completing the purchase."""

    def __init__(self, driver):
        self.driver = driver
        self.elements_utils = ElementsUtils(driver)
        self.wait_utils = WaitUtils(driver)

        # Locators
        self.shipping_form = {
            "first_name": (By.ID, "first-name"),
            "last_name": (By.ID, "last-name"),
            "email": (By.ID, "email"),
            "address": (By.ID, "address"),
            "city": (By.ID, "city"),
            "state": (By.ID, "state"),
            "zip": (By.ID, "zip"),
            "country": (By.ID, "country"),
        }
        self.continue_shipping_button = (By.ID, "continue-shipping")
        self.shipping_method_form = (By.ID, "shipping-method-form")
        self.shipping_methods = {
            1: (By.ID, "shipping-1"),
            2: (By.ID, "shipping-2"),
            3: (By.ID, "shipping-3"),
        }
        self.continue_payment_button = (By.ID, "continue-payment")
        self.payment_form = {
            "card_number": (By.ID, "card-number"),
            "card_expiry": (By.ID, "card-expiry"),
            "card_cvv": (By.ID, "card-cvv"),
        }
        self.place_order_button = (By.ID, "place-order")
        self.order_total = (By.ID, "order-total")

    def fill_shipping_information(self, user_data):
        """Fill out the shipping information form."""
        for field, locator in self.shipping_form.items():
            if field in user_data:
                self.elements_utils.fill_input(locator, user_data[field])
        self.elements_utils.click_element(self.continue_shipping_button)
        self.wait_utils.wait_for_element_visible(self.shipping_methods[1])
        logger.info("Filled shipping information")

    def select_shipping_method(self, shipping_id):
        """Select a shipping method by ID."""
        self.wait_utils.wait_for_element_visible(self.shipping_method_form)
        shipping_radio = self.shipping_methods.get(shipping_id)
        if not shipping_radio:
            raise ValueError(f"Invalid shipping method ID: {shipping_id}")
        self.elements_utils.click_element(shipping_radio)
        self.elements_utils.click_element(self.continue_payment_button)
        self.wait_utils.wait_for_element_visible(self.payment_form["card_number"])
        logger.info(f"Selected shipping method {shipping_id}")

    def fill_payment_information(self, payment_data):
        """Fill out the payment information form."""
        for field, locator in self.payment_form.items():
            if field in payment_data:
                self.elements_utils.fill_input(locator, payment_data[field])
        logger.info("Filled payment information")

    def get_order_total(self):
        """Get the current order total as a float."""
        total_text = self.elements_utils.get_text(self.order_total)
        return float(total_text.replace("$", "").strip())

    def place_order(self):
        """Place the order and navigate to confirmation page."""
        self.elements_utils.click_element(self.place_order_button)
        self.wait_utils.wait_for_title_contains("Confirmation")
        logger.info("Placed order")
        return ConfirmationPage(self.driver)


class ConfirmationPage:
    """Order confirmation page object."""

    def __init__(self, driver):
        self.driver = driver
        self.elements_utils = ElementsUtils(driver)

        # Locators
        self.confirmation_message = (By.CLASS_NAME, "confirmation-message")
        self.order_number = (By.ID, "order-number")
        self.order_details = (By.CLASS_NAME, "order-details")

    def get_order_number(self):
        """Get the order number from the confirmation page."""
        return self.elements_utils.get_text(self.order_number)

    def is_confirmation_displayed(self):
        """Check if the confirmation message is displayed."""
        is_displayed = self.elements_utils.is_element_present(self.confirmation_message)
        logger.info(f"Confirmation message displayed: {is_displayed}")
        return is_displayed


@pytest.fixture(scope="function")
def driver():
    """Initialize and quit the WebDriver for each test."""
    driver = initialize_driver(headless=True)
    logger.info("WebDriver initialized")
    yield driver
    quit_driver(driver)
    logger.info("WebDriver closed")


@pytest.fixture(scope="function")
def mock_ecommerce_site():
    """Create temporary HTML files for the e-commerce site testing."""
    # Create home page with products
    home_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test E-commerce Store</title>
        <style>
            .product-card { border: 1px solid #ccc; margin: 10px; padding: 10px; }
            .cart-count { background: red; color: white; padding: 2px 5px; border-radius: 50%; }
        </style>
    </head>
    <body>
        <h1>Test E-commerce Store</h1>
        <div id="cart-icon">Cart <span class="cart-count">0</span></div>
        
        <div class="products">
            <div class="product-card" data-product-id="1">
                <h3>Laptop</h3>
                <p>$999.99</p>
                <button class="add-to-cart-btn">Add to Cart</button>
            </div>
            <div class="product-card" data-product-id="2">
                <h3>Smartphone</h3>
                <p>$499.99</p>
                <button class="add-to-cart-btn">Add to Cart</button>
            </div>
            <div class="product-card" data-product-id="3">
                <h3>Headphones</h3>
                <p>$129.99</p>
                <button class="add-to-cart-btn">Add to Cart</button>
            </div>
        </div>
        
        <script>
            let cart = [];
            
            document.querySelectorAll('.add-to-cart-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const productCard = this.closest('.product-card');
                    const productId = productCard.dataset.productId;
                    cart.push(productId);
                    document.querySelector('.cart-count').textContent = cart.length;
                });
            });
            
            document.getElementById('cart-icon').addEventListener('click', function() {
                window.location.href = 'cart.html';
            });
        </script>
    </body>
    </html>
    """

    # Create cart page
    cart_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Shopping Cart</title>
        <style>
            .cart-item { border: 1px solid #ccc; margin: 10px; padding: 10px; }
        </style>
    </head>
    <body>
        <h1>Shopping Cart</h1>
        <div class="cart-items">
            <div class="cart-item" data-product-id="1">
                <h3>Laptop</h3>
                <p>$999.99</p>
                <input type="number" class="item-quantity" value="1" min="1">
                <div class="item-total">$999.99</div>
            </div>
            <div class="cart-item" data-product-id="2">
                <h3>Smartphone</h3>
                <p>$499.99</p>
                <input type="number" class="item-quantity" value="2" min="1">
                <div class="item-total">$999.98</div>
            </div>
            <div class="cart-item" data-product-id="3">
                <h3>Headphones</h3>
                <p>$129.99</p>
                <input type="number" class="item-quantity" value="1" min="1">
                <div class="item-total">$129.99</div>
            </div>
        </div>
        
        <div id="cart-total">$2129.96</div>
        <button id="update-cart">Update Cart</button>
        <button id="checkout-button">Proceed to Checkout</button>
        
        <script>
            document.getElementById('checkout-button').addEventListener('click', function() {
                window.location.href = 'checkout.html';
            });
            
            document.getElementById('update-cart').addEventListener('click', function() {
                // Just for demo purposes
                const quantities = document.querySelectorAll('.item-quantity');
                quantities.forEach(input => {
                    const cartItem = input.closest('.cart-item');
                    cartItem.querySelector('.item-total').textContent = '$' + 
                        (parseFloat(cartItem.querySelector('p').textContent.substring(1)) * input.value).toFixed(2);
                });
                // Recalculate total (simplified)
                document.getElementById('cart-total').textContent = '$' + 
                    Array.from(document.querySelectorAll('.item-total'))
                        .reduce((sum, el) => sum + parseFloat(el.textContent.substring(1)), 0)
                        .toFixed(2);
            });
        </script>
    </body>
    </html>
    """

    # Create checkout page
    checkout_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Checkout</title>
    </head>
    <body>
        <h1>Checkout</h1>
        
        <div id="shipping-form">
            <h2>Shipping Information</h2>
            <input type="text" id="first-name" placeholder="First Name">
            <input type="text" id="last-name" placeholder="Last Name">
            <input type="email" id="email" placeholder="Email">
            <input type="text" id="address" placeholder="Address">
            <input type="text" id="city" placeholder="City">
            <input type="text" id="state" placeholder="State">
            <input type="text" id="zip" placeholder="ZIP Code">
            <input type="text" id="country" placeholder="Country">
            <button id="continue-shipping">Continue to Shipping Method</button>
        </div>
        
        <div id="shipping-method-form" style="display:none;">
            <h2>Shipping Method</h2>
            <div>
                <input type="radio" name="shipping-method" value="1" id="shipping-1">
                <label for="shipping-1">Standard ($5.99) - 3-5 days</label>
            </div>
            <div>
                <input type="radio" name="shipping-method" value="2" id="shipping-2">
                <label for="shipping-2">Express ($15.99) - 1-2 days</label>
            </div>
            <div>
                <input type="radio" name="shipping-method" value="3" id="shipping-3">
                <label for="shipping-3">Next Day ($29.99) - 1 day</label>
            </div>
            <button id="continue-payment">Continue to Payment</button>
        </div>
        
        <div id="payment-form" style="display:none;">
            <h2>Payment Information</h2>
            <input type="text" id="card-number" placeholder="Card Number">
            <input type="text" id="card-expiry" placeholder="MM/YY">
            <input type="text" id="card-cvv" placeholder="CVV">
            <button id="place-order">Place Order</button>
        </div>
        
        <div id="order-summary">
            <h2>Order Summary</h2>
            <div>Laptop - $999.99</div>
            <div>Smartphone (x2) - $999.98</div>
            <div>Headphones - $129.99</div>
            <div>Shipping - <span id="shipping-cost">$0.00</span></div>
            <div>Total: <span id="order-total">$2129.96</span></div>
        </div>
        
        <script>
            document.getElementById('continue-shipping').addEventListener('click', function() {
                document.getElementById('shipping-form').style.display = 'none';
                document.getElementById('shipping-method-form').style.display = 'block';
            });
            
            document.querySelectorAll('input[name="shipping-method"]').forEach(radio => {
                radio.addEventListener('change', function() {
                    let cost = 0;
                    if (this.value === '1') cost = 5.99;
                    else if (this.value === '2') cost = 15.99;
                    else if (this.value === '3') cost = 29.99;
                    
                    document.getElementById('shipping-cost').textContent = '$' + cost.toFixed(2);
                    
                    // Update total
                    const subtotal = 2129.96;
                    document.getElementById('order-total').textContent = '$' + (subtotal + cost).toFixed(2);
                });
            });
            
            document.getElementById('continue-payment').addEventListener('click', function() {
                document.getElementById('shipping-method-form').style.display = 'none';
                document.getElementById('payment-form').style.display = 'block';
            });
            
            document.getElementById('place-order').addEventListener('click', function() {
                window.location.href = 'confirmation.html';
            });
        </script>
    </body>
    </html>
    """

    # Create confirmation page
    confirmation_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Order Confirmation</title>
    </head>
    <body>
        <h1>Order Confirmation</h1>
        <div class="confirmation-message">
            <p>Thank you for your order!</p>
            <p>Your order number is: <span id="order-number">ORD-12345-XYZ</span></p>
        </div>
        <div class="order-details">
            <h2>Order Details</h2>
            <p>Total: $2145.95</p>
            <p>Shipping: Express (1-2 business days)</p>
        </div>
    </body>
    </html>
    """

    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # Create files
    home_path = os.path.join(temp_dir, "index.html")
    with open(home_path, "w") as f:
        f.write(home_content)

    cart_path = os.path.join(temp_dir, "cart.html")
    with open(cart_path, "w") as f:
        f.write(cart_content)

    checkout_path = os.path.join(temp_dir, "checkout.html")
    with open(checkout_path, "w") as f:
        f.write(checkout_content)

    confirmation_path = os.path.join(temp_dir, "confirmation.html")
    with open(confirmation_path, "w") as f:
        f.write(confirmation_content)

    # Return the base URL
    yield "file://" + temp_dir + "/"

    # Clean up
    for file in ["index.html", "cart.html", "checkout.html", "confirmation.html"]:
        os.remove(os.path.join(temp_dir, file))
    os.rmdir(temp_dir)


@allure.feature("E-commerce Checkout")
@allure.story("Complete Checkout Flow")
@measure_performance(metrics)
def test_complete_checkout_flow(driver, mock_ecommerce_site, config):
    """
    Test the complete checkout flow from adding products to cart to order confirmation.
    This is a critical end-to-end test that validates the entire purchase flow.
    """
    # Load test data
    data_handler = DataHandler()
    products = data_handler.load_json_data("products.json")
    user_data = data_handler.load_json_data("user.json")

    # Step 1: Navigate to home page and add products
    home_page = HomePage(driver).open(mock_ecommerce_site)

    # Add each product to cart
    for product in products:
        home_page.add_product_to_cart(product["id"])

    # Step 2: Go to cart
    cart_page = home_page.go_to_cart()

    # Update quantities if needed
    for product in products:
        if "quantity" in product and product["quantity"] > 1:
            cart_page.update_product_quantity(product["id"], product["quantity"])

    # Step 3: Proceed to checkout
    checkout_page = cart_page.proceed_to_checkout()

    # Fill shipping information
    checkout_page.fill_shipping_information(user_data)

    # Select shipping method (using Express shipping)
    checkout_page.select_shipping_method(2)  # ID 2 is Express shipping

    # Fill payment information
    checkout_page.fill_payment_information(user_data)

    # Place order
    confirmation_page = checkout_page.place_order()

    # Verify order confirmation
    assert (
        confirmation_page.is_confirmation_displayed()
    ), "Order confirmation should be displayed"

    # Get and verify order number format
    order_number = confirmation_page.get_order_number()
    assert order_number.startswith("ORD-"), "Invalid order number format"

    logger.info(f"Order completed successfully with number: {order_number}")


@allure.feature("E-commerce Checkout")
@allure.story("Different Shipping Methods")
@pytest.mark.parametrize("shipping_id", [1, 2, 3])
@measure_performance(metrics)
def test_different_shipping_methods(driver, mock_ecommerce_site, shipping_id):
    """
    Test checkout process with different shipping methods.
    Verifies that each shipping method can be selected and affects the total price correctly.
    """
    # Load test data
    data_handler = DataHandler()
    products = data_handler.load_json_data("products.json")
    user_data = data_handler.load_json_data("user.json")

    # Add a single product to cart for simplicity
    home_page = HomePage(driver).open(mock_ecommerce_site)
    home_page.add_product_to_cart(products[0]["id"])

    # Proceed through checkout
    cart_page = home_page.go_to_cart()
    checkout_page = cart_page.proceed_to_checkout()

    # Fill shipping information
    checkout_page.fill_shipping_information(user_data)

    # Select the specified shipping method
    checkout_page.select_shipping_method(shipping_id)

    # Verify shipping cost is added to total
    shipping_costs = {1: 5.99, 2: 15.99, 3: 29.99}
    expected_total = products[0]["price"] + shipping_costs[shipping_id]
    actual_total = checkout_page.get_order_total()

    assert abs(actual_total - expected_total) < 0.01, (
        f"Order total ${actual_total} does not match "
        f"expected ${expected_total} for shipping method {shipping_id}"
    )

    logger.info(f"Successfully verified shipping method {shipping_id}")


def teardown_module(module):
    """Save test metrics and generate performance report."""
    metrics.save_metrics()
    metrics_path = metrics.get_metrics_path()
    logger.info(f"Test metrics saved to {metrics_path}")
