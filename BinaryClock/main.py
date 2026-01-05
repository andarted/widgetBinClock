# Datei: main.py
import tkinter as tk

from ui_palette_editor import PaletteEditor
from settings_manager import SettingsManager
from ui_nibble_editor import NibbleEditor
from ui_clock_display import ClockDisplay
from ui_layout_editor import LayoutEditor
from ui_profile_editor import ProfileEditor
from ui_shared import FlatButton, BG_COLOR, BG_OFF_COLOR, BG_BUTTON_COLOR


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Binary Time Machine")
        self.root.geometry("800x500")
        self.root.configure(bg=BG_COLOR)

        self.settings = SettingsManager()

        # --- NAVIGATION ---
        nav_frame = tk.Frame(self.root, bg=BG_OFF_COLOR, pady=5)
        nav_frame.pack(side=tk.TOP, fill=tk.X)

        # NAV Buttons (Kopfzeile)
            # Design Editor Button
        FlatButton(nav_frame, text="Nibble Editor", command=self.show_editor,
                   bg=BG_BUTTON_COLOR, width=12).pack(side=tk.LEFT, padx=5)
            # Palette Editor Button
        FlatButton(nav_frame, text="Palette Editor", command=self.show_palette,
                   bg=BG_BUTTON_COLOR, width=12).pack(side=tk.LEFT, padx=5)
            # Layout Editor Button
        FlatButton(nav_frame, text="Layout Editor", command=self.show_layout,
                   bg=BG_BUTTON_COLOR, width=12).pack(side=tk.LEFT, padx=5)
            # Setting Editor Button
        FlatButton(nav_frame, text="Profiles", command=self.show_profiles,
                   bg=BG_BUTTON_COLOR, width=12).pack(side=tk.LEFT,padx=5)
            # Live Clock Button
        FlatButton(nav_frame, text="Live Clock", command=self.show_clock,
                   bg=BG_BUTTON_COLOR, width=12).pack(side=tk.LEFT, padx=5)

        # --- CONTENT AREA ---
        self.content_area = tk.Frame(self.root, bg=BG_COLOR)
        self.content_area.pack(fill=tk.BOTH, expand=True)

        # Instanzen erstellen (aber noch nicht packen)
        self.editor_view = NibbleEditor(self.content_area, self.settings)
        self.palette_view = PaletteEditor(self.content_area, self.settings)
        self.layout_view = LayoutEditor(self.content_area, self.settings)
        self.profile_view = ProfileEditor(self.content_area, self.settings)
        self.clock_view = ClockDisplay(self.content_area, self.settings)

        # Standard-Ansicht
        self.show_clock()

    def show_editor(self):
        # Uhr stoppen (CPU sparen) & Uhr + Layout + Palette + Profile weg
        self.clock_view.stop()
        self.clock_view.pack_forget()
        self.layout_view.pack_forget()
        self.palette_view.pack_forget()
        self.profile_view.pack_forget()
        # Editor zeigen
        self.editor_view.pack(fill=tk.BOTH, expand=True)

    def show_palette(self):
        # Uhr stoppen (CPU sparen) & Uhr + Editor + Layout + Profile weg
        self.clock_view.stop()
        self.clock_view.pack_forget()
        self.layout_view.pack_forget()
        self.editor_view.pack_forget()
        self.profile_view.pack_forget()
        # Palette zeigen
        self.palette_view.pack(fill=tk.BOTH, expand=True)

    def show_layout(self):
        # Uhr stoppen (CPU sparen) & Uhr + Editor + Palette + Profiles weg
        self.clock_view.stop()
        self.clock_view.pack_forget()
        self.editor_view.pack_forget()
        self.palette_view.pack_forget()
        self.profile_view.pack_forget()
        # Layout zeigen
        self.layout_view.pack(fill=tk.BOTH, expand=True)

    def show_profiles(self):
        # Uhr stoppen (CPU sparen) & Uhr + Editor + Palette + Layout + Dashboard weg
        self.clock_view.stop()
        self.clock_view.pack_forget()
        self.editor_view.pack_forget()
        self.palette_view.pack_forget()
        self.layout_view.pack_forget()
        # Profile zeigen
        self.profile_view.pack(fill=tk.BOTH, expand=True)

        # WICHTIG: Vorschauen aktualisieren!
        self.profile_view.update_previews()


    def show_clock(self):
        # Editor + Layout + Palette + Profiles weg
        self.editor_view.pack_forget()
        self.layout_view.pack_forget()
        self.palette_view.pack_forget()
        self.profile_view.pack_forget()
        # Uhr zeigen und starten
        self.clock_view.pack(fill=tk.BOTH, expand=True)
        self.clock_view.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()