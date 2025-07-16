import pandas as pd
import os

def transform_data():
    os.makedirs('/opt/airflow/data/silver', exist_ok=True)
    df = pd.read_json('/opt/airflow/data/bronze/breweries_raw.json')
    df.dropna(subset=['state', 'brewery_type'], inplace=True)
    for state in df['state'].unique():
        partition = df[df['state'] == state]
        partition.to_parquet(f'/opt/airflow/data/silver/state={state}.parquet', index=False)
if __name__ == "__main__":
    transform_data()