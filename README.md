# Simple Expense Tracker

A small Python command-line app to record daily expenses and see
where your money goes — plus an MCP server, so an AI assistant
can use the same expense tracker through the Model Context
Protocol (MCP).

The CLI needs only the Python standard library. The MCP server
needs the official MCP Python SDK (see `requirements.txt`).

## What it does

- Add an expense with amount, category, note and date
- List all expenses
- Show the total spent
- Show a summary by category
- Delete an expense by id

Data is saved in `expenses.json` next to the script.

## Requirements

- Python 3.10 or newer
- For the MCP server only: `pip install -r requirements.txt`
  (installs `mcp>=1.0,<2`, the official MCP Python SDK)

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

## MCP server

`mcp_server.py` exposes the same expense tracker as a Model
Context Protocol (MCP) server, using the official MCP Python
SDK (`mcp>=1.0,<2`). An MCP client such as Claude Desktop,
VS Code, or Claude Code can then add, list, total, summarise
and delete expenses by calling tools, instead of running the CLI.
The server and the CLI share the same `expenses.json` file.

### Tools

| Tool | What it does |
| --- | --- |
| `add_expense` | Add one expense (amount, category, note, date) |
| `list_expenses` | List all expenses |
| `total_spent` | Total amount spent |
| `summary_by_category` | Total spent per category |
| `delete_expense` | Delete an expense by id |

It also exposes the `expenses://all` resource (all expenses as JSON).

### Run it

```bash
pip install -r requirements.txt
python mcp_server.py
```

The server speaks MCP over stdio, so a client starts it as a
subprocess. Set `EXPENSES_FILE` to use a different data file.

### Connect it to Claude Desktop

Add this to your Claude Desktop config (`claude_desktop_config.json`),
replacing the path with the path to this folder on your machine:

```json
{
  "mcpServers": {
    "simple-expense-tracker": {
      "command": "python",
      "args": ["/path/to/simple-expense-tracker/mcp_server.py"]
    }
  }
}
```

Then restart Claude Desktop and ask it, for example:
"Add 500 for food, lunch" or "How much did I spend in total?"

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

All 7 tests should pass — 6 for the CLI and 1 end-to-end MCP
test, which starts the real server and talks to it with a real
MCP client.

## Files

- `expense_tracker.py` — the app (CLI + logic)
- `test_expense_tracker.py` — unit tests for the CLI
- `mcp_server.py` — the MCP server (5 tools + 1 resource)
- `test_mcp_server.py` — end-to-end test for the MCP server
- `requirements.txt` — `mcp` SDK, needed only for the MCP server
- `.gitignore` — ignores `expenses.json` and `__pycache__`
- `expenses.json` — your data, created on first use (not in git)
