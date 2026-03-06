import requests

def fetch_data():
    url = "https://dummyjson.com/products"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return ["Error"], [["Failed to fetch data"]]

    data = response.json()
    products = data.get("products", [])

    headers = [
        "ID",
        "Title",
        "Price",
        "Discount %",
        "Rating",
        "Stock"
    ]

    rows = []
    for p in products:
        rows.append([
            p.get("id"),
            p.get("title"),
            p.get("price"),
            p.get("discountPercentage"),
            p.get("rating"),
            p.get("stock")
        ])

    return headers, rows
