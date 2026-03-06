import requests
from bs4 import BeautifulSoup

def fetch_data():
    url = "https://www.scrapingcourse.com/ecommerce/"

    headers = {
       "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return ["Error"], [["Failed to fetch data"]]

    soup = BeautifulSoup(response.content, "html.parser")

    products = soup.find_all("a", class_="woocommerce-LoopProduct-link woocommerce-loop-product__link")

    headers = ["Product Name", "Price"]
    rows = []

    for product in products:
        name_tag = product.find("h2")
        price_tag = product.find("span", class_="price")

        if name_tag and price_tag:
            rows.append([
                name_tag.get_text(strip=True),
                price_tag.get_text(strip=True)
            ])

    return headers, rows
