import time
from urllib.parse import quote_plus

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils import create_driver
from blinkit import _has_location_gate


def _switch_to_latest_tab(driver):
    handles = driver.window_handles
    if len(handles) > 1:
        driver.switch_to.window(handles[-1])


def open_product_amazon(product: str, headless: bool = False, keep_open: bool = True) -> dict:
    driver = create_driver(headless=headless)
    try:
        search_url = f"https://www.amazon.in/s?k={quote_plus(product)}"
        driver.get(search_url)

        wait = WebDriverWait(driver, 10)
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
            )
        )

        results = driver.find_elements(
            By.CSS_SELECTOR, "div[data-component-type='s-search-result'] h2 a"
        )
        if not results:
            return {"success": False, "message": "Amazon: No search results found.", "store": "Amazon", "driver": driver}

        results[0].click()
        _switch_to_latest_tab(driver)
        return {"success": True, "message": "Amazon: Product page opened.", "store": "Amazon", "driver": driver}
    except Exception as e:
        return {"success": False, "message": f"Amazon: Failed to open product page ({e}).", "store": "Amazon", "driver": driver}
    finally:
        if not keep_open:
            driver.quit()


def open_product_myntra(product: str, headless: bool = False, keep_open: bool = True) -> dict:
    driver = create_driver(headless=headless)
    try:
        search_url = f"https://www.myntra.com/{quote_plus(product)}"
        driver.get(search_url)

        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.product-base")))

        products = driver.find_elements(By.CSS_SELECTOR, "li.product-base a")
        if not products:
            return {"success": False, "message": "Myntra: No search results found.", "store": "Myntra", "driver": driver}

        products[0].click()
        _switch_to_latest_tab(driver)
        return {"success": True, "message": "Myntra: Product page opened.", "store": "Myntra", "driver": driver}
    except Exception as e:
        return {"success": False, "message": f"Myntra: Failed to open product page ({e}).", "store": "Myntra", "driver": driver}
    finally:
        if not keep_open:
            driver.quit()


def open_product_blinkit(product: str, headless: bool = False, keep_open: bool = True) -> dict:
    driver = create_driver(headless=headless)
    try:
        driver.get("https://blinkit.com/")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2)

        if _has_location_gate(driver):
            return {
                "success": False,
                "message": "Blinkit: Please set your location/login in the opened browser, then re-run.",
                "store": "Blinkit",
                "driver": driver,
            }

        search_url = f"https://blinkit.com/s/?q={quote_plus(product)}"
        driver.get(search_url)
        time.sleep(2)
        return {"success": True, "message": "Blinkit: Search results opened.", "store": "Blinkit", "driver": driver}
    except Exception as e:
        return {"success": False, "message": f"Blinkit: Failed to open search results ({e}).", "store": "Blinkit", "driver": driver}
    finally:
        if not keep_open:
            driver.quit()


def open_product_meesho(product: str, headless: bool = False, keep_open: bool = True) -> dict:
    driver = create_driver(headless=headless)
    try:
        search_url = f"https://www.meesho.com/search?q={quote_plus(product)}"
        driver.get(search_url)

        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2)

        results = driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/']")
        if not results:
            return {"success": False, "message": "Meesho: No search results found.", "store": "Meesho", "driver": driver}

        results[0].click()
        _switch_to_latest_tab(driver)
        return {"success": True, "message": "Meesho: Product page opened.", "store": "Meesho", "driver": driver}
    except Exception as e:
        return {"success": False, "message": f"Meesho: Failed to open product page ({e}).", "store": "Meesho", "driver": driver}
    finally:
        if not keep_open:
            driver.quit()


def open_product_page(store: str, product: str, headless: bool = False, keep_open: bool = True) -> dict:
    store_key = (store or "").strip().lower()
    if store_key == "amazon":
        return open_product_amazon(product, headless=headless, keep_open=keep_open)
    if store_key == "myntra":
        return open_product_myntra(product, headless=headless, keep_open=keep_open)
    if store_key == "blinkit":
        return open_product_blinkit(product, headless=headless, keep_open=keep_open)
    if store_key == "meesho":
        return open_product_meesho(product, headless=headless, keep_open=keep_open)

    return {"success": False, "message": f"Open product not supported for {store}.", "store": store, "driver": None}
