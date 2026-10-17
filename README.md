# Receipt Calculator

A small Python web application for recording shop receipts and
exploring personal spending.

Built with Streamlit, pandas and SQLite.

## Features

- Record a store name, receipt date and amount in CHF.
- Filter receipts by date.
- View total spending, receipt count, mean and median receipt amount.
- Display daily, weekly and monthly spending as bar charts.
- Export filtered receipts as CSV.
- Store receipts in a local SQLite database.

Weekly periods run from Monday to Sunday. Statistics and charts
include only the selected date range, so boundary periods may be partial.

## Requirements

- Python 3.13
- A web browser

## Setup

Clone the repository and open a terminal in its directory.

Create a virtual environment:

```powershell
py -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the tested dependency versions:

```powershell
python -m pip install -r requirements-lock.txt
```

## Run

```powershell
python -m streamlit run app.py
```

Open the local URL displayed in the terminal.

## Project structure

- `app.py`: Streamlit interface.
- `database.py`: database initialization, receipt insertion and retrieval.
- `analysis.py`: summary statistics and spending aggregation.
- `requirements.txt`: direct dependencies.
- `requirements-lock.txt`: pinned environment dependencies.

## Data storage

The application creates `receipts.db` in the project directory.

Amounts are stored as integer cents. Receipt dates use `YYYY-MM-DD`.
Creation timestamps are stored in UTC.

The database is excluded from Git. Back it up separately if you
want to preserve your receipts.

## CSV export

Exports contain the filtered receipts with these columns:

- `date`
- `store`
- `amount_chf`

Files use comma separators, decimal points and UTF-8 with BOM.

## Current limitations

- CHF only.
- No editing or deletion of receipts.
- No authentication; intended for local personal use.
- No automated tests yet.
