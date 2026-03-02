from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://m.dominos.co.in/jfl-discovery-ui/en/web/menu-v2/6585R?&showSearchModal=false&scrollTo=209")
time.sleep(2)
quotes = driver.find_elements(By.TAG_NAME, "div")
for quote in quotes:
    print(quote.text)
driver.quit()
