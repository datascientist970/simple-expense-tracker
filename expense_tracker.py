#!/usr/bin/env python3
"""Simple Expense Tracker.

A small command-line app to record daily expenses and see where
your money goes. No external packages needed, only the Python
standard library.

Data is stored as JSON in ``expenses.json`` next to this file
(or in the path given with ``--file``).

Usage:
    python expense_tracker.py add 500 food "Lunch"
    python expense_tracker.py add 1200 transport --date 2026-11-08
    python expense_tracker.py list
    python expense_tracker.py summary
    python expense_tracker.py total
    python expense_tracker.py delete 2
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

DEFAULT_FILE = Path(__file__).with_name("expenses.json")


def load_expenses(path: Path) -> list[dict]:
    """Load expenses from a JSON file. Return [] if it does not exist."""
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"Warning: {path} is not valid JSON, starting fresh.", file=sys.stderr)
        return []
    if not isinstance(data, list):
        return []
    return data


def save_expenses(path: Path, expenses: list[dict]) -> None:
    """Save expenses to a JSON file."""
    path.write_text(json.dumps(expenses, indent=2), encoding="utf-8")


def add_expense(path: Path, amount: float, category: str, note: str = "",
                when: str | None = None) -> dict:
    """Add one expense and return it."""
    if amount <= 0:
        raise ValueError("Amount must be greater than 0.")
    expenses = load_expenses(path)
    expense = {
        "id": max((e["id"] for e in expenses), default=0) + 1,
        "amount": round(float(amount), 2),
        "category": category.strip().lower(),
        "note": note.strip(),
        "date": when or date.today().isoformat(),
    }
    expenses.append(expense)
    save_expenses(path, expenses)
    return expense


def list_expenses(path: Path) -> list[dict]:
    """Return all expenses, oldest first."""
    return load_expenses(path)


def total_spent(path: Path) -> float:
    """Return the total of all expenses."""
    return round(sum(e["amount"] for e in load_expenses(path)), 2)


def summary_by_category(path: Path) -> dict[str, float]:
    """Return total spent per category."""
    totals: dict[str, float] = defaultdict(float)
    for expense in load_expenses(path):
        totals[expense["category"]] += expense["amount"]
    return {category: round(amount, 2)
            for category, amount in sorted(totals.items())}


def delete_expense(path: Path, expense_id: int) -> bool:
    """Delete an expense by id. Return True if something was deleted."""
    expenses = load_expenses(path)
    kept = [e for e in expenses if e["id"] != expense_id]
    if len(kept) == len(expenses):
        return False
    save_expenses(path, kept)
    return True


def _print_expenses(expenses: list[dict]) -> None:
    if not expenses:
        print("No expenses yet. Add one with: python expense_tracker.py add 500 food \"Lunch\"")
        return
    print(f"{'ID':<4} {'Date':<12} {'Category':<14} {'Amount':>10}  Note")
    print("-" * 60)
    for expense in expenses:
        print(f"{expense['id']:<4} {expense['date']:<12} "
              f"{expense['category']:<14} {expense['amount']:>10.2f}  {expense['note']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Simple Expense Tracker")
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE,
                        help="JSON file to store expenses in (default: expenses.json)")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="Add an expense")
    add.add_argument("amount", type=float, help="Amount spent, e.g. 500")
    add.add_argument("category", help="Category, e.g. food, transport, bills")
    add.add_argument("note", nargs="?", default="", help="Short note, e.g. Lunch")
    add.add_argument("--date", default=None, help="Date YYYY-MM-DD (default: today)")

    sub.add_parser("list", help="List all expenses")
    sub.add_parser("total", help="Show the total spent")
    sub.add_parser("summary", help="Show total spent per category")

    delete = sub.add_parser("delete", help="Delete an expense by id")
    delete.add_argument("id", type=int, help="Expense id from the list command")

    args = parser.parse_args(argv)

    if args.command == "add":
        try:
            expense = add_expense(args.file, args.amount, args.category,
                                  args.note, args.date)
        except ValueError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1
        print(f"Added #{expense['id']}: {expense['amount']:.2f} "
              f"({expense['category']}) on {expense['date']} — {expense['note']}")
    elif args.command == "list":
        _print_expenses(list_expenses(args.file))
    elif args.command == "total":
        print(f"Total spent: {total_spent(args.file):.2f}")
    elif args.command == "summary":
        summary = summary_by_category(args.file)
        if not summary:
            print("No expenses yet.")
        else:
            for category, amount in summary.items():
                print(f"{category:<14} {amount:>10.2f}")
            print(f"{'Total':<14} {total_spent(args.file):>10.2f}")
    elif args.command == "delete":
        if delete_expense(args.file, args.id):
            print(f"Deleted expense #{args.id}.")
        else:
            print(f"No expense with id {args.id}.", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
