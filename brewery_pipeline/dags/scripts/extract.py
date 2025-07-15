import requests
import json
import os

def extract_data():
    os.makedirs('/opt/airflow/data/bronze', exist_ok=True)
    url = 'https://api.openbrewerydb.org/breweries'
    page = 1
    all_data = []

    while True:
        response = requests.get(url, params={'page': page, 'per_page': 50})
        if not response.json():
            break
        all_data.extend(response.json())
        page += 1

    with open('/opt/airflow/data/bronze/breweries_raw.json', 'w') as f:
        json.dump(all_data, f)