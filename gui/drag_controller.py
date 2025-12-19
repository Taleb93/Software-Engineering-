class DragController:
    """
    Ermöglicht Drag & Drop von Tasks zwischen den Status-Spalten.

    Attributes:
        repo: TaskRepository für Status-Updates.
        reload: Callback zum Neuladen der GUI nach Änderungen.
        root: Tkinter-Hauptfenster (für Cursor-Änderungen).
        drag_data: Temporäre Speicherung des gezogenen Tasks.
        columns: Dictionary von Status -> Treeview-Objekten.
    """
    def __init__(self, repo, reload_callback, root):
        self.repo = repo
        self.reload = reload_callback
        self.root = root
        self.drag_data = {"task": None, "from_status": None}

    def bind(self, tree, status, task_map):
        #Bindet Treeview-Events für Drag & Drop.
        tree.bind("<ButtonPress-1>", lambda e: self.start_drag(e, status, task_map))
        tree.bind("<ButtonRelease-1>", self.drop)

    def start_drag(self, event, status, task_map):
        """
        Startet den Drag-Vorgang, wenn ein Task ausgewählt wird.
        Speichert den Task und den Ursprungsstatus in drag_data.
        """
        tree = event.widget
        item = tree.identify_row(event.y)
        if not item:
            return
        self.drag_data["task"] = task_map.get((status, item))
        self.drag_data["from_status"] = status
        tree.selection_set(item)
        self.root.config(cursor="hand2")

    def drop(self, event):
        """
        Beendet den Drag-Vorgang und verschiebt den Task, falls er in eine andere Spalte fällt.
        Aktualisiert die Datenbank und lädt die GUI neu.
        """
        if not self.drag_data["task"]:
            self.reset()
            return

        x, y = event.x_root, event.y_root
        for status, tree in self.columns.items():
            if self._inside(tree, x, y):
                if status != self.drag_data["from_status"]:
                    self.repo.update_task_status(self.drag_data["task"].id, status)
                    self.reload()
                break

        self.reset()

    def _inside(self, widget, x, y):
        #Prüft, ob ein Punkt (x, y) innerhalb eines Widgets liegt.
        return (
            widget.winfo_rootx() <= x <= widget.winfo_rootx() + widget.winfo_width()
            and widget.winfo_rooty() <= y <= widget.winfo_rooty() + widget.winfo_height()
        )

    def set_columns(self, columns):
        #Speichert die Treeview-Spalten für Drag & Drop.
        self.columns = columns

    def reset(self):
        #Setzt drag_data zurück und Cursor auf Standard
        self.drag_data = {"task": None, "from_status": None}
        self.root.config(cursor="")
