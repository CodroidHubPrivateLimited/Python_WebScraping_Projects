import requests
import pandas as pd
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
    
    # Create directory if it doesn't exist
    os.makedirs(data_folder, exist_ok=True)
    
    url = "https://codroidhub.com/api/testimonials"

    headers = {
    "User-Agent": "Mozilla/5.0"
    }

    try:
        logger.info(f"Making request to: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response content type: {response.headers.get('content-type')}")
        logger.info(f"Response content (first 500 chars): {response.text[:500]}")
        
        # Check if response is successful
        response.raise_for_status()
        
        # Try to parse JSON
        try:
            data = response.json()
        except Exception as json_error:
            logger.info(f"JSON parsing error: {json_error}")
            logger.info(f"Response text: {response.text}")
            # Create empty CSV with headers even on error
            df = pd.DataFrame({
                "id": [],
                "name": [],
                "role": [],
                "company": []
            })
            path = os.path.join(data_folder, "codroidHub_data.csv")
            df.to_csv(path, index=False)
            logger.info("Created empty CSV due to JSON parsing error")
            return "codroidHub_data.csv"
        
        # Check if data has the expected key
        if "testimonials" not in data:
            logger.info(f"Key 'testimonials' not found in response. Keys: {data.keys()}")
            # Create empty CSV with headers
            df = pd.DataFrame({
                "id": [],
                "name": [],
                "role": [],
                "company": []
            })
            path = os.path.join(data_folder, "codroidHub_data.csv")
            df.to_csv(path, index=False)
            logger.info("Created empty CSV due to missing 'testimonials' key")
            return "codroidHub_data.csv"
        
        main_data = data["testimonials"]
        
        logger.info(f"Type of main_data: {type(main_data)}")
        logger.info(f"Number of testimonials: {len(main_data) if isinstance(main_data, list) else 'N/A'}")

        id_list1 = []
        name_list1 = []
        role_list1 = []
        company_list1 = []

        if isinstance(main_data, list):
            for item in main_data:
                # Use _id instead of id since that's what the API returns
                id_list1.append(item.get("_id"))
                name_list1.append(item.get("name"))
                role_list1.append(item.get("role"))
                company_list1.append(item.get("company"))
        else:
            logger.info(f"main_data is not a list: {main_data}")

        df = pd.DataFrame({
            "id": id_list1,
            "name": name_list1,
            "role": role_list1,
            "company": company_list1
        })

        logger.info(f"Data preview: {df.head().to_string()}")
        path = os.path.join(data_folder, "codroidHub_data.csv")
        df.to_csv(path, index=False)
        logger.info(f"CSV saved to: {path}")

        logger.info("CodroidHub scraper done")
        return "codroidHub_data.csv"
        
    except requests.exceptions.RequestException as e:
        logger.info(f"Request error: {e}")
        # Create empty CSV with headers even on network error
        df = pd.DataFrame({
            "id": [],
            "name": [],
            "role": [],
            "company": []
        })
        path = os.path.join(data_folder, "codroidHub_data.csv")
        df.to_csv(path, index=False)
        logger.info("Created empty CSV due to request error")
        return "codroidHub_data.csv"
    
    except Exception as e:
        logger.info(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        # Create empty CSV with headers
        df = pd.DataFrame({
            "id": [],
            "name": [],
            "role": [],
            "company": []
        })
        path = os.path.join(data_folder, "codroidHub_data.csv")
        df.to_csv(path, index=False)
        logger.info("Created empty CSV due to unexpected error")
        return "codroidHub_data.csv"
