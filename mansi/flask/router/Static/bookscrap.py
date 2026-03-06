import requests
from bs4 import BeautifulSoup

def fetch_data():
    url = "http://books.toscrape.com/"

    headers = {
       "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return ["Error"], [["Failed to fetch data"]]

    soup = BeautifulSoup(response.content, "html.parser")

    products = soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")

    headers = ["Books Name", "Price"]
    rows = []

    for product in products:
        name_tag = product.find("h3")
        price_tag = product.find("p", class_="price_color")

        if name_tag and price_tag:
            rows.append([
                name_tag.get_text(strip=True),
                price_tag.get_text(strip=True)
            ])

    return headers, rows
