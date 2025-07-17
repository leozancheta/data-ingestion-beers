FROM apache/airflow:2.8.1

# Instalar as dependências como usuário root temporariamente
USER root

# Copiar requirements
COPY requirements.txt /tmp/requirements.txt

# Instalar dependências Python
RUN pip install -r /tmp/requirements.txt

# Voltar para usuário airflow
USER airflow
