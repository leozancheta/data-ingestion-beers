import sys
sys.path.append('/opt/airflow')

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.utils.email import send_email
from datetime import datetime, timedelta
from scripts.extract import extract_data
from scripts.transform import transform_data
from scripts.aggregate import aggregate_data
from dataquality.dq_bronze import validate_breweries_json

def failure_alert(context):
    subject = f"Falha na DAG: {context['dag'].dag_id} - Tarefa: {context['task_instance'].task_id}"
    html_content = f"""
    DAG: {context['dag'].dag_id}<br>
    Task: {context['task_instance'].task_id}<br>
    Execution date: {context['execution_date']}<br>
    Log: <a href="{context['task_instance'].log_url}">Ver log</a>
    """
    send_email(to="leozancheta@gmail.com", subject=subject, html_content=html_content)

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'on_failure_callback': failure_alert
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
    task_id='check_bronze_quality',
    python_callable=validate_breweries_json,
    dag=dag
)

t3 = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag
)

t4 = PythonOperator(
    task_id='aggregate_data',
    python_callable=aggregate_data,
    dag=dag
)

t1 >> t2 >> t3 >> t4