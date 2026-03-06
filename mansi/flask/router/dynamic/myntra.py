from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


def fetch_data():
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )
    driver.get("https://www.myntra.com/shoes")
    time.sleep(2)

    products = driver.find_elements(By.CLASS_NAME, "product-base")

    data = []

    for item in products:
        try:
            brand = item.find_element(By.CLASS_NAME, "product-brand").text
            name = item.find_element(By.CLASS_NAME, "product-product").text
            price = item.find_element(By.CLASS_NAME, "product-price").text

            data.append([brand, name, price])
        except:
            pass

    driver.quit()

    headers = ["Brand", "Product", "Price"]
    return headers, data