import pandas as pd
import requests
from bs4 import BeautifulSoup
def run():

    url="https://puirf.codroidhub.com/api/api/v1/instruments/user/getHomeFacilities"
    headers={
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36" 
    }
    response = requests.get(url, headers = headers)
    print(response)
    print(response.content)
    data = response.json()
    print(data["data"])
    main_data= data["data"]
    print(main_data.keys())
    saif_data = main_data["saif"]
    print(len(saif_data))
    cil_data = main_data["cil"]
    name_list = []
    unique_id_list = []

    for saif in saif_data:
    # print(saif)
        name_list.append(saif["name"])
        unique_id_list.append(saif["uniqueId"])
    
    df = pd.DataFrame({
        "Name": name_list,
        "Unique_Id": unique_id_list
    })
    print(df)
    path = "data/static_data/codroidHub_data.csv"
    df.to_csv(path, index=False)

    print(" codroidHub scraper done")
    return "codroidHub_data.csv"
