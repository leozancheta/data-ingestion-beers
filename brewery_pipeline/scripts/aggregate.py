import pandas as pd
import glob
import os

def aggregate_data():
    files = glob.glob('/opt/airflow/data/silver/state=*.parquet')
    df = pd.concat([pd.read_parquet(file) for file in files])
    result = df.groupby(['state', 'brewery_type']).size().reset_index(name='brewery_count')
    os.makedirs('/opt/airflow/data/gold', exist_ok=True)
    result.to_parquet('/opt/airflow/data/gold/aggregated_breweries.parquet', index=False)