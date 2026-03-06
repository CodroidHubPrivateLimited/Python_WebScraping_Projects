from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


def fetch_data():
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )

    driver.get("https://www.snapdeal.com/search?keyword=tshirt")
    time.sleep(5)

    products = driver.find_elements(By.CLASS_NAME, "product-tuple-listing")

    headers = ["Name", "Price"]
    rows = []

    for item in products:
        try:
            name = item.find_element(By.CLASS_NAME, "product-title").text
            price = item.find_element(By.CLASS_NAME, "product-price").text
            rows.append([name, price])
        except:
            pass

    driver.quit()
    return headers, rows
