import tkinter as tk

def show_task_details(parent, task):
    """
    Öffnet ein kleines Fenster, das alle Details eines Tasks anzeigt.

    Args:
        parent: Übergeordnetes Tkinter-Fenster.
        task: Task-Objekt, dessen Details angezeigt werden sollen.
    """

    win = tk.Toplevel(parent)
    win.title(task.title)

    for label, value in [
        ("Title", task.title),
        ("Description", task.description or "-"),
        ("Status", task.status),
        ("Deadline", task.deadline_display() or "-"),
        ("Priority", task.priority),
    ]:
        tk.Label(win, text=f"{label}: {value}").pack(anchor="w")

    tk.Button(win, text="Close", command=win.destroy).pack(pady=5)
