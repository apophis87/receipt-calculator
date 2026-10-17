import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

import database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)

        test_database_path = Path(temporary_directory.name) / "receipts.db"

        database_patch = patch.object(
            database,
            "DATABASE_PATH",
            test_database_path,
        )
        database_patch.start()
        self.addCleanup(database_patch.stop)

        database.initialize_database()

    def test_insert_and_read_receipt(self):
        receipt_id = database.insert_receipt(
            " L'Angolo ",
            1255,
            date(2026, 10, 17),
        )

        receipts = database.get_receipts()

        self.assertEqual(len(receipts), 1)
        self.assertEqual(receipts[0]["id"], receipt_id)
        self.assertEqual(receipts[0]["store"], "L'Angolo")
        self.assertEqual(receipts[0]["amount_cents"], 1255)
        self.assertEqual(receipts[0]["receipt_date"], "2026-10-17")

    def test_invalid_amounts_are_not_saved(self):
        for amount in [0, -100, 1255.5, True]:
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    database.insert_receipt(
                        "Coop",
                        amount,
                        date(2026, 10, 17),
                    )

        self.assertEqual(database.get_receipts(), [])

    def test_blank_store_is_not_saved(self):
        with self.assertRaises(ValueError):
            database.insert_receipt(
                "   ",
                1255,
                date(2026, 10, 17),
            )

        self.assertEqual(database.get_receipts(), [])
