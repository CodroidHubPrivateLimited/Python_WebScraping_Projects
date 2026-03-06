import requests
from bs4 import BeautifulSoup

def fetch_data():
    url = "https://www.amazon.in/s?k=chair"
    headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1"
    }

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code != 200:
        return ["Error"], [["Failed to fetch data"]]

    soup = BeautifulSoup(response.text, "html.parser")

    products = soup.find_all("div", {"data-component-type": "s-search-result"})

    headers = ["Chairs Name", "Price"]
    rows = []

    for product in products:
        name_tag = product.h2
        price_tag = product.find("span", class_="a-offscreen")

        if name_tag and price_tag:
            rows.append([
                name_tag.get_text(strip=True),
                price_tag.get_text(strip=True)
            ])

    if not rows:
        rows.append(["No data", "Amazon may have blocked the request"])

    return headers, rows
