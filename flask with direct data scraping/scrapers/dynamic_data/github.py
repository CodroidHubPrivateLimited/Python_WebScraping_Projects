import pandas as pd
from bs4 import BeautifulSoup
import requests
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
    
    # Create directory if it doesn't exist
    os.makedirs(data_folder, exist_ok=True)
    
    url="https://api.github.com/users/torvalds/repos"
    headers = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"}
    response = requests.get(url,headers= headers)
    logger.info(f"Response status code: {response.status_code}")
    data = response.json()
    main_data= data
    logger.info(f"Number of repos: {len(main_data)}")  
    name_list = []
    id_list = []
    full_name_list = []
    for main in main_data:
        name_list.append(main["name"])
        id_list.append(main["id"])
        full_name_list.append(main["full_name"])
    df = pd.DataFrame({
        "Name": name_list,
        "id": id_list,
        "full_name":full_name_list,
    })
    logger.info(f"Data preview: {df.head().to_string()}")
    path = os.path.join(data_folder, "github_data.csv")
    df.to_csv(path, index=False)

    logger.info("Github scraper done")
    return "github_data.csv"
