import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger()

def run():
    # Get the absolute path to the data folder - go up to project root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_folder = os.path.join(base_dir, "data", "api_data")
    
    os.makedirs(data_folder, exist_ok=True)
    
    url="https://gyansetu.codroidhub.com/api/feedbacks"
    headers={
    "User Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers = headers)
    logger.info(f"Response status code: {response.status_code}")
    logger.info(f"Response content: {response.content[:500]}")
    data=response.json()
    logger.info(f"Response type: {type(data)}")
    logger.info(f"Data: {data}")
    main_data=data[0]
    main_data.keys()
    id_data=main_data["_id"]
    logger.info(f"ID data length: {len(id_data)}")
    name_list = []
    unique_id_list = []

    for id in id_data:
    # print(saif)
        name_list.append(id[0])
        unique_id_list.append(id[0])
    
    df = pd.DataFrame({
        "Name": name_list,
        "Unique_Id": unique_id_list
    })
    logger.info(f"Data preview: {df.head().to_string()}")
    path = os.path.join(data_folder, "gyansetu_data.csv")
    df.to_csv(path, index=False)
    logger.info("Gyansetu scraper done")
    return "gyansetu_data.csv"
