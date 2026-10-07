# shapes/primitives.py

import math
import tkinter as tk
from .base import Shape  
# Relative import from the same package

class Rectangle(Shape):
    def __init__(self, w_pct, h_pct, **kwargs):
        super().__init__(**kwargs)
        self.w_pct = w_pct
        self.h_pct = h_pct

    def draw(self, canvas, w, h):
        x1 = (w - (w * self.w_pct)) / 2
        y1 = (h - (h * self.h_pct)) / 2
        x2 = x1 + (w * self.w_pct)
        y2 = y1 + (h * self.h_pct)
        canvas.create_rectangle(x1, y1, x2, y2, fill=self.color, outline=self.outline, width=self.width)

class Circle(Shape):
    def __init__(self, h_offset, k_offset, r_pct, **kwargs):
        super().__init__(**kwargs)
        self.h_offset = h_offset
        self.k_offset = k_offset
        self.r_pct = r_pct

    def contains_math_point(self, mx, my):
        """Returns True if a mathematical coordinate point falls inside the circle."""
        import math
        distance = math.sqrt((mx - self.h_offset)**2 + (my - self.k_offset)**2)
        return distance <= self.r_pct * min(w, h)

    def draw(self, canvas, w, h):
        center_x = (w / 2) + self.h_offset
        center_y = (h / 2) + self.k_offset
        radius = min(w, h) * self.r_pct
        canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            fill=self.color, outline=self.outline, width=self.width
        )
