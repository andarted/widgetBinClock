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
        self.root.geometry("800x700")
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

        # --- HOTKEYS ---
        # Wir binden alle Tastenanschläge an unsere Funktion
        self.root.bind("<Key>", self.handle_keypress)

    def handle_keypress(self, event):
        """
        Globaler Hotkey Handler.
        Erlaubt Profilwechsel mit 0-9 und a-f.
        """
        # WICHTIG: Wenn der User gerade in eine Spinbox tippt, ignorieren wir das Event!
        # Sonst springt das Profil um, während man eine Zahl eingeben will.
        if isinstance(event.widget, (tk.Entry, tk.Spinbox)):
            return

        key = event.char.lower()
        new_profile_id = None

        # 0-9
        if key.isdigit():
            new_profile_id = int(key)

        # a-f (Hex für 10-15)
        elif key in ['a', 'b', 'c', 'd', 'e', 'f']:
            # Kleiner ASCII Hack: 'a' ist 97. 97 - 87 = 10.
            new_profile_id = ord(key) - 87

        # Wenn valide ID gefunden: Wechseln
        if new_profile_id is not None and 0 <= new_profile_id <= 15:
            self.activate_profile_via_hotkey(new_profile_id)

    def activate_profile_via_hotkey(self, slot_id):
        print(f"Hotkey: Switch to Profile {slot_id}")

        # 1. Daten setzen
        self.settings.data["active_profileId"] = slot_id
        # Wir speichern hier NICHT auf die Festplatte (Performance & SSD schonen beim schnellen Wechseln)
        # Erst beim Beenden oder expliziten Speichern wird geschrieben.
        # Wenn du es unbedingt willst, kannst du self.settings.save_settings() einkommentieren.

        # 2. Uhr sofort updaten (Force Redraw)
        # Wir greifen direkt auf die Methode zu, auch wenn die View gerade nicht 'packed' ist.
        # Aber visuell Sinn macht es nur, wenn wir die Clock sehen.
        if self.clock_view.winfo_ismapped():
            self.clock_view.force_redraw()

        # 3. Falls das Dashboard offen ist, muss der Rahmen springen
        if self.profile_view.winfo_ismapped():
            self.profile_view.refresh_selection()

    # --- SHOW METHODEN ---
    def show_editor(self):
        self._hide_all()
        self.editor_view.pack(fill=tk.BOTH, expand=True)
        self.root.update_idletasks()

    def show_palette(self):
        self._hide_all()
        self.palette_view.pack(fill=tk.BOTH, expand=True)
        self.root.update_idletasks()

    def show_layout(self):
        self._hide_all()
        self.layout_view.pack(fill=tk.BOTH, expand=True)
        self.root.update_idletasks()

    def show_profiles(self):
        self._hide_all()
        self.profile_view.pack(fill=tk.BOTH, expand=True)
        self.profile_view.update_previews()
        self.root.update_idletasks()

    def show_clock(self):
        self._hide_all()
        self.clock_view.pack(fill=tk.BOTH, expand=True)
        self.clock_view.start()
        self.root.update_idletasks()

    def _hide_all(self):
        """Kleiner Helper um Code zu sparen"""
        self.clock_view.stop()
        self.clock_view.pack_forget()
        self.editor_view.pack_forget()
        self.palette_view.pack_forget()
        self.layout_view.pack_forget()
        self.profile_view.pack_forget()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()