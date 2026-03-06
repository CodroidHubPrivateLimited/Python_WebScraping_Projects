import requests
from bs4 import BeautifulSoup

def fetch_data():
    url = "https://www.flipkart.com/all/~cs-6ef68bc8d283b86730515a8f2c87ff23/pr?sid=0pm,fcn,821,a7x,2si&marketplace=FLIPKART&restrictLocale=true"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return ["Error"], [["Failed to fetch data"]]

    soup = BeautifulSoup(response.content, "html.parser")

    products = soup.find_all("div", class_="RGLWAk")

    headers = ["Product Name", "Price"]
    rows = []

    for product in products:
        name_tag = product.find("a", class_="pIpigb")
        price_tag = product.find("div", class_="hZ3P6w")

        if name_tag and price_tag:
            rows.append([
                name_tag.get_text(strip=True),
                price_tag.get_text(strip=True)
            ])

    return headers, rows
