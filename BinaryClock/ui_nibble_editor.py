# Datei: ui_nibble_editor.py
import tkinter as tk

# --- KONFIGURATION ---
CELL_SIZE = 40
GAP_SIZE = 10  # Groß gewählt, damit man den Bridge-Effekt gut sieht
CANVAS_SIZE = 400

# Farben für die 4 Gruppen (Bit 0 bis Bit 3) zum Editieren
# Gruppe 0 (Wert 1): 1 Zelle
# Gruppe 1 (Wert 2): 2 Zellen
# Gruppe 2 (Wert 4): 4 Zellen
# Gruppe 3 (Wert 8): 8 Zellen
GROUP_COLORS = {
    0: "#FF5733", # Rot/Orange
    1: "#33FF57", # Grün
    2: "#3357FF", # Blau
    3: "#F333FF"  # Magenta
}

GROUP_LIMITS = {0: 1, 1: 2, 2: 4, 3: 8}

class NibbleEditor(tk.Frame):  # Wir erben von Frame, nicht Tk (besser zum Einbinden!)
    def __init__(self, parent, settings_manager):
        super().__init__(parent)  # Konstruktor von tk.Frame aufrufen
        self.settings_manager = settings_manager  # Referenz auf Daten halten

        # Daten-Modell (lokal für den Editor)
        self.grid_data = [[None for _ in range(4)] for _ in range(4)]
        self.current_group_id = 3

        # UI Variablen
        self.bridge_gaps = tk.BooleanVar(value=True)
        self.fill_corners = tk.BooleanVar(value=True)

        # GUI aufbauen
        self.setup_ui()
        self.redraw_canvas()

    def setup_ui(self):
        # --- HAUPT-TOOLBAR CONTAINER ---
        toolbar = tk.Frame(self, pady=10, bg="#E0E0E0")  # Leicht grau, damit man sie sieht
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Wir bauen zwei Unter-Container, damit die Anordnung stabil bleibt
        left_area = tk.Frame(toolbar, bg="#E0E0E0")
        left_area.pack(side=tk.LEFT, padx=10)

        right_area = tk.Frame(toolbar, bg="#E0E0E0")
        right_area.pack(side=tk.RIGHT, padx=10)

        # --- LINKER BEREICH: Slot & Tools ---

        # 1. Slot Auswahl
        tk.Label(left_area, text="Slot:", bg="#E0E0E0").pack(side=tk.LEFT)

        # Spinbox Command direkt beim Klicken
        self.slot_spinner = tk.Spinbox(left_area, from_=0, to=15, width=3, command=self.load_current_slot)
        self.slot_spinner.pack(side=tk.LEFT, padx=5)

        # Laden Button
        tk.Button(left_area, text="Laden", command=self.load_current_slot, font=("Arial", 9)).pack(side=tk.LEFT)

        # Optischer Trenner
        tk.Label(left_area, text=" | ", bg="#E0E0E0", fg="#888888").pack(side=tk.LEFT, padx=5)

        # 2. Mal-Werkzeuge
        tk.Label(left_area, text="Tool:", bg="#E0E0E0").pack(side=tk.LEFT)

        self.group_buttons = {}
        for gid in range(4):
            btn = tk.Button(
                left_area,
                text=f"{gid}",  # Kurzer Text (nur 0, 1, 2, 3), spart Platz!
                width=3,  # Feste Breite sieht ordentlicher aus
                bg=GROUP_COLORS[gid],
                command=lambda g=gid: self.select_tool(g)
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.group_buttons[gid] = btn

        # --- RECHTER BEREICH: Aktionen ---

        # Reset Button (Hier ist er wieder!)
        tk.Button(right_area, text="Leeren", command=self.reset_grid, bg="#FFCCCC").pack(side=tk.LEFT, padx=5)

        # Speichern Button
        tk.Button(right_area, text="💾 Speichern", command=self.save_current_slot, bg="#CCFFCC").pack(side=tk.LEFT)

        # -----------------------------------------
        # --- DARUNTER: HAUPTBEREICH (CANVAS) ---
        main_frame = tk.Frame(self)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Canvas
        self.canvas = tk.Canvas(main_frame, bg="#202020", width=CANVAS_SIZE, height=CANVAS_SIZE)
        self.canvas.pack(side=tk.LEFT, padx=20, pady=20)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Sidebar (Rechts neben Canvas)
        sidebar = tk.Frame(main_frame)
        sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=20)

        tk.Checkbutton(sidebar, text="Gaps überbrücken", variable=self.bridge_gaps,
                       command=self.redraw_canvas).pack(anchor="w")
        tk.Checkbutton(sidebar, text="Ecken füllen", variable=self.fill_corners,
                       command=self.redraw_canvas).pack(anchor="w")

        # Info Label für Feedback ("Gespeichert!")
        self.info_label = tk.Label(sidebar, text="Bereit.", fg="blue", justify=tk.LEFT)
        self.info_label.pack(pady=20, anchor="w")

        # Initialen Status setzen
        self.update_ui_state()


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

    def on_canvas_click(self, event):
        # Klick-Koordinate in Grid-Index umrechnen
        # Wir zentrieren das Grid auf dem Canvas
        grid_width = 4 * CELL_SIZE + 3 * GAP_SIZE
        offset_x = (CANVAS_SIZE - grid_width) // 2
        offset_y = (CANVAS_SIZE - grid_width) // 2

        # Relativ zum Grid-Start
        rx = event.x - offset_x
        ry = event.y - offset_y

        # Annäherung an Spalte/Zeile (inklusive Gap-Hitbox Toleranz)
        # Einfache Berechnung: Wir teilen durch (Cell+Gap)
        col = rx // (CELL_SIZE + GAP_SIZE)
        row = ry // (CELL_SIZE + GAP_SIZE)

        if 0 <= col < 4 and 0 <= row < 4:
            # Checken, ob wir genau in eine Zelle geklickt haben (nicht in den Gap)
            # Im Editor ist es netter, wenn man auch den Gap trifft, daher ignorieren wir das
            # Fein-Tuning für jetzt.

            current_val = self.grid_data[row][col]

            if current_val == self.current_group_id:
                # Toggle OFF: Wenn man auf eigene Farbe klickt -> löschen
                self.grid_data[row][col] = None
            else:
                # Toggle ON: Aber erst prüfen ob Limit erreicht
                count = self.get_group_count(self.current_group_id)
                if count < GROUP_LIMITS[self.current_group_id]:
                    self.grid_data[row][col] = self.current_group_id
                else:
                    print("Limit für diese Gruppe erreicht! Lösche erst eine andere Zelle.")

            self.redraw_canvas()
            self.update_ui_state()

    def redraw_canvas(self):
        self.canvas.delete("all")

        # Zentrierung berechnen
        grid_pixel_size = 4 * CELL_SIZE + 3 * GAP_SIZE
        off_x = (CANVAS_SIZE - grid_pixel_size) // 2
        off_y = (CANVAS_SIZE - grid_pixel_size) // 2

        # 1. Basis-Zellen zeichnen
        for r in range(4):
            for c in range(4):
                gid = self.grid_data[r][c]

                x1 = off_x + c * (CELL_SIZE + GAP_SIZE)
                y1 = off_y + r * (CELL_SIZE + GAP_SIZE)
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                color = "#404040"  # Leer-Farbe
                if gid is not None:
                    color = GROUP_COLORS[gid]

                # Wir taggen die Rechtecke mit ihrer ID, falls wir später animieren wollen
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="", tags="cell")

        # Wenn Bridging deaktiviert ist, sind wir fertig
        if not self.bridge_gaps.get():
            return

        # 2. Gaps überbrücken (Horizonal & Vertikal)
        for r in range(4):
            for c in range(4):
                gid = self.grid_data[r][c]
                if gid is None: continue

                # Basis-Koordinaten der aktuellen Zelle
                x1 = off_x + c * (CELL_SIZE + GAP_SIZE)
                y1 = off_y + r * (CELL_SIZE + GAP_SIZE)

                # A. Nach rechts prüfen
                if c < 3:
                    right_gid = self.grid_data[r][c + 1]
                    if right_gid == gid:
                        # Zeichne Brücke
                        bx1 = x1 + CELL_SIZE - 1  # -1 für Overlap gegen Anti-Aliasing Blitzer
                        by1 = y1
                        bx2 = x1 + CELL_SIZE + GAP_SIZE + 1
                        by2 = y1 + CELL_SIZE
                        self.canvas.create_rectangle(bx1, by1, bx2, by2, fill=GROUP_COLORS[gid], outline="",
                                                     tags="bridge")

                # B. Nach unten prüfen
                if r < 3:
                    bottom_gid = self.grid_data[r + 1][c]
                    if bottom_gid == gid:
                        # Zeichne Brücke
                        bx1 = x1
                        by1 = y1 + CELL_SIZE - 1
                        bx2 = x1 + CELL_SIZE
                        by2 = y1 + CELL_SIZE + GAP_SIZE + 1
                        self.canvas.create_rectangle(bx1, by1, bx2, by2, fill=GROUP_COLORS[gid], outline="",
                                                     tags="bridge")

        # 3. Ecken füllen (Optional)
        if self.fill_corners.get():
            for r in range(3):
                for c in range(3):
                    # Wir betrachten das 2x2 Grid startend bei r,c
                    g1 = self.grid_data[r][c]
                    g2 = self.grid_data[r][c + 1]
                    g3 = self.grid_data[r + 1][c]
                    g4 = self.grid_data[r + 1][c + 1]

                    # Wenn alle 4 die gleiche ID haben (und nicht None sind)
                    if g1 is not None and g1 == g2 and g1 == g3 and g1 == g4:
                        # Fülle das Loch in der Mitte
                        # Koordinate ist unter der Zelle (r,c) im Gap Bereich
                        cx1 = off_x + c * (CELL_SIZE + GAP_SIZE) + CELL_SIZE - 1
                        cy1 = off_y + r * (CELL_SIZE + GAP_SIZE) + CELL_SIZE - 1
                        cx2 = cx1 + GAP_SIZE + 2
                        cy2 = cy1 + GAP_SIZE + 2

                        self.canvas.create_rectangle(cx1, cy1, cx2, cy2, fill=GROUP_COLORS[g1], outline="",
                                                     tags="corner")

        # Trick: Canvas Display Order.
        # Da wir Rechtecke über Rechtecke malen, sieht man manchmal Kanten.
        # "lift" holt Dinge nach vorne. Aber da alle die gleiche Farbe haben, passt das so meistens.

    def reset_grid(self):
        self.grid_data = [[None for _ in range(4)] for _ in range(4)]
        self.redraw_canvas()
        self.update_ui_state()

    def update_ui_state(self):
        # Buttons aktualisieren (Active State anzeigen)
        for gid, btn in self.group_buttons.items():
            count = self.get_group_count(gid)
            limit = GROUP_LIMITS[gid]
            if gid == self.current_group_id:
                btn.config(relief=tk.SUNKEN, text=f"Bit {gid} [{count}/{limit}]")
            else:
                btn.config(relief=tk.RAISED, text=f"Bit {gid} [{count}/{limit}]")


    # umwandeln für json datei, bzw. halt für unsere activ laufenden Daten
    def grid_to_list(self):
        """Wandelt das 4x4 Editor-Grid in eine flache Liste für JSON um."""
        flat_list = []
        for r in range(4):
            for c in range(4):
                val = self.grid_data[r][c]
                # Im Editor ist None leer, im JSON ist 0 leer (oder -1?
                # Warte, wir nutzen im Editor Gruppen 0-3.
                # Im JSON sollten wir definieren: -1 (oder 0) ist leer.
                # Lass uns sagen: 0 ist Gruppe 0, 1 ist Grp 1...
                # Aber was ist leer?
                # Vorschlag: Speichere -1 für leer.
                if val is None:
                    flat_list.append(-1)
                else:
                    flat_list.append(val)
        return flat_list

    def list_to_grid(self, flat_list):
        """Wandelt die flache JSON-Liste zurück in das 4x4 Editor-Grid."""
        new_grid = [[None for _ in range(4)] for _ in range(4)]
        for i, val in enumerate(flat_list):
            r = i // 4
            c = i % 4
            if val == -1:
                new_grid[r][c] = None
            else:
                new_grid[r][c] = val
        return new_grid

    # SPEICHERN und LADEN
    def load_current_slot(self):
        """Lädt die Daten aus dem SettingsManager in den Editor."""
        try:
            slot_id = int(self.slot_spinner.get())
            print(f"Lade Slot {slot_id}...")

            # Zugriff auf die Daten im Manager
            # Struktur: library -> nibbleGrids -> Liste -> Element an Index slot_id
            nibble_data = self.settings_manager.data["library"]["nibbleGrids"][slot_id]

            # Zellen holen und ins Grid umwandeln
            cells = nibble_data.get("cells", [-1] * 16)  # Default -1 falls leer
            self.grid_data = self.list_to_grid(cells)

            self.redraw_canvas()
            self.update_ui_state()

        except Exception as e:
            print(f"Fehler beim Laden: {e}")

    def save_current_slot(self):
        """Speichert das aktuelle Grid zurück ins JSON."""
        try:
            slot_id = int(self.slot_spinner.get())
            print(f"Speichere Slot {slot_id}...")

            # 1. Daten aus Editor holen
            flat_cells = self.grid_to_list()

            # 2. Ins Daten-Objekt schreiben
            # Wir holen uns eine Referenz auf das Dictionary im Speicher
            target_nibble = self.settings_manager.data["library"]["nibbleGrids"][slot_id]
            target_nibble["cells"] = flat_cells

            # 3. Auf Festplatte schreiben
            self.settings_manager.save_settings()

            # Feedback (optional in info_label schreiben)
            self.info_label.config(text=f"Slot {slot_id} gespeichert!")

        except Exception as e:
            print(f"Fehler beim Speichern: {e}")