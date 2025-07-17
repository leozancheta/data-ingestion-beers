#!/bin/bash

echo "Configurando permissões do Airflow..."

# Configurar permissões para todos os diretórios do Airflow
chmod -R 777 /opt/airflow/dags
chmod -R 777 /opt/airflow/scripts
chmod -R 777 /opt/airflow/data
chmod -R 777 /opt/airflow/dataquality

# Configurar ownership
chown -R airflow:root /opt/airflow/dags
chown -R airflow:root /opt/airflow/scripts
chown -R airflow:root /opt/airflow/data
chown -R airflow:root /opt/airflow/dataquality

echo "Permissões configuradas com sucesso!"

# Inicializar banco de dados do Airflow
echo "Inicializando banco de dados do Airflow..."
airflow db init

# Criar usuário admin se não existir
echo "Verificando usuário admin..."
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password admin 2>/dev/null || echo "Usuário admin já existe"

echo "Inicialização do Airflow concluída!"
