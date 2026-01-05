# Datei: settings_manager.py
import json
import os


class SettingsManager:
    def __init__(self, filename="binClockSettings.json"):
        self.filename = filename
        self.data = self.load_settings()


    def create_default_nibble(self, index):
        return {
            "id": index,
            "name": f"Nibble {index}",
            "cells": [-1] * 16,
            "gap": {"x": 2, "y": 2},
            "bridgeGaps": True,
            "fillCorners": True
        }

    def create_default_layout(self, index):
        return {
            "id": index,
            "name": f"Layout {index}",
            "margin": {"top": 10, "right": 10, "bottom": 10, "left": 10},
            "gap": {"x": 20, "y": 20},
            "placements": [
                {"nibbleId": 0, "position": {"x": 0, "y": 0}, "mirror": {"x": False, "y": False}}
            ]
        }

    def create_default_palette(self, index):
        default_colors = ["#333333"] * 16
        default_colors[0] = "#FFC800"  # Active Color (Gold)
        default_colors[1] = "#2A2A2A"  # Inactive Color (Dunkelgrau)
        return {
            "id": index,
            "name": f"Palette {index}",
            "colors": default_colors
        }

    def create_default_setting(self, index):
        return {
            "id": index,
            "name": f"Setting {index}",
            "layoutId": 0,
            "paletteId": 0,
            "nibbleGridId": 0
        }

    def get_defaults(self):
        # Hier bauen wir das Dictionary zusammen
        return {
            "version": "0.1",
            "active_settingId": 0,
            "library": {
                "nibbleGrids": [self.create_default_nibble(i) for i in range(16)],
                "layoutGrids": [self.create_default_layout(i) for i in range(16)],
                "palettes": [self.create_default_palette(i) for i in range(16)],
                "profiles": [self.create_default_setting(i) for i in range(16)]
            },
            "settings": [self.create_default_setting(i) for i in range(16)]
        }

    def load_settings(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    print(f"Lade {self.filename}...")
                    return json.load(f)
            except json.JSONDecodeError:
                print("JSON defekt.")

        # Fallback
        print("Erstelle neue Settings.")
        defaults = self.get_defaults()
        self.save_settings(defaults)  # Gleich mal speichern
        return defaults

    def save_settings(self, data=None):
        if data:
            self.data = data
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)
        print("Gespeichert.")