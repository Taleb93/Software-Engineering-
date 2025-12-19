import sqlite3
from pathlib import Path
from datetime import datetime
from .models import Task  

DB_PATH = Path(__file__).parent / "tasks.db"

class TaskRepository:
    #Kapselt alle CRUD-Operationen für Tasks in der SQLite-Datenbank.
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._initialize_database()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _initialize_database(self):
        schema = Path(__file__).parent / "schema.sql"
        if not schema.exists():
            print(f"[ERROR] Schema file not found at: {schema.resolve()}")
            return
        with self._connect() as conn, open(schema, "r") as f:
            conn.executescript(f.read())

    # CRUD Operations
    def create_task(self, title, description="", status="todo", priority=2, deadline=None, category_id=None):
        if not title or not title.strip():
            raise ValueError("Title is required.")
        if status not in ["todo", "in-progress", "done"]:
            raise ValueError("Invalid status value.")
        if priority not in [1, 2, 3]:
            raise ValueError("Priority must be 1, 2, or 3.")

        # Deadline in ISO konvertieren
        iso_deadline = None
        if deadline and deadline.strip():
            deadline_input = deadline.strip()
            for fmt in ("%d.%m.%Y", "%d-%m-%Y", "%Y-%m-%d"):
                try:
                    iso_deadline = datetime.strptime(deadline_input, fmt).strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue
            if iso_deadline is None:
                raise ValueError("Deadline must be DD.MM.YYYY, DD-MM-YYYY or YYYY-MM-DD.")

        with self._connect() as conn:
            conn.execute(
                """INSERT INTO tasks (title, description, status, priority, deadline, created_at, category_id)
                   VALUES (?, ?, ?, ?, ?, datetime('now'), ?)""",
                (title.strip(), description.strip(), status, priority, iso_deadline, category_id),
            )

    def get_tasks_by_status(self, status):
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT t.id, t.title, t.description, t.status, t.priority, t.deadline,
                          t.category_id, c.name, c.color
                   FROM tasks t
                   LEFT JOIN categories c ON t.category_id = c.id
                   WHERE t.status = ?
                   ORDER BY t.priority ASC, t.created_at DESC""",
                (status,),
            ).fetchall()

        # Wandelt jede Zeile in ein Task-Objekt um
        tasks = [
            Task(
                id=row[0],
                title=row[1],
                description=row[2],
                status=row[3],
                priority=row[4],
                deadline=row[5],
                category_id=row[6],
                category_name=row[7],
                category_color=row[8]
            )
            for row in rows
        ]
        return tasks

    def update_task_status(self, task_id, new_status):
        if new_status not in ["todo", "in-progress", "done"]:
            raise ValueError("Invalid status value.")
        with self._connect() as conn:
            conn.execute(
                """UPDATE tasks
                   SET status = ?, updated_at = datetime('now')
                   WHERE id = ?""",
                (new_status, task_id),
            )

    def update_task(self, task_id, title, description, priority, deadline, category_id):
        iso_deadline = None
        if deadline and deadline.strip():
            deadline_input = deadline.strip()
            for fmt in ("%d.%m.%Y", "%d-%m-%Y", "%Y-%m-%d"):
                try:
                    iso_deadline = datetime.strptime(deadline_input, fmt).strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue
            if iso_deadline is None:
                raise ValueError("Deadline must be DD.MM.YYYY, DD-MM-YYYY or YYYY-MM-DD.")

        with self._connect() as conn:
            conn.execute(
                """UPDATE tasks
                   SET title = ?, description = ?, priority = ?, deadline = ?, updated_at = datetime('now'),
                       category_id = ?
                   WHERE id = ?""",
                (title.strip(), description.strip(), priority, iso_deadline, category_id, task_id),
            )

    def delete_task(self, task_id):
        with self._connect() as conn:
            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
