# Datei: main.py
import tkinter as tk
from settings_manager import SettingsManager
from ui_nibble_editor import NibbleEditor


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Binary Time Machine")
        self.root.geometry("530x380")

        # 1. Daten laden
        self.settings = SettingsManager()

        # 2. UI aufbauen
        # Wir nutzen einen Container für verschiedene "Screens" (Menüs)
        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        # Hier laden wir unseren Editor
        # Wir übergeben 'self.container' als Eltern-Element
        self.editor_view = NibbleEditor(self.container, self.settings)
        self.editor_view.pack(fill="both", expand=True)

if __name__ == "__main__":
    print("1. Starting Binary Time Machine")
    root = tk.Tk()


    print("2. Erstelle MainApp...")
    app = MainApp(root)

    print("3. Setup fertig. Starte Mainloop (Fenster sollte kommen)...")
    root.mainloop()

    print("4. Programm beendet.")