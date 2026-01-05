import tkinter as tk
from ui_shared import FlatButton, BG_COLOR, GROUP_COLORS, TEXT_COLOR, UI_FONT, UI_FONT_SMALL

# --- KONFIGURATION ---
CELL_SIZE = 40
GAP_SIZE = 10

# Wir berechnen die Canvas-Größe dynamisch basierend auf dem Grid
# 4 Zellen + 3 Gaps + etwas Rand (2 * 20px)
GRID_PIXEL_WIDTH = (4 * CELL_SIZE) + (3 * GAP_SIZE)
CANVAS_SIZE = GRID_PIXEL_WIDTH + 40

GROUP_LIMITS = {0: 1, 1: 2, 2: 4, 3: 8}

class NibbleEditor(tk.Frame):
    def __init__(self, parent, settings_manager):
        super().__init__(parent, bg=BG_COLOR)
        self.settings_manager = settings_manager

        # Daten
        self.grid_data = [[None for _ in range(4)] for _ in range(4)]
        self.current_group_id = 3

        # Drag Logic
        self.drag_mode = None
        self.last_drag_cell = None

        # UI Vars
        self.bridge_gaps = tk.BooleanVar(value=True)
        self.fill_corners = tk.BooleanVar(value=True)

        self.setup_ui()
        self.redraw_canvas()

    def setup_ui(self):
        # --- TOOLBAR ---
        # Padding reduziert für kompakten Look
        toolbar = tk.Frame(self, pady=5, bg=BG_COLOR)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Container für die oberen Controls (Slot & Actions)
        top_row = tk.Frame(toolbar, bg=BG_COLOR)
        top_row.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(0, 5))

        # Container für die Bit-Buttons (darunter, zentriert)
        bit_row = tk.Frame(toolbar, bg=BG_COLOR)
        bit_row.pack(side=tk.TOP, pady=2)

        # --- OBERE REIHE: Slot links, Aktionen rechts ---

        # Slot
        tk.Label(top_row, text="Slot:", bg=BG_COLOR, fg=TEXT_COLOR, font=UI_FONT_SMALL).pack(side=tk.LEFT)
        self.slot_spinner = tk.Spinbox(top_row, from_=0, to=15, width=3,
                                       command=self.load_current_slot, font=UI_FONT_SMALL,
                                       bg="#444444", fg="white", buttonbackground="#444444", borderwidth=0)
        self.slot_spinner.pack(side=tk.LEFT, padx=5)

        FlatButton(top_row, text="Load", command=self.load_current_slot,
                   bg="#444444", width=4).pack(side=tk.LEFT, padx=2)

        # Save / Reset (Rechtsbündig)
        FlatButton(top_row, text="Save", command=self.save_current_slot,
                   bg="#44AA44", width=4).pack(side=tk.RIGHT, padx=2)

        FlatButton(top_row, text="Reset", command=self.reset_grid,
                   bg="#AA4444", width=4).pack(side=tk.RIGHT, padx=(5, 2))

        # --- UNTERE REIHE: Die 4 Bit Buttons ---
        # Wir versuchen die Gaps des Grids optisch nachzuahmen.
        # Grid Gap ist 10px. Wir nutzen padx=5 auf beiden Seiten = 10px Abstand.

        self.group_buttons = {}
        for gid in [3, 2, 1, 0]:
            btn = FlatButton(
                bit_row,
                text=str(gid),
                width=6,  # Schmaler, passt ca. zur Grid Zelle
                bg=GROUP_COLORS[gid],
                fg="black",
                command=lambda g=gid: self.select_tool(g)
            )
            # padx=5 sorgt für 10px Abstand zwischen den Buttons (5+5)
            # Das entspricht genau unserem GAP_SIZE im Grid
            btn.pack(side=tk.LEFT, padx=GAP_SIZE // 2)
            self.group_buttons[gid] = btn

        # -----------------------------------------
        # --- MAIN AREA ---
        main_frame = tk.Frame(self, bg=BG_COLOR)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Canvas (Größe reduziert)
        self.canvas = tk.Canvas(main_frame, bg=BG_COLOR, width=CANVAS_SIZE, height=CANVAS_SIZE, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=20, pady=5)

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        # Sidebar (Rechts)
        sidebar = tk.Frame(main_frame, bg=BG_COLOR)
        sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        chk_style = {"bg": BG_COLOR, "fg": TEXT_COLOR, "selectcolor": "#444444",
                     "activebackground": BG_COLOR, "activeforeground": TEXT_COLOR, "font": UI_FONT_SMALL}

        tk.Checkbutton(sidebar, text="Bridge", variable=self.bridge_gaps,
                       command=self.redraw_canvas, **chk_style).pack(anchor="w")
        tk.Checkbutton(sidebar, text="Corners", variable=self.fill_corners,
                       command=self.redraw_canvas, **chk_style).pack(anchor="w")

        self.info_label = tk.Label(sidebar, text="Ready.", bg=BG_COLOR, fg="#888888", font=UI_FONT_SMALL,
                                   justify=tk.LEFT)
        self.info_label.pack(pady=10, anchor="w")

        self.update_ui_state()

    # --- LOGIK (Unverändert gut) ---

    def grid_to_list(self):
        flat_list = []
        for r in range(4):
            for c in range(4):
                val = self.grid_data[r][c]
                if val is None:
                    flat_list.append(-1)
                else:
                    flat_list.append(val)
        return flat_list

    def list_to_grid(self, flat_list):
        new_grid = [[None for _ in range(4)] for _ in range(4)]
        for i, val in enumerate(flat_list):
            r = i // 4
            c = i % 4
            if val == -1:
                new_grid[r][c] = None
            else:
                new_grid[r][c] = val
        return new_grid

    def load_current_slot(self):
        try:
            slot_id = int(self.slot_spinner.get())
            nibble_data = self.settings_manager.data["library"]["nibbleGrids"][slot_id]
            cells = nibble_data.get("cells", [-1] * 16)
            self.grid_data = self.list_to_grid(cells)
            self.redraw_canvas()
            self.update_ui_state()
            self.info_label.config(text=f"Loaded {slot_id}")
        except Exception as e:
            self.info_label.config(text="Error")
            print(e)

    def save_current_slot(self):
        try:
            slot_id = int(self.slot_spinner.get())
            flat_cells = self.grid_to_list()
            target_nibble = self.settings_manager.data["library"]["nibbleGrids"][slot_id]
            target_nibble["cells"] = flat_cells
            self.settings_manager.save_settings()
            self.info_label.config(text=f"Saved {slot_id}!")
        except Exception as e:
            self.info_label.config(text="Error")
            print(e)

    def get_group_count(self, group_id):
        count = 0
        for row in self.grid_data:
            for cell in row:
                if cell == group_id:
                    count += 1
        return count

    def select_tool(self, group_id):
        self.current_group_id = group_id
        self.update_ui_state()

    def update_ui_state(self):
        for gid, btn in self.group_buttons.items():
            count = self.get_group_count(gid)
            limit = GROUP_LIMITS[gid]
            btn.config(text=f"{gid} [{count}/{limit}]")

            # Button Feedback ohne Springen
            if gid == self.current_group_id:
                btn.set_active(True)
            else:
                btn.set_active(False)

    def reset_grid(self):
        self.grid_data = [[None for _ in range(4)] for _ in range(4)]
        self.redraw_canvas()
        self.update_ui_state()

    def get_grid_pos(self, event):
        grid_width = 4 * CELL_SIZE + 3 * GAP_SIZE
        offset_x = (CANVAS_SIZE - grid_width) // 2
        offset_y = (CANVAS_SIZE - grid_width) // 2
        rx = event.x - offset_x
        ry = event.y - offset_y
        col = rx // (CELL_SIZE + GAP_SIZE)
        row = ry // (CELL_SIZE + GAP_SIZE)
        if 0 <= col < 4 and 0 <= row < 4:
            return row, col
        return None, None

    def on_mouse_down(self, event):
        row, col = self.get_grid_pos(event)
        if row is None: return
        current_val = self.grid_data[row][col]
        if current_val == self.current_group_id:
            self.drag_mode = "erase"
        else:
            self.drag_mode = "paint"
        self.apply_tool(row, col)
        self.last_drag_cell = (row, col)

    def on_mouse_drag(self, event):
        row, col = self.get_grid_pos(event)
        if row is None: return
        if (row, col) != self.last_drag_cell:
            self.apply_tool(row, col)
            self.last_drag_cell = (row, col)

    def on_mouse_up(self, event):
        self.drag_mode = None
        self.last_drag_cell = None

    def apply_tool(self, row, col):
        if self.drag_mode == "erase":
            if self.grid_data[row][col] == self.current_group_id:
                self.grid_data[row][col] = None
        elif self.drag_mode == "paint":
            count = self.get_group_count(self.current_group_id)
            if count < GROUP_LIMITS[self.current_group_id]:
                self.grid_data[row][col] = self.current_group_id

        self.redraw_canvas()
        self.update_ui_state()

    def redraw_canvas(self):
        self.canvas.delete("all")
        grid_pixel_size = 4 * CELL_SIZE + 3 * GAP_SIZE
        off_x = (CANVAS_SIZE - grid_pixel_size) // 2
        off_y = (CANVAS_SIZE - grid_pixel_size) // 2

        # 1. Basis-Zellen
        for r in range(4):
            for c in range(4):
                gid = self.grid_data[r][c]
                x1 = off_x + c * (CELL_SIZE + GAP_SIZE)
                y1 = off_y + r * (CELL_SIZE + GAP_SIZE)

                color = "#2A2A2A"  # Leer (etwas heller als BG)
                if gid is not None: color = GROUP_COLORS[gid]

                self.canvas.create_rectangle(x1, y1, x1 + CELL_SIZE, y1 + CELL_SIZE, fill=color, outline="",
                                             tags="cell")

        if not self.bridge_gaps.get(): return

        # 2. Brücken
        for r in range(4):
            for c in range(4):
                gid = self.grid_data[r][c]
                if gid is None: continue
                x1 = off_x + c * (CELL_SIZE + GAP_SIZE)
                y1 = off_y + r * (CELL_SIZE + GAP_SIZE)
                if c < 3 and self.grid_data[r][c + 1] == gid:
                    self.canvas.create_rectangle(x1 + CELL_SIZE - 1, y1, x1 + CELL_SIZE + GAP_SIZE + 1, y1 + CELL_SIZE,
                                                 fill=GROUP_COLORS[gid], outline="", tags="bridge")
                if r < 3 and self.grid_data[r + 1][c] == gid:
                    self.canvas.create_rectangle(x1, y1 + CELL_SIZE - 1, x1 + CELL_SIZE, y1 + CELL_SIZE + GAP_SIZE + 1,
                                                 fill=GROUP_COLORS[gid], outline="", tags="bridge")

        # 3. Ecken
        if self.fill_corners.get():
            for r in range(3):
                for c in range(3):
                    g = self.grid_data[r][c]
                    if g is not None and g == self.grid_data[r][c + 1] == self.grid_data[r + 1][c] == \
                            self.grid_data[r + 1][c + 1]:
                        cx1 = off_x + c * (CELL_SIZE + GAP_SIZE) + CELL_SIZE - 1
                        cy1 = off_y + r * (CELL_SIZE + GAP_SIZE) + CELL_SIZE - 1
                        self.canvas.create_rectangle(cx1, cy1, cx1 + GAP_SIZE + 2, cy1 + GAP_SIZE + 2,
                                                     fill=GROUP_COLORS[g], outline="", tags="corner")