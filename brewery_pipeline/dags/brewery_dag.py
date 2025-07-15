from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from scripts.extract import extract_data
from scripts.transform import transform_data
from scripts.aggregate import aggregate_data

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'brewery_pipeline',
    default_args=default_args,
    description='Brewery Medallion Pipeline',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
)

t1 = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag
)

t2 = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag
)

t3 = PythonOperator(
    task_id='aggregate_data',
    python_callable=aggregate_data,
    dag=dag
)

t1 >> t2 >> t3