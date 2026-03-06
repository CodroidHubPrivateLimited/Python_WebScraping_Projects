from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


def fetch_data():
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )

    driver.get("https://blinkit.com/cn/appliances/cid/1379/1886")
    time.sleep(6)

    elements = driver.find_elements(By.CSS_SELECTOR, "div[role='button']")

    rows = []

    for element in elements:
        text = element.text.strip()
        if text:
            rows.append([text])   

    driver.quit()

    headers = ["Product Info"]
    return headers, rows
