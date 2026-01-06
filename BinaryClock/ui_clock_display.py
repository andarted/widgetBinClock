import tkinter as tk
from datetime import datetime
from ui_shared import BG_COLOR

# --- KONFIGURATION ---
CELL_SIZE = 20
GAP_SIZE = 4
NIBBLE_GAP = 30


class ClockDisplay(tk.Frame):
    def __init__(self, parent, settings_manager):
        super().__init__(parent, bg=BG_COLOR)
        self.settings_manager = settings_manager

        self.running = False
        self.canvas = tk.Canvas(self, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.debug_label = tk.Label(self, text="", bg=BG_COLOR, fg="#555555", font=("Consolas", 10))
        self.debug_label.pack(side=tk.BOTTOM, pady=5)

    def start(self):
        if not self.running:
            self.running = True
            self.update_loop()

    def stop(self):
        self.running = False

    def get_day_ms(self):
        now = datetime.now()
        return (now.hour * 3600000) + (now.minute * 60000) + (now.second * 1000) + (now.microsecond // 1000)

    def update_loop(self):
        if not self.running: return

        # 1. Zeit berechnen
        ms_per_day = 86_400_000
        total_units = 65536
        ms_now = self.get_day_ms()

        v16 = int((ms_now * total_units) / ms_per_day)

        # 2. Zeichnen
        self.render_clock(v16)
        self.debug_label.config(text=f"VALUE: 0x{v16:04X} ({v16})")

        # 3. Smart Sleep
        ms_per_tick = ms_per_day / total_units
        next_tick_v16 = v16 + 1
        next_tick_ms = int(next_tick_v16 * ms_per_tick)
        delay = next_tick_ms - ms_now

        if delay < 10: delay = 10

        self.after(delay, self.update_loop)

    def render_clock(self, v16):
        self.canvas.delete("all")

        # --- DATEN LADEN (Aktuell alles Slot 0) ---
        try:
            # 1. Welches Setting ist aktiv?
            active_id = self.settings_manager.data.get("active_profileId", 0)
            # Sicherheitscheck, falls ID out of range
            if active_id >= len(self.settings_manager.data["profiles"]): active_id = 0

            current_profile = self.settings_manager.data["profiles"][active_id]

            # 2. Die IDs aus dem Setting holen
            nibble_id = current_profile.get("nibbleGridId", 0)
            layout_id = current_profile.get("layoutId", 0)
            palette_id = current_profile.get("paletteId", 0)

            # 3. Die eigentlichen Daten anhand der IDs laden

            # A) Design
            design_cells = self.settings_manager.data["library"]["nibbleGrids"][nibble_id]["cells"]
            grid_design = self.list_to_grid(design_cells)

            # B) Layout
            layout_placements = self.settings_manager.data["library"]["layoutGrids"][layout_id].get("placements", [])

            # C) Palette
            palette_data = self.settings_manager.data["library"]["palettes"][palette_id]
            palette_colors = palette_data.get("colors", ["#333333"] * 16)

            if len(palette_colors) < 16: palette_colors = ["#333333"] * 16

        except Exception as e:
            print(f"Error reading data: {e}")
            return

        if not layout_placements: return

        # --- POSITIONIERUNG ---
        nibble_pixel_size = (4 * CELL_SIZE) + (3 * GAP_SIZE)
        layout_w = 4 * nibble_pixel_size + 3 * NIBBLE_GAP
        layout_h = 4 * nibble_pixel_size + 3 * NIBBLE_GAP

        start_x = (self.canvas.winfo_width() - layout_w) // 2
        start_y = (self.canvas.winfo_height() - layout_h) // 2
        if start_x < 0: start_x = 10
        if start_y < 0: start_y = 10

        # --- RENDERING ---
        for p in layout_placements:
            nibble_id = p["nibbleId"]  # 3, 2, 1, 0

            grid_x = p["position"]["x"]
            grid_y = p["position"]["y"]

            # Mirror Flags lesen
            mirror_opts = p.get("mirror", {"x": False, "y": False})
            mirror_x = mirror_opts.get("x", False)
            mirror_y = mirror_opts.get("y", False)

            # Wert extrahieren
            shift_amount = nibble_id * 4
            val = (v16 >> shift_amount) & 0xF

            # Pixel-Position
            px = start_x + grid_x * (nibble_pixel_size + NIBBLE_GAP)
            py = start_y + grid_y * (nibble_pixel_size + NIBBLE_GAP)

            # Grid transformieren (falls nötig)
            current_grid_design = grid_design  # Kopie der Referenz
            if mirror_x or mirror_y:
                current_grid_design = self.transform_grid(grid_design, mirror_x, mirror_y)

            # Zeichnen - Jetzt mit Palette und nibble_id!
            self.draw_single_nibble(px, py, val, current_grid_design, nibble_id, palette_colors)

    def transform_grid(self, original_grid, mx, my):
        """
        Erstellt eine gespiegelte Kopie des 4x4 Grids.
        Das ist viel einfacher als Koordinaten-Mathematik beim Zeichnen!
        """
        # 1. Tiefe Kopie erstellen (damit wir das Original nicht ändern)
        # Ein einfaches List Comprehension reicht hier, da wir Strings/Ints spiegeln
        new_grid = [row[:] for row in original_grid]

        # 2. Horizontal spiegeln (Zeilen umkehren)
        if mx:
            for r in range(4):
                new_grid[r] = new_grid[r][::-1]

        # 3. Vertikal spiegeln (Reihenfolge der Zeilen umkehren)
        if my:
            new_grid = new_grid[::-1]

        return new_grid

    def draw_single_nibble(self, ox, oy, val, grid, nibble_id, palette):
        """
        ox, oy: Pixel Koordinate
        val: Wert (0-15)
        grid: Form-Template
        nibble_id: Welches Nibble ist das? (3=H1, 0=M0) -> Wichtig für Farbe!
        palette: Liste mit 16 Hex-Codes
        """

        def is_active(gid):
            if gid is None or gid == -1: return False
            return (val >> gid) & 1

        # Helper um die richtige Farbe zu holen
        def get_color(gid):
            # Formel: Welches Bit im 16-Bit Integer ist das?
            # Nibble 3 (Bits 15-12), Nibble 0 (Bits 3-0)
            abs_bit_index = (nibble_id * 4) + gid
            try:
                return palette[abs_bit_index]
            except:
                return "#FF0000"  # Fehler-Rot

        # 1. Basis Zellen
        for r in range(4):
            for c in range(4):
                gid = grid[r][c]

                if is_active(gid):
                    x1 = ox + c * (CELL_SIZE + GAP_SIZE)
                    y1 = oy + r * (CELL_SIZE + GAP_SIZE)

                    self.canvas.create_rectangle(x1, y1, x1 + CELL_SIZE, y1 + CELL_SIZE,
                                                 fill=get_color(gid), outline="", tags="clock_cell")

        # 2. Brücken
        for r in range(4):
            for c in range(4):
                gid = grid[r][c]
                if not is_active(gid): continue

                x1 = ox + c * (CELL_SIZE + GAP_SIZE)
                y1 = oy + r * (CELL_SIZE + GAP_SIZE)
                color = get_color(gid)

                # Rechts
                if c < 3 and grid[r][c + 1] == gid:
                    self.canvas.create_rectangle(x1 + CELL_SIZE - 1, y1, x1 + CELL_SIZE + GAP_SIZE + 1, y1 + CELL_SIZE,
                                                 fill=color, outline="", tags="clock_bridge")
                # Unten
                if r < 3 and grid[r + 1][c] == gid:
                    self.canvas.create_rectangle(x1, y1 + CELL_SIZE - 1, x1 + CELL_SIZE, y1 + CELL_SIZE + GAP_SIZE + 1,
                                                 fill=color, outline="", tags="clock_bridge")

        # 3. Ecken
        for r in range(3):
            for c in range(3):
                g1 = grid[r][c]
                # Check ob 2x2 Block identisch ist
                if g1 is not None and g1 == grid[r][c + 1] == grid[r + 1][c] == grid[r + 1][c + 1]:
                    if is_active(g1):
                        cx1 = ox + c * (CELL_SIZE + GAP_SIZE) + CELL_SIZE - 1
                        cy1 = oy + r * (CELL_SIZE + GAP_SIZE) + CELL_SIZE - 1

                        self.canvas.create_rectangle(cx1, cy1, cx1 + GAP_SIZE + 2, cy1 + GAP_SIZE + 2,
                                                     fill=get_color(g1), outline="", tags="clock_corner")

        # In ClockDisplay Klasse einfügen:
    def force_redraw(self):
        # Zeit neu berechnen für instant feedback
        ms_per_day = 86_400_000
        total_units = 65536
        ms_now = self.get_day_ms()
        v16 = int((ms_now * total_units) / ms_per_day)

        self.render_clock(v16)

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