# data/database.py
import sqlite3
from pathlib import Path
from datetime import datetime
from abc import ABC, abstractmethod

from .models import Task

DB_PATH = Path(__file__).parent / "tasks.db"


class AbstractTaskRepository(ABC):
    """Abstraktes Interface für Task-Speicher (DIP/OCP)."""

    @abstractmethod
    def create_task(self, title, description="", status="todo",
                    priority=2, deadline=None, category_id=None):
        pass

    @abstractmethod
    def get_tasks_by_status(self, status):
        pass

    @abstractmethod
    def update_task_status(self, task_id, new_status):
        pass

    @abstractmethod
    def update_task(self, task_id, title, description, priority,
                    deadline, category_id):
        pass

    @abstractmethod
    def delete_task(self, task_id):
        pass


class TaskRepository(AbstractTaskRepository):
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        print(f"[DEBUG] Using database at: {self.db_path.resolve()}")
        self._initialize_database()

    def _connect(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            print("[DEBUG] DB connection successful")
            return conn
        except sqlite3.Error as e:
            print(f"[ERROR] Could not connect to DB: {e}")
            raise

    def _initialize_database(self):
        schema = Path(__file__).parent / "schema.sql"
        if not schema.exists():
            print(f"[ERROR] Schema file not found at: {schema.resolve()}")
            return
        with self._connect() as conn, open(schema, "r") as f:
            conn.executescript(f.read())
            print("[DEBUG] Database initialized or already exists")

    # ---------------- CRUD Operations ----------------

    def create_task(self, title, description="", status="todo", priority=2, deadline=None, category_id=None):
        print(f"[DEBUG] create_task called with: title={title!r}, deadline={deadline!r}")

        if not title or not title.strip():
            raise ValueError("Title is required.")
        if status not in ["todo", "in-progress", "done"]:
            raise ValueError("Invalid status value.")
        if priority not in [1, 2, 3]:
            raise ValueError("Priority must be 1, 2, or 3.")

        if deadline and str(deadline).strip():
            deadline_input = str(deadline).strip()
            iso_deadline = None
            for fmt in ("%d.%m.%Y", "%d-%m-%Y", "%Y-%m-%d"):
                try:
                    iso_deadline = datetime.strptime(deadline_input, fmt).strftime("%Y-%m-%d")
                    break
                except ValueError as e:
                    print(f"[DEBUG] Failed parsing with format {fmt}: {e}")
            if iso_deadline is None:
                raise ValueError("Deadline must be DD.MM.YYYY, DD-MM-YYYY or YYYY-MM-DD.")
            deadline = iso_deadline
        else:
            deadline = None
            print("[DEBUG] No deadline provided, set to None")

        try:
            with self._connect() as conn:
                conn.execute(
                    """INSERT INTO tasks (title, description, status, priority, deadline, created_at, category_id)
                       VALUES (?, ?, ?, ?, ?, datetime('now'), ?)""",
                    (title.strip(), description.strip(), status, priority, deadline, category_id),
                )
                print("[DEBUG] Task inserted successfully")
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to insert task: {e}")
            raise

    def get_tasks_by_status(self, status):
        print(f"[DEBUG] get_tasks_by_status called with: status={status}")
        try:
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
                print(f"[DEBUG] Retrieved {len(rows)} tasks")
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to retrieve tasks: {e}")
            raise

        return [
            Task(
                id=row[0],
                title=row[1],
                description=row[2],
                status=row[3],
                priority=row[4],
                deadline=row[5],
                category_id=row[6],
                category_name=row[7],
                category_color=row[8],
            )
            for row in rows
        ]

    def update_task_status(self, task_id, new_status):
        print(f"[DEBUG] update_task_status called: task_id={task_id}, new_status={new_status}")
        if new_status not in ["todo", "in-progress", "done"]:
            raise ValueError("Invalid status value.")

        try:
            with self._connect() as conn:
                conn.execute(
                    """UPDATE tasks
                       SET status = ?, updated_at = datetime('now')
                       WHERE id = ?""",
                    (new_status, task_id),
                )
                print("[DEBUG] Task status updated successfully")
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to update status: {e}")
            raise

    def update_task(self, task_id, title, description, priority, deadline, category_id):
        print(f"[DEBUG] update_task called: task_id={task_id}, deadline={deadline!r}")

        if deadline and str(deadline).strip():
            deadline_input = str(deadline).strip()
            iso_deadline = None
            for fmt in ("%d.%m.%Y", "%d-%m-%Y", "%Y-%m-%d"):
                try:
                    iso_deadline = datetime.strptime(deadline_input, fmt).strftime("%Y-%m-%d")
                    break
                except ValueError as e:
                    print(f"[DEBUG] Failed parsing with format {fmt}: {e}")
            if iso_deadline is None:
                raise ValueError("Deadline must be DD.MM.YYYY, DD-MM-YYYY or YYYY-MM-DD.")
            deadline = iso_deadline
        else:
            deadline = None
            print("[DEBUG] No deadline provided, set to None")

        try:
            with self._connect() as conn:
                conn.execute(
                    """UPDATE tasks
                       SET title = ?, description = ?, priority = ?, deadline = ?, updated_at = datetime('now'),
                           category_id = ?
                       WHERE id = ?""",
                    (title.strip(), description.strip(), priority, deadline, category_id, task_id),
                )
                print("[DEBUG] Task updated successfully")
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to update task: {e}")
            raise

    def delete_task(self, task_id):
        print(f"[DEBUG] delete_task called: task_id={task_id}")
        try:
            with self._connect() as conn:
                conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                print("[DEBUG] Task deleted successfully")
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to delete task: {e}")
            raise
