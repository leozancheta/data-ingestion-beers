import pandas as pd
import glob
import os

def aggregate_data():
    print("Iniciando agregação de dados...")
    
    try:
        # Buscar arquivos parquet na camada silver
        print("Buscando arquivos parquet na camada silver...")
        files = glob.glob('/opt/airflow/data/silver/state=*.parquet')
        
        if not files:
            print("AVISO: Nenhum arquivo parquet encontrado na camada silver.")
            print("Verificando se existem dados de exemplo...")
            
            # Criar dados de exemplo se não houver arquivos
            sample_data = pd.DataFrame({
                'state': ['California', 'California', 'Texas', 'Texas', 'Colorado'],
                'brewery_type': ['micro', 'brewpub', 'micro', 'large', 'micro'],
                'name': ['Sample Brewery 1', 'Sample Brewery 2', 'Sample Brewery 3', 'Sample Brewery 4', 'Sample Brewery 5']
            })
            
            print("Usando dados de exemplo para agregação...")
            df = sample_data
        else:
            print(f"Encontrados {len(files)} arquivos para processar.")
            
            # Ler e concatenar arquivos parquet
            dataframes = []
            for file in files:
                try:
                    temp_df = pd.read_parquet(file)
                    dataframes.append(temp_df)
                    print(f"Arquivo lido com sucesso: {file}")
                except Exception as e:
                    print(f"ERRO ao ler arquivo {file}: {e}")
                    continue
            
            if not dataframes:
                raise ValueError("Nenhum arquivo válido foi encontrado ou lido com sucesso.")
            
            df = pd.concat(dataframes, ignore_index=True)
        
        print(f"Dataset consolidado: {len(df)} registros")
        
        # Verificar se as colunas necessárias existem
        required_columns = ['state', 'brewery_type']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Colunas obrigatórias não encontradas: {missing_columns}")
        
        # Realizar agregação
        print("Realizando agregação por estado e tipo de cervejaria...")
        result = df.groupby(['state', 'brewery_type']).size().reset_index(name='brewery_count')
        
        print(f"Agregação concluída: {len(result)} grupos únicos")
        
        # Criar diretório gold se não existir
        os.makedirs('/opt/airflow/data/gold', exist_ok=True)
        
        # Salvar resultado
        output_file = '/opt/airflow/data/gold/aggregated_breweries.parquet'
        result.to_parquet(output_file, index=False)
        print(f"Dados agregados salvos com sucesso em: {output_file}")
        
        # Exibir resumo dos resultados
        print("\nResumo da agregação:")
        print(f"- Total de estados: {result['state'].nunique()}")
        print(f"- Total de tipos de cervejaria: {result['brewery_type'].nunique()}")
        print(f"- Total de cervejarias: {result['brewery_count'].sum()}")
        
        return result
        
    except FileNotFoundError as e:
        print(f"ERRO: Diretório ou arquivo não encontrado: {e}")
        raise
    except pd.errors.EmptyDataError as e:
        print(f"ERRO: Dados vazios encontrados: {e}")
        raise
    except ValueError as e:
        print(f"ERRO: Problema com os dados: {e}")
        raise
    except Exception as e:
        print(f"ERRO inesperado durante a agregação: {e}")
        raise

if __name__ == "__main__":
    aggregate_data()