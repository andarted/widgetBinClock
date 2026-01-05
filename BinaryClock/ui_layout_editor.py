import tkinter as tk
from ui_shared import FlatButton, BG_COLOR, TEXT_COLOR, UI_FONT, UI_FONT_SMALL

# Layout-Zellen sind größer, damit man sieht, was drin ist
CELL_SIZE = 60
GAP_SIZE = 10
GRID_PIXEL_WIDTH = (4 * CELL_SIZE) + (3 * GAP_SIZE)
CANVAS_SIZE = GRID_PIXEL_WIDTH + 40

# Farben für die 4 Zeit-Bausteine
TOKEN_COLORS = {
    3: "#FF5733",  # H1
    2: "#FF8C33",  # H0
    1: "#3357FF",  # M1
    0: "#33FFF5"  # M0
}
TOKEN_NAMES = {
    3: "H1", 2: "H0", 1: "M1", 0: "M0"
}


class LayoutEditor(tk.Frame):
    def __init__(self, parent, settings_manager):
        super().__init__(parent, bg=BG_COLOR)
        self.settings_manager = settings_manager

        # Grid speichert jetzt Dictionaries:
        # {'id': 3, 'mx': True, 'my': False} oder None
        self.grid_data = [[None for _ in range(4)] for _ in range(4)]

        self.current_token_id = 3

        # Mirror Variablen
        self.mirror_x_var = tk.BooleanVar(value=False)
        self.mirror_y_var = tk.BooleanVar(value=False)

        self.setup_ui()
        self.load_current_slot()

    def setup_ui(self):
        # --- TOOLBAR ---
        toolbar = tk.Frame(self, pady=5, bg=BG_COLOR)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Slot Auswahl & Save
        top_row = tk.Frame(toolbar, bg=BG_COLOR)
        top_row.pack(side=tk.TOP, fill=tk.X, padx=10)

        tk.Label(top_row, text="Layout Slot:", bg=BG_COLOR, fg=TEXT_COLOR, font=UI_FONT_SMALL).pack(side=tk.LEFT)
        self.slot_spinner = tk.Spinbox(top_row, from_=0, to=15, width=3,
                                       command=self.load_current_slot, font=UI_FONT_SMALL,
                                       bg="#444444", fg="white", buttonbackground="#444444", borderwidth=0)
        self.slot_spinner.pack(side=tk.LEFT, padx=5)

        FlatButton(top_row, text="Load", command=self.load_current_slot, bg="#444444", width=4).pack(side=tk.LEFT,
                                                                                                     padx=2)
        FlatButton(top_row, text="Save", command=self.save_current_slot, bg="#44AA44", width=4).pack(side=tk.RIGHT,
                                                                                                     padx=2)
        FlatButton(top_row, text="Clear", command=self.clear_grid, bg="#AA4444", width=4).pack(side=tk.RIGHT,
                                                                                               padx=(5, 2))

        # --- TOKEN AUSWAHL ---
        token_row = tk.Frame(toolbar, bg=BG_COLOR)
        token_row.pack(side=tk.TOP, pady=10)

        tk.Label(token_row, text="Place:", bg=BG_COLOR, fg=TEXT_COLOR, font=UI_FONT_SMALL).pack(side=tk.LEFT, padx=5)

        self.token_buttons = {}
        for tid in [3, 2, 1, 0]:
            btn = FlatButton(
                token_row,
                text=TOKEN_NAMES[tid],
                width=4,
                bg=TOKEN_COLORS[tid],
                fg="black",
                command=lambda t=tid: self.select_token(t)
            )
            btn.pack(side=tk.LEFT, padx=5)
            self.token_buttons[tid] = btn

        # --- CANVAS ---
        main_frame = tk.Frame(self, bg=BG_COLOR)
        main_frame.pack(expand=True, fill=tk.BOTH)

        self.canvas = tk.Canvas(main_frame, bg=BG_COLOR, width=CANVAS_SIZE, height=CANVAS_SIZE, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=20, pady=20)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # --- SIDEBAR (Info & Mirror) ---
        sidebar = tk.Frame(main_frame, bg=BG_COLOR)
        sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=20)

        # Mirror Settings (NEU)
        tk.Label(sidebar, text="Options:", bg=BG_COLOR, fg=TEXT_COLOR, font=UI_FONT_SMALL).pack(anchor="w", pady=(0, 5))

        chk_style = {"bg": BG_COLOR, "fg": TEXT_COLOR, "selectcolor": "#444444",
                     "activebackground": BG_COLOR, "activeforeground": TEXT_COLOR, "font": UI_FONT_SMALL}

        tk.Checkbutton(sidebar, text="Mirror Horizontal (↔)", variable=self.mirror_x_var, **chk_style).pack(anchor="w")
        tk.Checkbutton(sidebar, text="Mirror Vertical (↕)", variable=self.mirror_y_var, **chk_style).pack(anchor="w")

        tk.Label(sidebar, text="----------------", bg=BG_COLOR, fg="#444444").pack(pady=10)

        tk.Label(sidebar, text="H1 = Hour 10s\nH0 = Hour 1s\nM1 = Min 10s\nM0 = Min 1s",
                 bg=BG_COLOR, fg="#888888", font=UI_FONT_SMALL, justify=tk.LEFT).pack(anchor="w")

        self.info_label = tk.Label(sidebar, text="Ready.", bg=BG_COLOR, fg="#888888", font=UI_FONT_SMALL)
        self.info_label.pack(pady=20, anchor="w")

        self.update_ui_state()

    # --- LOGIK ---

    def select_token(self, tid):
        self.current_token_id = tid
        self.update_ui_state()

    def update_ui_state(self):
        for tid, btn in self.token_buttons.items():
            if tid == self.current_token_id:
                btn.set_active(True)
            else:
                btn.set_active(False)

    def clear_grid(self):
        self.grid_data = [[None for _ in range(4)] for _ in range(4)]
        self.redraw_canvas()

    def on_canvas_click(self, event):
        grid_width = 4 * CELL_SIZE + 3 * GAP_SIZE
        offset_x = (CANVAS_SIZE - grid_width) // 2
        offset_y = (CANVAS_SIZE - grid_width) // 2
        rx = event.x - offset_x
        ry = event.y - offset_y
        col = rx // (CELL_SIZE + GAP_SIZE)
        row = ry // (CELL_SIZE + GAP_SIZE)

        if 0 <= col < 4 and 0 <= row < 4:
            # 1. Altes Vorkommen dieses Tokens löschen
            old_pos = None
            for r in range(4):
                for c in range(4):
                    item = self.grid_data[r][c]
                    if item is not None and item['id'] == self.current_token_id:
                        self.grid_data[r][c] = None
                        old_pos = (r, c)

            # 2. Wenn wir nicht auf die alte Position geklickt haben -> Neu setzen
            if old_pos != (row, col):
                self.grid_data[row][col] = {
                    'id': self.current_token_id,
                    'mx': self.mirror_x_var.get(),
                    'my': self.mirror_y_var.get()
                }

            self.redraw_canvas()

    def redraw_canvas(self):
        self.canvas.delete("all")
        grid_pixel_size = 4 * CELL_SIZE + 3 * GAP_SIZE
        off_x = (CANVAS_SIZE - grid_pixel_size) // 2
        off_y = (CANVAS_SIZE - grid_pixel_size) // 2

        for r in range(4):
            for c in range(4):
                item = self.grid_data[r][c]

                x1 = off_x + c * (CELL_SIZE + GAP_SIZE)
                y1 = off_y + r * (CELL_SIZE + GAP_SIZE)
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                # Leere Zelle
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="#2A2A2A", outline="#333333", width=2)

                if item is not None:
                    tid = item['id']
                    mx = item['mx']
                    my = item['my']

                    color = TOKEN_COLORS[tid]
                    text = TOKEN_NAMES[tid]

                    # Token Box
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                    # Haupt Text
                    self.canvas.create_text(x1 + CELL_SIZE // 2, y1 + CELL_SIZE // 2,
                                            text=text, font=("Futura", 14, "bold"), fill="black")

                    # Spiegel Indikatoren (klein in den Ecken oder neben dem Text)
                    indicators = ""
                    if mx: indicators += "↔"
                    if my: indicators += "↕"

                    if indicators:
                        self.canvas.create_text(x1 + CELL_SIZE - 5, y1 + 10,
                                                text=indicators, font=("Arial", 10, "bold"), fill="black", anchor="e")

    # --- JSON LOGIK ---

    def load_current_slot(self):
        try:
            slot_id = int(self.slot_spinner.get())
            layout_data = self.settings_manager.data["library"]["layoutGrids"][slot_id]
            placements = layout_data.get("placements", [])

            self.clear_grid()

            for p in placements:
                tid = p["nibbleId"]
                pos = p["position"]
                mirror = p.get("mirror", {"x": False, "y": False})

                c = pos["x"]
                r = pos["y"]
                if 0 <= r < 4 and 0 <= c < 4:
                    self.grid_data[r][c] = {
                        'id': tid,
                        'mx': mirror.get("x", False),
                        'my': mirror.get("y", False)
                    }

            self.redraw_canvas()
            self.info_label.config(text=f"Loaded Slot {slot_id}")
        except Exception as e:
            print(e)
            self.info_label.config(text="Error loading")

    def save_current_slot(self):
        try:
            slot_id = int(self.slot_spinner.get())
            placements = []
            for r in range(4):
                for c in range(4):
                    item = self.grid_data[r][c]
                    if item is not None:
                        obj = {
                            "nibbleId": item['id'],
                            "position": {"x": c, "y": r},
                            "mirror": {"x": item['mx'], "y": item['my']}
                        }
                        placements.append(obj)

            self.settings_manager.data["library"]["layoutGrids"][slot_id]["placements"] = placements
            self.settings_manager.save_settings()

            self.info_label.config(text=f"Saved Slot {slot_id}!")
        except Exception as e:
            print(e)
            self.info_label.config(text="Error saving")