import streamlit as st
from datetime import datetime, timedelta
from src.data.config import AppConfig
from src.data.data_loader import DataLoader
from src.data.processor import DataProcessor
from src.utils.logger import get_logger
import pandas as pd

class Dashboard:
    """Renders the Streamlit dashboard for the Bank Statement Analyzer."""
    
    def __init__(self, config: AppConfig, data_loader: DataLoader, data_processor: DataProcessor):
        self.config = config
        self.data_loader = data_loader
        self.data_processor = data_processor
        self.logger = get_logger(__name__)

    def run(self):
        """Run the Streamlit application."""
        st.set_page_config(
            page_title=self.config.APP_TITLE,
            page_icon=self.config.PAGE_ICON,
            layout=self.config.LAYOUT,
        )
        st.title(self.config.APP_TITLE)

        # File upload
        uploaded_file = st.file_uploader("Upload your Bank Statement CSV file", type=["csv"])
        if uploaded_file is None:
            st.info("Please upload a CSV file to begin analysis.")
            return

        # Load data
        df = self.data_loader.load_data(uploaded_file)
        if df is None or df.empty:
            if df is not None:
                st.warning("The uploaded CSV file is empty or could not be processed.")
            return

        st.success("File uploaded and processed successfully!")

        # Sidebar filters
        st.sidebar.header("Filters")
        min_date = df["date"].min().date()
        max_date = df["date"].max().date()
        print(type(min_date) , min_date )
        # default_start = max(min_date, max_date - timedelta(days=self.config.DEFAULT_DAYS_RANGE))
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1] if len(date_range) > 1 else date_range[0])

        # Filter data
        df_filtered = self.data_processor.filter_by_date(df, start_date, end_date)
        if df_filtered.empty:
            st.warning("No transactions found in the selected date range.")
            return

        # Display KPIs
        st.header("Summary Metrics")
        kpis = self.data_processor.calculate_kpis(df_filtered, start_date, end_date)
        cols = st.columns(6)
        cols[0].metric("Total Income", f"₹{kpis['total_income']:,.2f}")
        cols[1].metric("Total Expenses", f"₹{kpis['total_expenses']:,.2f}")
        cols[2].metric(
            "Net Cash Flow",
            f"₹{kpis['net_flow']:,.2f}",
            delta=f"{kpis['net_flow']:,.2f}",
            delta_color="normal" if kpis["net_flow"] >= 0 else "inverse",
        )
        cols[3].metric("Avg. Daily Spend", f"₹{kpis['avg_daily_spend']:,.2f}")
        cols[4].metric("Opening Bal.", f"₹{kpis['opening_balance']:,.2f}")
        cols[5].metric("Closing Bal.", f"₹{kpis['closing_balance']:,.2f}")
        st.markdown("---")

        # Visualizations
        st.header("Visualizations")
        viz_cols = st.columns([3, 2])
        with viz_cols[0]:
            st.subheader("Income vs. Expense Trend")
            fig_trend = self.data_processor.get_trend_data(df_filtered)
            if fig_trend:
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("Unable to display trend chart due to missing data.")

        with viz_cols[1]:
            st.subheader("Spending by Category")
            fig_pie = self.data_processor.get_category_pie_chart(df_filtered)
            if fig_pie:
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No expenses found to display category breakdown.")

        st.markdown("---")

        # Transaction table
        st.header("Transaction Details")
        all_categories = ["All"] + sorted(df_filtered["category"].unique().tolist())
        selected_category = st.selectbox("Filter by Category:", all_categories)
        category_filter = None if selected_category == "All" else selected_category
        df_display = self.data_processor.get_main_table(df_filtered, category_filter)
        if df_display is not None:
            st.dataframe(df_display,
                        column_config={
                        "Date": st.column_config.DatetimeColumn(
                            "Date",  # Label for the column
                            format="DD-MMM-YYYY", # Format: Day-Abbreviated Month-Year
                        ),
                        # Optional: Add formatting for currency columns if desired
                        # "Amount": st.column_config.NumberColumn(format="%.2f"),
                        # "Debit (-)": st.column_config.NumberColumn(format="$%.2f"),
                        # "Credit (+)": st.column_config.NumberColumn(format="$%.2f"),
                        }, use_container_width=True)
        else:
            st.error("Unable to display transaction table due to missing columns.")

        # Largest expenses
        st.subheader("Largest Expenses")
        largest_expenses = self.data_processor.get_largest_expenses(df_filtered)
        if largest_expenses is not None:
            st.dataframe(largest_expenses,
                         column_config = {
                        "Date": st.column_config.DatetimeColumn(
                            "Date",  # Label for the column
                            format="DD-MMM-YYYY", # Format: Day-Abbreviated Month-Year
                        )},
                        use_container_width=True)
        else:
            st.info("No expenses found to display.")

        st.markdown("---")
        st.caption("Bank Statement Analyzer v0.1")