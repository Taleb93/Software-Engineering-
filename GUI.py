import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from data.database import TaskRepository

repo = TaskRepository()

STATUS_COLUMNS = ["todo", "in-progress", "done"]
STATUS_LABELS = {
    "todo": "To Do",
    "in-progress": "In Progress",
    "done": "Done"
}

PRIORITY_COLORS = {1: "red", 2: "yellow", 3: "green"}

class TaskGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Productivity App - Task Board")
        self.root.geometry("950x500")

        self.columns = {}
        self._build_ui()
        self._load_tasks()

        # Kontextmenü
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Bearbeiten", command=self.edit_task)
        self.context_menu.add_command(label="Löschen", command=self.delete_task)
        self.selected_task = None

    def _build_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        for i, status in enumerate(STATUS_COLUMNS):
            col_frame = tk.Frame(frame, bd=2, relief="groove", padx=5, pady=5)
            col_frame.grid(row=0, column=i, sticky="nsew", padx=5)
            tk.Label(col_frame, text=STATUS_LABELS[status], font=("Arial", 14, "bold")).pack()

            tree = ttk.Treeview(col_frame, columns=("title", "deadline"), show="tree")
            tree.pack(fill="both", expand=True)
            tree.bind("<Button-3>", self.show_context_menu)
            tree.bind("<Double-Button-1>", self.show_task_details_dbl)

            self.columns[status] = tree

        tk.Button(self.root, text="➕ Create Task", font=("Arial", 12),
                  command=self.open_create_window).pack(pady=5)

        for i in range(len(STATUS_COLUMNS)):
            frame.grid_columnconfigure(i, weight=1)

    def _load_tasks(self):
        self.task_map = {}
        for status in STATUS_COLUMNS:
            tree = self.columns[status]
            for row in tree.get_children():
                tree.delete(row)
            tasks = repo.get_tasks_by_status(status)
            for task in tasks:
                display_text = f"{task.title}"
                if task.deadline_display():
                    display_text += f" (Deadline: {task.deadline_display()})"
                item_id = tree.insert("", "end", text=display_text, tags=(f"prio{task.priority}",))
                tree.tag_configure(f"prio{task.priority}", background=PRIORITY_COLORS[task.priority])
                self.task_map[(status, item_id)] = task

    def move_task(self, current_status):
        tree = self.columns[current_status]
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("No Task Selected", "Select a task to move.")
            return
        task = self.task_map.get((current_status, selection[0]))
        next_index = STATUS_COLUMNS.index(current_status) + 1
        if next_index >= len(STATUS_COLUMNS):
            messagebox.showinfo("Already Done", "Task already completed.")
            return
        new_status = STATUS_COLUMNS[next_index]
        repo.update_task_status(task.id, new_status)
        self._load_tasks()

    # --- Create / Edit Task ---
    def open_create_window(self, task=None):
        win = tk.Toplevel(self.root)
        win.title("Create Task" if task is None else "Edit Task")

        tk.Label(win, text="Title:").grid(row=0, column=0, sticky="w")
        title_entry = tk.Entry(win, width=40)
        title_entry.grid(row=0, column=1)
        if task:
            title_entry.insert(0, task.title)

        tk.Label(win, text="Description:").grid(row=1, column=0, sticky="w")
        desc_entry = tk.Entry(win, width=40)
        desc_entry.grid(row=1, column=1)
        if task:
            desc_entry.insert(0, task.description)

        tk.Label(win, text="Deadline (DD-MM-YYYY or DD.MM.YYYY):").grid(row=2, column=0, sticky="w")
        deadline_entry = tk.Entry(win, width=40)
        deadline_entry.grid(row=2, column=1)
        if task and task.deadline_display():
            deadline_entry.insert(0, task.deadline_display())

        tk.Label(win, text="Priority:").grid(row=3, column=0, sticky="w")
        priority_frame = tk.Frame(win)
        priority_frame.grid(row=3, column=1, pady=5)
        selected_priority = tk.IntVar()
        if task:
            selected_priority.set(task.priority)
        squares = {}
        for prio, color in PRIORITY_COLORS.items():
            sq = tk.Label(priority_frame, bg=color, width=4, height=2, bd=2, relief="solid")
            sq.grid(row=0, column=prio)
            squares[prio] = sq
            # Initial schwarzer Rand, wenn ausgewählt
            sq.config(highlightthickness=2 if selected_priority.get() == prio else 0, highlightbackground="black")

            def on_click(p=prio):
                selected_priority.set(p)
                for s_p, s_lbl in squares.items():
                    s_lbl.config(highlightthickness=2 if s_p == p else 0)

            sq.bind("<Button-1>", lambda e, p=prio: on_click(p))

        def save_task():
            title = title_entry.get().strip()
            description = desc_entry.get().strip()
            deadline_input = deadline_entry.get().strip()
            iso_deadline = None
            if deadline_input:
                for fmt in ("%d-%m-%Y", "%d.%m.%Y", "%Y-%m-%d"):
                    try:
                        iso_deadline = datetime.strptime(deadline_input, fmt).strftime("%Y-%m-%d")
                        break
                    except ValueError:
                        continue
                if iso_deadline is None:
                    messagebox.showerror("Error", "Deadline muss DD-MM-YYYY oder DD.MM.YYYY sein.")
                    return
            priority = selected_priority.get()
            if priority == 0:
                messagebox.showerror("Error", "Bitte eine Priorität wählen.")
                return
            try:
                if task is None:
                    repo.create_task(title=title, description=description, priority=priority, deadline=iso_deadline)
                else:
                    repo.update_task(task.id, title, description, priority, iso_deadline, task.category_id)
                win.destroy()
                self._load_tasks()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Save", command=save_task).grid(row=4, column=1, pady=10)

    # --- Kontextmenü ---
    def show_context_menu(self, event):
        widget = event.widget
        item = widget.identify_row(event.y)
        status = next((s for s, t in self.columns.items() if t == widget), None)
        if status is None:
            return
        task = self.task_map.get((status, item))
        if task:
            self.selected_task = task
            self.context_menu.post(event.x_root, event.y_root)

    def edit_task(self):
        if self.selected_task:
            self.open_create_window(self.selected_task)

    def delete_task(self):
        if not self.selected_task:
            return
        if messagebox.askyesno("Confirm Delete", f"Delete task '{self.selected_task.title}'?"):
            repo.delete_task(self.selected_task.id)
            self._load_tasks()
            self.selected_task = None

    # --- Doppelklick zeigt Details ---
    def show_task_details_dbl(self, event):
        widget = event.widget
        item = widget.identify_row(event.y)
        status = next((s for s, t in self.columns.items() if t == widget), None)
        task = self.task_map.get((status, item))
        if task:
            self._show_details_window(task)

    def _show_details_window(self, task):
        win = tk.Toplevel(self.root)
        win.title(f"Task Details - {task.title}")
        tk.Label(win, text=f"Title: {task.title}", font=("Arial", 12, "bold")).pack(anchor="w")
        tk.Label(win, text=f"Description: {task.description or '-'}").pack(anchor="w")
        tk.Label(win, text=f"Status: {task.status}").pack(anchor="w")
        tk.Label(win, text=f"Deadline: {task.deadline_display() or '-'}").pack(anchor="w")
        tk.Label(win, text=f"Priority: {task.priority}").pack(anchor="w")
        tk.Button(win, text="Close", command=win.destroy).pack(pady=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskGUI(root)
    root.mainloop()
