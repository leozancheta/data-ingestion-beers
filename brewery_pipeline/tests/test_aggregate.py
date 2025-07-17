import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from scripts.aggregate import aggregate_data

class TestAggregateData(unittest.TestCase):
    @patch("scripts.aggregate.glob.glob")
    @patch("scripts.aggregate.pd.read_parquet")
    @patch("scripts.aggregate.pd.concat")
    @patch("scripts.aggregate.os.makedirs")
    @patch("scripts.aggregate.pd.DataFrame.to_parquet")
    def test_aggregate_data(self, mock_to_parquet, mock_makedirs, mock_concat, mock_read_parquet, mock_glob):
        # Mocka os arquivos encontrados
        mock_glob.return_value = ["file1.parquet", "file2.parquet"]
        # Mocka o retorno do read_parquet
        df1 = pd.DataFrame({
            "state": ["Oklahoma", "Texas"],
            "brewery_type": ["micro", "regional"]
        })
        df2 = pd.DataFrame({
            "state": ["Oklahoma", "Texas"],
            "brewery_type": ["regional", "micro"]
        })
        mock_read_parquet.side_effect = [df1, df2]
        # Mocka o concat para retornar um DataFrame de exemplo
        mock_concat.return_value = pd.concat([df1, df2])
        # Mocka o to_parquet para não salvar nada

        try:
            aggregate_data()
        except Exception as e:
            self.fail(f"aggregate_data() lançou uma exceção: {e}")

if __name__ == "__main__":
    unittest.main()