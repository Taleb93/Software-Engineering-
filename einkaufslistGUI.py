import tkinter as tk
from tkinter import messagebox

class Item:
    """
    Repräsentiert einen einzelnen Einkaufsartikel.
    """
    def __init__(self, name: str, quantity: int = 1):
        self.name = name
        self.quantity = quantity
        self.bought = False

    def mark_bought(self):
        self.bought = True

    def __str__(self):
        status = "✔" if self.bought else " "
        return f"[{status}] {self.name} (Menge: {self.quantity})"


class ShoppingList:
    """
    Verwalten der gesamten Einkaufsliste.
    """
    def __init__(self):
        self.items: list[Item] = []

    def add_item(self, name: str, quantity: int = 1):
        item = Item(name, quantity)
        self.items.append(item)

    def remove_item(self, index: int) -> bool:
        if 0 <= index < len(self.items):
            del self.items[index]
            return True
        return False

    def mark_item_bought(self, index: int) -> bool:
        if 0 <= index < len(self.items):
            self.items[index].mark_bought()
            return True
        return False

    def list_items(self) -> list[Item]:
        return self.items


class ShoppingListApp(tk.Tk):
    """
    Einfache GUI für die Einkaufsliste mit Tkinter.
    """
    def __init__(self):
        super().__init__()
        self.title("Einkaufsliste")
        self.geometry("400x300")

        self.shopping_list = ShoppingList()
        self.create_widgets()

    def create_widgets(self):
        # Eingabebereich oben
        frame_input = tk.Frame(self)
        frame_input.pack(padx=10, pady=10, fill="x")

        tk.Label(frame_input, text="Artikel:").grid(row=0, column=0, sticky="w")
        self.entry_name = tk.Entry(frame_input)
        self.entry_name.grid(row=0, column=1, sticky="we", padx=(5, 5))

        tk.Label(frame_input, text="Menge:").grid(row=1, column=0, sticky="w", pady=(5,0))
        self.entry_quantity = tk.Entry(frame_input)
        self.entry_quantity.insert(0, "1")
        self.entry_quantity.grid(row=1, column=1, sticky="we", padx=(5, 5), pady=(5,0))

        frame_input.columnconfigure(1, weight=1)

        btn_add = tk.Button(frame_input, text="Hinzufügen", command=self.handle_add_item)
        btn_add.grid(row=0, column=2, rowspan=2, padx=(5,0), sticky="ns")

        # Listbox in der Mitte
        frame_list = tk.Frame(self)
        frame_list.pack(padx=10, pady=(0,10), fill="both", expand=True)

        self.listbox = tk.Listbox(frame_list)
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame_list, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Buttons unten
        frame_buttons = tk.Frame(self)
        frame_buttons.pack(padx=10, pady=5, fill="x")

        btn_mark = tk.Button(frame_buttons, text="Als gekauft markieren", command=self.handle_mark_bought)
        btn_mark.pack(side="left")

        btn_delete = tk.Button(frame_buttons, text="Löschen", command=self.handle_delete_item)
        btn_delete.pack(side="left", padx=5)

    def refresh_listbox(self):
        """Listbox-Inhalt an die Daten in ShoppingList anpassen."""
        self.listbox.delete(0, tk.END)
        for item in self.shopping_list.list_items():
            self.listbox.insert(tk.END, str(item))

    def handle_add_item(self):
        """Artikel aus den Eingabefeldern zur Liste hinzufügen."""
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showwarning("Fehler", "Name darf nicht leer sein.")
            return

        quantity_text = self.entry_quantity.get().strip()
        if quantity_text == "":
            quantity = 1
        else:
            if not quantity_text.isdigit():
                messagebox.showwarning("Fehler", "Menge muss eine Zahl sein.")
                return
            quantity = int(quantity_text)

        self.shopping_list.add_item(name, quantity)
        self.entry_name.delete(0, tk.END)
        self.entry_quantity.delete(0, tk.END)
        self.entry_quantity.insert(0, "1")
        self.refresh_listbox()

    def get_selected_index(self):
        selection = self.listbox.curselection()
        if not selection:
            return None
        return selection[0]

    def handle_mark_bought(self):
        """Ausgewählten Artikel als gekauft markieren."""
        index = self.get_selected_index()
        if index is None:
            messagebox.showinfo("Hinweis", "Bitte zuerst einen Artikel auswählen.")
            return

        if self.shopping_list.mark_item_bought(index):
            self.refresh_listbox()

    def handle_delete_item(self):
        """Ausgewählten Artikel löschen."""
        index = self.get_selected_index()
        if index is None:
            messagebox.showinfo("Hinweis", "Bitte zuerst einen Artikel auswählen.")
            return

        if self.shopping_list.remove_item(index):
            self.refresh_listbox()


if __name__ == "__main__":
    app = ShoppingListApp()
    app.mainloop()
