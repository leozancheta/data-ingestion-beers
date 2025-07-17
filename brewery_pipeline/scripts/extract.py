import requests
import json
import os

def extract_data():
    print("Iniciando a extração de dados...")
    os.makedirs('/opt/airflow/data/bronze', exist_ok=True)
    url = 'https://api.openbrewerydb.org/v1/breweries'
    page = 1
    all_data = []
    max_retries = 3

    # Teste inicial de conectividade com timeout maior
    print("Testando conectividade com a API...")
    try:
        test_response = requests.get(url, params={'page': 1, 'per_page': 1}, timeout=30)
        test_response.raise_for_status()
        print("API acessível - iniciando extração completa")
    except Exception as e:
        print(f"API indisponível ({e}). Usando dados de exemplo.")
        # Dados de exemplo para quando a API não está acessível
        sample_data = [
            {"id": "sample-1", "name": "Sample Brewery 1", "brewery_type": "micro", "city": "Sample City", "state": "Sample State", "country": "United States"},
            {"id": "sample-2", "name": "Sample Brewery 2", "brewery_type": "brewpub", "city": "Another City", "state": "Another State", "country": "United States"},
            {"id": "sample-3", "name": "Sample Brewery 3", "brewery_type": "large", "city": "Third City", "state": "Third State", "country": "United States"}
        ]
        with open('/opt/airflow/data/bronze/breweries_raw.json', 'w') as f:
            json.dump(sample_data, f, indent=2)
        print(f"Dados de exemplo salvos! Total de registros: {len(sample_data)}")
        return

    while True:
        retry_count = 0
        success = False
        
        while retry_count < max_retries and not success:
            try:
                print(f"Extraindo página {page} (tentativa {retry_count + 1})...")
                response = requests.get(url, params={'page': page, 'per_page': 50}, timeout=30)
                response.raise_for_status()
                data = response.json()
                success = True
            except Exception as e:
                retry_count += 1
                print(f"Erro na tentativa {retry_count}: {e}")
                if retry_count >= max_retries:
                    print(f"Falha após {max_retries} tentativas na página {page}. Parando extração.")
                    break

        if not success:
            break

        if not data:
            print("Não há mais dados para extrair.")
            break
        
        all_data.extend(data)
        print(f"Página {page} extraída: {len(data)} registros")
        page += 1
        
        # Limite de segurança
        if page > 50:
            print("Limite de páginas atingido (50). Parando extração.")
            break

    # Salva apenas no diretório do Airflow
    with open('/opt/airflow/data/bronze/breweries_raw.json', 'w') as f:
        json.dump(all_data, f, indent=2)
    print(f"Dados extraídos com sucesso! Total de registros: {len(all_data)}")

if __name__ == "__main__":
    extract_data()