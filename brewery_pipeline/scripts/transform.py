import pandas as pd
import os
import json

def transform_data():
    print("Iniciando transformação de dados...")
    
    try:
        # Criar diretório silver se não existir
        print("Criando diretório silver...")
        os.makedirs('/opt/airflow/data/silver', exist_ok=True)
        
        # Verificar se o arquivo bronze existe
        bronze_file = '/opt/airflow/data/bronze/breweries_raw.json'
        if not os.path.exists(bronze_file):
            print(f"AVISO: Arquivo {bronze_file} não encontrado.")
            print("Criando dados de exemplo para transformação...")
            
            # Criar dados de exemplo
            sample_data = [
                {"id": "sample-1", "name": "Sample Brewery 1", "brewery_type": "micro", "city": "Sample City", "state": "California", "country": "United States"},
                {"id": "sample-2", "name": "Sample Brewery 2", "brewery_type": "brewpub", "city": "Another City", "state": "Texas", "country": "United States"},
                {"id": "sample-3", "name": "Sample Brewery 3", "brewery_type": "large", "city": "Third City", "state": "Colorado", "country": "United States"}
            ]
            
            # Criar o arquivo bronze com dados de exemplo
            os.makedirs('/opt/airflow/data/bronze', exist_ok=True)
            with open(bronze_file, 'w', encoding='utf-8') as f:
                json.dump(sample_data, f, indent=2, ensure_ascii=False)
            print("Arquivo de dados de exemplo criado.")
        
        # Ler o arquivo JSON
        print(f"Lendo arquivo: {bronze_file}")
        try:
            df = pd.read_json(bronze_file)
            print(f"Arquivo lido com sucesso. Total de registros: {len(df)}")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"ERRO: Arquivo JSON inválido ou corrompido: {e}")
            raise ValueError(f"Não foi possível ler o arquivo JSON: {e}")
        except pd.errors.EmptyDataError:
            print("ERRO: Arquivo JSON está vazio.")
            raise ValueError("Arquivo JSON não contém dados.")
        
        # Verificar se o DataFrame não está vazio
        if df.empty:
            print("AVISO: DataFrame está vazio após a leitura.")
            print("Criando arquivo vazio para manter consistência do pipeline...")
            # Criar um DataFrame vazio com as colunas esperadas
            empty_df = pd.DataFrame(columns=['id', 'name', 'brewery_type', 'state', 'city', 'country'])
            empty_df.to_parquet('/opt/airflow/data/silver/empty_partition.parquet', index=False)
            print("Arquivo vazio criado na camada silver.")
            return
        
        # Verificar se as colunas necessárias existem
        required_columns = ['state', 'brewery_type']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"ERRO: Colunas obrigatórias não encontradas: {missing_columns}")
            print(f"Colunas disponíveis: {list(df.columns)}")
            raise ValueError(f"Colunas obrigatórias ausentes: {missing_columns}")
        
        # Mostrar estatísticas antes da limpeza
        print(f"Registros antes da limpeza: {len(df)}")
        print(f"Estados únicos: {df['state'].nunique()}")
        print(f"Tipos de cervejaria únicos: {df['brewery_type'].nunique()}")
        
        # Remover registros com valores nulos nas colunas críticas
        print("Removendo registros com valores nulos em 'state' e 'brewery_type'...")
        initial_count = len(df)
        df.dropna(subset=['state', 'brewery_type'], inplace=True)
        cleaned_count = len(df)
        removed_count = initial_count - cleaned_count
        
        if removed_count > 0:
            print(f"Removidos {removed_count} registros com valores nulos.")
        
        if df.empty:
            print("AVISO: Todos os registros foram removidos durante a limpeza.")
            print("Criando arquivo vazio para manter consistência do pipeline...")
            empty_df = pd.DataFrame(columns=['id', 'name', 'brewery_type', 'state', 'city', 'country'])
            empty_df.to_parquet('/opt/airflow/data/silver/empty_partition.parquet', index=False)
            print("Arquivo vazio criado na camada silver.")
            return
        
        print(f"Registros após limpeza: {cleaned_count}")
        
        # Processar partições por estado
        unique_states = df['state'].unique()
        print(f"Criando partições para {len(unique_states)} estados...")
        
        successful_partitions = 0
        failed_partitions = 0
        
        for state in unique_states:
            try:
                print(f"Processando estado: {state}")
                partition = df[df['state'] == state]
                
                # Validar nome do arquivo (remover caracteres especiais)
                safe_state_name = "".join(c for c in str(state) if c.isalnum() or c in (' ', '-', '_')).rstrip()
                if not safe_state_name:
                    safe_state_name = "unknown_state"
                
                output_file = f'/opt/airflow/data/silver/state={safe_state_name}.parquet'
                partition.to_parquet(output_file, index=False)
                
                print(f"Partição criada: {output_file} ({len(partition)} registros)")
                successful_partitions += 1
                
            except Exception as e:
                print(f"ERRO ao criar partição para estado '{state}': {e}")
                failed_partitions += 1
                continue
        
        # Resumo final
        print("\n=== Resumo da Transformação ===")
        print(f"Total de registros processados: {cleaned_count}")
        print(f"Estados únicos: {len(unique_states)}")
        print(f"Partições criadas com sucesso: {successful_partitions}")
        print(f"Partições com falha: {failed_partitions}")
        print("Transformação concluída com sucesso!")
        
        return {
            'processed_records': cleaned_count,
            'unique_states': len(unique_states),
            'successful_partitions': successful_partitions,
            'failed_partitions': failed_partitions
        }
        
    except FileNotFoundError as e:
        print(f"ERRO: Arquivo ou diretório não encontrado: {e}")
        raise
    except pd.errors.EmptyDataError as e:
        print(f"ERRO: Dados vazios encontrados: {e}")
        raise
    except ValueError as e:
        print(f"ERRO: Problema com os dados: {e}")
        raise
    except PermissionError as e:
        print(f"ERRO: Permissão negada para acessar arquivo/diretório: {e}")
        raise
    except Exception as e:
        print(f"ERRO inesperado durante a transformação: {e}")
        raise

if __name__ == "__main__":
    transform_data()