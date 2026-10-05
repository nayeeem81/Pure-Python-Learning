# shapes/primitives.py
import math
import tkinter as tk
from .base import Shape  # Relative import from the same package

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

    def draw(self, canvas, w, h):
        center_x = (w / 2) + self.h_offset
        center_y = (h / 2) + self.k_offset
        radius = min(w, h) * self.r_pct
        canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            fill=self.color, outline=self.outline, width=self.width
        )

# (You can bundle Ellipse and RegularPolygon right below in this file)

# shapes/primitives.py

class MathCircle(Shape):
    def __init__(self, h, k, r, steps=100, **kwargs):
        super().__init__(**kwargs)
        self.h = h        # Math X-center
        self.k = k        # Math Y-center
        self.r = r        # Math radius
        self.steps = steps

    def get_coordinates(self):
        """Returns a comprehensive list of all raw (x, y) math points."""
        coords = []
        for i in range(self.steps + 1):
            t = (2 * math.pi * i) / self.steps
            # Parametric Circle Equation: x = h + r*cos(t), y = k + r*sin(t)
            x = self.h + self.r * math.cos(t)
            y = self.k + self.r * math.sin(t)
            coords.append((x, y))
        return coords

    def draw(self, canvas, w, h, grid):
        math_points = self.get_coordinates()
        pixel_points = []
        
        # Transform every explicit coordinate point into screen pixels
        for mx, my in math_points:
            px, py = grid.to_pixels(mx, my, w, h)
            pixel_points.extend([px, py])
            
        # Draw the collection as a continuous line loop
        canvas.create_polygon(pixel_points, fill="", outline=self.outline, width=self.width)


class MathParabola(Shape):
    def __init__(self, a, h, k, **kwargs):
        super().__init__(**kwargs)
        self.a = a        # Vertical stretch / direction factor
        self.h = h        # Vertex X coordinate
        self.k = k        # Vertex Y coordinate

    def get_coordinates(self, x_start, x_end, steps=100):
        """Generates explicit mathematical coordinates along the parabola curve."""
        coords = []
        step_size = (x_end - x_start) / steps
        for i in range(steps + 1):
            x = x_start + (i * step_size)
            # Standard Vertex Form Equation: y = a(x - h)^2 + k
            y = self.a * ((x - self.h) ** 2) + self.k
            coords.append((x, y))
        return coords

    def draw(self, canvas, w, h, grid):
        # Calculate points over the visible grid viewport range
        math_points = self.get_coordinates(grid.x_min, grid.x_max)
        pixel_points = []
        
        for mx, my in math_points:
            px, py = grid.to_pixels(mx, my, w, h)
            pixel_points.extend([px, py])
            
        canvas.create_line(pixel_points, fill=self.outline, width=self.width)
