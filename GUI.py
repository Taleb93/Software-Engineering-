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

        # status -> Listbox
        self.columns: dict[str, tk.Listbox] = {}
        # Listbox -> status (für Drag & Drop / Kontextmenü)
        self.listbox_status: dict[tk.Listbox, str] = {}

        # Daten für Drag & Drop
        self.drag_data = {
            "widget": None,
            "index": None,
            "text": None,
            "status": None,
        }

        # Für Rechtsklick-Kontextmenü
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Delete Task", command=self.delete_selected_task)
        self._context_listbox: tk.Listbox | None = None

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

            # Listbox interaktiv machen (Drag & Drop + Rechtsklick)
            self._make_listbox_interactive(listbox, status)

            btn_move = tk.Button(col_frame, text="→ Move", command=lambda s=status: self.move_task(s))
            btn_move.pack(pady=5)

            self.columns[status] = listbox
            self.listbox_status[listbox] = status

        tk.Button(self.root, text="➕ Create Task", font=("Arial", 12),
                  command=self.open_create_window).pack(pady=5)

        self.root.grid_columnconfigure((0, 1, 2), weight=1)

    # ---------- Drag & Drop + Kontextmenü-Bindings ----------

    def _make_listbox_interactive(self, listbox: tk.Listbox, status: str):
        # Linksklick starten → möglicher Drag-Start
        listbox.bind("<ButtonPress-1>", lambda e, s=status: self.on_start_drag(e, s))
        # Mausbewegung mit gedrückter Taste (optional; hier nur für Cursor)
        listbox.bind("<B1-Motion>", self.on_drag_motion)
        # Maustaste loslassen → Drop
        listbox.bind("<ButtonRelease-1>", self.on_drop)

        # Rechtsklick-Kontextmenü
        listbox.bind("<Button-3>", self.show_context_menu)  # Windows / Linux
        listbox.bind("<Button-2>", self.show_context_menu)  # häufig macOS

    # ---------- Laden der Aufgaben ----------

    def _load_tasks(self):
        for status in STATUS_COLUMNS:
            self.columns[status].delete(0, tk.END)
            tasks = repo.get_tasks_by_status(status)
            for t in tasks:
                task_id, title, desc, priority, deadline, cat_id, cat_name, cat_color = t
                if deadline:
                    try:
                        deadline_display = datetime.strptime(deadline, "%Y-%m-%d").strftime("%d-%m-%Y")
                    except Exception:
                        deadline_display = deadline
                else:
                    deadline_display = ""
                display_text = f"{task_id} — {title}"
                if deadline_display:
                    display_text += f" (Deadline: {deadline_display})"
                self.columns[status].insert(tk.END, display_text)

    # ---------- Move-Button (wie bisher) ----------

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

    # ---------- Drag & Drop Logik ----------

    def on_start_drag(self, event: tk.Event, status: str):
        """Start des Drag-Vorgangs: merken, von wo wir ziehen."""
        widget: tk.Listbox = event.widget
        index = widget.nearest(event.y)

        if index < 0 or index >= widget.size():
            return

        # Auswahl in der Listbox setzen
        widget.selection_clear(0, tk.END)
        widget.selection_set(index)

        text = widget.get(index)

        self.drag_data["widget"] = widget
        self.drag_data["index"] = index
        self.drag_data["text"] = text
        self.drag_data["status"] = status

        # optional visuelles Feedback
        self.root.config(cursor="hand2")

    def on_drag_motion(self, event: tk.Event):
        """Während des Draggens (hier nur Cursor-Anzeige)."""
        # Hier könnte man z.B. noch ein 'Ghost'-Label zeigen – für euch reicht der Cursor.
        pass

    def on_drop(self, event: tk.Event):
        """Maus losgelassen → Element in Ziel-Listbox einfügen."""
        if self.drag_data["widget"] is None:
            # kein aktiver Drag
            self.root.config(cursor="")
            return

        source_widget: tk.Listbox = self.drag_data["widget"]
        source_index: int = self.drag_data["index"]
        text: str = self.drag_data["text"]
        source_status: str = self.drag_data["status"]

        target_widget: tk.Listbox = event.widget
        target_status = self.listbox_status.get(target_widget)
        if target_status is None:
            # nicht auf einer gültigen Listbox gelandet
            self._reset_drag()
            return

        # Zielposition in der Ziel-Listbox bestimmen
        if target_widget.size() == 0:
            target_index = 0
        else:
            target_index = target_widget.nearest(event.y)
            if target_index < 0:
                target_index = 0
            if target_index > target_widget.size():
                target_index = target_widget.size()

        # Element aus Quell-Listbox entfernen
        source_widget.delete(source_index)

        # Falls gleiche Listbox und Element wurde nach unten gezogen, Index anpassen
        if source_widget is target_widget and target_index > source_index:
            target_index -= 1

        # Element in Ziel-Listbox einfügen
        if target_widget.size() == 0 or target_index >= target_widget.size():
            target_widget.insert(tk.END, text)
        else:
            target_widget.insert(target_index, text)

        # Status in DB aktualisieren, falls Spalte gewechselt
        if source_status != target_status:
            try:
                task_id = int(text.split(" — ")[0])
                repo.update_task_status(task_id, target_status)
            except Exception as e:
                messagebox.showerror("Error", f"Could not update task status:\n{e}")

        self._reset_drag()

    def _reset_drag(self):
        """Drag-Daten zurücksetzen."""
        self.drag_data = {
            "widget": None,
            "index": None,
            "text": None,
            "status": None,
        }
        self.root.config(cursor="")

    # ---------- Rechtsklick-Kontextmenü ----------

    def show_context_menu(self, event: tk.Event):
        """Kontextmenü für die angeklickte Aufgabe anzeigen."""
        widget: tk.Listbox = event.widget
        if widget.size() == 0:
            return

        index = widget.nearest(event.y)
        if index < 0 or index >= widget.size():
            return

        # Aufgabe anklicken/selektieren
        widget.selection_clear(0, tk.END)
        widget.selection_set(index)

        self._context_listbox = widget

        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def delete_selected_task(self):
        """Task aus DB und aus der Listbox löschen (Rechtsklick-Menü)."""
        if self._context_listbox is None:
            return

        widget = self._context_listbox
        selection = widget.curselection()
        if not selection:
            return

        index = selection[0]
        text = widget.get(index)

        try:
            task_id = int(text.split(" — ")[0])
        except ValueError:
            messagebox.showerror("Error", "Could not parse task id.")
            return

        # Nachfrage zur Sicherheit
        if not messagebox.askyesno("Delete Task", f"Do you really want to delete task #{task_id}?"):
            return

        try:
            # WICHTIG: hier evtl. Methodennamen an eure DB-Klasse anpassen
            repo.delete_task(task_id)
        except AttributeError:
            messagebox.showerror(
                "Error",
                "TaskRepository.delete_task(task_id) ist nicht implementiert.\n"
                "Bitte in data/database.py hinzufügen."
            )
            return
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete task:\n{e}")
            return

        # Aus der GUI-Listbox entfernen
        widget.delete(index)
        self._context_listbox = None

    # ---------- Create-Task-Fenster ----------

    def open_create_window(self):
        win = tk.Toplevel(self.root)
        win.title("Create Task")

        tk.Label(win, text="Title:").grid(row=0, column=0, sticky="w")
        title_entry = tk.Entry(win, width=40)
        title_entry.grid(row=0, column=1)

        tk.Label(win, text="Description:").grid(row=1, column=0, sticky="w")
        desc_entry = tk.Entry(win, width=40)
        desc_entry.grid(row=1, column=1)

        tk.Label(win, text="Deadline (DD-MM-YYYY):").grid(row=2, column=0, sticky="w")
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
                    iso_deadline = datetime.strptime(deadline_input, "%d-%m-%Y").strftime("%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Error", "Deadline muss im Format DD-MM-YYYY sein.")
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
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Save", command=save).grid(row=4, column=1, pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskGUI(root)
    root.mainloop()
