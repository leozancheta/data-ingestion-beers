# Brewery Pipeline

Este projeto implementa um pipeline de dados que consome informações da API Open Brewery DB e armazena em uma arquitetura Medallion (Bronze, Silver, Gold) usando Apache Airflow.

---

## **Como executar no Windows (WSL)**

1. **Instale o WSL e Ubuntu**
   - Execute no PowerShell:
     ```bash
     wsl --install
     ```
   - Reinicie o computador se necessário.

2. **Instale dependências no WSL**
   ```bash
   sudo apt update
   sudo apt install git python3-pip python3-venv docker.io
   ```

3. **Clone o repositório**
   ```bash
   git clone <URL-do-repositorio>
   cd data-ingestion-beers/brewery_pipeline
   ```

4. **Crie as pastas de dados**
   ```bash
   mkdir -p data/bronze data/silver data/gold
   ```

5. **Dê permissão às pastas**
   ```bash
   sudo chmod -R 777 data
   ```

6. **Execute o Docker Compose**
   ```bash
   cd docker
   docker-compose up
   ```

7. **Acesse o Airflow**
   - Abra [http://localhost:8080](http://localhost:8080) no navegador.

---

## **Como executar no Linux (Docker direto)**

1. **Instale Docker e Git**
   ```bash
   sudo apt update
   sudo apt install docker.io git
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

2. **Clone o repositório**
   ```bash
   git clone https://github.com/leozancheta/data-ingestion-beers.git
   cd data-ingestion-beers/brewery_pipeline
   ```

3. **Crie as pastas de dados**
   ```bash
   mkdir -p data/bronze data/silver data/gold
   sudo chmod -R 777 data
   ```

4. **Execute o Docker Compose**
   ```bash
   cd docker
   docker-compose up
   ```

5. **Acesse o Airflow**
   - Abra [http://localhost:8080](http://localhost:8080) no navegador.

---

## **Executar testes unitários**

```bash
pytest tests/
```

---

## **Observações**
- Certifique-se que as pastas `data/bronze`, `data/silver` e `data/gold` existem e têm permissão de escrita.
- O pipeline pode ser monitorado e gerenciado via interface web do Airflow.
- Para dúvidas sobre configuração de ambiente, consulte a documentação oficial do [Airflow](https://airflow.apache.org/docs/apache-airflow/stable/index.html) e [Docker](https://docs.docker.com/).


## Documentação do Job Airflow: brewery_pipeline

### Visão Geral

A DAG `brewery_pipeline` orquestra o fluxo de dados da API Open Brewery DB até a geração de camadas Bronze, Silver e Gold, seguindo a arquitetura Medallion. O pipeline é executado diariamente e possui monitoramento de falhas via e-mail.

---

### Fluxo das Tasks

1. **extract_data**
   - Extrai dados da API Open Brewery DB.
   - Salva o resultado bruto em `/opt/airflow/data/bronze/breweries_raw.json`.

2. **check_bronze_quality**
   - Valida a qualidade dos dados extraídos (schema, campos obrigatórios, nulos).
   - Garante que o arquivo bronze está pronto para processamento.

3. **transform_data**
   - Lê o arquivo bronze.
   - Realiza limpeza e transforma os dados para formato Parquet.
   - Particiona os dados por estado em `/opt/airflow/data/silver/state=<state>.parquet`.

4. **aggregate_data**
   - Lê todos os arquivos da camada Silver.
   - Realiza agregação por estado e tipo de cervejaria.
   - Salva o resultado em `/opt/airflow/data/gold/aggregated_breweries.parquet`.

---

### Monitoramento e Alertas

- Em caso de falha em qualquer tarefa, um e-mail é enviado automaticamente para o responsável, contendo informações da DAG, tarefa, data de execução e link para o log do erro.

---

### Agendamento

- O pipeline é executado diariamente (`schedule_interval='@daily'`).
- O parâmetro `catchup=False` garante que execuções perdidas não sejam processadas retroativamente.

---

### Como Executar

1. Certifique-se que todas as dependências estão instaladas e o ambiente Docker está configurado.
2. Inicie o Airflow via Docker Compose.
3. Acesse a interface web do Airflow em [http://localhost:8080](http://localhost:8080).
4. Ative a DAG `brewery_pipeline` e monitore a execução e os logs das tarefas.

---

### Observações

- O pipeline pode ser facilmente adaptado para outros agendamentos ou validações.
- Para alterar o destinatário dos alertas, edite o e-mail em `failure_alert`.
- Todas as etapas são modularizadas e podem ser testadas individualmente.
