import time
import pytest
import allure
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SignUpPage:
    def __init__(self, driver):
        self.driver = driver
        # Instead of (//button[@type='button'])[3], find button with span text 'Sign Up'
        self.open_signup_button = (
            By.XPATH,
            "//button[.//span[text()='Sign Up' and contains(@class,'d-none d-sm-inline')]]"
        )
        self.first_name_input = (By.XPATH, "//input[@id='username']")
        self.last_name_input = (By.XPATH, "//input[@id='lastname']")
        self.email_input = (By.XPATH, "//input[@name='email']")
        self.country_select = (By.XPATH, "//div[@role='button']")
        self.mobile_input = (By.XPATH, "//input[@type='tel']")
        self.password_input = (By.XPATH, "//input[@id='signuppassword']")
        self.confirm_password_input = (By.XPATH, "//input[@name='confirmPassword']")
        self.checkbox = (By.XPATH, "//input[@type='checkbox']")
        self.submit_button = (By.XPATH, "//button[@type='submit']")

    def open(self, url):
        print(f"Opening URL: {url}")
        self.driver.get(url)
        wait = WebDriverWait(self.driver, 30)
        print("Waiting for Sign Up button to appear...")
        signup_btn = wait.until(EC.element_to_be_clickable(self.open_signup_button))
        print("Sign Up button found, clicking it...")
        signup_btn.click()

    def fill_form(self, first_name, last_name, email, mobile, password, confirm_password):
        wait = WebDriverWait(self.driver, 30)

        print("Filling First Name...")
        wait.until(EC.visibility_of_element_located(self.first_name_input)).send_keys(first_name)

        print("Filling Last Name...")
        wait.until(EC.visibility_of_element_located(self.last_name_input)).send_keys(last_name)

        print("Filling Email...")
        wait.until(EC.visibility_of_element_located(self.email_input)).send_keys(email)

        print("Opening country dropdown...")
        wait.until(EC.element_to_be_clickable(self.country_select)).click()

        india_option_xpath = "//span[@class='country-name' and text()='India']"
        print("Waiting for India option in country list...")
        india_option = wait.until(EC.presence_of_element_located((By.XPATH, india_option_xpath)))

        print("Scrolling India option into view...")
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", india_option)
        print("Clicking India option...")
        wait.until(EC.element_to_be_clickable((By.XPATH, india_option_xpath))).click()
        print("India selected")

        print("Filling Mobile...")
        wait.until(EC.visibility_of_element_located(self.mobile_input)).send_keys(mobile)

        print("Filling Password...")
        wait.until(EC.visibility_of_element_located(self.password_input)).send_keys(password)

        print("Filling Confirm Password...")
        wait.until(EC.visibility_of_element_located(self.confirm_password_input)).send_keys(confirm_password)

        checkbox_element = wait.until(EC.presence_of_element_located(self.checkbox))
        print("Scrolling checkbox into view...")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_element)
        print("Clicking checkbox...")
        wait.until(EC.element_to_be_clickable(self.checkbox)).click()
        print("Checkbox clicked")

    def submit(self):
        wait = WebDriverWait(self.driver, 30)
        print("Waiting for Submit button to be clickable...")
        wait.until(EC.element_to_be_clickable(self.submit_button)).click()
        print("Submit button clicked")


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


@allure.feature("Sign Up")
@allure.story("Valid Sign Up")
def test_user_can_signup(driver):
    page = SignUpPage(driver)
    page.open("https://node-trial.webnexs.org/en")

    page.fill_form(
        first_name="Ruban",
        last_name="Test",
        email="ruban1234578@example.com",  # Change for unique emails
        mobile="9876543210",
        password="Password@123",
        confirm_password="Password@123"
    )
    page.submit()

    WebDriverWait(driver, 30).until(
        lambda d: "dashboard" in d.current_url.lower() or "success" in d.page_source.lower()
    )

    assert "dashboard" in driver.current_url.lower() or "success" in driver.page_source.lower(), \
        "Signup failed or success page not loaded."
