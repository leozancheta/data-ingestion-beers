import unittest
import sys
import os
from unittest.mock import patch, MagicMock, mock_open
import json
import requests

# Add the parent directory to the path to import scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scripts.extract import extract_data


class TestExtractData(unittest.TestCase):
    
    @patch('scripts.extract.os.makedirs')
    @patch('scripts.extract.requests.get')
    @patch('builtins.open', new_callable=mock_open)
    @patch('scripts.extract.json.dump')
    def test_extract_data_successful_api_connection(self, mock_json_dump, mock_file_open, mock_requests_get, mock_makedirs):
        """Testa extração bem-sucedida com conexão à API"""
        # Mock da resposta de teste de conectividade
        mock_test_response = MagicMock()
        mock_test_response.raise_for_status.return_value = None
        
        # Mock das respostas das páginas
        mock_page1_response = MagicMock()
        mock_page1_response.raise_for_status.return_value = None
        mock_page1_response.json.return_value = [
            {"id": "1", "name": "Brewery 1", "brewery_type": "micro", "city": "City1", "state": "State1", "country": "US"},
            {"id": "2", "name": "Brewery 2", "brewery_type": "brewpub", "city": "City2", "state": "State2", "country": "US"}
        ]
        
        mock_page2_response = MagicMock()
        mock_page2_response.raise_for_status.return_value = None
        mock_page2_response.json.return_value = []  # Página vazia para parar o loop
        
        # Configurar o mock para retornar diferentes respostas para diferentes chamadas
        mock_requests_get.side_effect = [mock_test_response, mock_page1_response, mock_page2_response]
        
        # Executar a função
        extract_data()
        
        # Verificações
        mock_makedirs.assert_called_once_with('/opt/airflow/data/bronze', exist_ok=True)
        self.assertEqual(mock_requests_get.call_count, 3)  # 1 teste + 2 páginas
        mock_file_open.assert_called_once_with('/opt/airflow/data/bronze/breweries_raw.json', 'w')
        mock_json_dump.assert_called_once()
        
        # Verificar se os dados corretos foram passados para json.dump
        dumped_data = mock_json_dump.call_args[0][0]
        self.assertEqual(len(dumped_data), 2)
        self.assertEqual(dumped_data[0]["name"], "Brewery 1")

    @patch('scripts.extract.os.makedirs')
    @patch('scripts.extract.requests.get')
    @patch('builtins.open', new_callable=mock_open)
    @patch('scripts.extract.json.dump')
    def test_extract_data_api_unavailable_fallback_to_sample(self, mock_json_dump, mock_file_open, mock_requests_get, mock_makedirs):
        """Testa fallback para dados de exemplo quando API não está disponível"""
        # Mock da falha na conectividade
        mock_requests_get.side_effect = requests.exceptions.ConnectionError("Network unreachable")
        
        # Executar a função
        extract_data()
        
        # Verificações
        mock_makedirs.assert_called_once_with('/opt/airflow/data/bronze', exist_ok=True)
        mock_requests_get.assert_called_once()  # Apenas o teste de conectividade
        mock_file_open.assert_called_once_with('/opt/airflow/data/bronze/breweries_raw.json', 'w')
        mock_json_dump.assert_called_once()
        
        # Verificar se os dados de exemplo foram salvos
        dumped_data = mock_json_dump.call_args[0][0]
        self.assertEqual(len(dumped_data), 3)
        self.assertEqual(dumped_data[0]["id"], "sample-1")
        self.assertEqual(dumped_data[0]["name"], "Sample Brewery 1")

    @patch('scripts.extract.os.makedirs')
    @patch('scripts.extract.requests.get')
    @patch('builtins.open', new_callable=mock_open)
    @patch('scripts.extract.json.dump')
    def test_extract_data_with_retry_mechanism(self, mock_json_dump, mock_file_open, mock_requests_get, mock_makedirs):
        """Testa o mecanismo de retry quando há falhas temporárias"""
        # Mock da resposta de teste de conectividade (sucesso)
        mock_test_response = MagicMock()
        mock_test_response.raise_for_status.return_value = None
        
        # Mock de resposta que falha nas primeiras 2 tentativas e sucede na terceira
        mock_page_response_success = MagicMock()
        mock_page_response_success.raise_for_status.return_value = None
        mock_page_response_success.json.return_value = [
            {"id": "1", "name": "Brewery 1", "brewery_type": "micro", "city": "City1", "state": "State1", "country": "US"}
        ]
        
        mock_empty_response = MagicMock()
        mock_empty_response.raise_for_status.return_value = None
        mock_empty_response.json.return_value = []
        
        # Configurar side_effect para simular falhas seguidas de sucesso
        mock_requests_get.side_effect = [
            mock_test_response,  # Teste de conectividade
            requests.exceptions.Timeout("Read timeout"),  # Primeira tentativa falha
            requests.exceptions.Timeout("Read timeout"),  # Segunda tentativa falha
            mock_page_response_success,  # Terceira tentativa sucede
            mock_empty_response  # Página vazia para parar
        ]
        
        # Executar a função
        extract_data()
        
        # Verificações
        self.assertEqual(mock_requests_get.call_count, 5)  # 1 teste + 3 tentativas + 1 página vazia
        mock_json_dump.assert_called_once()
        
        # Verificar se os dados foram salvos corretamente após retry
        dumped_data = mock_json_dump.call_args[0][0]
        self.assertEqual(len(dumped_data), 1)
        self.assertEqual(dumped_data[0]["name"], "Brewery 1")

    @patch('scripts.extract.os.makedirs')
    @patch('scripts.extract.requests.get')
    @patch('builtins.open', new_callable=mock_open)
    @patch('scripts.extract.json.dump')
    def test_extract_data_max_retries_exceeded(self, mock_json_dump, mock_file_open, mock_requests_get, mock_makedirs):
        """Testa quando o máximo de tentativas é excedido"""
        # Mock da resposta de teste de conectividade (sucesso)
        mock_test_response = MagicMock()
        mock_test_response.raise_for_status.return_value = None
        
        # Configurar para sempre falhar após o teste de conectividade
        mock_requests_get.side_effect = [
            mock_test_response,  # Teste de conectividade sucede
            requests.exceptions.Timeout("Read timeout"),  # Primeira tentativa falha
            requests.exceptions.Timeout("Read timeout"),  # Segunda tentativa falha
            requests.exceptions.Timeout("Read timeout"),  # Terceira tentativa falha
        ]
        
        # Executar a função
        extract_data()
        
        # Verificações
        self.assertEqual(mock_requests_get.call_count, 4)  # 1 teste + 3 tentativas
        mock_json_dump.assert_called_once()
        
        # Verificar se uma lista vazia foi salva
        dumped_data = mock_json_dump.call_args[0][0]
        self.assertEqual(len(dumped_data), 0)

    @patch('scripts.extract.os.makedirs')
    @patch('scripts.extract.requests.get')
    @patch('builtins.open', new_callable=mock_open)
    @patch('scripts.extract.json.dump')
    def test_extract_data_page_limit_reached(self, mock_json_dump, mock_file_open, mock_requests_get, mock_makedirs):
        """Testa o limite de páginas (50 páginas)"""
        # Mock da resposta de teste de conectividade
        mock_test_response = MagicMock()
        mock_test_response.raise_for_status.return_value = None
        
        # Mock de resposta que sempre retorna dados (para forçar o limite)
        mock_page_response = MagicMock()
        mock_page_response.raise_for_status.return_value = None
        mock_page_response.json.return_value = [
            {"id": "1", "name": "Brewery 1", "brewery_type": "micro", "city": "City1", "state": "State1", "country": "US"}
        ]
        
        # Configurar para retornar sempre dados (até atingir o limite)
        mock_requests_get.side_effect = [mock_test_response] + [mock_page_response] * 50
        
        # Executar a função
        extract_data()
        
        # Verificações
        self.assertEqual(mock_requests_get.call_count, 51)  # 1 teste + 50 páginas
        mock_json_dump.assert_called_once()
        
        # Verificar se 50 registros foram salvos (50 páginas × 1 registro por página)
        dumped_data = mock_json_dump.call_args[0][0]
        self.assertEqual(len(dumped_data), 50)

    @patch('scripts.extract.os.makedirs')
    @patch('scripts.extract.requests.get')
    @patch('builtins.open', new_callable=mock_open)
    @patch('scripts.extract.json.dump')
    @patch('builtins.print')
    def test_extract_data_logging_messages(self, mock_print, mock_json_dump, mock_file_open, mock_requests_get, mock_makedirs):
        """Testa se as mensagens de log são exibidas corretamente"""
        # Mock da falha na conectividade para testar logs de fallback
        mock_requests_get.side_effect = requests.exceptions.ConnectionError("Network unreachable")
        
        # Executar a função
        extract_data()
        
        # Verificar se as mensagens corretas foram printadas
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        
        self.assertIn("Iniciando a extração de dados...", print_calls)
        self.assertIn("Testando conectividade com a API...", print_calls)
        self.assertTrue(any("API indisponível" in call for call in print_calls))
        self.assertTrue(any("Dados de exemplo salvos!" in call for call in print_calls))


if __name__ == "__main__":
    unittest.main()