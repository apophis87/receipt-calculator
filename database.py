import sqlite3
from pathlib import Path
from datetime import date

DATABASE_PATH = Path(__file__).resolve().parent / "receipts.db"


def initialize_database():
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY,
                store TEXT NOT NULL CHECK (length(trim(store)) > 0),
                amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
                receipt_date TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


def insert_receipt(store: str, amount_cents: int, receipt_date: date) -> int:
    store = store.strip()

    if not store:
        raise ValueError("Il nome del negozio è obbligatorio.")

    if amount_cents <= 0:
        raise ValueError("L'importo deve essere maggiore di zero.")

    with sqlite3.connect(DATABASE_PATH) as connection:

        cursor = connection.execute(
            """
            INSERT INTO receipts (store, amount_cents, receipt_date)
            VALUES (?, ?, ?)
            """,
            (store, amount_cents, receipt_date.isoformat()),
        )
        receipt_id = cursor.lastrowid

    return receipt_id


def get_receipts() -> list[sqlite3.Row]:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row

        receipts = connection.execute("""
            SELECT id, store, amount_cents, receipt_date
            FROM receipts
            ORDER BY receipt_date DESC, id DESC
            """).fetchall()

    return receipts
