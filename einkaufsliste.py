class Item:
    """
    Repräsentiert einen einzelnen Einkaufsartikel.
    """
    def __init__(self, name: str, quantity: int = 1):
        self.name = name
        self.quantity = quantity
        self.bought = False

    def mark_bought(self):
        """Markiert den Artikel als gekauft."""
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
        """
        Entfernt einen Artikel anhand des Index (0-basiert intern).
        Gibt True zurück, wenn erfolgreich, sonst False.
        """
        if 0 <= index < len(self.items):
            del self.items[index]
            return True
        return False

    def mark_item_bought(self, index: int) -> bool:
        """
        Markiert einen Artikel als gekauft.
        """
        if 0 <= index < len(self.items):
            self.items[index].mark_bought()
            return True
        return False

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def list_items(self) -> list[Item]:
        return self.items


def print_menu():
    print("\n=== Einkaufslisten-Manager ===")
    print("1) Artikel hinzufügen")
    print("2) Liste anzeigen")
    print("3) Artikel als gekauft markieren")
    print("4) Artikel löschen")
    print("5) Beenden")


def show_items(shopping_list: ShoppingList):
    if shopping_list.is_empty():
        print("\nDie Einkaufsliste ist leer.")
        return

    print("\nAktuelle Einkaufsliste:")
    for i, item in enumerate(shopping_list.list_items(), start=1):
        print(f"{i}. {item}")


def handle_add_item(shopping_list: ShoppingList):
    name = input("Name des Artikels: ").strip()
    if not name:
        print("Name darf nicht leer sein.")
        return

    quantity_input = input("Menge (Standard 1): ").strip()
    if quantity_input == "":
        quantity = 1
    else:
        if not quantity_input.isdigit():
            print("Bitte gib eine gültige Zahl für die Menge ein.")
            return
        quantity = int(quantity_input)

    shopping_list.add_item(name, quantity)
    print(f"Artikel '{name}' wurde hinzugefügt.")


def handle_mark_bought(shopping_list: ShoppingList):
    if shopping_list.is_empty():
        print("Liste ist leer, nichts zu markieren.")
        return

    show_items(shopping_list)
    choice = input("Nummer des Artikels, der gekauft wurde: ").strip()
    if not choice.isdigit():
        print("Bitte eine gültige Zahl eingeben.")
        return

    index = int(choice) - 1
    if shopping_list.mark_item_bought(index):
        print("Artikel wurde als gekauft markiert.")
    else:
        print("Ungültige Artikelnr.")


def handle_delete_item(shopping_list: ShoppingList):
    if shopping_list.is_empty():
        print("Liste ist leer, nichts zu löschen.")
        return

    show_items(shopping_list)
    choice = input("Nummer des zu löschenden Artikels: ").strip()
    if not choice.isdigit():
        print("Bitte eine gültige Zahl eingeben.")
        return

    index = int(choice) - 1
    if shopping_list.remove_item(index):
        print("Artikel wurde gelöscht.")
    else:
        print("Ungültige Artikelnr.")


def main():
    shopping_list = ShoppingList()

    while True:
        print_menu()
        choice = input("Wähle eine Option: ").strip()

        if choice == "1":
            handle_add_item(shopping_list)
        elif choice == "2":
            show_items(shopping_list)
        elif choice == "3":
            handle_mark_bought(shopping_list)
        elif choice == "4":
            handle_delete_item(shopping_list)
        elif choice == "5":
            print("Programm wird beendet. Tschüss!")
            break
        else:
            print("Ungültige Auswahl. Bitte 1–5 eingeben.")


if __name__ == "__main__":
    main()
