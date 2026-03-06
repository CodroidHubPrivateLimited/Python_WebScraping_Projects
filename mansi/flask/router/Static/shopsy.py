import requests
from bs4 import BeautifulSoup

def fetch_data():
    url = "https://www.shopsy.in/search?q=mobiles&as=on&as-show=on"

    headers = {
       "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return ["Error"], [["Failed to fetch data"]]

    soup = BeautifulSoup(response.content, "html.parser")

    products = soup.find_all("div",class_="css-175oi2r r-13awgt0 r-18u37iz r-1w6e6rj r-kzbkwu r-ttdzmv")

    headers = [" Name", "Price"]
    rows = []

    for product in products:
        name_tag = product.find("div",class_="sc-c50e187b-0 bkNEtl")
        price_tag = product.find("div",class_="css-146c3p1 r-cqee49 r-1vgyyaa r-1rsjblm r-13hce6t")

        if name_tag and price_tag:
            rows.append([
                name_tag.get_text(strip=True),
                price_tag.get_text(strip=True)
            ])

    return headers, rows
