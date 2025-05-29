import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

def get_scroll_height(driver):
    return driver.execute_script("return document.body.scrollHeight")

def slow_scroll(driver, step=100, pause=0.5):
    wait_for_full_load(driver)
    time.sleep(2)
    last_height = get_scroll_height(driver)
    current_y = 0
    while current_y < last_height:
        driver.execute_script(f"window.scrollTo(0, {current_y});")
        print(f"🔽 Scrolling down to {current_y}px")
        time.sleep(pause)
        new_height = get_scroll_height(driver)
        if new_height > last_height:
            last_height = new_height
        current_y += step

def slow_scroll_up(driver, step=100, pause=0.5):
    wait_for_full_load(driver)
    current_y = driver.execute_script("return window.pageYOffset")
    while current_y > 0:
        scroll_amount = step if current_y >= step else current_y
        driver.execute_script(f"window.scrollBy(0, -{scroll_amount});")
        current_y -= scroll_amount
        print(f"🔼 Scrolling up to {current_y}px")
        time.sleep(pause)

def test_homepage_scroll_and_viewall(driver):
    wait = WebDriverWait(driver, 15)

    # Step 1: Go to login page
    driver.get("https://node-trial.webnexs.org/tr")
    wait_for_full_load(driver)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Sign In']]"))).click()

    # Step 2: Login
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='signinemail']"))).send_keys("ruban.k@webnexs.in")
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='signinpassword']"))).send_keys("program12@12A")
    wait.until(EC.element_to_be_clickable((By.XPATH, "(//button[@type='submit'])"))).click()
    wait_for_full_load(driver)
    time.sleep(5)

    # Step 3: Choose profile
    wait.until(EC.element_to_be_clickable((By.XPATH, "(//img[@alt='Avatar'])[1]"))).click()
    wait_for_full_load(driver)
    time.sleep(4)

    # Step 4: Full scroll down and up
    print(" Performing full scroll to load thumbnails...")
    slow_scroll(driver, step=200, pause=0.5)
    slow_scroll_up(driver, step=200, pause=0.8)

    # Step 5: Check if thumbnails are loaded
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//img[contains(@src, 'thumbnail')]")))
        print("✅ Thumbnails loaded.")
    except:
        print("❌ Thumbnails not found.")

    # Step 6: Click each View All and verify videos
    view_all_xpaths = [
        "(//a[@href='/tr/featured-videos'])[2]",
        "//a[@href='/tr/latest-videos'][2]",
        "//a[@href='/tr/videocategories'][2]",
        "//a[@href='/tr/videocategories/horror'][2]",
        "//a[@href='/tr/videocategories/actionking'][2]",
        "//a[@href='/tr/latest-series'][2]",
        "//a[@href='/tr/series-genre'][2]",
        "//a[@href='/tr/series-categories/action'][2]",
        "//a[@href='/tr/series-categories/drama'][2]",
    ]

    for xpath in view_all_xpaths:
        try:
            print(f"➡️ Opening: {xpath}")
            element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(2)
            element.click()
            wait_for_full_load(driver)
            time.sleep(2)

            videos = driver.find_elements(By.XPATH, "//img[contains(@src, 'thumbnail')]")
            print("✅ Videos found." if videos else "❌ No videos found.")

            driver.get("https://node-trial.webnexs.org/home")
            wait_for_full_load(driver)
            time.sleep(0.5)

            videos = driver.find_elements(By.XPATH, "//img[contains(@src, 'thumbnail')]")
            print("✅ Videos found." if videos else "❌ No videos found.")

            driver.get("https://node-trial.webnexs.org/home")
            wait_for_full_load(driver)
            time.sleep(0.5)

            videos = driver.find_elements(By.XPATH, "//img[contains(@src, 'thumbnail')]")
            print("✅ Videos found." if videos else "❌ No videos found.")

            driver.get("https://node-trial.webnexs.org/home")
            wait_for_full_load(driver)
            time.sleep(0.5)

        except Exception as e:
            print(f"⚠️ Could not process {xpath} - {e}")

    # Step 7: Search bar - enter 'retro' then 'ruban'
    try:
        print("🔍 Clicking search icon...")
        search_icon = wait.until(EC.element_to_be_clickable((By.XPATH, "//svg[contains(@class, 'theme-text-color')]")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", search_icon)
        time.sleep(2)
        search_icon.click()
        time.sleep(2)

        search_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search']")))

        # Search for "retro"
        search_input.send_keys("retro")
        search_input.send_keys(Keys.ENTER)
        print("🔎 Searched: retro")
        time.sleep(3)

        # Clear input and search "ruban"
        search_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search']")))
        search_input.clear()
        search_input.send_keys("ruban")
        search_input.send_keys(Keys.ENTER)
        print("🔎 Searched: ruban")
        time.sleep(3)

    except Exception as e:
        print(f"❌ Search failed: {e}")
