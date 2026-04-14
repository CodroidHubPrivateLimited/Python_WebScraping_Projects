from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
driver2 = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver2.get("https://m.dominos.co.in/jfl-discovery-ui/en/web/menu-v2/6585R?&showSearchModal=false&scrollTo=209")
time.sleep(2)
quotes2 = driver2.find_elements(By.TAG_NAME, "div")
for quote in quotes2:
    print(quote.text)
driver2.quit()


