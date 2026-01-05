# Datei: ui_profile_editor.py
import tkinter as tk
from ui_shared import FlatButton, BG_COLOR, TEXT_COLOR, UI_FONT, UI_FONT_SMALL


class ProfileEditor(tk.Frame):
    def __init__(self, parent, settings_manager):
        super().__init__(parent, bg=BG_COLOR)
        self.settings_manager = settings_manager

        # Aktuelle Auswahl im Editor
        self.current_layout_id = 0
        self.current_palette_id = 0
        self.current_nibble_id = 0

        self.setup_ui()
        self.load_current_slot()

    def setup_ui(self):
        # --- TOOLBAR ---
        toolbar = tk.Frame(self, pady=5, bg=BG_COLOR)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        top_row = tk.Frame(toolbar, bg=BG_COLOR)
        top_row.pack(side=tk.TOP, fill=tk.X, padx=10)

        # Slot Auswahl (Das Profil, das wir bearbeiten)
        tk.Label(top_row, text="Profile Slot:", bg=BG_COLOR, fg=TEXT_COLOR, font=UI_FONT_SMALL).pack(side=tk.LEFT)
        self.slot_spinner = tk.Spinbox(top_row, from_=0, to=15, width=3,
                                       command=self.load_current_slot, font=UI_FONT_SMALL,
                                       bg="#444444", fg="white", buttonbackground="#444444", borderwidth=0)
        self.slot_spinner.pack(side=tk.LEFT, padx=5)

        FlatButton(top_row, text="Load", command=self.load_current_slot, bg="#444444", width=4).pack(side=tk.LEFT,
                                                                                                     padx=2)
        FlatButton(top_row, text="Save", command=self.save_current_slot, bg="#44AA44", width=4).pack(side=tk.RIGHT,
                                                                                                     padx=2)

        # --- MAIN SELECTION AREA ---
        # Hier wählen wir die Zutaten für das Profil

        center_frame = tk.Frame(self, bg=BG_COLOR)
        center_frame.pack(expand=True)

        # Wir bauen 3 Zeilen für die 3 Komponenten
        self.create_selector(center_frame, "Nibble Design (Shape):", "nibble")
        self.create_selector(center_frame, "Layout (Position):", "layout")
        self.create_selector(center_frame, "Palette (Color):", "palette")

        # Info
        self.info_label = tk.Label(self, text="Ready.", bg=BG_COLOR, fg="#888888", font=UI_FONT_SMALL)
        self.info_label.pack(side=tk.BOTTOM, pady=10)

    def create_selector(self, parent, label_text, type_key):
        """Erstellt eine Zeile mit Label und Spinbox/Buttons"""
        row = tk.Frame(parent, bg=BG_COLOR, pady=10)
        row.pack(fill=tk.X)

        lbl = tk.Label(row, text=label_text, bg=BG_COLOR, fg=TEXT_COLOR, font=UI_FONT, width=20, anchor="e")
        lbl.pack(side=tk.LEFT, padx=10)

        # Spinbox für die ID Auswahl (0-15)
        # Wir speichern die Referenz auf das Widget dynamisch in 'self'
        spin = tk.Spinbox(row, from_=0, to=15, width=5, font=UI_FONT,
                          bg="#444444", fg="white", buttonbackground="#444444", borderwidth=0)
        spin.pack(side=tk.LEFT, padx=5)

        # Referenz speichern, damit wir später drauf zugreifen können
        setattr(self, f"spin_{type_key}", spin)

    # --- LOGIK ---

    def load_current_slot(self):
        try:
            slot_id = int(self.slot_spinner.get())
            # Setting laden
            setting_data = self.settings_manager.data["settings"][slot_id]

            # IDs holen
            nid = setting_data.get("nibbleGridId", 0)
            lid = setting_data.get("layoutId", 0)
            pid = setting_data.get("paletteId", 0)

            # UI setzen (Spinboxen aktualisieren)
            self.set_spinbox_value(self.spin_nibble, nid)
            self.set_spinbox_value(self.spin_layout, lid)
            self.set_spinbox_value(self.spin_palette, pid)

            # Wir setzen das auch gleich als "Aktives Setting" im Manager,
            # damit die Uhr es sofort weiß, wenn wir speichern?
            # Nein, das machen wir lieber explizit über einen "Activate" Button später.

            self.info_label.config(text=f"Loaded Profile {slot_id}")

        except Exception as e:
            print(e)
            self.info_label.config(text="Error loading profile")

    def save_current_slot(self):
        try:
            slot_id = int(self.slot_spinner.get())

            # Werte aus Spinboxen lesen
            nid = int(self.spin_nibble.get())
            lid = int(self.spin_layout.get())
            pid = int(self.spin_palette.get())

            # Ins JSON schreiben
            target = self.settings_manager.data["settings"][slot_id]
            target["nibbleGridId"] = nid
            target["layoutId"] = lid
            target["paletteId"] = pid

            # Wir speichern auch, dass DIESES Setting jetzt das aktive ist
            self.settings_manager.data["active_settingId"] = slot_id

            self.settings_manager.save_settings()

            self.info_label.config(text=f"Saved & Activated Profile {slot_id}!")
        except Exception as e:
            print(e)
            self.info_label.config(text="Error saving profile")

    def set_spinbox_value(self, spinbox, value):
        spinbox.delete(0, "end")
        spinbox.insert(0, value)