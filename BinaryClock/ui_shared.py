import tkinter as tk

# --- GLOBALE UI KONSTANTEN ---
BG_COLOR = "#202020"
TEXT_COLOR = "#FFFFFF"
UI_FONT = ("Futura", 10, "bold")
UI_FONT_SMALL = ("Futura", 9)

GROUP_COLORS = {
    0: "#FF5733",  # Rot
    1: "#33FF57",  # Grün
    2: "#3357FF",  # Blau
    3: "#F333FF"  # Magenta
}

class FlatButton(tk.Label):
    """
    Ein Button ohne Betriebssystem-Style.
    Kann überall wiederverwendet werden.
    """

    def __init__(self, parent, text, command, bg="#444444", fg="white", width=10, font=None):
        # Falls kein Font übergeben wird, Standard nutzen
        use_font = font if font else UI_FONT

        super().__init__(parent, text=text, bg=bg, fg=fg, font=use_font,
                         width=width, cursor="hand2", bd=2, relief="flat")
        self.command = command
        self.default_bg = bg
        self.hover_bg = self.adjust_color_lightness(bg, 1.2)

        self.config(pady=4)  # Standard Padding

        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_click(self, event):
        if self.command:
            self.command()

    def on_enter(self, event):
        self.config(bg=self.hover_bg)

    def on_leave(self, event):
        self.config(bg=self.default_bg)

    def set_active(self, active):
        if active:
            self.config(relief="solid")
        else:
            self.config(relief="flat")

    def adjust_color_lightness(self, color_hex, factor):
        try:
            color_hex = color_hex.lstrip('#')
            r, g, b = tuple(int(color_hex[i:i + 2], 16) for i in (0, 2, 4))
            r = min(255, int(r * factor))
            g = min(255, int(g * factor))
            b = min(255, int(b * factor))
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color_hex