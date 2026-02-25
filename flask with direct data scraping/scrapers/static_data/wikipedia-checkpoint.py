import pandas as pd
from bs4 import BeautifulSoup
import requests
def run():
    url2="https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population"
    headers2={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
    }
    response=requests.get(url2,headers=headers2)
    response.status_code==200
    print(response)
    soup=BeautifulSoup(response.content,'html.parser')
    print(soup)
    products=soup.findAll("div",class_="mw-page-container")
    print(products)
    print(len(products))
    df2 = pd.DataFrame()
    name_list = []
    title_list = []

    for product in products:
        name=product.find("span",class_="mw-page-title-main")
        title=product.find("div",class_="hatnote navigation-not-searchable")
        if name!=None:
            name=name.get_text()
        if title!=None:
            title=title.get_text()

        if (title!=None) and (name!=None):
            title_list.append(title)
            name_list.append(name)
    df2["Name"]=name_list
    df2["title"]=title_list
    print(df2)
    path = "data/static_data/wikipedia_data.csv"
    df2.to_csv(path, index=False)
    print(" Wikipedia scraper done")
    return "wikipedia_data.csv"



