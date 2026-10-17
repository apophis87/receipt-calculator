import pandas as pd


def receipts_to_csv(receipts: pd.DataFrame) -> bytes:
    export_df = receipts[["receipt_date", "store", "amount_cents"]].copy()

    export_df["receipt_date"] = export_df["receipt_date"].dt.strftime("%Y-%m-%d")

    export_df["amount_chf"] = export_df["amount_cents"].map(
        lambda cents: f"{cents // 100}.{cents % 100:02d}"
    )

    export_df = export_df[["receipt_date", "store", "amount_chf"]].rename(
        columns={"receipt_date": "date"}
    )

    return export_df.to_csv(index=False).encode("utf-8-sig")
