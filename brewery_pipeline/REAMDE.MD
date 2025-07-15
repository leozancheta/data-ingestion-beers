# README.md
# Brewery Pipeline

Pipeline que consome dados da API Open Brewery DB e os armazena em uma arquitetura Medallion (Bronze, Silver, Gold).

## Como executar localmente

1. Clone o repositório:
```bash
git clone <repo>
cd brewery_pipeline
```

2. Suba os containers:
```bash
cd docker
docker-compose up
```

3. Acesse o Airflow: [http://localhost:8080](http://localhost:8080)

## Executar testes
```bash
pytest tests/
