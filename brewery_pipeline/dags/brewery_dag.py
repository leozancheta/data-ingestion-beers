import sys
import logging
import traceback
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

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def failure_alert(context):
    """Função de alerta para falhas com múltiplas estratégias"""
    
    task_instance = context['task_instance']
    dag_id = context['dag'].dag_id
    task_id = task_instance.task_id
    execution_date = context['execution_date']
    
    # 1. Log detalhado no Airflow
    error_message = f"""
    ❌ FALHA NA DAG DETECTADA ❌
    
    📋 Detalhes:
    - DAG: {dag_id}
    - Task: {task_id} 
    - Data de Execução: {execution_date}
    - Log URL: {task_instance.log_url}
    
    🔍 Para ver detalhes completos:
    1. Acesse http://localhost:8080
    2. Vá para DAGs > {dag_id}
    3. Clique na task {task_id}
    4. Veja os logs completos
    """
    
    logger.error(error_message)
    print(error_message)  # Para aparecer nos logs do container
    
    # 2. Tentar enviar email (se configurado)
    try:
        subject = f"🚨 Falha na DAG: {dag_id} - Task: {task_id}"
        html_content = f"""
        <h2>🚨 Falha Detectada no Pipeline de Dados</h2>
        
        <h3>📋 Informações da Falha:</h3>
        <ul>
            <li><strong>DAG:</strong> {dag_id}</li>
            <li><strong>Task:</strong> {task_id}</li>
            <li><strong>Data/Hora:</strong> {execution_date}</li>
            <li><strong>Status:</strong> FAILED ❌</li>
        </ul>
        
        <h3>🔗 Links Úteis:</h3>
        <ul>
            <li><a href="http://localhost:8080">Interface do Airflow</a></li>
            <li><a href="{task_instance.log_url}">Ver Log Detalhado</a></li>
        </ul>
        
        <h3>📝 Próximos Passos:</h3>
        <ol>
            <li>Verifique os logs detalhados</li>
            <li>Identifique a causa do erro</li>
            <li>Corrija o problema</li>
            <li>Re-execute a task se necessário</li>
        </ol>
        
        <p><em>Este email foi gerado automaticamente pelo sistema de monitoramento do Airflow.</em></p>
        """
        
        send_email(
            to=["leozancheta@gmail.com"], 
            subject=subject, 
            html_content=html_content
        )
        logger.info("✅ Email de notificação enviado com sucesso")
        
    except Exception as email_error:
        logger.warning(f"⚠️ Falha ao enviar email: {str(email_error)}")
        
        # 3. Fallback: Salvar notificação em arquivo
        try:
            notification_file = f"/opt/airflow/data/failure_notifications_{datetime.now().strftime('%Y%m%d')}.log"
            with open(notification_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"TIMESTAMP: {datetime.now()}\n")
                f.write(error_message)
                f.write(f"EMAIL_ERROR: {str(email_error)}\n")
                f.write(f"{'='*50}\n")
            
            logger.info(f"📝 Notificação salva em arquivo: {notification_file}")
            
        except Exception as file_error:
            logger.error(f"❌ Falha ao salvar notificação em arquivo: {str(file_error)}")

def success_callback(context):
    """Callback para sucesso da task"""
    task_instance = context['task_instance']
    logger.info(f"✅ Task {task_instance.task_id} executada com sucesso!")

def validate_breweries_with_path():
    """Wrapper para validação com caminho fixo"""
    return validate_breweries_json('/opt/airflow/data/bronze/breweries_raw.json')

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'on_failure_callback': failure_alert,
    'on_success_callback': success_callback
}

dag = DAG(
    'brewery_pipeline',
    default_args=default_args,
    description='Brewery Medallion Pipeline com Notificações Avançadas',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['brewery', 'etl', 'medallion']
)

t1 = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag
)

t2 = PythonOperator(
    task_id='check_bronze_quality',
    python_callable=validate_breweries_with_path,
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

# Configurar dependências
t1 >> t2 >> t3 >> t4