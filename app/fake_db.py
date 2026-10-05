"""
FAKE DATABASE (temporary)
--------------------------
A hardcoded list standing in for a real database, so we can build and test
the query agent's logic before wiring up SQLite + MCP in Phase 3.
"""

EXPENSES = [
    {"category": "groceries", "amount": 450, "date": "2026-09-02"},
    {"category": "transport", "amount": 120, "date": "2026-09-03"},
    {"category": "food",      "amount": 300, "date": "2026-09-05"},
    {"category": "food",      "amount": 250, "date": "2026-09-14"},
    {"category": "groceries", "amount": 600, "date": "2026-09-20"},
    {"category": "transport", "amount": 80,  "date": "2026-09-22"},
    {"category": "food",      "amount": 400, "date": "2026-09-25"},
]


def get_all_expenses():
    return EXPENSES