import requests
import json
import os

def save_data_local(data, filename="breweries_raw.json"):
    """
    Salva os dados em formato JSON na pasta local data/bronze.
    """
    local_path = "data/bronze"
    os.makedirs(local_path, exist_ok=True)
    file_path = os.path.join(local_path, filename)
    with open(file_path, "w") as f:
        json.dump(data, f)
    print(f"Dados salvos em: {file_path}")

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

    # Salva no diretório do Airflow
    with open('/opt/airflow/data/bronze/breweries_raw.json', 'w') as f:
        json.dump(all_data, f)
    print(f"Dados extraídos com sucesso! Total de registros: {len(all_data)}")

    # Salva também localmente na pasta data/bronze do projeto
    save_data_local(all_data)

if __name__ == "__main__":
    extract_data()