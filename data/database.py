import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "tasks.db"


class TaskRepository:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._initialize_database()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _initialize_database(self):
        schema = Path(__file__).parent / "schema.sql"
        with self._connect() as conn, open(schema, "r") as f:
            conn.executescript(f.read())

    # ✅ CRUD Operations
    def create_task(self, title, description="", status="todo", priority=2, deadline=None, category_id=None):
        if not title or not title.strip():
            raise ValueError("Title is required.")

        if status not in ["todo", "in-progress", "done"]:
            raise ValueError("Invalid status value.")

        if priority not in [1, 2, 3]:
            raise ValueError("Priority must be 1, 2, or 3.")

        if deadline:
            try:
                datetime.strptime(deadline, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Deadline must be YYYY-MM-DD.")

        with self._connect() as conn:
            conn.execute(
                """INSERT INTO tasks (title, description, status, priority, deadline, created_at, category_id)
                   VALUES (?, ?, ?, ?, ?, datetime('now'), ?)""",
                (title, description, status, priority, deadline, category_id),
            )

    def get_tasks_by_status(self, status):
        with self._connect() as conn:
            return conn.execute(
                """SELECT t.id, t.title, t.description, t.priority, t.deadline, t.category_id, c.name, c.color
                   FROM tasks t
                   LEFT JOIN categories c ON t.category_id = c.id
                   WHERE t.status = ?
                   ORDER BY t.created_at DESC""",
                (status,),
            ).fetchall()

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
        with self._connect() as conn:
            conn.execute(
                """UPDATE tasks
                   SET title = ?, description = ?, priority = ?, deadline = ?, updated_at = datetime('now'),
                       category_id = ?
                   WHERE id = ?""",
                (title, description, priority, deadline, category_id, task_id),
            )

    def delete_task(self, task_id):
        with self._connect() as conn:
            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
