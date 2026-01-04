import tkinter as tk
from datetime import datetime
import json
import os

# --- JSON CONFIGURATION START ---

DATEI_NAME = "binClockSettings.json"


# 1. Vorlage für ein einzelnes Nibble-Grid
def create_default_nibble(index):
    return {
        "id": index,
        "name": f"Nibble {index}",
        "cells": [0] * 16,
        "gap": {"x": 2, "y": 2},
        "bridgeGaps": True,
        "fillCorners": True
    }


# 2. Vorlage für das Layout-Grid
def create_default_layout(index):
    return {
        "id": index,
        "name": f"Layout {index}",
        "margin": {"top": 10, "right": 10, "bottom": 10, "left": 10},
        "gap": {"x": 20, "y": 20},
        "placements": [
            {"nibbleId": 0, "position": {"x": 0, "y": 0}, "mirror": {"x": False, "y": False}}
        ]
    }


# 3. Vorlage für die Farbpalette
def create_default_palette(index):
    default_colors = ["#333333"] * 16
    default_colors[0] = "#FFC800"  # Active Color (Gold)
    default_colors[1] = "#2A2A2A"  # Inactive Color (Dunkelgrau)
    return {
        "id": index,
        "name": f"Palette {index}",
        "colors": default_colors
    }


# 4. Vorlage für ein Setting
def create_default_setting(index):
    return {
        "id": index,
        "name": f"Setting {index}",
        "layoutId": 0,
        "paletteId": 0
    }


DEFAULT_SETTINGS = {
    "version": "0.1",
    "active_settingId": 0,
    "library": {
        "nibbleGrids": [create_default_nibble(i) for i in range(16)],
        "layoutGrids": [create_default_layout(i) for i in range(16)],
        "palettes": [create_default_palette(i) for i in range(16)]
    },
    "settings": [create_default_setting(i) for i in range(16)]
}


def load_settings():
    if os.path.exists(DATEI_NAME):
        try:
            with open(DATEI_NAME, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except json.JSONDecodeError:
            print("Fehler: JSON-Datei ist beschädigt. Lade Standards.")

    with open(DATEI_NAME, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_SETTINGS, f, indent=4)
    return DEFAULT_SETTINGS


# --- JSON CONFIGURATION END ---


# --- LOGIC & UI START ---

bit_rects = []
hex_label_id = None  # ID für das Text-Element auf dem Canvas

# Konstanten
MS_PER_DAY = 86_400_000
TOTAL_UNITS = 65536
MS_PER_TICK = MS_PER_DAY / TOTAL_UNITS


def get_day_ms():
    now = datetime.now()
    return (now.hour * 3600000) + (now.minute * 60000) + (now.second * 1000) + (now.microsecond // 1000)


def update_clock():
    """Berechnet V16, aktualisiert Bits & Hex-Text, plant nächsten Tick."""
    ms_now = get_day_ms()

    # 1. Berechne den 16-Bit Wert (0 bis 65535)
    v16 = int((ms_now * TOTAL_UNITS) / MS_PER_DAY)

    # 2. Bits zeichnen
    for i in range(16):
        is_active = (v16 >> i) & 1
        color = active_color if is_active else inactive_color
        canvas.itemconfig(bit_rects[i], fill=color, outline=bg_color)

    # 3. Hex-Text aktualisieren
    # :04X bedeutet: 4 Stellen, mit 0 auffüllen, uppercase Hex
    hex_string = f"{v16:04X}"
    canvas.itemconfig(hex_label_id, text=hex_string)

    # 4. Smart Scheduling
    next_tick_v16 = v16 + 1
    next_tick_ms = int(next_tick_v16 * MS_PER_TICK)

    delay = next_tick_ms - ms_now
    if delay < 10:
        delay = 10

    root.after(delay, update_clock)


def start_move(event):
    root.x = event.x
    root.y = event.y


def stop_move(event):
    root.x = None
    root.y = None


def do_move(event):
    deltax = event.x - root.x
    deltay = event.y - root.y
    x = root.winfo_x() + deltax
    y = root.winfo_y() + deltay
    root.geometry(f"+{x}+{y}")


def quit_app(event):
    root.destroy()


# --- APP SETUP ---

app_data = load_settings()
root = tk.Tk()

# Fenstereinstellungen
root.attributes('-topmost', True)
root.overrideredirect(True)
root.attributes('-alpha', 0.90)

# Farben laden
try:
    active_id = app_data["active_settingId"]
    palette_id = app_data["settings"][active_id]["paletteId"]
    palette = app_data["library"]["palettes"][palette_id]

    active_color = palette["colors"][0]
    inactive_color = palette["colors"][1] if len(palette["colors"]) > 1 else "#333333"
    bg_color = "#202020"
except Exception as e:
    active_color = "#FFC800"
    inactive_color = "#333333"
    bg_color = "#202020"

root.configure(bg=bg_color)
# Höhe auf 140 erhöht für den Text unten drunter
root.geometry("340x140+100+100")

canvas = tk.Canvas(root, width=340, height=140, bg=bg_color, highlightthickness=0)
canvas.pack(expand=True, fill='both')

# --- INITIALISIERUNG ---

box_size = 30
gap = 5
start_x = 20
start_y = 20

# 1. Boxen erstellen
bit_rects = [None] * 16
for i in range(16):
    if i < 8:
        # Low Byte (Unten) -> Bits 0-7
        row = 1
        col = 7 - i
    else:
        # High Byte (Oben) -> Bits 8-15
        row = 0
        col = 7 - (i - 8)

    x1 = start_x + (col * (box_size + gap))
    y1 = start_y + (row * (box_size + gap))
    x2 = x1 + box_size
    y2 = y1 + box_size

    rect_id = canvas.create_rectangle(x1, y1, x2, y2, fill=inactive_color, outline=bg_color)
    bit_rects[i] = rect_id

# 2. Hex-Text Label erstellen (Zentriert unter den Boxen)
# Die Breite der Grafik ist 8 * (30+5) - 5 + 40 Rand ≈ 300px
text_x = 340 / 2
text_y = start_y + (2 * (box_size + gap)) + 25  # Etwas Abstand unter den Boxen

hex_label_id = canvas.create_text(
    text_x,
    text_y,
    text="0x0000",
    fill=active_color,
    font=("Consolas", 24, "bold")  # Monospace Font für Code-Look
)

# Events
root.bind("<ButtonPress-1>", start_move)
root.bind("<ButtonRelease-1>", stop_move)
root.bind("<B1-Motion>", do_move)
root.bind("<q>", quit_app)
root.bind("<Escape>", quit_app)

update_clock()
root.mainloop()