import sqlite3
import os

# ✅ Absolute path to tasks.db inside /backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "tasks.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            assignee TEXT,
            time TEXT,
            notes TEXT,
            status TEXT DEFAULT 'Pending'
        )
        ''')
        conn.commit()

def save_task(data):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO tasks (task, assignee, time, notes) VALUES (?, ?, ?, ?)",
                  (data["task"], data["assignee"], data["time"], data["notes"]))
        task_id = c.lastrowid
        conn.commit()
        return task_id

def get_tasks(assignee=None):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        if assignee:
            c.execute("SELECT * FROM tasks WHERE assignee=?", (assignee,))
        else:
            c.execute("SELECT * FROM tasks")
        rows = c.fetchall()
        return [{"id": r[0], "task": r[1], "assignee": r[2], "time": r[3], "notes": r[4], "status": r[5]} for r in rows]

def mark_task_as_done(task_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("UPDATE tasks SET status='Done' WHERE id=?", (task_id,))
        conn.commit()

init_db()
