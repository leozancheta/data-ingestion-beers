import unittest
import sys
import os
from unittest.mock import patch, MagicMock, mock_open
import pandas as pd

# Add the parent directory to the path to import scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scripts.aggregate import aggregate_data


class TestAggregateData(unittest.TestCase):
    
    @patch('scripts.aggregate.os.makedirs')
    @patch('scripts.aggregate.glob.glob')
    @patch('scripts.aggregate.pd.read_parquet')
    @patch('scripts.aggregate.pd.DataFrame.to_parquet')
    def test_aggregate_data_successful_processing(self, mock_to_parquet, mock_read_parquet, mock_glob, mock_makedirs):
        """Testa processamento bem-sucedido com arquivos parquet válidos"""
        # Mock dos arquivos encontrados
        mock_glob.return_value = [
            '/opt/airflow/data/silver/state=California.parquet',
            '/opt/airflow/data/silver/state=Texas.parquet'
        ]
        
        # Mock dos DataFrames lidos
        df1 = pd.DataFrame({
            'state': ['California', 'California'],
            'brewery_type': ['micro', 'brewpub'],
            'name': ['Brewery 1', 'Brewery 2']
        })
        df2 = pd.DataFrame({
            'state': ['Texas', 'Texas'],
            'brewery_type': ['micro', 'large'],
            'name': ['Brewery 3', 'Brewery 4']
        })
        
        mock_read_parquet.side_effect = [df1, df2]
        
        # Executar a função
        result = aggregate_data()
        
        # Verificações
        mock_glob.assert_called_once_with('/opt/airflow/data/silver/state=*.parquet')
        self.assertEqual(mock_read_parquet.call_count, 2)
        mock_makedirs.assert_called_once_with('/opt/airflow/data/gold', exist_ok=True)
        mock_to_parquet.assert_called_once()
        
        # Verificar estrutura do resultado
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('state', result.columns)
        self.assertIn('brewery_type', result.columns)
        self.assertIn('brewery_count', result.columns)

    @patch('scripts.aggregate.os.makedirs')
    @patch('scripts.aggregate.glob.glob')
    @patch('scripts.aggregate.pd.DataFrame.to_parquet')
    def test_aggregate_data_no_files_found_fallback_to_sample(self, mock_to_parquet, mock_glob, mock_makedirs):
        """Testa fallback para dados de exemplo quando nenhum arquivo é encontrado"""
        # Mock para não encontrar arquivos
        mock_glob.return_value = []
        
        # Executar a função
        result = aggregate_data()
        
        # Verificações
        mock_glob.assert_called_once_with('/opt/airflow/data/silver/state=*.parquet')
        mock_makedirs.assert_called_once_with('/opt/airflow/data/gold', exist_ok=True)
        mock_to_parquet.assert_called_once()
        
        # Verificar que dados de exemplo foram usados
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(len(result) > 0)
        self.assertIn('state', result.columns)
        self.assertIn('brewery_type', result.columns)
        self.assertIn('brewery_count', result.columns)

    @patch('scripts.aggregate.os.makedirs')
    @patch('scripts.aggregate.glob.glob')
    @patch('scripts.aggregate.pd.read_parquet')
    def test_aggregate_data_file_reading_error(self, mock_read_parquet, mock_glob, mock_makedirs):
        """Testa tratamento de erro ao ler arquivos corrompidos"""
        # Mock dos arquivos encontrados
        mock_glob.return_value = [
            '/opt/airflow/data/silver/state=California.parquet',
            '/opt/airflow/data/silver/state=Texas.parquet'
        ]
        
        # Mock para simular erro no primeiro arquivo e sucesso no segundo
        valid_df = pd.DataFrame({
            'state': ['Texas'],
            'brewery_type': ['micro'],
            'name': ['Brewery 1']
        })
        
        mock_read_parquet.side_effect = [
            pd.errors.ParserError("Corrupted file"),  # Primeiro arquivo falha
            valid_df  # Segundo arquivo sucede
        ]
        
        # Executar a função
        with patch('scripts.aggregate.pd.DataFrame.to_parquet') as mock_to_parquet:
            result = aggregate_data()
        
        # Verificações
        self.assertEqual(mock_read_parquet.call_count, 2)
        mock_to_parquet.assert_called_once()
        
        # Verificar que apenas dados válidos foram processados
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(len(result) > 0)

    @patch('scripts.aggregate.os.makedirs')
    @patch('scripts.aggregate.glob.glob')
    @patch('scripts.aggregate.pd.read_parquet')
    def test_aggregate_data_all_files_corrupted(self, mock_read_parquet, mock_glob, mock_makedirs):
        """Testa quando todos os arquivos estão corrompidos"""
        # Mock dos arquivos encontrados
        mock_glob.return_value = [
            '/opt/airflow/data/silver/state=California.parquet',
            '/opt/airflow/data/silver/state=Texas.parquet'
        ]
        
        # Mock para simular erro em todos os arquivos
        mock_read_parquet.side_effect = [
            pd.errors.ParserError("Corrupted file 1"),
            pd.errors.ParserError("Corrupted file 2")
        ]
        
        # Executar a função e verificar se levanta exceção
        with self.assertRaises(ValueError) as context:
            aggregate_data()
        
        self.assertIn("Nenhum arquivo válido foi encontrado", str(context.exception))

    @patch('scripts.aggregate.os.makedirs')
    @patch('scripts.aggregate.glob.glob')
    @patch('scripts.aggregate.pd.read_parquet')
    def test_aggregate_data_missing_required_columns(self, mock_read_parquet, mock_glob, mock_makedirs):
        """Testa erro quando colunas obrigatórias estão ausentes"""
        # Mock dos arquivos encontrados
        mock_glob.return_value = ['/opt/airflow/data/silver/state=California.parquet']
        
        # Mock de DataFrame sem colunas obrigatórias
        invalid_df = pd.DataFrame({
            'name': ['Brewery 1'],
            'city': ['San Francisco']
            # Faltam 'state' e 'brewery_type'
        })
        
        mock_read_parquet.return_value = invalid_df
        
        # Executar a função e verificar se levanta exceção
        with self.assertRaises(ValueError) as context:
            aggregate_data()
        
        self.assertIn("Colunas obrigatórias não encontradas", str(context.exception))

    @patch('scripts.aggregate.os.makedirs')
    @patch('scripts.aggregate.glob.glob')
    @patch('scripts.aggregate.pd.read_parquet')
    @patch('scripts.aggregate.pd.DataFrame.to_parquet')
    def test_aggregate_data_empty_dataframe(self, mock_to_parquet, mock_read_parquet, mock_glob, mock_makedirs):
        """Testa processamento com DataFrame vazio mas com colunas corretas"""
        # Mock dos arquivos encontrados
        mock_glob.return_value = ['/opt/airflow/data/silver/state=California.parquet']
        
        # Mock de DataFrame vazio mas com colunas corretas
        empty_df = pd.DataFrame(columns=['state', 'brewery_type', 'name'])
        mock_read_parquet.return_value = empty_df
        
        # Executar a função
        result = aggregate_data()
        
        # Verificações
        mock_to_parquet.assert_called_once()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 0)  # Resultado vazio é válido
        self.assertIn('brewery_count', result.columns)

    @patch('scripts.aggregate.os.makedirs')
    @patch('scripts.aggregate.glob.glob')
    @patch('scripts.aggregate.pd.read_parquet')
    @patch('scripts.aggregate.pd.DataFrame.to_parquet')
    @patch('builtins.print')
    def test_aggregate_data_logging_messages(self, mock_print, mock_to_parquet, mock_read_parquet, mock_glob, mock_makedirs):
        """Testa se as mensagens de log são exibidas corretamente"""
        # Mock para cenário de sucesso
        mock_glob.return_value = ['/opt/airflow/data/silver/state=California.parquet']
        
        df = pd.DataFrame({
            'state': ['California'],
            'brewery_type': ['micro'],
            'name': ['Brewery 1']
        })
        mock_read_parquet.return_value = df
        
        # Executar a função
        aggregate_data()
        
        # Verificar se as mensagens corretas foram printadas
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        
        self.assertIn("Iniciando agregação de dados...", print_calls)
        self.assertIn("Buscando arquivos parquet na camada silver...", print_calls)
        self.assertTrue(any("Encontrados" in call and "arquivos para processar" in call for call in print_calls))
        self.assertIn("Realizando agregação por estado e tipo de cervejaria...", print_calls)
        self.assertTrue(any("Dados agregados salvos com sucesso" in call for call in print_calls))


if __name__ == "__main__":
    unittest.main()