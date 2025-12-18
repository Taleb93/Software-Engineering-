import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from .config import PRIORITY_COLORS

class TaskForm(tk.Toplevel):
    def __init__(self, parent, repo, on_save, task=None):
        super().__init__(parent)
        self.repo = repo
        self.task = task
        self.on_save = on_save

        self.title("Create Task" if task is None else "Edit Task")

        self._build()

    def _build(self):
        tk.Label(self, text="Title:").grid(row=0, column=0, sticky="w")
        self.title_entry = tk.Entry(self, width=40)
        self.title_entry.grid(row=0, column=1)

        tk.Label(self, text="Description:").grid(row=1, column=0, sticky="w")
        self.desc_entry = tk.Entry(self, width=40)
        self.desc_entry.grid(row=1, column=1)

        tk.Label(self, text="Deadline (DD-MM-YYYY):").grid(row=2, column=0, sticky="w")
        self.deadline_entry = tk.Entry(self, width=40)
        self.deadline_entry.grid(row=2, column=1)

        tk.Label(self, text="Priority:").grid(row=3, column=0, sticky="w")
        self.priority = tk.IntVar()
        frame = tk.Frame(self)
        frame.grid(row=3, column=1)

        self.squares = {}
        for p, color in PRIORITY_COLORS.items():
            lbl = tk.Label(frame, bg=color, width=4, height=2, bd=2, relief="solid")
            lbl.grid(row=0, column=p)
            lbl.bind("<Button-1>", lambda e, pr=p: self.select_priority(pr))
            self.squares[p] = lbl

        if self.task:
            self.title_entry.insert(0, self.task.title)
            self.desc_entry.insert(0, self.task.description)
            self.deadline_entry.insert(0, self.task.deadline_display())
            self.select_priority(self.task.priority)

        tk.Button(self, text="Save", command=self.save).grid(row=4, column=1, pady=10)

    def select_priority(self, p):
        self.priority.set(p)
        for k, lbl in self.squares.items():
            lbl.config(highlightthickness=2 if k == p else 0, highlightbackground="black")

    def save(self):
        if not self.priority.get():
            messagebox.showerror("Error", "Bitte Priorität wählen")
            return

        deadline = self.deadline_entry.get().strip()
        iso = None
        if deadline:
            try:
                iso = datetime.strptime(deadline, "%d-%m-%Y").strftime("%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Falsches Datumsformat")
                return

        if self.task:
            self.repo.update_task(
                self.task.id,
                self.title_entry.get(),
                self.desc_entry.get(),
                self.priority.get(),
                iso,
                self.task.category_id
            )
        else:
            self.repo.create_task(
                title=self.title_entry.get(),
                description=self.desc_entry.get(),
                priority=self.priority.get(),
                deadline=iso
            )

        self.on_save()
        self.destroy()
