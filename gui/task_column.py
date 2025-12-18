import tkinter as tk
from tkinter import ttk
from .config import PRIORITY_COLORS

class TaskColumn(tk.Frame):
    def __init__(self, parent, status, label_text, context_cb, dbl_cb, drag_controller, task_map):
        super().__init__(parent, padx=5, pady=5)
        self.status = status
        self.task_map = task_map

        tk.Label(self, text=label_text, font=("Arial", 12, "bold")).pack()

        self.tree = ttk.Treeview(self, show="tree")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<Button-3>", context_cb)
        self.tree.bind("<Double-Button-1>", dbl_cb)

        drag_controller.bind(self.tree, status, task_map)

    def clear(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

    def insert_task(self, task):
        text = task.title
        if task.deadline_display():
            text += f" (Deadline: {task.deadline_display()})"

        item = self.tree.insert("", "end", text=text, tags=(f"prio{task.priority}",))
        self.tree.tag_configure(f"prio{task.priority}", background=PRIORITY_COLORS[task.priority])
        return item
