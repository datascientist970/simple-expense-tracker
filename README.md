# Simple Expense Tracker

A small Python command-line app to record daily expenses and see
where your money goes. No external packages needed — only the
Python standard library.

## What it does

- Add an expense with amount, category, note and date
- List all expenses
- Show the total spent
- Show a summary by category
- Delete an expense by id

Data is saved in `expenses.json` next to the script.

## Requirements

- Python 3.10 or newer

## How to run

```bash
# Add an expense
python expense_tracker.py add 500 food "Lunch"

# Add with a specific date
python expense_tracker.py add 1200 transport "Bus" --date 2026-11-08

# List all expenses
python expense_tracker.py list

# Total spent
python expense_tracker.py total

# Summary by category
python expense_tracker.py summary

# Delete expense #2
python expense_tracker.py delete 2
```

Use `--file` to store expenses somewhere else:

```bash
python expense_tracker.py --file my-expenses.json list
```

## Example

```bash
$ python expense_tracker.py add 500 food "Lunch"
Added #1: 500.00 (food) on 2026-11-08 — Lunch

$ python expense_tracker.py add 1200 transport "Bus"
Added #2: 1200.00 (transport) on 2026-11-08 — Bus

$ python expense_tracker.py summary
food             500.00
transport       1200.00
Total           1700.00
```

## Tests

```bash
python -m unittest -v
```

All 6 tests should pass.

## Files

- `expense_tracker.py` — the app (CLI + logic)
- `test_expense_tracker.py` — unit tests
- `expenses.json` — your data, created on first use (not in git)
