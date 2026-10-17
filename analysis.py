from statistics import mean, median
import pandas as pd


def calculate_summary(amounts_cents: list[int]) -> dict:
    if not amounts_cents:
        return {
            "count": 0,
            "total_cents": 0,
            "mean_cents": None,
            "median_cents": None,
        }

    return {
        "count": len(amounts_cents),
        "total_cents": sum(amounts_cents),
        "mean_cents": mean(amounts_cents),
        "median_cents": median(amounts_cents),
    }


def aggregate_expenses(
    receipts: pd.DataFrame,
    frequency: str,
    start_date,
    end_date,
) -> pd.DataFrame:
    daily_totals = (
        receipts.set_index("receipt_date")["amount_cents"].resample("D").sum()
    )

    # Comprende anche i giorni senza acquisti nel periodo scelto.
    all_days = pd.date_range(start=start_date, end=end_date, freq="D")
    daily_totals = daily_totals.reindex(all_days, fill_value=0)

    totals = daily_totals.resample(frequency).sum()

    return totals.rename("amount_cents").to_frame()
