import tkinter as tk
from ui_shared import BG_COLOR
from ui_mini_grid import MiniGridSelector


class ProfileEditor(tk.Frame):
    def __init__(self, parent, settings_manager):
        super().__init__(parent, bg=BG_COLOR)
        self.settings_manager = settings_manager

        # Wir starten mit dem Profil, das gerade aktiv ist
        self.current_profile_id = self.settings_manager.data.get("active_profileId", 0)

        self.setup_ui()
        self.refresh_selection()

    def setup_ui(self):
        # 2x2 Grid Layout für die 4 Quadranten
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. NIBBLES - Oben Links (0, 0)
        self.grid_nibbles = MiniGridSelector(self, self.settings_manager,
                                             "NIBBLE DESIGNS", "nibble", "#FF5733", self.on_nibble_click)
        self.grid_nibbles.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # 2. PALETTES - Oben Rechts (0, 1)
        self.grid_palettes = MiniGridSelector(self, self.settings_manager,
                                              "PALETTES", "palette", "#44AA44", self.on_palette_click)
        self.grid_palettes.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # 3. LAYOUTS - Unten Links (1, 0)
        self.grid_layouts = MiniGridSelector(self, self.settings_manager,
                                             "LAYOUTS", "layout", "#3357FF", self.on_layout_click)
        self.grid_layouts.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # 4. PROFILES (Master) - Unten Rechts (1, 1)
        self.grid_profiles = MiniGridSelector(self, self.settings_manager,
                                              "PROFILES (Master)", "profile", "#FFFFFF", self.on_profile_click)
        self.grid_profiles.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

    def refresh_selection(self):
        """Liest das aktuelle Profil aus den Daten und setzt die Markierungen"""

        # 1. Master Profil markieren
        self.grid_profiles.set_selection(self.current_profile_id)

        # 2. Inhalt lesen (Refactoring: "profiles" statt "settings")
        try:
            profile_data = self.settings_manager.data["profiles"][self.current_profile_id]

            nid = profile_data.get("nibbleGridId", 0)
            lid = profile_data.get("layoutId", 0)
            pid = profile_data.get("paletteId", 0)

            # 3. Sub-Grids markieren
            self.grid_nibbles.set_selection(nid)
            self.grid_layouts.set_selection(lid)
            self.grid_palettes.set_selection(pid)

            # 4. Als aktiv speichern
            self.settings_manager.data["active_profileId"] = self.current_profile_id
            self.settings_manager.save_settings()

        except Exception as e:
            print(f"Error referencing profile: {e}")

    def update_previews(self):
        """Zeichnet alle Grids komplett neu (Aufruf aus Main, wenn Tab gewechselt wird)"""
        # Wir warten kurz, bis das Fenster da ist, damit die Größen stimmen
        self.after(10, self._redraw_internal)

    def _redraw_internal(self):
        self.grid_nibbles.redraw_all_slots()
        self.grid_layouts.redraw_all_slots()
        self.grid_palettes.redraw_all_slots()
        self.grid_profiles.redraw_all_slots()
        self.refresh_selection()

    # --- INTERAKTION ---

    def on_profile_click(self, slot_id):
        # User wechselt das ganze Profil
        self.current_profile_id = slot_id
        self.refresh_selection()

    def on_nibble_click(self, slot_id):
        # User ändert nur das Nibble für das aktuelle Profil
        target = self.settings_manager.data["profiles"][self.current_profile_id]
        target["nibbleGridId"] = slot_id
        self.refresh_selection()

    def on_layout_click(self, slot_id):
        target = self.settings_manager.data["profiles"][self.current_profile_id]
        target["layoutId"] = slot_id
        self.refresh_selection()

    def on_palette_click(self, slot_id):
        target = self.settings_manager.data["profiles"][self.current_profile_id]
        target["paletteId"] = slot_id
        self.refresh_selection()