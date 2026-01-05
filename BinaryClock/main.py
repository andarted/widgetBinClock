import tkinter as tk
from settings_manager import SettingsManager
from ui_nibble_editor import NibbleEditor
from ui_clock_display import ClockDisplay
from ui_layout_editor import LayoutEditor
from ui_shared import FlatButton, BG_COLOR


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Binary Time Machine")
        self.root.geometry("800x500")
        self.root.configure(bg=BG_COLOR)

        self.settings = SettingsManager()

        # --- NAVIGATION ---
        nav_frame = tk.Frame(self.root, bg="#303030", pady=5)
        nav_frame.pack(side=tk.TOP, fill=tk.X)

        # NAV Buttons (Kopfzeile)
            # Design Editor Button
        FlatButton(nav_frame, text="Design Editor", command=self.show_editor,
                   bg="#505050", width=12).pack(side=tk.LEFT, padx=5)
            # Layout Editor Button
        FlatButton(nav_frame, text="Layout Editor", command=self.show_layout,
                   bg="#505050", width=12).pack(side=tk.LEFT, padx=5)
            # Live Clock Button
        FlatButton(nav_frame, text="Live Clock", command=self.show_clock,
                   bg="#505050", width=12).pack(side=tk.LEFT, padx=5)

        # --- CONTENT AREA ---
        self.content_area = tk.Frame(self.root, bg=BG_COLOR)
        self.content_area.pack(fill=tk.BOTH, expand=True)

        # Instanzen erstellen (aber noch nicht packen)
        self.editor_view = NibbleEditor(self.content_area, self.settings)
        self.layout_view = LayoutEditor(self.content_area, self.settings)
        self.clock_view = ClockDisplay(self.content_area, self.settings)

        # Standard-Ansicht
        self.show_editor()

    def show_editor(self):
        # Uhr stoppen (CPU sparen) & Layout weg
        self.clock_view.stop()
        self.clock_view.pack_forget()
        self.layout_view.pack_forget()

        # Editor zeigen
        self.editor_view.pack(fill=tk.BOTH, expand=True)

    def show_layout(self):
        # Uhr stoppen (CPU sparen) & Editor weg
        self.clock_view.stop()
        self.clock_view.pack_forget()
        self.editor_view.pack_forget()

        # Layout zeigen
        self.layout_view.pack(fill=tk.BOTH, expand=True)


    def show_clock(self):
        # Editor weg & Layout weg
        self.editor_view.pack_forget()
        self.layout_view.pack_forget()

        # Uhr zeigen und starten
        self.clock_view.pack(fill=tk.BOTH, expand=True)
        self.clock_view.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()