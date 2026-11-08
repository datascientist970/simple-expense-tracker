"""Tests for the Simple Expense Tracker. Run with: python -m unittest -v"""

import json
import tempfile
import unittest
from pathlib import Path

from expense_tracker import (
    add_expense,
    delete_expense,
    list_expenses,
    load_expenses,
    summary_by_category,
    total_spent,
)


class TestExpenseTracker(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "expenses.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_add_and_list(self):
        expense = add_expense(self.path, 500, "Food", "Lunch", "2026-11-08")
        self.assertEqual(expense["id"], 1)
        self.assertEqual(expense["amount"], 500)
        self.assertEqual(expense["category"], "food")
        self.assertEqual(len(list_expenses(self.path)), 1)

    def test_total_and_summary(self):
        add_expense(self.path, 500, "food", "Lunch", "2026-11-08")
        add_expense(self.path, 300, "food", "Dinner", "2026-11-08")
        add_expense(self.path, 1200, "transport", "Bus", "2026-11-08")
        self.assertEqual(total_spent(self.path), 2000)
        self.assertEqual(summary_by_category(self.path),
                         {"food": 800, "transport": 1200})

    def test_delete(self):
        add_expense(self.path, 500, "food", "Lunch", "2026-11-08")
        self.assertTrue(delete_expense(self.path, 1))
        self.assertEqual(list_expenses(self.path), [])
        self.assertFalse(delete_expense(self.path, 99))

    def test_negative_amount_rejected(self):
        with self.assertRaises(ValueError):
            add_expense(self.path, -100, "food", "Bad", "2026-11-08")

    def test_empty_file(self):
        self.assertEqual(load_expenses(self.path), [])
        self.assertEqual(total_spent(self.path), 0)
        self.assertEqual(summary_by_category(self.path), {})

    def test_data_is_saved_as_json(self):
        add_expense(self.path, 250, "bills", "Mobile", "2026-11-08")
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(data[0]["note"], "Mobile")


if __name__ == "__main__":
    unittest.main()
