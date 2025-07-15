from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from src.etl.extract import fetch_and_store_raw_data
from src.etl.transform import transform_to_silver, aggregate_to_gold

with DAG(
    'brewery_pipeline',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',
    catchup=False,
    retries=1,
    retry_delay=timedelta(minutes=5),
) as dag:

    fetch_raw = PythonOperator(
        task_id='fetch_raw_data',
        python_callable=fetch_and_store_raw_data,
    )

    silver = PythonOperator(
        task_id='transform_to_silver',
        python_callable=transform_to_silver,
    )

    gold = PythonOperator(
        task_id='aggregate_to_gold',
        python_callable=aggregate_to_gold,
    )

    fetch_raw >> silver >> gold