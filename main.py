import tkinter as tk
from gui.main_gui import TaskGUI

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("950x500")
    root.title("Productivity App")
    TaskGUI(root)
    root.mainloop()
