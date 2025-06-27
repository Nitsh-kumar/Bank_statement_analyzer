import unittest
import pandas as pd
from datetime import datetime
from src.data.config import AppConfig
from src.data.processor import DataProcessor

class TestDataProcessor(unittest.TestCase):
    def setUp(self):
        self.config = AppConfig()
        self.processor = DataProcessor(self.config)
        self.df = pd.DataFrame({
            "date": [datetime(2023, 1, 1), datetime(2023, 1, 2)],
            "description": ["Salary", "Grocery"],
            "debit": [0, 100],
            "credit": [1000, 0],
            "amount": [1000, -100],
            "transaction_type": ["Income", "Expense"],
            "category": ["Salary", "Groceries"],
        })

    def test_filter_by_date(self):
        filtered = self.processor.filter_by_date(
            self.df, datetime(2023, 1, 1), datetime(2023, 1, 1)
        )
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered.iloc[0]["description"], "Salary")

    def test_calculate_kpis(self):
        kpis = self.processor.calculate_kpis(
            self.df, datetime(2023, 1, 1), datetime(2023, 1, 2)
        )
        self.assertEqual(kpis["total_income"], 1000)
        self.assertEqual(kpis["total_expenses"], 100)
        self.assertEqual(kpis["net_flow"], 900)

if __name__ == "__main__":
    unittest.main()