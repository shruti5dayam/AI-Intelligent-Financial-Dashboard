# AI Intelligent Financial Dashboard

A Python and Streamlit-based financial automation dashboard that processes uploaded bank statements into mapped transactions, Trial Balance, and Profit & Loss reports.

## Features

- Upload multiple bank statement files
- Detect metadata such as store, brand, bank account, and date range
- Select report scope using filters
- Parse bank feed rules
- Apply deterministic GL mapping
- Enrich transactions with Chart of Accounts
- Generate Trial Balance
- Generate Profit & Loss
- Show executive dashboard KPIs
- Review mapped transactions
- Review unmatched and missing COA exceptions

## Tech Stack

- Python
- Pandas
- Streamlit
- Excel / CSV
- JSON rules
- Modular financial processing pipeline

## How to Run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run src/app.py