import pandas as pd
import numpy as np
from typing import Optional
import streamlit as st
from src.data.config import AppConfig
from src.utils.logger import get_logger

class DataLoader:
    """Loads and preprocesses bank statement data from a CSV file."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = get_logger(__name__)

    @st.cache_data
    def load_data(_self, uploaded_file) -> Optional[pd.DataFrame]:
        """Loads and preprocesses the bank statement data."""
        if uploaded_file is None:
            _self.logger.warning("No file uploaded")
            return None
        try:
            df = pd.read_csv(uploaded_file)
            return _self._preprocess_data(df)
        except Exception as e:
            _self.logger.error(f"Error loading file: {e}")
            st.error(f"An error occurred while processing the file: {e}")
            return None

    def _preprocess_data(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Preprocesses the DataFrame."""
        # Rename columns
        df = df.rename(columns={v: k for k, v in self.config.COLUMN_MAPPING.items()})

        # Validate required columns
        required_cols = ["date", "description", "debit", "credit"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.error(
                f"Missing required columns: {', '.join(missing_cols)}. "
                f"Please ensure columns named {', '.join(self.config.COLUMN_MAPPING.values())} exist."
            )
            self.logger.error(f"Missing columns: {missing_cols}")
            return None

        # Convert date to datetime
        try:
            df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=False)
            if df["date"].isna().any():
                df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)
            df.dropna(subset=["date"], inplace=True)
        except Exception as e:
            st.error(f"Failed to parse 'date' column: {e}")
            self.logger.error(f"Date parsing error: {e}")
            return None

        # Convert debit/credit to numeric
        for col in ["debit", "credit"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # Create amount and transaction_type columns
        df["amount"] = df["credit"] - df["debit"]
        df["transaction_type"] = np.where(
            df["amount"] > 0, "Income", "Expense"
        )
        df.loc[
            (df["amount"] == 0) & (df["debit"] == 0) & (df["credit"] == 0),
            "transaction_type",
        ] = "Neutral"

        # Categorize transactions
        df["category"] = df["description"].apply(self._categorize_transaction)

        # Sort by date
        df = df.sort_values(by="date").reset_index(drop=True)
        self.logger.info("Data preprocessing completed successfully")
        return df

    def _categorize_transaction(self, description: str) -> str:
        """Categorizes a transaction based on description."""
        description = str(description).lower()
        for category, keywords in self.config.CATEGORIZATION_RULES.items():
            if any(keyword in description for keyword in keywords):
                return category
        return self.config.DEFAULT_CATEGORY