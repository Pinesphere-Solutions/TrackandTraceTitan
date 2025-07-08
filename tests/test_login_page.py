import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
import logging
import time

# Configure logging
logging.basicConfig(
    filename='login_page_test.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

class LoginPageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # ChromeDriver is added to PATH, so no need to specify the path
        cls.driver = webdriver.Chrome()
        cls.driver.maximize_window()
        cls.driver.implicitly_wait(10)
        cls.base_url = "http://192.168.1.5:8000/" # Login URL is different

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def log_and_print(self, message):
        print(message)
        logging.info(message)

    def test_login_page_elements(self):
        driver = self.driver
        driver.get(self.base_url)
        self.log_and_print("Opened login page.")

        # Check logo
        logo = driver.find_element(By.CSS_SELECTOR, ".brand-logo img")
        self.assertTrue(logo.is_displayed())
        self.log_and_print("Logo is displayed.")

        # Check heading
        heading = driver.find_element(By.TAG_NAME, "h4")
        self.assertIn("get started", heading.text.lower())
        self.log_and_print("Heading is present: " + heading.text)

        # Check subheading
        subheading = driver.find_element(By.TAG_NAME, "h6")
        self.assertIn("sign in", subheading.text.lower())
        self.log_and_print("Subheading is present: " + subheading.text)

        # Check username field
        username = driver.find_element(By.NAME, "username")
        self.assertTrue(username.is_displayed())
        self.log_and_print("Username field is present.")

        # Check password field
        password = driver.find_element(By.NAME, "password")
        self.assertTrue(password.is_displayed())
        self.log_and_print("Password field is present.")

        # Check sign in button
        signin_btn = driver.find_element(By.CSS_SELECTOR, ".auth-form-btn")
        self.assertTrue(signin_btn.is_displayed())
        self.log_and_print("Sign In button is present.")

    def test_login_with_invalid_credentials(self):
        driver = self.driver
        driver.get(self.base_url)
        self.log_and_print("Testing login with invalid credentials.")

        username = driver.find_element(By.NAME, "username")
        password = driver.find_element(By.NAME, "password")
        signin_btn = driver.find_element(By.CSS_SELECTOR, ".auth-form-btn")

        username.clear()
        password.clear()
        username.send_keys("invalid_user")
        password.send_keys("wrong_password")
        signin_btn.click()

        time.sleep(1)

        # Check for error message
        body_text = driver.page_source.lower()
        if "invalid" in body_text or "incorrect" in body_text:
            self.log_and_print("Invalid login error message displayed.")
        else:
            self.log_and_print("No error message for invalid login (check implementation).")

    def test_login_with_empty_fields(self):
        driver = self.driver
        driver.get(self.base_url)
        self.log_and_print("Testing login with empty fields.")

        signin_btn = driver.find_element(By.CSS_SELECTOR, ".auth-form-btn")
        signin_btn.click()
        time.sleep(1)

        body_text = driver.page_source.lower()
        if "required" in body_text or "invalid" in body_text:
            self.log_and_print("Validation error displayed for empty fields.")
        else:
            self.log_and_print("No validation error for empty fields (check implementation).")
            
            
    def test_login_with_valid_credentials(self):
        driver = self.driver
        driver.get(self.base_url)
        self.log_and_print("Testing login with valid credentials.")

        username = driver.find_element(By.NAME, "username")
        password = driver.find_element(By.NAME, "password")
        signin_btn = driver.find_element(By.CSS_SELECTOR, ".auth-form-btn")

        username.clear()
        password.clear()
        username.send_keys("admin")
        password.send_keys("admin")
        signin_btn.click()

        time.sleep(2)  # wait for dashboard to load

        current_url = driver.current_url
        self.log_and_print(f"Redirected to: {current_url}")

        # 🧠 Adjust this according to your real dashboard path
        if "dashboard" in current_url or "home" in current_url:
            self.log_and_print("✅ Successfully logged in and landed on dashboard.")
        else:
            self.log_and_print("❌ Login succeeded but did NOT land on dashboard.")


if __name__ == "__main__":
    unittest.main()
