import tkinter as tk
from ui_shared import BG_COLOR, GROUP_COLORS  # <--- NEU: GROUP_COLORS importieren


class MiniGridSelector(tk.Frame):
    def __init__(self, parent, settings_manager, title, grid_type, color_theme, on_click_callback):
        super().__init__(parent, bg=BG_COLOR, bd=1, relief="solid")
        self.settings_manager = settings_manager
        self.grid_type = grid_type
        self.on_click_callback = on_click_callback
        self.color_theme = color_theme

        self.canvases = []
        self.active_slot = -1

        self.setup_ui(title)

    def setup_ui(self, title):
        header = tk.Label(self, text=title, bg=BG_COLOR, fg=self.color_theme,
                          font=("Futura", 10, "bold"), pady=5)
        header.pack(side=tk.TOP, fill=tk.X)

        grid_frame = tk.Frame(self, bg=BG_COLOR)
        grid_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        for i in range(16):
            r = i // 4
            c = i % 4

            cv = tk.Canvas(grid_frame, width=40, height=40, bg="#303030",
                           highlightthickness=1, highlightbackground="#444444")
            cv.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")

            cv.bind("<Button-1>", lambda event, idx=i: self.on_slot_click(idx))

            grid_frame.grid_columnconfigure(c, weight=1)
            grid_frame.grid_rowconfigure(r, weight=1)

            self.canvases.append(cv)

        self.redraw_all_slots()

    def on_slot_click(self, slot_id):
        if self.on_click_callback:
            self.on_click_callback(slot_id)

    def set_selection(self, slot_id):
        self.active_slot = slot_id
        self.redraw_borders()

    def redraw_borders(self):
        for i, cv in enumerate(self.canvases):
            if i == self.active_slot:
                cv.config(highlightbackground=self.color_theme, highlightthickness=2, bg="#3A3A3A")
            else:
                cv.config(highlightbackground="#444444", highlightthickness=1, bg="#303030")

    def redraw_all_slots(self):
        for i in range(16):
            self.draw_slot_content(i)

    def draw_slot_content(self, slot_id):
        cv = self.canvases[slot_id]
        cv.delete("all")

        w = int(cv.cget("width"))
        h = int(cv.cget("height"))
        if w < 10: w = 40
        if h < 10: h = 40

        if self.grid_type == "profile":
            cv.create_text(w // 2, h // 2, text=str(slot_id), fill="white", font=("Futura", 14, "bold"))

        elif self.grid_type == "nibble":
            self.draw_nibble(cv, slot_id, w, h)

        elif self.grid_type == "layout":
            self.draw_layout(cv, slot_id, w, h)

        elif self.grid_type == "palette":
            self.draw_palette(cv, slot_id, w, h)

    # --- ZEICHEN HELFER ---

    def draw_nibble(self, cv, slot_id, w, h):
        try:
            data = self.settings_manager.data["library"]["nibbleGrids"][slot_id]["cells"]
            cell_w, cell_h = w / 4, h / 4
            for i, val in enumerate(data):
                if val != -1:
                    c, r = i % 4, i // 4
                    x, y = c * cell_w, r * cell_h
                    # FIX 4: Echte Gruppenfarben statt Grau!
                    color = GROUP_COLORS.get(val, "#AAAAAA")
                    cv.create_rectangle(x, y, x + cell_w, y + cell_h, fill=color, outline="")
        except:
            pass

    def draw_palette(self, cv, slot_id, w, h):
        try:
            colors = self.settings_manager.data["library"]["palettes"][slot_id]["colors"]
            cell_w, cell_h = w / 4, h / 4
            for i in range(16):
                if i < len(colors):
                    # FIX 2: Spiegelung der Vorschau (H1 oben, M0 unten; MSB links)
                    # i=0 (Bit 0) -> Soll unten rechts sein (r=3, c=3)
                    # i=15 (Bit 15) -> Soll oben links sein (r=0, c=0)

                    # Zeile: Umkehren (3 - ...)
                    r = 3 - (i // 4)
                    # Spalte: Umkehren (3 - ...)
                    c = 3 - (i % 4)

                    x, y = c * cell_w, r * cell_h
                    cv.create_rectangle(x, y, x + cell_w, y + cell_h, fill=colors[i], outline="")
        except:
            pass

    def draw_layout(self, cv, slot_id, w, h):
        try:
            placements = self.settings_manager.data["library"]["layoutGrids"][slot_id]["placements"]
            cell_w, cell_h = w / 4, h / 4
            token_cols = {3: "#FF5733", 2: "#FF8C33", 1: "#3357FF", 0: "#33FFF5"}
            for p in placements:
                tid = p["nibbleId"]
                c, r = p["position"]["x"], p["position"]["y"]
                x, y = c * cell_w + 2, r * cell_h + 2
                cv.create_rectangle(x, y, x + cell_w - 4, y + cell_h - 4, fill=token_cols.get(tid, "white"), outline="")
        except:
            pass