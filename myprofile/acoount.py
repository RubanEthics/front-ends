import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

class MyProfilePage:
    def __init__(self, driver):
        self.driver = driver
        self.email = "ruban.k@webnexs.in"
        self.password = "program12@12A"
        self.login_url = "https://node-trial.webnexs.org/en"

        # Locators
        self.signin_button = (By.XPATH, "//button[.//span[text()='Sign In' and contains(@class,'d-none d-sm-inline')]]")
        self.email_input = (By.XPATH, "(//input[@id='signinemail'])")
        self.password_input = (By.XPATH, "(//input[@id='signinpassword'])")
        self.login_button = (By.XPATH, "(//button[@type='submit'])")
        self.avatar_select = (By.XPATH, "(//img[@alt='Avatar'])[1]")
        self.profile_icon = (By.XPATH, "(//img[@alt='RT'])")  # update alt if needed
        self.my_profile_link = (By.XPATH, "//a[@href='/myprofile/info']")
        self.first_name_input = (By.XPATH, "(//input[@name='name'])")
        self.last_name_input = (By.XPATH, "(//input[@name='last_name'])")
        self.gender_dropdown = (By.NAME, "gender")
        self.submit_button = (By.XPATH, "(//span[@class=' '])")
        self.profile_image_input = (By.CSS_SELECTOR, "input.profileInput[type='file']")

    def wait_and_click(self, locator):
        element = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable(locator)
        )
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(1)
            element.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", element)
        return element

    def login_and_go_to_profile(self):
        self.driver.get(self.login_url)
        wait = WebDriverWait(self.driver, 15)

        # Click main "Sign In" button before login fields appear
        self.wait_and_click(self.signin_button)

        wait.until(EC.visibility_of_element_located(self.email_input)).send_keys(self.email)
        self.driver.find_element(*self.password_input).send_keys(self.password)
        self.driver.find_element(*self.login_button).click()

        self.wait_and_click(self.avatar_select)
        time.sleep(2)

        self.wait_and_click(self.profile_icon)
        self.wait_and_click(self.my_profile_link)

    def update_profile(self, first_name, last_name, gender):
        wait = WebDriverWait(self.driver, 15)

        fname = wait.until(EC.visibility_of_element_located(self.first_name_input))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", fname)
        fname.clear()
        fname.send_keys(first_name)

        lname = self.driver.find_element(*self.last_name_input)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", lname)
        lname.clear()
        lname.send_keys(last_name)

        gender_dropdown = wait.until(EC.element_to_be_clickable(self.gender_dropdown))
        Select(gender_dropdown).select_by_visible_text(gender.capitalize())

        submit_btn = wait.until(EC.element_to_be_clickable(self.submit_button))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        submit_btn.click()
        time.sleep(2)

    def upload_profile_image(self, image_path):
        full_path = os.path.abspath(image_path)
        file_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.profile_image_input)
        )
        file_input.send_keys(full_path)
        time.sleep(2)

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

def test_update_my_profile(driver):
    page = MyProfilePage(driver)
    try:
        page.login_and_go_to_profile()
        page.upload_profile_image("/home/webnexs/Desktop/front-end /profile img.jpeg")
        page.update_profile("RubanEdit", "Tester", "male")
        time.sleep(3)
        assert "myprofile" in driver.current_url.lower()
    except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
        driver.save_screenshot("failure_screenshot.png")
        print("Test failed:", str(e))
        raise
