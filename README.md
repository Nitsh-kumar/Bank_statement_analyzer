# Bank Statement Analyzer

A Python and Streamlit prototype for exploring bank-statement CSV files. It separates ingestion, transaction processing, and dashboard rendering.

## Implemented workflow

Upload CSV → normalize columns → calculate net transaction amounts → apply keyword categories → filter and display charts and tables.

- Income, expense, net cash flow, and average daily spending calculations.
- Date and category filters, monthly trends, and largest-expense views.
- Keyword-based categorization. This is a deterministic rule system, not an LLM classifier.

## Input format

The current mapping is defined in [src/data/config.py](src/data/config.py).

| CSV column | Meaning |
| --- | --- |
| `Date` | Transaction date |
| `Narration` | Transaction description |
| `Withdrawal Amt.` | Debit amount |
| `Deposit Amt.` | Credit amount |

Use synthetic examples first. Use ISO dates and plain numeric amounts to reduce ambiguity:

```csv
Date,Narration,Withdrawal Amt.,Deposit Amt.
2026-01-01,Salary,0,50000
2026-01-02,Supermarket,1200,0
2026-01-03,Uber,250,0
```

The loader calculates `amount = credit - debit`. It currently coerces invalid numeric values to zero and drops unparseable dates.

## Local setup

From the repository root, create and activate a Python virtual environment, then run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run src/main.py
```

Open the local URL printed by Streamlit.

## Source map

- [src/main.py](src/main.py): application entry point.
- [src/data/data_loader.py](src/data/data_loader.py): CSV parsing and categorization.
- [src/data/processor.py](src/data/processor.py): metrics, filtering, and charts.
- [src/display/dashboard.py](src/display/dashboard.py): Streamlit views.
- [tests/test_data_processor.py](tests/test_data_processor.py): existing date-filter and KPI tests.

Run the existing checks with `python -m unittest discover -s tests -v`.

## Current limitations

Opening and closing balances are zero placeholders. The category pie chart does not yet use the calculated expense totals. Neither output should be treated as a reliable financial result until corrected. Date parsing and rejected-row reporting also need work.

Uploaded data uses Streamlit caching. Avoid real statements in shared demonstrations until retention and isolation have been reviewed. See [project status](docs/PROJECT_STATUS.md).

## Validation

This documentation was checked against repository files on 13 October 2026. Builds, application runs, and test suites were not executed during this documentation pass. Commands below describe the intended local workflow, not a verified deployment.
