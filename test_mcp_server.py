"""Tests for the MCP server. Run with: python -m unittest -v

These tests start the real MCP server as a subprocess and talk
to it with a real MCP client (initialize, list_tools, call_tool),
so they prove the server actually speaks MCP — not just that the
underlying functions work.
"""

import asyncio
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = Path(__file__).resolve().parent


class TestMcpServer(unittest.IsolatedAsyncioTestCase):
    async def test_mcp_tools_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            expenses_file = str(Path(tmp) / "expenses.json")
            env = dict(os.environ)
            env["EXPENSES_FILE"] = expenses_file
            params = StdioServerParameters(
                command=sys.executable,
                args=[str(HERE / "mcp_server.py")],
                env=env,
            )
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    tools = await session.list_tools()
                    names = {tool.name for tool in tools.tools}
                    self.assertEqual(
                        names,
                        {"add_expense", "list_expenses", "total_spent",
                         "summary_by_category", "delete_expense"},
                    )

                    added = await session.call_tool(
                        "add_expense",
                        {"amount": 500, "category": "food",
                         "note": "Lunch", "date": "2026-11-08"},
                    )
                    added_data = json.loads(added.content[0].text)
                    self.assertEqual(added_data["id"], 1)
                    self.assertEqual(added_data["amount"], 500)

                    await session.call_tool(
                        "add_expense",
                        {"amount": 1200, "category": "transport",
                         "note": "Bus", "date": "2026-11-08"},
                    )

                    total = await session.call_tool("total_spent", {})
                    self.assertEqual(json.loads(total.content[0].text),
                                     {"total": 1700})

                    summary = await session.call_tool(
                        "summary_by_category", {})
                    self.assertEqual(
                        json.loads(summary.content[0].text),
                        {"food": 500, "transport": 1200},
                    )

                    listed = await session.call_tool("list_expenses", {})
                    self.assertEqual(
                        len(json.loads(listed.content[0].text)["expenses"]),
                        2)

                    deleted = await session.call_tool(
                        "delete_expense", {"expense_id": 2})
                    self.assertEqual(
                        json.loads(deleted.content[0].text),
                        {"deleted": True, "id": 2})


if __name__ == "__main__":
    unittest.main()
