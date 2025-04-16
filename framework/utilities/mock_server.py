# framework/utilities/mock_server.py
import http.server
import socketserver
import threading
import os
import time
from pathlib import Path

class MockServer:
    """A simple HTTP server for testing purposes."""
    
    def __init__(self, port=8000, mock_dir="test_mock"):
        """Initialize the mock server.
        
        Args:
            port: Port number to run the server on
            mock_dir: Directory containing mock HTML files
        """
        self.port = port
        self.mock_dir = mock_dir
        self.server = None
        self.server_thread = None
        
        # Create mock directory if it doesn't exist
        Path(mock_dir).mkdir(exist_ok=True)
        
        # Create basic mock files if they don't exist
        self._create_default_mocks()
    
    def _create_default_mocks(self):
        """Create default mock HTML files if they don't exist."""
        login_html = """
        <!DOCTYPE html>
        <html>
        <head><title>Login Page</title></head>
        <body>
            <h1>Login Form</h1>
            <form id="loginForm">
                <input id="username" type="text" placeholder="Username">
                <input id="password" type="password" placeholder="Password">
                <button id="loginBtn" type="submit">Login</button>
            </form>
            <script>
                document.getElementById('loginForm').addEventListener('submit', function(e) {
                    e.preventDefault();
                    const username = document.getElementById('username').value;
                    if (username === 'testuser' || username === 'testuser1' || username === 'testuser2') {
                        window.location.href = '/dashboard.html';
                    } else {
                        alert('Invalid credentials');
                    }
                });
            </script>
        </body>
        </html>
        """
        
        dashboard_html = """
        <!DOCTYPE html>
        <html>
        <head><title>Dashboard</title></head>
        <body>
            <h1>Welcome to Dashboard</h1>
            <div>You are successfully logged in!</div>
        </body>
        </html>
        """
        
        home_html = """
        <!DOCTYPE html>
        <html>
        <head><title>Home Page</title></head>
        <body>
            <h1>Product Catalog</h1>
            <div class="products">
                <div class="product-card" data-product-id="1">
                    <h3>Product 1</h3>
                    <p>$19.99</p>
                    <button class="add-to-cart-btn">Add to Cart</button>
                </div>
                <div class="product-card" data-product-id="2">
                    <h3>Product 2</h3>
                    <p>$29.99</p>
                    <button class="add-to-cart-btn">Add to Cart</button>
                </div>
                <div class="product-card" data-product-id="3">
                    <h3>Product 3</h3>
                    <p>$39.99</p>
                    <button class="add-to-cart-btn">Add to Cart</button>
                </div>
            </div>
            <a href="/cart.html" id="view-cart">View Cart</a>
        </body>
        </html>
        """
        
        # Write the files if they don't exist
        self._write_mock_file("login.html", login_html)
        self._write_mock_file("dashboard.html", dashboard_html)
        self._write_mock_file("index.html", home_html)
    
    def _write_mock_file(self, filename, content):
        """Write content to a mock file if it doesn't exist."""
        file_path = os.path.join(self.mock_dir, filename)
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(content)
    
    def start(self):
        """Start the mock server in a separate thread."""
        handler = http.server.SimpleHTTPRequestHandler
        
        # Change to the mock directory
        os.chdir(self.mock_dir)
        
        self.server = socketserver.TCPServer(("", self.port), handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Give the server a moment to start
        time.sleep(1)
        
        return f"http://localhost:{self.port}"
    
    def stop(self):
        """Stop the mock server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            # Change back to the original directory
            os.chdir("..")