import pandas as pd
from bs4 import BeautifulSoup
import requests
def run():
    url="https://books.toscrape.com/"
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
    }
    response = requests.get(url,headers= headers)
    print(response.status_code)
    if response.status_code == 200:
        print("request successfull")
    else:
        print("error in statues code:", response.status_code)
    response
    soup = BeautifulSoup(response.content,"html.parser")
    parent_class="col-xs-6 col-sm-4 col-md-3 col-lg-3"
    products = soup.find_all("li", class_= parent_class)
    print(len(products))
    name_list =[]
    price_list = []
    for product in products:
        name= product.find("h3").find("a")
        price_tag = product.find("p", class_="price_color")
        if(name !=None):
            name = name.get_text()
            name_list.append(name)
            price = price_tag.get_text()
            price_list.append(price)
        print(name,price)
    df=pd.DataFrame({
        "book_name":name_list,
        "price_list":price_list
    })
    print(df)
    path = "data/static_data/booktoscrape_data.csv"
    df.to_csv(path, index=False)

    print(" booktoscrape scraper done")
    return "booktoscrape_data.csv"