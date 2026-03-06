import requests
from bs4 import BeautifulSoup

def fetch_data():
    url = "https://automationexercise.com/brand_products/Polo"

    headers = {
       "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return ["Error"], [["Failed to fetch data"]]

    soup = BeautifulSoup(response.content, "html.parser")

    products = soup.find_all("div",class_="productinfo text-center")
    headers = [" Name", "Price"]
    rows = []

    for product in products:
        name_tag = product.find("p")
        price_tag = product.find("h2")

        if name_tag and price_tag:
            rows.append([
                name_tag.get_text(strip=True),
                price_tag.get_text(strip=True)
            ])

    return headers, rows
