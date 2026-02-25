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
    
    url="https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"
    headers = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"}
    response = requests.get(url,headers= headers)
    logger.info(f"CoinGecko API response status: {response.status_code}")
    data = response.json()
    main_data= data
    logger.info(f"Data keys: {main_data[0].keys()}")
    name_list = []
    id_list = []
    symbol_list = []
    for main in main_data:
        name_list.append(main["name"])
        id_list.append(main["id"])
        symbol_list.append(main["symbol"])
    
    df = pd.DataFrame({
        "Name": name_list,
        "id": id_list,
        "symbol":symbol_list
    })
    logger.info(f"CoinGecko data preview: {df.head().to_string()}")
    
    path = os.path.join(data_folder, "coingeckoh_data.csv")
    df.to_csv(path, index=False)

    logger.info("Coingecko API scraper done")
    return "coingeckoh_data.csv"
