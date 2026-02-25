import pandas as pd
from bs4 import BeautifulSoup
import requests
def run():
    url="https://www.flipkart.com/tyy/4io/~cs-yyz0z07a06/pr?sid=tyy%2C4io&collection-tab-name=samsung+S24+5G+SD&pageCriteria=default&param=3838&hpid=H3kVFvfATcBjl0FYDg15tqp7_Hsxr70nj65vMAAFKlc%3D&ctx=eyJjYXJkQ29udGV4dCI6eyJhdHRyaWJ1dGVzIjp7InZhbHVlQ2FsbG91dCI6eyJtdWx0aVZhbHVlZEF0dHJpYnV0ZSI6eyJrZXkiOiJ2YWx1ZUNhbGxvdXQiLCJpbmZlcmVuY2VUeXBlIjoiVkFMVUVfQ0FMTE9VVCIsInZhbHVlcyI6WyJGcm9tIOKCuTQwLDk5OSJdLCJ2YWx1ZVR5cGUiOiJNVUxUSV9WQUxVRUQifX0sImhlcm9QaWQiOnsic2luZ2xlVmFsdWVBdHRyaWJ1dGUiOnsia2V5IjoiaGVyb1BpZCIsImluZmVyZW5jZVR5cGUiOiJQSUQiLCJ2YWx1ZSI6Ik1PQkhEVkZLU1NIUFVZSEIiLCJ2YWx1ZVR5cGUiOiJTSU5HTEVfVkFMVUVEIn19LCJ0aXRsZSI6eyJtdWx0aVZhbHVlZEF0dHJpYnV0ZSI6eyJrZXkiOiJ0aXRsZSIsImluZmVyZW5jZVR5cGUiOiJUSVRMRSIsInZhbHVlcyI6WyJHYWxheHkgUzI0IDVHIl0sInZhbHVlVHlwZSI6Ik1VTFRJX1ZBTFVFRCJ9fX19fQ%3D%3D"
    headers={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
    }
    response=requests.get(url,headers=headers)
    if response.status_code==200:
        print(response)
    soup=BeautifulSoup(response.content,'html.parser')
    print(soup)
    parent_class="lvJbLV col-12-12"
    print(parent_class)
    print(len(parent_class))
    products=soup.findAll("div",class_="lvJbLV col-12-12")
    print(products)
    print(len(products))
    df = pd.DataFrame()
    name_list = []
    price_list = []
    for product in products:
        name=product.find("div",class_="RG5Slk")
        price=product.find("div",class_="hZ3P6w DeU9vF")
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
        path = "data/static_data/flipkart_data.csv"
        df.to_csv(path, index=False)
        print(" Flipkart scraper done")
        return "flipkart_data.csv"