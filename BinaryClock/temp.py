import json
import os
import sys


class SettingsManager:
    def __init__(self, filename="binClockSettings.json"):
        # --- PFAD LOGIK FÜR FREEZE / STANDALONE ---
        if getattr(sys, 'frozen', False):
            # Fall A: Das Programm läuft als compilierte Datei (PyInstaller/Py2App)
            # Wir nehmen den Ordner, in dem die executable liegt
            application_path = os.path.dirname(sys.executable)
        else:
            # Fall B: Das Programm läuft normal als Skript
            # Wir nehmen den Ordner, in dem dieses Script liegt
            application_path = os.path.dirname(os.path.abspath(__file__))

        # Wir bauen den absoluten Pfad zusammen:
        self.filename = os.path.join(application_path, filename)

        # Einstellungen laden
        self.data = self.load_settings()

    def create_default_nibble(self, index):
        # --- CUSTOM DEFAULT FÜR SLOT 0 ---
        if index == 0:
            return {
                "id": 0,
                "name": "Nibble 0",
                "cells": [
                    3, 3, 3, 3,
                    3, 2, 2, 3,
                    3, 2, 1, -1,
                    3, 2, 1, 0
                ],
                "gap": {"x": 2, "y": 2},
                "bridgeGaps": True,
                "fillCorners": True
            }

        # --- STANDARD FÜR REST ---
        return {
            "id": index,
            "name": f"Nibble {index}",
            "cells": [-1] * 16,
            "gap": {"x": 2, "y": 2},
            "bridgeGaps": True,
            "fillCorners": True
        }

    def create_default_layout(self, index):
        # --- CUSTOM DEFAULT FÜR SLOT 0 ---
        if index == 0:
            return {
                "id": 0,
                "name": "Layout 0",
                "margin": {"top": 10, "right": 10, "bottom": 10, "left": 10},
                "gap": {"x": 20, "y": 20},
                "placements": [
                    {
                        "nibbleId": 3,
                        "position": {"x": 1, "y": 1},
                        "mirror": {"x": False, "y": False}
                    },
                    {
                        "nibbleId": 2,
                        "position": {"x": 2, "y": 1},
                        "mirror": {"x": True, "y": False}
                    },
                    {
                        "nibbleId": 1,
                        "position": {"x": 1, "y": 2},
                        "mirror": {"x": False, "y": True}
                    },
                    {
                        "nibbleId": 0,
                        "position": {"x": 2, "y": 2},
                        "mirror": {"x": True, "y": True}
                    }
                ]
            }

        # --- STANDARD FÜR REST ---
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
        # --- CUSTOM DEFAULT FÜR SLOT 0 ---
        if index == 0:
            return {
                "id": 0,
                "name": "Palette 0",
                "colors": [
                    "#007E7F", "#007E7F", "#007E7F", "#007E7F",
                    "#7F6300", "#7F6300", "#7F6300", "#7F6300",
                    "#00FCFF", "#00FCFF", "#00FCFF", "#00FCFF",
                    "#FFC700", "#FFC700", "#FFC700", "#FFC700"
                ]
            }

        # --- STANDARD FÜR REST ---
        default_colors = ["#333333"] * 16
        default_colors[0] = "#FFC800"  # Active Color (Gold)
        default_colors[1] = "#2A2A2A"  # Inactive Color (Dunkelgrau)
        return {
            "id": index,
            "name": f"Palette {index}",
            "colors": default_colors
        }

    def create_default_profile(self, index):
        # --- CUSTOM DEFAULT FÜR SLOT 0 ---
        if index == 0:
            return {
                "id": 0,
                "name": "Profile 0",
                "layoutId": 0,
                "paletteId": 0,
                "nibbleGridId": 0
            }

        # --- STANDARD FÜR REST ---
        return {
            "id": index,
            "name": f"Profile {index}",
            "layoutId": 0,
            "paletteId": 0,
            "nibbleGridId": 0
        }

    def get_defaults(self):
        return {
            "version": "0.1",
            "active_profileId": 0,
            "library": {
                "nibbleGrids": [self.create_default_nibble(i) for i in range(16)],
                "layoutGrids": [self.create_default_layout(i) for i in range(16)],
                "palettes": [self.create_default_palette(i) for i in range(16)]
            },
            "profiles": [self.create_default_profile(i) for i in range(16)]
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
        self.save_settings(defaults)
        return defaults

    def save_settings(self, data=None):
        if data:
            self.data = data
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)
        print("Gespeichert.")