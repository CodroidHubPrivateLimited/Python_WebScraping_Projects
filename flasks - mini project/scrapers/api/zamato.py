from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
driver2 = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver2.get("https://www.zomato.com/chandigarh/restaurants")
time.sleep(2)
quotes2 = driver2.find_elements(By.TAG_NAME, "a")
for quote in quotes2:
    print(quote.text)
driver2.quit()