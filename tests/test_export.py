import csv
import io
import unittest

import pandas as pd

from export import receipts_to_csv


class TestReceiptsToCsv(unittest.TestCase):
    def setUp(self):
        self.receipts = pd.DataFrame(
            {
                "receipt_date": pd.to_datetime(
                    [
                        "2026-10-17",
                        "2026-10-18",
                    ]
                ),
                "store": ['Caffè, "Centro"', "Coop"],
                "amount_cents": [1255, 2000],
            }
        )

    def test_csv_preserves_values_and_special_characters(self):
        result = receipts_to_csv(self.receipts)

        text = result.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)

        self.assertEqual(
            reader.fieldnames,
            ["date", "store", "amount_chf"],
        )
        self.assertEqual(
            rows,
            [
                {
                    "date": "2026-10-17",
                    "store": 'Caffè, "Centro"',
                    "amount_chf": "12.55",
                },
                {
                    "date": "2026-10-18",
                    "store": "Coop",
                    "amount_chf": "20.00",
                },
            ],
        )

    def test_export_does_not_modify_original_data(self):
        original = self.receipts.copy(deep=True)

        receipts_to_csv(self.receipts)

        pd.testing.assert_frame_equal(self.receipts, original)
