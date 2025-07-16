import os
import unittest
os.makedirs("data/silver", exist_ok=True)
from scripts.transform import transform_data

class TestTransformData(unittest.TestCase):
    def test_transform_data_runs(self):
        # O teste verifica se a função executa sem lançar exceção
        try:
            transform_data()
        except Exception as e:
            self.fail(f"transform_data() lançou uma exceção: {e}")

if __name__ == "__main__":
    unittest.main()