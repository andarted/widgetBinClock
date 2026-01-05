import tkinter as tk
from ui_shared import FlatButton, BG_COLOR, TEXT_COLOR, UI_FONT, UI_FONT_SMALL

# Layout-Zellen sind größer, damit man sieht, was drin ist
CELL_SIZE = 60
GAP_SIZE = 10
GRID_PIXEL_WIDTH = (4 * CELL_SIZE) + (3 * GAP_SIZE)
CANVAS_SIZE = GRID_PIXEL_WIDTH + 40

# Farben für die 4 Zeit-Bausteine (Token) zur Unterscheidung
TOKEN_COLORS = {
    3: "#FF5733",  # H1 (Stunden Zehner)
    2: "#FF8C33",  # H0 (Stunden Einer)
    1: "#3357FF",  # M1 (Minuten Zehner)
    0: "#33FFF5"  # M0 (Minuten Einer)
}
TOKEN_NAMES = {
    3: "H1",  # High Byte High Nibble
    2: "H0",  # High Byte Low Nibble
    1: "M1",  # Low Byte High Nibble
    0: "M0"  # Low Byte Low Nibble
}


class LayoutEditor(tk.Frame):
    def __init__(self, parent, settings_manager):
        super().__init__(parent, bg=BG_COLOR)
        self.settings_manager = settings_manager

        # Das Grid speichert hier KEINE Farben, sondern Token-IDs (3, 2, 1, 0) oder None
        self.grid_data = [[None for _ in range(4)] for _ in range(4)]

        # Welches Token wollen wir gerade platzieren?
        self.current_token_id = 3  # Start mit H1

        self.setup_ui()
        self.redraw_canvas()

    def setup_ui(self):
        # --- TOOLBAR ---
        toolbar = tk.Frame(self, pady=5, bg=BG_COLOR)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Slot Auswahl & Save (Gleiche Logik wie im Nibble Editor)
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
        # 3 (H1) bis 0 (M0)
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

        # Info Sidebar
        sidebar = tk.Frame(main_frame, bg=BG_COLOR)
        sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=20)

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
        # 1. Koordinaten berechnen
        grid_width = 4 * CELL_SIZE + 3 * GAP_SIZE
        offset_x = (CANVAS_SIZE - grid_width) // 2
        offset_y = (CANVAS_SIZE - grid_width) // 2
        rx = event.x - offset_x
        ry = event.y - offset_y
        col = rx // (CELL_SIZE + GAP_SIZE)
        row = ry // (CELL_SIZE + GAP_SIZE)

        if 0 <= col < 4 and 0 <= row < 4:
            # 2. Logik: Token platzieren

            # A. Prüfen: Ist dieses Token schon irgendwo anders? Wenn ja, dort löschen!
            for r in range(4):
                for c in range(4):
                    if self.grid_data[r][c] == self.current_token_id:
                        self.grid_data[r][c] = None

            # B. Wenn wir auf eine Zelle klicken, wo schon DASSELBE Token liegt -> Löschen (Toggle Off)
            # C. Wenn wir auf eine Zelle klicken, wo ein ANDERES Token liegt -> Überschreiben

            # Hier: Einfach setzen (da wir es oben gelöscht haben, ist es ein "Move")
            # Aber Moment: Wenn ich auf die Zelle klicke, wo es gerade war, habe ich es oben gelöscht.
            # Wir müssen uns merken, wo es war.

            # Besserer Ansatz:
            old_pos = None
            clicked_content = self.grid_data[row][col]

            # Alle Instanzen des aktuellen Tokens entfernen
            for r in range(4):
                for c in range(4):
                    if self.grid_data[r][c] == self.current_token_id:
                        self.grid_data[r][c] = None
                        old_pos = (r, c)

            # Wenn wir NICHT auf die alte Position geklickt haben (oder es keine gab), setzen wir es neu.
            # (D.h. Klick auf sich selbst = Löschen)
            if old_pos != (row, col):
                self.grid_data[row][col] = self.current_token_id

            self.redraw_canvas()

    def redraw_canvas(self):
        self.canvas.delete("all")
        grid_pixel_size = 4 * CELL_SIZE + 3 * GAP_SIZE
        off_x = (CANVAS_SIZE - grid_pixel_size) // 2
        off_y = (CANVAS_SIZE - grid_pixel_size) // 2

        # Grid zeichnen
        for r in range(4):
            for c in range(4):
                tid = self.grid_data[r][c]

                x1 = off_x + c * (CELL_SIZE + GAP_SIZE)
                y1 = off_y + r * (CELL_SIZE + GAP_SIZE)
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                # Leere Zelle
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="#2A2A2A", outline="#333333", width=2)

                # Token
                if tid is not None:
                    color = TOKEN_COLORS[tid]
                    text = TOKEN_NAMES[tid]

                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                    self.canvas.create_text(x1 + CELL_SIZE // 2, y1 + CELL_SIZE // 2,
                                            text=text, font=("Futura", 14, "bold"), fill="black")

    # --- DATEN LOGIK (JSON) ---

    def load_current_slot(self):
        try:
            slot_id = int(self.slot_spinner.get())
            layout_data = self.settings_manager.data["library"]["layoutGrids"][slot_id]
            placements = layout_data.get("placements", [])

            self.clear_grid()

            # JSON Placements -> Grid
            # JSON Format: [{"nibbleId": 3, "position": {"x": 0, "y": 0}}, ...]
            for p in placements:
                tid = p["nibbleId"]
                pos = p["position"]
                c = pos["x"]
                r = pos["y"]
                if 0 <= r < 4 and 0 <= c < 4:
                    self.grid_data[r][c] = tid

            self.redraw_canvas()
            self.info_label.config(text=f"Loaded Slot {slot_id}")
        except Exception as e:
            print(e)
            self.info_label.config(text="Error loading")

    def save_current_slot(self):
        try:
            slot_id = int(self.slot_spinner.get())

            # Grid -> JSON Placements Liste
            placements = []
            for r in range(4):
                for c in range(4):
                    tid = self.grid_data[r][c]
                    if tid is not None:
                        # Wir speichern position x/y und das Token (nibbleId)
                        # Mirror speichern wir erstmal als False (Feature kommt später)
                        obj = {
                            "nibbleId": tid,
                            "position": {"x": c, "y": r},
                            "mirror": {"x": False, "y": False}
                        }
                        placements.append(obj)

            # Ins Setting schreiben
            self.settings_manager.data["library"]["layoutGrids"][slot_id]["placements"] = placements
            self.settings_manager.save_settings()

            self.info_label.config(text=f"Saved Slot {slot_id}!")
        except Exception as e:
            print(e)
            self.info_label.config(text="Error saving")