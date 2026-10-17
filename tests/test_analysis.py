import unittest
from datetime import date

import pandas as pd

from analysis import calculate_summary, aggregate_expenses


class TestCalculateSummary(unittest.TestCase):
    def test_empty_list(self):
        result = calculate_summary([])

        self.assertEqual(result["count"], 0)
        self.assertEqual(result["total_cents"], 0)
        self.assertIsNone(result["mean_cents"])
        self.assertIsNone(result["median_cents"])

    def test_summary_with_outlier(self):
        result = calculate_summary([1000, 1500, 10000])

        self.assertEqual(result["count"], 3)
        self.assertEqual(result["total_cents"], 12500)
        self.assertAlmostEqual(result["mean_cents"], 12500 / 3)
        self.assertEqual(result["median_cents"], 1500)

    def test_median_with_even_number_of_receipts(self):
        result = calculate_summary([3000, 1000, 2000, 4000])

        self.assertEqual(result["median_cents"], 2500)


class TestAggregateExpenses(unittest.TestCase):
    def test_sunday_and_monday_belong_to_different_weeks(self):
        receipts = pd.DataFrame(
            {
                "receipt_date": pd.to_datetime(
                    [
                        "2026-10-04",
                        "2026-10-05",
                    ]
                ),
                "amount_cents": [1255, 2000],
            }
        )

        result = aggregate_expenses(
            receipts,
            "W-SUN",
            date(2026, 10, 4),
            date(2026, 10, 5),
        )

        self.assertEqual(
            result.index.tolist(),
            [
                pd.Timestamp("2026-10-04"),
                pd.Timestamp("2026-10-11"),
            ],
        )
        self.assertEqual(
            result["amount_cents"].tolist(),
            [1255, 2000],
        )
