import unittest
import sys
import os
from unittest.mock import patch, MagicMock, mock_open
import pandas as pd
import json

# Add the parent directory to the path to import scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scripts.transform import transform_data


class TestTransformData(unittest.TestCase):
    
    @patch('scripts.transform.os.makedirs')
    @patch('scripts.transform.os.path.exists')
    @patch('scripts.transform.pd.read_json')
    @patch('scripts.transform.pd.DataFrame.to_parquet')
    def test_transform_data_successful_processing(self, mock_to_parquet, mock_read_json, mock_exists, mock_makedirs):
        """Testa processamento bem-sucedido com dados válidos"""
        # Mock - arquivo existe
        mock_exists.return_value = True
        
        # Mock do DataFrame lido
        sample_df = pd.DataFrame({
            'id': ['1', '2', '3', '4'],
            'name': ['Brewery 1', 'Brewery 2', 'Brewery 3', 'Brewery 4'],
            'brewery_type': ['micro', 'brewpub', 'large', 'micro'],
            'state': ['California', 'California', 'Texas', 'Texas'],
            'city': ['LA', 'SF', 'Austin', 'Houston'],
            'country': ['US', 'US', 'US', 'US']
        })
        mock_read_json.return_value = sample_df
        
        # Executar a função
        result = transform_data()
        
        # Verificações
        mock_makedirs.assert_called_with('/opt/airflow/data/silver', exist_ok=True)
        mock_read_json.assert_called_once_with('/opt/airflow/data/bronze/breweries_raw.json')
        self.assertEqual(mock_to_parquet.call_count, 2)  # 2 estados únicos
        
        # Verificar estrutura do resultado
        self.assertIsInstance(result, dict)
        self.assertEqual(result['processed_records'], 4)
        self.assertEqual(result['unique_states'], 2)
        self.assertEqual(result['successful_partitions'], 2)
        self.assertEqual(result['failed_partitions'], 0)

    @patch('scripts.transform.os.makedirs')
    @patch('scripts.transform.os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('scripts.transform.json.dump')
    @patch('scripts.transform.pd.read_json')
    @patch('scripts.transform.pd.DataFrame.to_parquet')
    def test_transform_data_file_not_found_creates_sample(self, mock_to_parquet, mock_read_json, mock_json_dump, mock_file_open, mock_exists, mock_makedirs):
        """Testa criação de dados de exemplo quando arquivo bronze não existe"""
        # Mock - arquivo não existe na primeira verificação, existe na segunda
        mock_exists.side_effect = [False, True]
        
        # Mock do DataFrame com dados de exemplo
        sample_df = pd.DataFrame({
            'id': ['sample-1', 'sample-2', 'sample-3'],
            'name': ['Sample Brewery 1', 'Sample Brewery 2', 'Sample Brewery 3'],
            'brewery_type': ['micro', 'brewpub', 'large'],
            'state': ['California', 'Texas', 'Colorado'],
            'city': ['Sample City', 'Another City', 'Third City'],
            'country': ['United States', 'United States', 'United States']
        })
        mock_read_json.return_value = sample_df
        
        # Executar a função
        result = transform_data()
        
        # Verificações
        mock_json_dump.assert_called_once()  # Arquivo de exemplo foi criado
        mock_read_json.assert_called_once()
        self.assertEqual(mock_to_parquet.call_count, 3)  # 3 estados únicos
        
        # Verificar resultado
        self.assertIsInstance(result, dict)
        self.assertEqual(result['processed_records'], 3)
        self.assertEqual(result['unique_states'], 3)

    @patch('scripts.transform.os.makedirs')
    @patch('scripts.transform.os.path.exists')
    @patch('scripts.transform.pd.read_json')
    def test_transform_data_invalid_json_file(self, mock_read_json, mock_exists, mock_makedirs):
        """Testa tratamento de arquivo JSON inválido"""
        # Mock - arquivo existe
        mock_exists.return_value = True
        
        # Mock para simular erro de JSON
        mock_read_json.side_effect = json.JSONDecodeError("Invalid JSON", "doc", 0)
        
        # Executar a função e verificar se levanta exceção
        with self.assertRaises(ValueError) as context:
            transform_data()
        
        self.assertIn("Não foi possível ler o arquivo JSON", str(context.exception))

    @patch('scripts.transform.os.makedirs')
    @patch('scripts.transform.os.path.exists')
    @patch('scripts.transform.pd.read_json')
    @patch('scripts.transform.pd.DataFrame.to_parquet')
    def test_transform_data_empty_dataframe(self, mock_to_parquet, mock_read_json, mock_exists, mock_makedirs):
        """Testa tratamento de DataFrame vazio"""
        # Mock - arquivo existe
        mock_exists.return_value = True
        
        # Mock de DataFrame vazio
        empty_df = pd.DataFrame()
        mock_read_json.return_value = empty_df
        
        # Executar a função
        transform_data()
        
        # Verificações - deve criar arquivo vazio
        mock_to_parquet.assert_called_once()
        # Verificar se foi chamado com DataFrame vazio mas com colunas corretas
        call_args = mock_to_parquet.call_args_list[0]
        self.assertIn('empty_partition.parquet', call_args[0][0])

    @patch('scripts.transform.os.makedirs')
    @patch('scripts.transform.os.path.exists')
    @patch('scripts.transform.pd.read_json')
    def test_transform_data_missing_required_columns(self, mock_read_json, mock_exists, mock_makedirs):
        """Testa erro quando colunas obrigatórias estão ausentes"""
        # Mock - arquivo existe
        mock_exists.return_value = True
        
        # Mock de DataFrame sem colunas obrigatórias
        invalid_df = pd.DataFrame({
            'id': ['1', '2'],
            'name': ['Brewery 1', 'Brewery 2']
            # Faltam 'state' e 'brewery_type'
        })
        mock_read_json.return_value = invalid_df
        
        # Executar a função e verificar se levanta exceção
        with self.assertRaises(ValueError) as context:
            transform_data()
        
        self.assertIn("Colunas obrigatórias ausentes", str(context.exception))

    @patch('scripts.transform.os.makedirs')
    @patch('scripts.transform.os.path.exists')
    @patch('scripts.transform.pd.read_json')
    @patch('scripts.transform.pd.DataFrame.to_parquet')
    def test_transform_data_with_null_values_cleanup(self, mock_to_parquet, mock_read_json, mock_exists, mock_makedirs):
        """Testa limpeza de valores nulos"""
        # Mock - arquivo existe
        mock_exists.return_value = True
        
        # Mock do DataFrame com alguns valores nulos
        df_with_nulls = pd.DataFrame({
            'id': ['1', '2', '3', '4'],
            'name': ['Brewery 1', 'Brewery 2', 'Brewery 3', 'Brewery 4'],
            'brewery_type': ['micro', None, 'large', 'micro'],  # Um valor nulo
            'state': ['California', 'California', None, 'Texas'],  # Um valor nulo
            'city': ['LA', 'SF', 'Austin', 'Houston'],
            'country': ['US', 'US', 'US', 'US']
        })
        mock_read_json.return_value = df_with_nulls
        
        # Executar a função
        result = transform_data()
        
        # Verificações - devem restar apenas 2 registros válidos
        self.assertEqual(result['processed_records'], 2)
        self.assertEqual(result['unique_states'], 2)  # California e Texas
        self.assertEqual(mock_to_parquet.call_count, 2)

    @patch('scripts.transform.os.makedirs')
    @patch('scripts.transform.os.path.exists')
    @patch('scripts.transform.pd.read_json')
    @patch('scripts.transform.pd.DataFrame.to_parquet')
    def test_transform_data_partition_creation_error(self, mock_to_parquet, mock_read_json, mock_exists, mock_makedirs):
        """Testa tratamento de erro na criação de partições"""
        # Mock - arquivo existe
        mock_exists.return_value = True
        
        # Mock do DataFrame válido
        sample_df = pd.DataFrame({
            'id': ['1', '2'],
            'name': ['Brewery 1', 'Brewery 2'],
            'brewery_type': ['micro', 'brewpub'],
            'state': ['California', 'Texas'],
            'city': ['LA', 'Austin'],
            'country': ['US', 'US']
        })
        mock_read_json.return_value = sample_df
        
        # Mock para simular erro na primeira partição, sucesso na segunda
        mock_to_parquet.side_effect = [
            PermissionError("Permission denied"),  # Primeira partição falha
            None  # Segunda partição sucede
        ]
        
        # Executar a função
        result = transform_data()
        
        # Verificações
        self.assertEqual(result['successful_partitions'], 1)
        self.assertEqual(result['failed_partitions'], 1)
        self.assertEqual(mock_to_parquet.call_count, 2)

    @patch('scripts.transform.os.makedirs')
    @patch('scripts.transform.os.path.exists')
    @patch('scripts.transform.pd.read_json')
    @patch('scripts.transform.pd.DataFrame.to_parquet')
    @patch('builtins.print')
    def test_transform_data_logging_messages(self, mock_print, mock_to_parquet, mock_read_json, mock_exists, mock_makedirs):
        """Testa se as mensagens de log são exibidas corretamente"""
        # Mock - arquivo existe
        mock_exists.return_value = True
        
        # Mock do DataFrame válido
        sample_df = pd.DataFrame({
            'id': ['1'],
            'name': ['Brewery 1'],
            'brewery_type': ['micro'],
            'state': ['California'],
            'city': ['LA'],
            'country': ['US']
        })
        mock_read_json.return_value = sample_df
        
        # Executar a função
        transform_data()
        
        # Verificar se as mensagens corretas foram printadas
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        
        self.assertIn("Iniciando transformação de dados...", print_calls)
        self.assertIn("Criando diretório silver...", print_calls)
        self.assertTrue(any("Lendo arquivo:" in call for call in print_calls))
        self.assertTrue(any("Arquivo lido com sucesso" in call for call in print_calls))
        self.assertIn("Transformação concluída com sucesso!", print_calls)


if __name__ == "__main__":
    unittest.main()