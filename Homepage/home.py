import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


def wait_for_full_load(driver, timeout=15):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def short_wait(driver, seconds=3):
    WebDriverWait(driver, seconds).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def slow_scroll(driver, step=200):
    last_height = driver.execute_script("return document.body.scrollHeight")
    y = 0
    while y < last_height:
        driver.execute_script(f"window.scrollTo(0, {y});")
        y += step
        short_wait(driver, 1)


def slow_scroll_up(driver, step=200):
    y = driver.execute_script("return window.pageYOffset")
    while y > 0:
        scroll_amount = step if y >= step else y
        driver.execute_script(f"window.scrollBy(0, -{scroll_amount});")
        y -= scroll_amount
        short_wait(driver, 1)


def test_home_automation_flow(driver):
    wait = WebDriverWait(driver, 15)

    # Step 1: Navigate to login page
    driver.get("https://node-trial.webnexs.org")
    wait_for_full_load(driver)
    
    # Step 2: Click Sign In
    wait.until(EC.element_to_be_clickable((By.XPATH,"(//button[@type='button'])[2]"))).click()
    time.sleep(5)  # Wait for the modal to appear

    # Step 3: Enter login credentials
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='signinemail']"))).send_keys("ruban.k@webnexs.in")
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='signinpassword']"))).send_keys("program12@12A")
    wait.until(EC.element_to_be_clickable((By.XPATH, "(//button[@type='submit'])"))).click()
    wait_for_full_load(driver)

    # Step 4: Choose profile avatar
    wait.until(EC.element_to_be_clickable((By.XPATH, "(//img[@alt='Avatar'])[1]"))).click()
    wait_for_full_load(driver)

    # Step 5: Select language (English)
    wait.until(EC.element_to_be_clickable((By.XPATH, "(//button[@type='button'])"))).click()
    wait_for_full_load(driver)

    # Step 6: Scroll down and up the home page
    slow_scroll(driver)
    slow_scroll_up(driver)

    # Step 7: Click & back from each section
    section_paths = [
        "(//a[@href='/en/movies'])",
        "(//a[@href='/en/music'])",
        "(//a[@href='/en/show'])",
        "(//a[@href='/en/livestream'])",
        "(//a[@href='/en/videocategories'])",
    ]

    for path in section_paths:
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, path))).click()
            wait_for_full_load(driver)
            print(f"✅ Visited: {path}")
            driver.back()
            wait_for_full_load(driver)
        except Exception as e:
            print(f"❌ Failed to visit {path}: {e}")

    # Step 8: Search bar - 1st search: "retro"
    try:
        search_icon_xpath = "(//*[name()='svg'][@class='theme-text-color'])[1]"
        wait.until(EC.element_to_be_clickable((By.XPATH, search_icon_xpath))).click()

        search_input_xpath = "//input[@placeholder='Search']"
        wait.until(EC.presence_of_element_located((By.XPATH, search_input_xpath))).send_keys("retro")

        driver.execute_script("document.querySelector('form').dispatchEvent(new Event('submit', {bubbles: true}))")
        wait_for_full_load(driver)
        print("🔍 Searched 'retro'")
        driver.back()
        wait_for_full_load(driver)
    except Exception as e:
        print(f"❌ Search 'retro' failed: {e}")

    # Step 9: Search bar - 2nd search: "leo"
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, search_icon_xpath))).click()
        wait.until(EC.presence_of_element_located((By.XPATH, search_input_xpath))).send_keys("leo")
        driver.execute_script("document.querySelector('form').dispatchEvent(new Event('submit', {bubbles: true}))")
        wait_for_full_load(driver)
        print("🔍 Searched 'leo'")
        driver.back()
        wait_for_full_load(driver)
    except Exception as e:
        print(f"❌ Search 'leo' failed: {e}")

    # Step 10: View All navigation and return
    view_all_xpaths = [
        "//a[@href='/featured-videos']",
        "//a[@href='/latest-videos']",
        "//a[@href='/videocategories']",
        "//a[@href='/videocategories/horror']",
        "//a[@href='/videocategories/actionking']",
        "//a[@href='/latest-series']",
        "//a[@href='/series-genre']",
        "//a[@href='/series-categories/action']",
        "//a[@href='/series-categories/drama']",
    ]

    for xpath in view_all_xpaths:
        try:
            print(f"➡️ Navigating to View All: {xpath}")
            element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
            wait_for_full_load(driver)

            # Check if thumbnails are present
            if driver.find_elements(By.XPATH, "//img[contains(@src, 'thumbnail')]"):
                print("✅ Videos found.")
            else:
                print("❌ No videos found.")

            driver.back()
            wait_for_full_load(driver)
        except Exception as e:
            print(f"⚠️ Skipped {xpath}: {e}")
