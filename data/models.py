from datetime import datetime

class Task:
    #Datenmodell für einen Task mit optionaler Kategorie.
    def __init__(self, id, title, description, status, priority, deadline, category_id=None, category_name=None, category_color=None):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.deadline = deadline  # ISO-Format YYYY-MM-DD
        self.category_id = category_id
        self.category_name = category_name
        self.category_color = category_color

    def deadline_display(self):
        """Gibt Deadline als DD-MM-YYYY zurück, leer wenn None"""
        if self.deadline:
            try:
                return datetime.strptime(self.deadline, "%Y-%m-%d").strftime("%d-%m-%Y")
            except:
                return self.deadline
        return ""
