import tkinter as tk
from tkinter import colorchooser
from ui_shared import FlatButton, BG_COLOR, TEXT_COLOR, UI_FONT, UI_FONT_SMALL

# Konstanten für die Darstellung
GAP_SIZE = 5


class PaletteEditor(tk.Frame):
    def __init__(self, parent, settings_manager):
        super().__init__(parent, bg=BG_COLOR)
        self.settings_manager = settings_manager

        # Lokaler Speicher für 16 Farben
        self.current_colors = ["#000000"] * 16

        # Pinsel-Modus: "pixel", "nibble", "global"
        self.brush_mode = tk.StringVar(value="pixel")

        # Liste für die Button-Referenzen vorinitialisieren
        self.color_buttons = [None] * 16

        self.setup_ui()
        self.load_current_slot()

    def setup_ui(self):
        # --- TOOLBAR (Oben) ---
        toolbar = tk.Frame(self, pady=5, bg=BG_COLOR)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Container: Slot & Actions
        top_row = tk.Frame(toolbar, bg=BG_COLOR)
        top_row.pack(side=tk.TOP, fill=tk.X, padx=10)

        # Slot Auswahl
        tk.Label(top_row, text="Palette Slot:", bg=BG_COLOR, fg=TEXT_COLOR, font=UI_FONT_SMALL).pack(side=tk.LEFT)
        self.slot_spinner = tk.Spinbox(top_row, from_=0, to=15, width=3,
                                       command=self.load_current_slot, font=UI_FONT_SMALL,
                                       bg="#444444", fg="white", buttonbackground="#444444", borderwidth=0)
        self.slot_spinner.pack(side=tk.LEFT, padx=5)

        FlatButton(top_row, text="Load", command=self.load_current_slot, bg="#444444", width=4).pack(side=tk.LEFT,
                                                                                                     padx=2)
        FlatButton(top_row, text="Save", command=self.save_current_slot, bg="#44AA44", width=4).pack(side=tk.RIGHT,
                                                                                                     padx=2)

        # --- BRUSH MODES (Werkzeuge) ---
        tool_row = tk.Frame(toolbar, bg=BG_COLOR)
        tool_row.pack(side=tk.TOP, pady=10)

        tk.Label(tool_row, text="Paint Mode:", bg=BG_COLOR, fg=TEXT_COLOR, font=UI_FONT_SMALL).pack(side=tk.LEFT,
                                                                                                    padx=5)

        modes = [("Single Bit", "pixel"), ("Nibble (Row)", "nibble"), ("All (Global)", "global")]

        for text, mode in modes:
            # Einfache Radiobuttons (Systemstyle ist hier meist okay, sonst müssten wir Custom bauen)
            rb = tk.Radiobutton(tool_row, text=text, variable=self.brush_mode, value=mode,
                                bg=BG_COLOR, fg=TEXT_COLOR, selectcolor="#444444",
                                activebackground=BG_COLOR, activeforeground=TEXT_COLOR,
                                font=UI_FONT_SMALL)
            rb.pack(side=tk.LEFT, padx=5)

        # --- MAIN AREA (4x4 Color Grid) ---
        main_frame = tk.Frame(self, bg=BG_COLOR)
        main_frame.pack(expand=True, fill=tk.BOTH)

        self.grid_container = tk.Frame(main_frame, bg=BG_COLOR)
        self.grid_container.pack(expand=True)

        # Grid Aufbau (4 Zeilen à 4 Bits)
        for row in range(4):
            row_frame = tk.Frame(self.grid_container, bg=BG_COLOR)
            row_frame.pack(side=tk.TOP, pady=GAP_SIZE // 2)

            # Label links (H1, H0...)
            nibble_names = ["H1", "H0", "M1", "M0"]
            lbl = tk.Label(row_frame, text=nibble_names[row], width=3, bg=BG_COLOR, fg="#888888", font=UI_FONT_SMALL)
            lbl.pack(side=tk.LEFT, padx=(0, 5))

            for col in range(4):
                # Bit Index berechnen (MSB links)
                bit_index = (3 - row) * 4 + (3 - col)

                # WICHTIG: Hier nutzen wir jetzt FlatButton statt tk.Button!
                btn = FlatButton(
                    row_frame,
                    text="",  # Kein Text auf dem Farbfeld
                    width=6,
                    bg="#000000",  # Startfarbe (wird eh überschrieben)
                    command=lambda b=bit_index: self.on_cell_click(b)
                )

                # Da FlatButton width/height nicht im Konstruktor für Height nimmt (Label behavior),
                # setzen wir height nachträglich, damit es quadratischer wirkt.
                btn.config(height=2)

                btn.pack(side=tk.LEFT, padx=GAP_SIZE // 2)

                # In Liste speichern
                self.color_buttons[bit_index] = btn

        # Info Sidebar
        self.info_label = tk.Label(self, text="Ready.", bg=BG_COLOR, fg="#888888", font=UI_FONT_SMALL)
        self.info_label.pack(side=tk.BOTTOM, pady=10)

    # --- LOGIK ---

    def on_cell_click(self, bit_index):
        # 1. Farbe auswählen
        current_hex = self.current_colors[bit_index]
        color = colorchooser.askcolor(color=current_hex, title="Pick Color")

        if not color[1]: return
        new_color = color[1].upper()

        mode = self.brush_mode.get()

        # 2. Logik anwenden
        if mode == "pixel":
            self.apply_color(bit_index, new_color)

        elif mode == "nibble":
            nibble_idx = bit_index // 4
            start_bit = nibble_idx * 4
            for i in range(start_bit, start_bit + 4):
                self.apply_color(i, new_color)

        elif mode == "global":
            for i in range(16):
                self.apply_color(i, new_color)

    def apply_color(self, index, hex_val):
        self.current_colors[index] = hex_val
        self.update_button_display(index, hex_val)

    def update_button_display(self, index, hex_val):
        btn = self.color_buttons[index]

        # WICHTIG: Wir müssen die internen Werte des FlatButton updaten,
        # sonst setzt der Hover-Effekt die Farbe zurück!
        btn.default_bg = hex_val
        btn.hover_bg = btn.adjust_color_lightness(hex_val, 1.2)

        # Visuell updaten
        btn.config(bg=hex_val)

    # --- JSON HANDLING ---

    def load_current_slot(self):
        try:
            slot_id = int(self.slot_spinner.get())
            palette_data = self.settings_manager.data["library"]["palettes"][slot_id]

            loaded_colors = palette_data.get("colors", ["#333333"] * 16)

            if len(loaded_colors) < 16:
                loaded_colors.extend(["#333333"] * (16 - len(loaded_colors)))

            self.current_colors = list(loaded_colors[:16])

            for i in range(16):
                self.update_button_display(i, self.current_colors[i])

            self.info_label.config(text=f"Loaded Palette {slot_id}")

        except Exception as e:
            print(e)
            self.info_label.config(text="Error loading palette")

    def save_current_slot(self):
        try:
            slot_id = int(self.slot_spinner.get())

            self.settings_manager.data["library"]["palettes"][slot_id]["colors"] = self.current_colors
            self.settings_manager.save_settings()

            self.info_label.config(text=f"Saved Palette {slot_id}!")
        except Exception as e:
            print(e)
            self.info_label.config(text="Error saving palette")