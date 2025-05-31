import pytest
import allure
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


@pytest.mark.usefixtures("browser_setup")
class TestAuthFlow:
    driver = webdriver.Firefox
 

    def test_login(self):
        email = "ruban.k@webnexs.in"
        valid_password = "program12@12A"
        invalid_passwords = ["wrong1", "wrong2", "wrong3"]

        # Open homepage and click Sign In button
        self.driver.get("https://node-trial.webnexs.org/")
        sign_in_button = (By.XPATH, "//button[.//span[text()='Sign In' and contains(@class,'d-none d-sm-inline')]]")
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(sign_in_button)).click()

        email_input = (By.XPATH, "(//input[@id='signinemail'])")
        password_input = (By.XPATH, "(//input[@id='signinpassword'])")
        login_button = (By.XPATH, "(//button[@type='submit'])")

        # 3 invalid login attempts
        for idx, wrong_pwd in enumerate(invalid_passwords):
            print(f"❌ Attempt {idx + 1} with wrong password: {wrong_pwd}")
            try:
                WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(email_input))
                self.driver.find_element(*email_input).clear()
                self.driver.find_element(*email_input).send_keys(email)
                self.driver.find_element(*password_input).clear()
                self.driver.find_element(*password_input).send_keys(wrong_pwd)
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(login_button)).click()

                # Wait to see if login failed by waiting for email input again
                WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(email_input))
                assert "dashboard" not in self.driver.current_url.lower(), "Login succeeded with wrong password"
                print("✅ Login failed as expected")
            except TimeoutException:
                print("⚠️ Login form not found again, reopening sign-in...")
                self.driver.get("https://node-trial.webnexs.org/")
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(sign_in_button)).click()

        # Valid login
        print("✅ Attempting valid login...")
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(email_input))
        self.driver.find_element(*email_input).clear()
        self.driver.find_element(*email_input).send_keys(email)
        self.driver.find_element(*password_input).clear()
        self.driver.find_element(*password_input).send_keys(valid_password)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(login_button)).click()

        WebDriverWait(self.driver, 10).until(
            lambda d: "dashboard" in d.current_url.lower() or "choose-profile" in d.current_url.lower()
        )
        assert "dashboard" in self.driver.current_url.lower() or "choose-profile" in self.driver.current_url.lower()
        print("🎉 Valid login successful")

        time.sleep(5)

        # Forgot password flow
        print("🔁 Starting forgot password flow...")
        self.driver.get("https://node-trial.webnexs.org/verify/forget")

        forgot_email_input = (By.XPATH, "(//input[@type='email'])")
        submit_button = (By.XPATH, "(//button[@type='submit'])")

        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(forgot_email_input))
        self.driver.find_element(*forgot_email_input).clear()
        self.driver.find_element(*forgot_email_input).send_keys(email)

        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(submit_button)).click()
        time.sleep(2)

        page_source = self.driver.page_source.lower()
        assert "sent" in page_source or "email" in page_source, "❌ Forgot password request failed"
        print("✅ Forgot password flow successful")
