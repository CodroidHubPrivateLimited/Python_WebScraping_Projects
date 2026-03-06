from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def fetch_data():
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )

    url = "https://www.ajio.com/search/?text=shirts"
    driver.get(url)
    time.sleep(6)

    products = driver.find_elements(By.CLASS_NAME, "item")

    headers = ["Product Name", "Price"]
    rows = []

    for item in products:
        try:
            name = item.find_element(By.CLASS_NAME, "nameCls").text
            price = item.find_element(By.CLASS_NAME, "price").text
            rows.append([name, price])
        except:
            pass

    driver.quit()
    return headers, rows
