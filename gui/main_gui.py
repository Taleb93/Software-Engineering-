import tkinter as tk
from data.database import TaskRepository
from .config import STATUS_COLUMNS, STATUS_LABELS
from .task_column import TaskColumn
from .task_form import TaskForm
from .task_details import show_task_details
from .drag_controller import DragController

class TaskGUI:
    def __init__(self, root):
        self.root = root
        self.repo = TaskRepository()
        self.task_map = {}
        self.columns = {}
        self.task_columns = {}  # <-- Hier speichern wir die TaskColumn-Objekte

        self.drag = DragController(self.repo, self.load_tasks, root)

        self._build()
        self.load_tasks()

    def _build(self):
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True)

        for i, status in enumerate(STATUS_COLUMNS):
            col = TaskColumn(
                frame,
                status,
                STATUS_LABELS[status],
                self.show_context_menu,
                self.show_details,
                self.drag,
                self.task_map
            )
            col.grid(row=0, column=i, sticky="nsew")
            self.columns[status] = col.tree
            self.task_columns[status] = col  # <-- speichern

        self.drag.set_columns(self.columns)

        tk.Button(self.root, text="➕ Create Task",
                  command=lambda: TaskForm(self.root, self.repo, self.load_tasks)).pack(pady=5)

        for i in range(len(STATUS_COLUMNS)):
            frame.grid_columnconfigure(i, weight=1)

    def load_tasks(self):
        self.task_map.clear()
        for status in STATUS_COLUMNS:
            task_column_obj = self.task_columns[status]  # TaskColumn-Objekt
            task_column_obj.clear()
            for task in self.repo.get_tasks_by_status(status):
                item = task_column_obj.insert_task(task)
                self.task_map[(status, item)] = task

    def show_context_menu(self, event):
        pass  # optional Erweiterung

    def show_details(self, event):
        tree = event.widget
        item = tree.identify_row(event.y)
        status = next(s for s, t in self.columns.items() if t == tree)
        task = self.task_map.get((status, item))
        if task:
            show_task_details(self.root, task)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("950x500")
    root.title("Productivity App")
    TaskGUI(root)
    root.mainloop()
