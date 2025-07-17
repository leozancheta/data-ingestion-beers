import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from scripts.transform import transform_data

class TestTransformData(unittest.TestCase):
    @patch("scripts.transform.pd.read_json")
    @patch("scripts.transform.os.makedirs")
    @patch("scripts.transform.pd.DataFrame.to_parquet")
    def test_transform_data(self, mock_to_parquet, mock_makedirs, mock_read_json):
        # Mocka o DataFrame retornado pelo read_json
        mock_df = pd.DataFrame({
            "id": [1, 2],
            "name": ["Brewery A", "Brewery B"],
            "state": ["Oklahoma", "Texas"],
            "brewery_type": ["micro", "regional"]
        })
        mock_read_json.return_value = mock_df

        try:
            transform_data()
        except Exception as e:
            self.fail(f"transform_data() lançou uma exceção: {e}")

        # Verifica se to_parquet foi chamado para cada estado
        self.assertEqual(mock_to_parquet.call_count, 2)
        mock_to_parquet.assert_any_call('/opt/airflow/data/silver/state=Oklahoma.parquet', index=False)
        mock_to_parquet.assert_any_call('/opt/airflow/data/silver/state=Texas.parquet', index=False)

if __name__ == "__main__":
    unittest.main()