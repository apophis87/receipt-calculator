import unittest
from datetime import date

import pandas as pd

from analysis import calculate_summary, aggregate_expenses, filter_receipts


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


class TestFilterReceipts(unittest.TestCase):
    def setUp(self):
        self.receipts = pd.DataFrame(
            {
                "receipt_date": pd.to_datetime(
                    [
                        "2026-10-01",
                        "2026-10-02",
                        "2026-10-03",
                        "2026-10-04",
                    ]
                ),
                "amount_cents": [1000, 2000, 3000, 4000],
            }
        )

    def test_date_boundaries_are_inclusive(self):
        result = filter_receipts(
            self.receipts,
            date(2026, 10, 2),
            date(2026, 10, 3),
        )

        self.assertEqual(
            result["amount_cents"].tolist(),
            [2000, 3000],
        )

    def test_period_without_receipts(self):
        result = filter_receipts(
            self.receipts,
            date(2026, 11, 1),
            date(2026, 11, 30),
        )

        self.assertTrue(result.empty)

    def test_reversed_period_is_rejected(self):
        with self.assertRaises(ValueError):
            filter_receipts(
                self.receipts,
                date(2026, 10, 3),
                date(2026, 10, 2),
            )
