from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


def fetch_data():
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )

    url = "https://www.meesho.com/search?q=saree"
    driver.get(url)
    time.sleep(6)

    products = driver.find_elements(
        By.CSS_SELECTOR, 'div[class*="ProductListItem__GridCol"]'
    )

    headers = ["Product Name", "Price"]
    rows = []

    for item in products:
        try:
            name = item.find_element(By.TAG_NAME, "p").text
            price = item.find_element(By.TAG_NAME, "h5").text
            rows.append([name, price])
        except:
            pass

    driver.quit()
    return headers, rows
