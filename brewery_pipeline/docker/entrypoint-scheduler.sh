#!/bin/bash

# Configurar permissões antes de iniciar o serviço
echo "Configurando permissões para o scheduler..."
chmod -R 777 /opt/airflow/dags
chmod -R 777 /opt/airflow/scripts
chmod -R 777 /opt/airflow/data
chmod -R 777 /opt/airflow/dataquality

# Executar o comando original
exec "$@"
