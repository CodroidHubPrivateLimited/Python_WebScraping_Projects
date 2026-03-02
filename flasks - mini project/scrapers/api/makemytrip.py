from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
driver2 = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver2.get("https://www.makemytrip.com/railways/listing?date=20260213&srcStn=NDLS&srcCity=New%20Delhi&destStn=UMB&destCity=Ambala&classCode=SL")
time.sleep(2)
quotes2 = driver2.find_elements(By.TAG_NAME, "div")
for quote in quotes2:
    print(quote.text)
driver2.quit()