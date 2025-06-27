import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# print("Current working directory:", os.getcwd())
# print("sys.path:", sys.path)
from src.data.config import AppConfig
from src.data.data_loader import DataLoader
from src.data.processor import DataProcessor
from src.display.dashboard import Dashboard

def main():
    """Run the Bank Statement Analyzer application."""
    config = AppConfig()
    data_loader = DataLoader(config)
    data_processor = DataProcessor(config)
    dashboard = Dashboard(config, data_loader, data_processor)
    dashboard.run()

if __name__ == "__main__":
    main()