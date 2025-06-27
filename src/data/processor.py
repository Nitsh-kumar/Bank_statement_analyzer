import pandas as pd
from typing import Optional, List, Dict
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from src.data.config import AppConfig
from src.utils.logger import get_logger

class DataProcessor:
    """Processes DataFrame for dashboard visualizations and tables."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = get_logger(__name__)

    def validate_columns(self, df: pd.DataFrame, required_cols: List[str]) -> bool:
        """Validate that required columns exist."""
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            self.logger.error(f"Missing columns: {missing_cols}")
            return False
        return True

    def filter_by_date(self, df: pd.DataFrame, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Filter DataFrame by date range."""
        end_date = end_date + timedelta(days=1)  # Include end date
        return df[(df["date"] >= start_date) & (df["date"] < end_date)].copy()

    def calculate_kpis(self, df: pd.DataFrame, start_date: datetime, end_date: datetime) -> Dict:
        """Calculate key performance indicators."""
        total_income = df[df["amount"] > 0]["amount"].sum()
        total_expenses = -df[df["amount"] < 0]["amount"].sum()
        net_flow = total_income - total_expenses
        num_days = (end_date - start_date).days + 1
        avg_daily_spend = total_expenses / num_days if num_days > 0 else 0
        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_flow": net_flow,
            "avg_daily_spend": avg_daily_spend,
            "opening_balance": 0,  # Placeholder (requires balance data)
            "closing_balance": 0,  # Placeholder
        }

    def get_trend_data(self, df: pd.DataFrame) -> Optional[go.Figure]:
        """Generate income vs expense trend chart."""
        if not self.validate_columns(df, ["date", "amount"]):
            return None
        try:
            df_resampled = (
                df.set_index("date")
                .resample("ME")["amount"]
                .agg(["sum", lambda x: x[x > 0].sum(), lambda x: x[x < 0].sum()])
                .rename(columns={"<lambda_0>": "income", "<lambda_1>": "expense"})
                .reset_index()
            )
            df_resampled["expense"] = -df_resampled["expense"]

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=df_resampled["date"],
                    y=df_resampled["income"],
                    mode="lines+markers",
                    name="Income",
                    line=dict(color="green"),
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=df_resampled["date"],
                    y=df_resampled["expense"],
                    mode="lines+markers",
                    name="Expense",
                    line=dict(color="red"),
                )
            )
            fig.update_layout(
                title="Monthly Income vs. Expense",
                xaxis_title="Month",
                yaxis_title="Amount (₹)",
                hovermode="x unified",
            )
            return fig
        except Exception as e:
            self.logger.error(f"Error generating trend chart: {e}")
            return None

    def get_category_pie_chart(self, df: pd.DataFrame) -> Optional[go.Figure]:
        """Generate spending by category pie chart."""
        if not self.validate_columns(df, ["amount", "category"]):
            return None
        expenses_df = df[df["amount"] < 0].copy()
        if expenses_df.empty:
            return None
        expenses_df["expense_amount"] = -expenses_df["amount"]
        category_spend = (
            expenses_df.groupby("category")["expense_amount"]
            .sum()
            .reset_index()
            .sort_values(by="expense_amount", ascending=False)
        )
        fig = px.pie(
            df,
            names="category",
            title="Spending Distribution",
            hole=0.3,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        return fig

    def get_main_table(self, df: pd.DataFrame, category_filter: Optional[str] = None) -> Optional[pd.DataFrame]:
        """Prepare DataFrame for main transaction table."""
        if not self.validate_columns(df, self.config.MAIN_TABLE_COLS):
            return None
        df_display = df if category_filter is None else df[df["category"] == category_filter]
        return df_display[self.config.MAIN_TABLE_COLS].rename(columns=self.config.DISPLAY_COLUMNS)

    def get_largest_expenses(self, df: pd.DataFrame, n: int = 10) -> Optional[pd.DataFrame]:
        """Get top N expenses."""
        if not self.validate_columns(df, [self.config.INTERNAL_COLUMNS["transaction_type"], self.config.INTERNAL_COLUMNS["amount"]]):
            return None
        expenses = df[df[self.config.INTERNAL_COLUMNS["transaction_type"]] == "Expense"]
        if expenses.empty:
            return None
        return (
            expenses[self.config.EXPENSE_TABLE_COLS]
            .sort_values(by="amount", ascending=True)
            .head(n)
            .rename(columns=self.config.DISPLAY_COLUMNS | self.config.EXPENSE_RENAME)
        )