import requests
import os
import json
from datetime import datetime

def fetch_and_store_raw_data():
    url = "https://api.openbrewerydb.org/v1/breweries"
    page = 1
    all_data = []
    while True:
        response = requests.get(url, params={"page": page, "per_page": 50})
        data = response.json()
        if not data:
            break
        all_data.extend(data)
        page += 1

    os.makedirs("data/bronze", exist_ok=True)
    file_path = f"data/bronze/breweries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(file_path, "w") as f:
        json.dump(all_data, f)