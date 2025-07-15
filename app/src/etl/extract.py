import requests
import os
from datetime import datetime
from pyspark.sql import SparkSession

def fetch_and_store_raw_data():
    url = "https://api.openbrewerydb.org/breweries"
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
    file_path = f"data/bronze/breweries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"

    spark = SparkSession.builder.getOrCreate()
    df = spark.createDataFrame(all_data)
    df.write.mode("overwrite").parquet(file_path)