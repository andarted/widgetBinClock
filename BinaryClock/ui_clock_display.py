import tkinter as tk
from datetime import datetime
from ui_shared import BG_COLOR, GROUP_COLORS

# --- KONFIGURATION ---
CELL_SIZE = 20  # Kleiner als im Editor, damit 4 Stück auf den Schirm passen
GAP_SIZE = 4  # Lücke zwischen Zellen
NIBBLE_GAP = 30  # Lücke zwischen den 4 Nibbles (Blöcken)


class ClockDisplay(tk.Frame):
    def __init__(self, parent, settings_manager):
        super().__init__(parent, bg=BG_COLOR)
        self.settings_manager = settings_manager

        self.running = False
        self.canvas = tk.Canvas(self, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Test-Label (optional, um den Hex-Wert zu sehen)
        self.debug_label = tk.Label(self, text="", bg=BG_COLOR, fg="#555555", font=("Consolas", 10))
        self.debug_label.pack(side=tk.BOTTOM, pady=5)

    def start(self):
        """Startet die Animations-Schleife"""
        if not self.running:
            self.running = True
            self.update_loop()

    def stop(self):
        """Stoppt die Schleife (wichtig beim Tab-Wechsel)"""
        self.running = False

    def get_day_ms(self):
        now = datetime.now()
        return (now.hour * 3600000) + (now.minute * 60000) + (now.second * 1000) + (now.microsecond // 1000)

    def update_loop(self):
        if not self.running: return

        # 1. Zeit berechnen (V16)
        ms_per_day = 86_400_000
        total_units = 65536
        ms_now = self.get_day_ms()

        # Der 16-Bit Wert (0 - 65535)
        v16 = int((ms_now * total_units) / ms_per_day)

        # 2. Zeichnen
        self.render_clock(v16)
        self.debug_label.config(text=f"VALUE: 0x{v16:04X} ({v16})")

        # 3. Smart Sleep Berechnen
        ms_per_tick = ms_per_day / total_units
        next_tick_v16 = v16 + 1
        next_tick_ms = int(next_tick_v16 * ms_per_tick)
        delay = next_tick_ms - ms_now

        if delay < 10: delay = 10

        # Loop
        self.after(delay, self.update_loop)

    def render_clock(self, v16):
        self.canvas.delete("all")

        # Wir laden das Design aus Slot 0 (Hardcoded für den Anfang)
        # Später kommt das aus "active_setting"
        try:
            design_data = self.settings_manager.data["library"]["nibbleGrids"][0]["cells"]
            # Umwandeln in 2D Grid (4x4)
            grid = self.list_to_grid(design_data)
        except:
            return  # Daten noch nicht bereit

        # Wir haben 4 Nibbles im v16 Wert:
        # v16 = [Nibble 3][Nibble 2][Nibble 1][Nibble 0]
        #         (Bits 12-15) (8-11)   (4-7)    (0-3)

        # Positionierung: Wir machen 2x2 Anordnung oder 1x4
        # Lass uns 1x4 machen (nebeneinander), zentriert.

        nibble_pixel_size = (4 * CELL_SIZE) + (3 * GAP_SIZE)
        total_width = (4 * nibble_pixel_size) + (3 * NIBBLE_GAP)

        start_x = (self.canvas.winfo_width() - total_width) // 2
        start_y = (self.canvas.winfo_height() - nibble_pixel_size) // 2

        # Falls Fenster noch nicht aufgebaut, Standard nehmen
        if start_x < 0: start_x = 20
        if start_y < 0: start_y = 50

        # Die 4 Nibbles zeichnen (MSB links -> Nibble 3, 2, 1, 0)
        for i in range(4):
            nibble_index = 3 - i  # 3, 2, 1, 0

            # Wert dieses Nibbles extrahieren (0-15)
            # Verschieben und maskieren
            shift_amount = nibble_index * 4
            nibble_val = (v16 >> shift_amount) & 0xF

            # X-Position für dieses Nibble
            pos_x = start_x + i * (nibble_pixel_size + NIBBLE_GAP)
            pos_y = start_y

            # Zeichne dieses Nibble!
            self.draw_single_nibble(pos_x, pos_y, nibble_val, grid)

    def draw_single_nibble(self, ox, oy, val, grid):
        """
        ox, oy: Oben links Pixel-Koordinate für dieses Nibble
        val: Der Wert (0-15), den wir darstellen wollen (der Status der Bits)
        grid: Das Design-Template (4x4 Array mit Gruppen-IDs)
        """

        # Hilfsfunktion: Ist dieses Bit im aktuellen Wert gesetzt?
        def is_active(gid):
            if gid is None or gid == -1: return False
            return (val >> gid) & 1

        # 1. Basis Zellen zeichnen
        for r in range(4):
            for c in range(4):
                gid = grid[r][c]

                # Nur zeichnen, wenn das Bit für diese Gruppe AN ist
                if is_active(gid):
                    x1 = ox + c * (CELL_SIZE + GAP_SIZE)
                    y1 = oy + r * (CELL_SIZE + GAP_SIZE)

                    color = GROUP_COLORS[gid]
                    self.canvas.create_rectangle(x1, y1, x1 + CELL_SIZE, y1 + CELL_SIZE,
                                                 fill=color, outline="", tags="clock_cell")

        # 2. Brücken zeichnen (Bridge Gaps)
        # Wir machen das hier immer an. Später könnten wir das auch aus den Settings lesen.
        for r in range(4):
            for c in range(4):
                gid = grid[r][c]

                # Wenn diese Zelle nicht aktiv ist, kann sie keine Brücke bilden
                if not is_active(gid): continue

                x1 = ox + c * (CELL_SIZE + GAP_SIZE)
                y1 = oy + r * (CELL_SIZE + GAP_SIZE)

                # Nach Rechts prüfen
                if c < 3:
                    right_gid = grid[r][c + 1]
                    # Brücke nur, wenn Nachbar gleiche ID hat UND auch aktiv ist (Redundant, aber sicher)
                    if right_gid == gid:
                        # Da 'gid' aktiv ist, ist 'right_gid' automatisch auch aktiv (weil gleiche ID)
                        self.canvas.create_rectangle(x1 + CELL_SIZE - 1, y1, x1 + CELL_SIZE + GAP_SIZE + 1,
                                                     y1 + CELL_SIZE,
                                                     fill=GROUP_COLORS[gid], outline="", tags="clock_bridge")

                # Nach Unten prüfen
                if r < 3:
                    bottom_gid = grid[r + 1][c]
                    if bottom_gid == gid:
                        self.canvas.create_rectangle(x1, y1 + CELL_SIZE - 1, x1 + CELL_SIZE,
                                                     y1 + CELL_SIZE + GAP_SIZE + 1,
                                                     fill=GROUP_COLORS[gid], outline="", tags="clock_bridge")

        # 3. Ecken füllen (Fill Corners)
        for r in range(3):
            for c in range(3):
                # Hole die 4 IDs im 2x2 Block
                g1 = grid[r][c]
                g2 = grid[r][c + 1]
                g3 = grid[r + 1][c]
                g4 = grid[r + 1][c + 1]

                # Prüfen: Sind alle 4 gleich?
                if g1 is not None and g1 == g2 and g1 == g3 and g1 == g4:
                    # Prüfen: Ist diese Gruppe gerade AN?
                    if is_active(g1):
                        cx1 = ox + c * (CELL_SIZE + GAP_SIZE) + CELL_SIZE - 1
                        cy1 = oy + r * (CELL_SIZE + GAP_SIZE) + CELL_SIZE - 1

                        self.canvas.create_rectangle(cx1, cy1, cx1 + GAP_SIZE + 2, cy1 + GAP_SIZE + 2,
                                                     fill=GROUP_COLORS[g1], outline="", tags="clock_corner")

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