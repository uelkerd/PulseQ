# pulseq/page_objects/login_page.py
from selenium.webdriver.common.by import By

from pulseq.utilities.retry import retry


class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.username_field = (By.ID, "username")
        self.password_field = (By.ID, "password")
        self.login_button = (By.ID, "loginBtn")

    def enter_username(self, username):
        self.driver.find_element(*self.username_field).send_keys(username)

    def enter_password(self, password):
        self.driver.find_element(*self.password_field).send_keys(password)

    def click_login(self):
        self.driver.find_element(*self.login_button).click()

    @retry(max_attempts=3, delay=1, backoff=2)
    def login(self, username, password):
        """Login with retry mechanism for increased reliability."""
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()
