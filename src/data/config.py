from typing import Dict, List

class AppConfig:
    """Configuration for the Bank Statement Analyzer."""
    
    # Column mappings (source column in CSV -> internal column name)
    COLUMN_MAPPING: Dict[str, str] = {
        "date": "Date",               # CSV column name for date
        "description": "Narration",    # CSV column name for description
        "debit": "Withdrawal Amt.",   # CSV column name for debit
        "credit": "Deposit Amt.",      # CSV column name for credit
    }

    # Internal column names (used in DataFrame)
    INTERNAL_COLUMNS: Dict[str, str] = {
        "date": "date",
        "description": "description",
        "debit": "debit",
        "credit": "credit",
        "amount": "amount",
        "transaction_type": "transaction_type",
        "category": "category",
    }

    # Display column names for UI
    DISPLAY_COLUMNS: Dict[str, str] = {
        "date": "Date",
        "description": "Description",
        "debit": "Debit (-)",
        "credit": "Credit (+)",
        "amount": "Amount",
        "transaction_type": "Type",
        "category": "Category",
    }

    # Columns to display in the main table
    MAIN_TABLE_COLS: List[str] = [
        "date", "description", "category", "debit", "credit", "amount", "transaction_type"
    ]

    # Columns to display in the expenses table
    EXPENSE_TABLE_COLS: List[str] = ["date", "description", "category", "amount"]

    # Renaming for expenses table
    EXPENSE_RENAME: Dict[str, str] = {"amount": "Expense Amount"}

    # Categorization keywords
    CATEGORIZATION_RULES: Dict[str, List[str]] = {
        # "Salary": ["salary", "paycheck", "payroll"],
        "Groceries": ["grocery", "supermarket", "walmart", "tesco", "safeway"],
        "Dining Out": ["restaurant", "cafe", "dining", "food", "starbucks", "mcdonalds"],
        "Rent/Mortgage": ["rent", "mortgage"],
        "Utilities": ["gas", "electricity", "water", "utility", "phone", "internet", "mobile"],
        "Transport": ["highways", "uber", "lyft", "taxi", "fuel", "petrol", "train", "bus"  , "bpcl"],
        "Shopping": ["amazon", "shopping", "store", "clothes" ,"play" , 'rzp' , 'billpay' ],
        "Entertainment": ["entertainment", "cinema", "movies", "concert" , 'Netflix' , 'apple'],
        "Investment Income/Interest": ["interest", "div" ,"indian clearing corp"  , "neft"  , "grow"],
        "Refunds": ["refund"],
        "Transfers/Payments": ["transfer", "payment"],
        "ATM Withdrawal": ["atm", "withdrawal"],
    }

    DEFAULT_CATEGORY: str = "Uncategorized"
    APP_TITLE: str = "Bank Statement Analyzer"
    PAGE_ICON: str = "💰"
    LAYOUT: str = "wide"
    DEFAULT_DAYS_RANGE: int = 90