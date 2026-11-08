#!/usr/bin/env python3
"""MCP server for the Simple Expense Tracker.

Exposes the expense tracker as a Model Context Protocol (MCP)
server, so an MCP client (Claude Desktop, VS Code, Claude Code,
or any other MCP client) can add, list, total, summarise and
delete expenses by calling tools — instead of running the CLI.

Tools:
    add_expense        Add one expense
    list_expenses      List all expenses
    total_spent        Total amount spent
    summary_by_category  Total spent per category
    delete_expense     Delete an expense by id

Resource:
    expenses://all     All expenses as JSON

Run it (after installing dependencies):
    pip install -r requirements.txt
    python mcp_server.py

It speaks MCP over stdio, so a client starts it as a subprocess.
See README.md for a Claude Desktop / VS Code config example.

The expenses file defaults to ``expenses.json`` next to
``expense_tracker.py``. Set ``EXPENSES_FILE`` to use another file,
for example in tests.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from expense_tracker import (
    DEFAULT_FILE,
    add_expense as _add_expense,
    delete_expense as _delete_expense,
    list_expenses as _list_expenses,
    summary_by_category as _summary_by_category,
    total_spent as _total_spent,
)

DATA_FILE = Path(os.environ["EXPENSES_FILE"]) if os.environ.get("EXPENSES_FILE") else DEFAULT_FILE

mcp = FastMCP(
    "simple-expense-tracker",
    instructions=(
        "A simple expense tracker. Use add_expense to record spending, "
        "list_expenses to see all expenses, total_spent for the total, "
        "summary_by_category for totals per category, and delete_expense "
        "to remove one by id."
    ),
)


@mcp.tool()
def add_expense(amount: float, category: str, note: str = "",
                date: str | None = None) -> dict:
    """Add one expense.

    Args:
        amount: Amount spent, must be greater than 0, e.g. 500.
        category: Category, e.g. food, transport, bills.
        note: Short note, e.g. Lunch.
        date: Date as YYYY-MM-DD, defaults to today.
    """
    return _add_expense(DATA_FILE, amount, category, note, date)


@mcp.tool()
def list_expenses() -> dict:
    """List all expenses, oldest first."""
    return {"expenses": _list_expenses(DATA_FILE)}


@mcp.tool()
def total_spent() -> dict:
    """Return the total amount spent across all expenses."""
    return {"total": _total_spent(DATA_FILE)}


@mcp.tool()
def summary_by_category() -> dict:
    """Return total spent per category."""
    return _summary_by_category(DATA_FILE)


@mcp.tool()
def delete_expense(expense_id: int) -> dict:
    """Delete an expense by id. Returns whether it was deleted."""
    deleted = _delete_expense(DATA_FILE, expense_id)
    return {"deleted": deleted, "id": expense_id}


@mcp.resource("expenses://all")
def all_expenses_resource() -> str:
    """All expenses as JSON."""
    return json.dumps(_list_expenses(DATA_FILE), indent=2)


if __name__ == "__main__":
    mcp.run()
