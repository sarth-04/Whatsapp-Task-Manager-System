from flask import Flask, render_template, request, redirect, url_for
import sys
import os
import sqlite3

# Add backend path to import db and messaging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from db import get_tasks, mark_task_as_done
from task_handler import send_whatsapp_message

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'backend', 'tasks.db')

@app.route("/")
def index():
    selected_assignee = request.args.get("assignee")
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT DISTINCT assignee FROM tasks")
        assignees = [row[0] for row in c.fetchall()]

        if selected_assignee:
            c.execute("SELECT * FROM tasks WHERE assignee=?", (selected_assignee,))
        else:
            c.execute("SELECT * FROM tasks")
        tasks = c.fetchall()

    return render_template("index.html", tasks=tasks, assignees=assignees, selected_assignee=selected_assignee)

@app.route("/done/<int:task_id>", methods=["POST"])
def mark_done(task_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT assignee, task FROM tasks WHERE id=?", (task_id,))
        row = c.fetchone()

    if row:
        assignee, task = row
        mark_task_as_done(task_id)
        message = f"✅ Task #{task_id} marked as completed.\n📝 Task: {task}\n👤 Assignee: {assignee}"
        send_whatsapp_message(assignee, message)
        send_whatsapp_message(" ", message)  # Replace with admin/user number

    return redirect(url_for("index"))

@app.route("/update/<int:task_id>", methods=["POST"])
def update_notes(task_id):
    new_notes = request.form.get("notes")
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("UPDATE tasks SET notes=? WHERE id=?", (new_notes, task_id))
        c.execute("SELECT assignee, task FROM tasks WHERE id=?", (task_id,))
        row = c.fetchone()

    if row:
        assignee, task = row
        message = f"✏️ Task #{task_id} notes updated.\n📝 Task: {task}\n🧾 New Notes: {new_notes}"
        print("*"*15)
        print(assignee)
        print("*"*15)
        send_whatsapp_message(assignee, message)
        send_whatsapp_message(" ", message)  # Replace with admin/user number

    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True, port=5500)
