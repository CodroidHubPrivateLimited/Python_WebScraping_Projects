from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://blinkit.com/cn/chips-crisps/cid/1237/940")
time.sleep(2)
quotes = driver.find_elements(By.CSS_SELECTOR, "div[role='button']")
for quote in quotes:
    print(quote.text)
    
driver.quit()