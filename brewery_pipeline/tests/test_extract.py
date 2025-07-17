import unittest
from unittest.mock import patch, MagicMock

import pandas as pd
from scripts.transform import transform_data

class TestTransformData(unittest.TestCase):
    @patch("scripts.transform.pd.read_json")
    def test_transform_data_runs(self, mock_read_json):
        # Mocka o retorno do pd.read_json para um DataFrame de exemplo
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

if __name__ == "__main__":
    unittest.main()