import requests
import json
import os

def extract_data():
    print("Iniciando a extração de dados...")
    os.makedirs('/opt/airflow/data/bronze', exist_ok=True)
    url = 'https://api.openbrewerydb.org/v1/breweries'
    page = 1
    all_data = []

    while True:
        try:
            response = requests.get(url, params={'page': page, 'per_page': 50}, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"Erro ao requisitar página {page}: {e}")
            break

        if not data:
            break
        all_data.extend(data)
        page += 1

    # Salva apenas no diretório do Airflow
    with open('/opt/airflow/data/bronze/breweries_raw.json', 'w') as f:
        json.dump(all_data, f)
    print(f"Dados extraídos com sucesso! Total de registros: {len(all_data)}")

if __name__ == "__main__":
    extract_data()