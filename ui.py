from datetime import date

import pandas as pd
import streamlit as st


def render_date_filter(
    receipts: pd.DataFrame,
) -> tuple[date, date]:
    st.subheader("Periodo da analizzare")

    start_col, end_col = st.columns(2)

    start_date = start_col.date_input(
        "Dal",
        value=receipts["receipt_date"].min().date(),
        key="filter_start_date",
    )

    end_date = end_col.date_input(
        "Al",
        value=receipts["receipt_date"].max().date(),
        key="filter_end_date",
    )

    return start_date, end_date


def render_summary(summary: dict) -> None:
    count_col, total_col, mean_col, median_col = st.columns(4)

    count_col.metric("Ricevute", summary["count"])
    total_col.metric(
        "Totale",
        f'{summary["total_cents"] / 100:.2f} CHF',
    )

    for column, label, value in [
        (mean_col, "Media per ricevuta", summary["mean_cents"]),
        (median_col, "Mediana per ricevuta", summary["median_cents"]),
    ]:
        column.metric(
            label,
            "—" if value is None else f"{value / 100:.2f} CHF",
        )


def render_receipts_table(receipts: pd.DataFrame) -> None:
    st.dataframe(
        receipts,
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


def render_grouping_selector() -> str:
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

    return frequencies[grouping]


def render_expenses_chart(
    expenses: pd.DataFrame,
    frequency: str,
) -> None:
    chart_data = pd.DataFrame(
        {
            "Spesa (CHF)": expenses["amount_cents"] / 100,
        }
    )

    st.bar_chart(
        chart_data,
        x_label="Periodo",
        y_label="Spesa (CHF)",
    )

    if frequency == "W-SUN":
        st.caption(
            "Settimane da lunedì a domenica, " "indicate dalla data della domenica."
        )

    st.caption(
        "Ogni barra comprende solo le date del periodo selezionato. "
        "La prima e l'ultima settimana o mese possono essere parziali."
    )


def render_receipt_form() -> tuple[str, float, date] | None:
    st.subheader("Nuova ricevuta")

    with st.form("receipt_form", clear_on_submit=True):
        store = st.text_input("Negozio")

        amount = st.number_input(
            "Importo (CHF)",
            min_value=0.0,
            step=0.01,
            format="%.2f",
        )

        receipt_date = st.date_input("Data della ricevuta")

        submitted = st.form_submit_button("Salva ricevuta")

    if submitted:
        return store, amount, receipt_date

    return None
