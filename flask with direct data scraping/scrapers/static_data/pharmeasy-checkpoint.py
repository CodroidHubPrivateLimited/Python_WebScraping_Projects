import pandas as pd
from bs4 import BeautifulSoup
import requests
def run():
    url7="https://pharmeasy.in/health-care/sports-nutrition-12931"
    header7={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
    }
    response7=requests.get(url7,headers=header7)
# print(response6)
    response7.status_code==200
# print(response6)
    soup7=BeautifulSoup(response7.content,'html.parser')
# print(soup6)
    parent_class7="ProductCard_productCard__ftHIX"
    print(parent_class7)
# print(len(parent_class6))
    products7=soup7.find_all("div",class_="ProductCard_productCard__ftHIX")
# print(products6)
    print(len(products7))
    df7 = pd.DataFrame()
    name_list7 = []
    price_list7 = []

    for product in products7:
        name=product.find("div",class_="ProductCard_productName__nWQ3x")
        price=product.find("div",class_="ProductCard_priceContainer__99QdN ProductCard_otcListingPriceContainer__PXAT_")
        if name!=None:
            name=name.get_text()
        if price!=None:
            price=price.get_text()

        if (price!=None) and (name!=None):
            price_list7.append(price)
            name_list7.append(name)
    df7["Name"]=name_list7
    df7["Price"]=price_list7
    df7
    path = "data/static_data/pharmeasy_data.csv"
    df7.to_csv(path, index=False)
    print(" Pharmeasy scraper done")
    return "pharmeasy_data.csv"