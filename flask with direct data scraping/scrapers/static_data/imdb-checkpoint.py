import pandas as pd
from bs4 import BeautifulSoup
import requests
def run():
    url="https://static.app/#features"
    headers={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
    }
    response=requests.get(url,headers=headers)
    response.status_code==200
    print(response)
    soup=BeautifulSoup(response.content,'html.parser')
    print(soup)
    parent_class="fix-4-12 toLeft padding-2 equalElement pad rounded"
    print(parent_class)
    print(len(parent_class))
    products=soup.findAll("div",class_="fix-4-12 toLeft padding-2 equalElement pad rounded")
    print(products)
    print(len(products))
    df = pd.DataFrame()
    name_list = []
    price_list = []

    for product in products:
        name=product.find("div",class_="margin-bottom-2")
        price=product.find("p",class_="crop font-size-14 opacity-8")
        if name!=None:
            name=name.get_text()
        if price!=None:
            price=price.get_text()

        if (price!=None) and (name!=None):
            price_list.append(price)
            name_list.append(name)
    df["Name"]=name_list
    df["Price"]=price_list
    print(df)
    path = "data/static_data/imdb_data.csv"
    df.to_csv(path, index=False)
    print(" IMDB scraper done")
    return "imdb_data.csv"