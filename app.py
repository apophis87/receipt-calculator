from decimal import Decimal, ROUND_HALF_UP

import pandas as pd
import streamlit as st

from analysis import aggregate_expenses, calculate_summary
from database import get_receipts, initialize_database, insert_receipt

st.set_page_config(
    page_title="Receipt Calculator",
    page_icon="🧾",
    layout="wide",
)

initialize_database()

st.title("🧾 Receipt Calculator")
st.write("Registra le ricevute e analizza le tue spese.")

with st.form("receipt_form", clear_on_submit=True):
    store = st.text_input("Negozio")

    amount = st.number_input("Importo (CHF)", min_value=0.0, step=0.01, format="%.2f")

    receipt_date = st.date_input("Data della ricevuta")

    submitted = st.form_submit_button("Salva ricevuta")

if submitted:
    amount_cents = int(
        (Decimal(str(amount)) * 100).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
    )

    try:
        receipt_id = insert_receipt(store, amount_cents, receipt_date)
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
    st.subheader("Periodo da analizzare")

    start_col, end_col = st.columns(2)

    start_date = start_col.date_input(
        "Dal",
        value=receipts_df["receipt_date"].min().date(),
        key="filter_start_date",
    )

    end_date = end_col.date_input(
        "Al",
        value=receipts_df["receipt_date"].max().date(),
        key="filter_end_date",
    )

    if start_date > end_date:
        st.error("La data iniziale deve precedere o coincidere con quella finale.")
        st.stop()

    receipt_dates = receipts_df["receipt_date"].dt.date

    filtered_df = receipts_df.loc[
        (receipt_dates >= start_date) & (receipt_dates <= end_date)
    ].copy()

    if filtered_df.empty:
        st.info("Non ci sono ricevute nel periodo selezionato.")
        st.stop()

    # Calculate summary statistics
    summary = calculate_summary(filtered_df["amount_cents"].tolist())

    count_col, total_col, mean_col, median_col = st.columns(4)

    count_col.metric("Ricevute", summary["count"])
    total_col.metric(
        "Totale",
        f'{summary["total_cents"] / 100:.2f} CHF',
    )
    mean_col.metric(
        "Media per ricevuta",
        f'{summary["mean_cents"] / 100:.2f} CHF',
    )
    median_col.metric(
        "Mediana per ricevuta",
        f'{summary["median_cents"] / 100:.2f} CHF',
    )

    st.dataframe(
        filtered_df,
        column_order=["receipt_date", "store", "amount_chf"],
        column_config={
            "receipt_date": st.column_config.DateColumn("Data"),
            "store": st.column_config.TextColumn("Negozio"),
            "amount_chf": st.column_config.NumberColumn(
                "Importo (CHF)",
                format="%.2f",
            ),
        },
        hide_index=True,
        width="stretch",
    )

    # Export filtered receipts to CSV
    export_df = filtered_df[["receipt_date", "store", "amount_cents"]].copy()

    export_df["receipt_date"] = export_df["receipt_date"].dt.strftime("%Y-%m-%d")

    export_df["amount_chf"] = export_df["amount_cents"].map(
        lambda cents: f"{cents // 100}.{cents % 100:02d}"
    )

    export_df = export_df[["receipt_date", "store", "amount_chf"]].rename(
        columns={"receipt_date": "date"}
    )

    csv_data = export_df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="Scarica ricevute CSV",
        data=csv_data,
        file_name=f"receipts_{start_date}_{end_date}.csv",
        mime="text/csv",
    )

    st.subheader("Andamento delle spese")

    grouping = st.selectbox(
        "Raggruppamento",
        options=["Giorno", "Settimana", "Mese"],
    )

    frequencies = {
        "Giorno": "D",
        "Settimana": "W-SUN",
        "Mese": "MS",
    }

    expenses = aggregate_expenses(
        filtered_df,
        frequencies[grouping],
        start_date,
        end_date,
    )

    expenses["Spesa (CHF)"] = expenses["amount_cents"] / 100

    st.bar_chart(
        expenses[["Spesa (CHF)"]],
        x_label="Periodo",
        y_label="Spesa (CHF)",
    )

    if grouping == "Settimana":
        st.caption(
            "Settimane da lunedì a domenica, indicate dalla data della domenica."
        )

    st.caption(
        "Ogni barra comprende solo le date del periodo selezionato. "
        "La prima e l'ultima settimana o mese possono essere parziali."
    )
