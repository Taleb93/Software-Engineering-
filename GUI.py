import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from data.database import TaskRepository

repo = TaskRepository()

STATUS_COLUMNS = ["todo", "in-progress", "done"]
STATUS_LABELS = {
    "todo": "To Do",
    "in-progress": "In Progress",
    "done": "Done"
}

class TaskGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Productivity App - Task Board")
        self.root.geometry("950x500")

        self.columns = {}
        self._build_ui()
        self._load_tasks()

    def _build_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        for i, status in enumerate(STATUS_COLUMNS):
            col_frame = tk.Frame(frame, bd=2, relief="groove", padx=10, pady=10)
            col_frame.grid(row=0, column=i, sticky="nsew", padx=5)

            tk.Label(col_frame, text=STATUS_LABELS[status], font=("Arial", 14, "bold")).pack()

            listbox = tk.Listbox(col_frame, width=30, height=20)
            listbox.pack(fill="both", expand=True, pady=5)

            btn_move = tk.Button(col_frame, text="→ Move", command=lambda s=status: self.move_task(s))
            btn_move.pack(pady=5)

            self.columns[status] = listbox

        tk.Button(self.root, text="➕ Create Task", font=("Arial", 12),
                  command=self.open_create_window).pack(pady=5)

        self.root.grid_columnconfigure((0, 1, 2), weight=1)

    def _load_tasks(self):
        for status in STATUS_COLUMNS:
            self.columns[status].delete(0, tk.END)
            tasks = repo.get_tasks_by_status(status)
            for task in tasks:  # Task-Objekt
                display_text = f"{task.id} — {task.title}"
                if task.deadline_display():
                    display_text += f" (Deadline: {task.deadline_display()})"
                self.columns[status].insert(tk.END, display_text)
                print(f"[DEBUG] Loaded task: {task.id}, deadline: {task.deadline}")

    def move_task(self, current_status):
        listbox = self.columns[current_status]
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("No Task Selected", "Select a task to move.")
            return
        task_id = int(listbox.get(selection[0]).split(" — ")[0])
        next_status_index = STATUS_COLUMNS.index(current_status) + 1
        if next_status_index >= len(STATUS_COLUMNS):
            messagebox.showinfo("Already Done", "Task already completed.")
            return
        new_status = STATUS_COLUMNS[next_status_index]
        repo.update_task_status(task_id, new_status)
        self._load_tasks()

    def open_create_window(self):
        win = tk.Toplevel(self.root)
        win.title("Create Task")

        tk.Label(win, text="Title:").grid(row=0, column=0, sticky="w")
        title_entry = tk.Entry(win, width=40)
        title_entry.grid(row=0, column=1)

        tk.Label(win, text="Description:").grid(row=1, column=0, sticky="w")
        desc_entry = tk.Entry(win, width=40)
        desc_entry.grid(row=1, column=1)

        tk.Label(win, text="Deadline (DD-MM-YYYY or DD.MM.YYYY):").grid(row=2, column=0, sticky="w")
        deadline_entry = tk.Entry(win, width=40)
        deadline_entry.grid(row=2, column=1)

        tk.Label(win, text="Priority (1-3):").grid(row=3, column=0, sticky="w")
        priority_entry = tk.Entry(win, width=40)
        priority_entry.grid(row=3, column=1)

        def save():
            deadline_input = deadline_entry.get().strip()
            iso_deadline = None
            if deadline_input:
                try:
                    try:
                        iso_deadline = datetime.strptime(deadline_input, "%d-%m-%Y").strftime("%Y-%m-%d")
                    except ValueError:
                        iso_deadline = datetime.strptime(deadline_input, "%d.%m.%Y").strftime("%Y-%m-%d")
                    print(f"[DEBUG] Parsed ISO deadline: {iso_deadline}")
                except ValueError as e:
                    print(f"[DEBUG] Failed parsing deadline: {deadline_input} - {e}")
                    messagebox.showerror("Error", "Deadline muss im Format DD-MM-YYYY oder DD.MM.YYYY sein.")
                    return
            try:
                repo.create_task(
                    title=title_entry.get().strip(),
                    description=desc_entry.get().strip(),
                    priority=int(priority_entry.get() or 2),
                    deadline=iso_deadline
                )
                win.destroy()
                self._load_tasks()
            except Exception as e:
                print(f"[DEBUG] create_task exception: {e}")
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Save", command=save).grid(row=4, column=1, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskGUI(root)
    root.mainloop()
