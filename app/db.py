"""
REAL DATABASE (replaces app/fake_db.py)
----------------------------------------
SQLite instead of an in-memory list. Same shape of data, but now it
actually persists to a file on disk between runs.
"""
import sqlite3
from pathlib import Path

DB_PATH =Path(__file__).parent.parent / "finpilot.db"

def get_connection():
    conn =sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    return conn

def init_db():
    conn =get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
    """)
    conn.commit()

    count =conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
    if count ==0:
        sample =[
             ("groceries", 450, "2026-09-02"),
            ("transport", 120, "2026-09-03"),
            ("food",      300, "2026-09-05"),
            ("food",      250, "2026-09-14"),
            ("groceries", 600, "2026-09-20"),
            ("transport", 80,  "2026-09-22"),
            ("food",      400, "2026-09-25"),
        ]
        conn.executemany(
            "INSERT INTO expenses (category,amount,date) VALUES (?,?,?)",sample

        )
        conn.commit()
    conn.close()

def get_all_expenses() ->list[dict]:
    conn =get_connection()
    rows =conn.execute('SELECT * FROM expenses').fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_expense(category:str,amount:float,date:str)->int:
    conn =get_connection()
    cursor =conn.execute(
        'INSERT INTO expenses (category,amount,date) VALUES (?,?,?)',
        (category,amount,date),
    )
    conn.commit()
    new_id =cursor.lastrowid
    conn.close()
    return new_id

def delete_expense_by_category(category:str)->int:
    conn = get_connection()
    row =conn.execute(
        "SELECT id FROM expenses WHERE category =? LIMIT 1",(category,)
    
    ).fetchone()
    if row is None:
        conn.close()
        return 0
    conn.execute("DELETE FROM expenses WHERE id = ?", (row["id"],))
    conn.commit()
    conn.close()
    return 1

