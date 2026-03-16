from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import StaleElementReferenceException
import pandas as pd
import time

def scrape():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.naukri.com/it-jobs?src=gnbjobs_homepage_srch")

    time.sleep(5)

    text_data = []
    image_data = []
    link_data = []

    # -------- TEXT SCRAPE --------
    elements = driver.find_elements(By.XPATH, "//*")

    for el in elements:
        try:
            text = el.text.strip()
            if text != "":
                text_data.append(text)
        except StaleElementReferenceException:
            continue

    # -------- IMAGE SCRAPE --------
    images = driver.find_elements(By.TAG_NAME, "img")

    for img in images:
        try:
            src = img.get_attribute("src")
            if src:
                image_data.append(src)
        except StaleElementReferenceException:
            continue

    # -------- LINK SCRAPE --------
    links = driver.find_elements(By.TAG_NAME, "a")

    for link in links:
        try:
            href = link.get_attribute("href")
            if href:
                link_data.append(href)
        except StaleElementReferenceException:
            continue

    driver.quit()

    # -------- TABLE --------
    max_len = max(len(text_data), len(image_data), len(link_data))

    text_data.extend([""] * (max_len - len(text_data)))
    image_data.extend([""] * (max_len - len(image_data)))
    link_data.extend([""] * (max_len - len(link_data)))

    df = pd.DataFrame({
        "TEXT": text_data,
        "IMAGE": image_data,
        "LINK": link_data
    })

    print(df)
    df.to_csv("naukri_scraped_data.csv", index=False, encoding="utf-8")

    print("CSV file successfully created!")
    return df.to_dict('records')
