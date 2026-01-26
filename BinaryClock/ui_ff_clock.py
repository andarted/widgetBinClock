import tkinter as tk
from datetime import datetime, timezone
from ui_shared import BG_COLOR

# --- KONFIGURATION ---
CELL_SIZE = 20
GAP_SIZE = 4
NIBBLE_GAP = 30
STACK_GAP = NIBBLE_GAP

# Epoch: 27.01.2026 UTC
EPOCH_DATE = datetime(2026, 1, 27, 0, 0, 0, tzinfo=timezone.utc)

class FFClockDisplay(tk.Frame):
    def __init__(self, parent, settings_manager):
        super().__init__(parent, bg=BG_COLOR)
        self.settings_manager = settings_manager

        self.running = False
        self.canvas = tk.Canvas(self, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Info Label (angepasst für mehr Infos)
        self.debug_label = tk.Label(self, text="", bg=BG_COLOR, fg="#666666", font=("Consolas", 10))
        self.debug_label.pack(side=tk.BOTTOM, pady=10)

    def start(self):
        if not self.running:
            self.running = True
            self.update_loop()

    def stop(self):
        self.running = False

    def get_ff_value_and_info(self):
        """
        Berechnet den F.F Wert und gibt Infos zur lokalen Zeitzone zurück.
        """
        # 1. Aktuelle Zeit in UTC (für die Berechnung)
        utc_now = datetime.now(timezone.utc)

        # 2. Aktuelle Zeit lokal (für die Anzeige der Zeitzone)
        local_now = datetime.now().astimezone()

        # Berechnung F.F Wert
        delta = utc_now - EPOCH_DATE
        total_seconds = delta.total_seconds()
        raw_val = (total_seconds / 86400.0) * 65536.0

        # Zeitzonen-String bauen (z.B. "UTC+01:00")
        tz_name = local_now.strftime("%Z")  # z.B. CET oder CEST
        utc_offset = local_now.strftime("%z")  # z.B. +0100
        # Formatieren für schönere Lesbarkeit: +01:00
        if len(utc_offset) == 5:
            utc_offset = f"UTC{utc_offset[:3]}:{utc_offset[3:]}"
        else:
            utc_offset = "UTC"

        return int(raw_val), utc_offset

    def update_loop(self):
        if not self.running: return

        # Werte holen
        v32, tz_info = self.get_ff_value_and_info()

        # Zeichnen
        self.render_clock(v32)

        # Label Update mit Zeitzonen-Info
        # Zeigt: F.F Wert | (Lokale Zeitzone erkannt)
        display_val = v32 & 0xFFFFFFFF
        self.debug_label.config(text=f"F.F: {display_val:08X}  (Local: {tz_info})")

        self.after(50, self.update_loop)

    def get_layout_bounds(self, placements):
        if not placements: return 0, 0, 0, 0
        xs = [p["position"]["x"] for p in placements]
        ys = [p["position"]["y"] for p in placements]
        return min(xs), max(xs), min(ys), max(ys)

    def render_clock(self, v32):
        self.canvas.delete("all")

        try:
            active_id = self.settings_manager.data.get("active_profileId", 0)
            if active_id >= len(self.settings_manager.data["profiles"]): active_id = 0
            current_profile = self.settings_manager.data["profiles"][active_id]

            nid = current_profile.get("nibbleGridId", 0)
            lid = current_profile.get("layoutId", 0)
            pid = current_profile.get("paletteId", 0)

            design_cells = self.settings_manager.data["library"]["nibbleGrids"][nid]["cells"]
            grid_design = self.list_to_grid(design_cells)
            layout_placements = self.settings_manager.data["library"]["layoutGrids"][lid].get("placements", [])

            palette_data = self.settings_manager.data["library"]["palettes"][pid]
            palette_colors = palette_data.get("colors", ["#333333"] * 16)
        except:
            return

        if not layout_placements: return

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        min_x, max_x, min_y, max_y = self.get_layout_bounds(layout_placements)
        cols_used = max_x - min_x + 1
        rows_used = max_y - min_y + 1

        nibble_px = (4 * CELL_SIZE) + (3 * GAP_SIZE)
        block_width = (cols_used * nibble_px) + ((cols_used - 1) * NIBBLE_GAP)
        block_height = (rows_used * nibble_px) + ((rows_used - 1) * NIBBLE_GAP)
        total_stack_height = (block_height * 2) + STACK_GAP

        start_x = (w - block_width) // 2
        start_y = (h - total_stack_height) // 2

        # --- ZEICHNEN ---

        # Oberer Block (Tage) -> Palette von Nibble 0 erzwingen (durch Mapping)
        high_16 = (v32 >> 16) & 0xFFFF
        self.draw_layout_block(start_x, start_y, high_16,
                               layout_placements, grid_design, palette_colors,
                               offset_grid_x=min_x, offset_grid_y=min_y,
                               is_day_counter=True)

        # Unterer Block (Zeit)
        y_bot = start_y + block_height + STACK_GAP
        low_16 = v32 & 0xFFFF
        self.draw_layout_block(start_x, y_bot, low_16,
                               layout_placements, grid_design, palette_colors,
                               offset_grid_x=min_x, offset_grid_y=min_y,
                               is_day_counter=False)

    def draw_layout_block(self, px, py, val_16, placements, design, palette, offset_grid_x, offset_grid_y,
                          is_day_counter=False):
        nibble_px = (4 * CELL_SIZE) + (3 * GAP_SIZE)
        step = nibble_px + NIBBLE_GAP

        for p in placements:
            nibble_id = p["nibbleId"]

            # --- COLOR MAPPING ---
            palette_nibble_id = nibble_id
            if is_day_counter:
                # Tageszähler nutzt immer Palette von Nibble 0 (LSB Time)
                palette_nibble_id = 0

            rel_grid_x = p["position"]["x"] - offset_grid_x
            rel_grid_y = p["position"]["y"] - offset_grid_y
            curr_x = px + rel_grid_x * step
            curr_y = py + rel_grid_y * step

            mx = p.get("mirror", {}).get("x", False)
            my = p.get("mirror", {}).get("y", False)
            curr_design = design
            if mx or my: curr_design = self.transform_grid(design, mx, my)

            shift = nibble_id * 4
            nibble_val = (val_16 >> shift) & 0xF

            self.draw_single_nibble(curr_x, curr_y, nibble_val, curr_design, palette_nibble_id, palette)

    def draw_single_nibble(self, ox, oy, val, grid, nibble_id, palette):
        def is_active(gid):
            if gid is None or gid == -1: return False
            return (val >> gid) & 1

        def get_color(gid):
            abs_bit_index = (nibble_id * 4) + gid
            try:
                return palette[abs_bit_index]
            except:
                return "#FF0000"

        for r in range(4):
            for c in range(4):
                gid = grid[r][c]
                if is_active(gid):
                    x1 = ox + c * (CELL_SIZE + GAP_SIZE)
                    y1 = oy + r * (CELL_SIZE + GAP_SIZE)
                    self.canvas.create_rectangle(x1, y1, x1 + CELL_SIZE, y1 + CELL_SIZE, fill=get_color(gid),
                                                 outline="")
        for r in range(4):
            for c in range(4):
                gid = grid[r][c]
                if not is_active(gid): continue
                x1 = ox + c * (CELL_SIZE + GAP_SIZE)
                y1 = oy + r * (CELL_SIZE + GAP_SIZE)
                col = get_color(gid)
                if c < 3 and grid[r][c + 1] == gid:
                    self.canvas.create_rectangle(x1 + CELL_SIZE - 1, y1, x1 + CELL_SIZE + GAP_SIZE + 1, y1 + CELL_SIZE,
                                                 fill=col, outline="")
                if r < 3 and grid[r + 1][c] == gid:
                    self.canvas.create_rectangle(x1, y1 + CELL_SIZE - 1, x1 + CELL_SIZE, y1 + CELL_SIZE + GAP_SIZE + 1,
                                                 fill=col, outline="")
        for r in range(3):
            for c in range(3):
                g1 = grid[r][c]
                if g1 is not None and g1 == grid[r][c + 1] == grid[r + 1][c] == grid[r + 1][c + 1]:
                    if is_active(g1):
                        cx1 = ox + c * (CELL_SIZE + GAP_SIZE) + CELL_SIZE - 1
                        cy1 = oy + r * (CELL_SIZE + GAP_SIZE) + CELL_SIZE - 1
                        self.canvas.create_rectangle(cx1, cy1, cx1 + GAP_SIZE + 2, cy1 + GAP_SIZE + 2,
                                                     fill=get_color(g1), outline="")

    def list_to_grid(self, flat_list):
        new_grid = [[None for _ in range(4)] for _ in range(4)]
        for i, val in enumerate(flat_list):
            r = i // 4
            c = i % 4
            if val != -1: new_grid[r][c] = val
        return new_grid

    def transform_grid(self, original_grid, mx, my):
        new_grid = [row[:] for row in original_grid]
        if mx:
            for r in range(4): new_grid[r] = new_grid[r][::-1]
        if my:
            new_grid = new_grid[::-1]
        return new_grid