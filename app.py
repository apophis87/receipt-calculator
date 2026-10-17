from decimal import Decimal, ROUND_HALF_UP

import pandas as pd
import streamlit as st

from analysis import (
    aggregate_expenses,
    calculate_summary,
    filter_receipts,
)
from ui import (
    render_date_filter,
    render_receipts_table,
    render_summary,
    render_expenses_chart,
    render_grouping_selector,
    render_receipt_form,
)
from database import get_receipts, initialize_database, insert_receipt

from export import receipts_to_csv

st.set_page_config(
    page_title="Receipt Calculator",
    page_icon="🧾",
    layout="wide",
)

initialize_database()

st.title("🧾 Receipt Calculator")
st.write("Registra le ricevute e analizza le tue spese.")

receipt_input = render_receipt_form()

if receipt_input is not None:
    store, amount, receipt_date = receipt_input

    amount_cents = int(
        (Decimal(str(amount)) * 100).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
    )

    try:
        receipt_id = insert_receipt(
            store,
            amount_cents,
            receipt_date,
        )
    except ValueError as error:
        st.error(str(error))
    else:
        st.success(f"Ricevuta n. {receipt_id} salvata.")

st.subheader("Ricevute registrate")

receipts = get_receipts()

if not receipts:
    st.info("Non hai ancora registrato ricevute.")
else:
    receipts_df = pd.DataFrame([dict(receipt) for receipt in receipts])

    receipts_df["receipt_date"] = pd.to_datetime(receipts_df["receipt_date"])
    receipts_df["amount_chf"] = receipts_df["amount_cents"] / 100

    # Filter receipts by date range
    start_date, end_date = render_date_filter(receipts_df)

    try:
        filtered_df = filter_receipts(
            receipts_df,
            start_date,
            end_date,
        )
    except ValueError as error:
        st.error(str(error))
        st.stop()

    if filtered_df.empty:
        st.info("Non ci sono ricevute nel periodo selezionato.")
        st.stop()

    # Calculate summary statistics
    summary = calculate_summary(filtered_df["amount_cents"].tolist())

    render_summary(summary)
    render_receipts_table(filtered_df)

    # Export filtered receipts to CSV
    csv_data = receipts_to_csv(filtered_df)

    st.download_button(
        label="Scarica ricevute CSV",
        data=csv_data,
        file_name=f"receipts_{start_date}_{end_date}.csv",
        mime="text/csv",
    )

    frequency = render_grouping_selector()

    expenses = aggregate_expenses(
        filtered_df,
        frequency,
        start_date,
        end_date,
    )

    render_expenses_chart(expenses, frequency)
