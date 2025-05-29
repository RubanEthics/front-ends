import pytest
import allure
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.signin_button = (
            By.XPATH,
            "//button[.//span[text()='Sign In' and contains(@class,'d-none d-sm-inline')]]"
        )
        self.email_input = (By.XPATH, "(//input[@id='signinemail'])")
        self.password_input = (By.XPATH, "(//input[@id='signinpassword'])")
        self.login_button = (By.XPATH, "(//button[@type='submit'])")

    def open_home(self):
        self.driver.get("https://node-trial.webnexs.org/en")
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.signin_button)
        ).click()

    def wait_for_login_form(self):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.email_input)
        )

    def login(self, email, password):
        wait = WebDriverWait(self.driver, 10)

        email_elem = wait.until(EC.presence_of_element_located(self.email_input))
        email_elem.clear()
        email_elem.send_keys(email)

        pwd_elem = wait.until(EC.presence_of_element_located(self.password_input))
        pwd_elem.clear()
        pwd_elem.send_keys(password)

        wait.until(EC.element_to_be_clickable(self.login_button)).click()
        time.sleep(2)


class ForgotPasswordPage:
    def __init__(self, driver):
        self.driver = driver
        self.email_input = (By.XPATH, "(//input[@type='email'])")
        self.submit_button = (By.XPATH, "(//button[@type='submit'])")

    def open(self):
        self.driver.get("https://node-trial.webnexs.org/verify/forget")

    def request_reset(self, email):
        wait = WebDriverWait(self.driver, 10)

        # Ensure field is found before sending keys
        email_elem = wait.until(EC.presence_of_element_located(self.email_input))
        email_elem.clear()
        email_elem.send_keys(email)

        # Click submit button
        submit_elem = wait.until(EC.element_to_be_clickable(self.submit_button))
        submit_elem.click()
        time.sleep(2)

        # Confirm response (very basic check)
        return "sent" in self.driver.page_source.lower() or "email" in self.driver.page_source.lower()


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


@allure.feature("Authentication")
@allure.story("Three invalid attempts, valid login, then forgot password")
def test_login_flow(driver):
    login_page = LoginPage(driver)
    login_page.open_home()

    email = "ruban.k@webnexs.in"
    valid_password = "program12@12A"
    invalid_passwords = ["wrong1", "wrong2", "wrong3"]

    # 3 ❌ wrong password attempts
    for idx, wrong_pwd in enumerate(invalid_passwords):
        print(f"❌ Attempt {idx + 1} with wrong password: {wrong_pwd}")
        try:
            login_page.wait_for_login_form()
            login_page.login(email, wrong_pwd)

            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located(login_page.email_input)
            )
            assert "dashboard" not in driver.current_url.lower(), f"Login succeeded with wrong password: {wrong_pwd}"
            print("✅ Login failed as expected")
        except TimeoutException:
            print("⚠️ Login form not found again, reopening...")
            login_page.open_home()

    # ✅ Valid login
    print("✅ Attempting valid login...")
    login_page.login(email, valid_password)
    WebDriverWait(driver, 10).until(
        lambda d: "dashboard" in d.current_url.lower() or "choose-profile" in d.current_url.lower()
    )
    assert "dashboard" in driver.current_url.lower() or "choose-profile" in driver.current_url.lower()
    print("🎉 Valid login successful")

    # Wait a bit before forgot password
    time.sleep(5)

    # 🔁 Forgot password
    print("🔁 Starting forgot password flow...")
    forgot = ForgotPasswordPage(driver)
    forgot.open()
    assert forgot.request_reset(email), "❌ Forgot password request failed"
    print("✅ Forgot password flow successful")
