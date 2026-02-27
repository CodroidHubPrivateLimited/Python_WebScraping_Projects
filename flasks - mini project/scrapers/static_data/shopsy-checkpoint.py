import pandas as pd
from bs4 import BeautifulSoup
import requests
def run():
    url3="https://www.shopsy.in/search?q=mobiles&as=on&as-show=on"
    header3={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
    }
    response3=requests.get(url3,headers=header3)
    response3.status_code==200
    soup3=BeautifulSoup(response3.content,'html.parser')
    parent_class3="css-175oi2r r-13awgt0 r-18u37iz r-1w6e6rj r-kzbkwu r-ttdzmv"
    print(parent_class3)
    products3=soup3.find_all("div",class_="css-175oi2r r-13awgt0 r-18u37iz r-1w6e6rj r-kzbkwu r-ttdzmv")
    print(len(products3))
    df7 = pd.DataFrame()
    name_list3 = []
    price_list3 = []

    for product in products3:
        name=product.find("div",class_="sc-c50e187b-0 bkNEtl")
        price=product.find("div",class_="css-146c3p1 r-cqee49 r-1vgyyaa r-1rsjblm r-13hce6t")
        if name!=None:
            name=name.get_text()
        if price!=None:
            price=price.get_text()

        if (price!=None) and (name!=None):
            price_list3.append(price)
            name_list3.append(name)
    df7["Name"]=name_list3
    df7["Price"]=price_list3
    df7
    path = "data/static_data/shopsy_data.csv"
    df7.to_csv(path, index=False)
    print(" Shopsy scraper done")
    return "shopsy_data.csv"