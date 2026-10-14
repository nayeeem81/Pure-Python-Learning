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

# MathCircle and MathParabola primitives
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


class MathRectangle(Shape):
    def __init__(self, h, k, w_math, h_math, default_color="#e3f2fd", collision_color="#ffcdd2", **kwargs):
        """
        Defines a rectangle locked entirely to Cartesian Math Space with custom state behavior.
        (h, k)           = Math Center coordinates of the rectangle
        w_math, h_math   = Total width and height spans in math units
        """
        super().__init__(**kwargs)
        self.h = h
        self.k = k
        self.w_math = w_math
        self.h_math = h_math
        
        # Color state properties
        self.default_color = default_color
        self.collision_color = collision_color
        self.color = default_color

    def contains_math_point(self, mx, my):
        """Returns True if a mathematical coordinate point falls inside the rectangle bounds."""
        mx1, my1, mx2, my2 = self.get_corners()
        # mx1 is left, mx2 is right, my2 is bottom, my1 is top
        return (mx1 <= mx <= mx2) and (my2 <= my <= my1)

    def get_corners(self):
        half_w = self.w_math / 2
        half_h = self.h_math / 2
        return self.h - half_w, self.k + half_h, self.h + half_w, self.k - half_h

    def check_collision_with_circle(self, circle):
        """Calculates mathematical bounding box overlaps against a target circle."""
        mx1, my1, mx2, my2 = self.get_corners()
        
        # Clamp the circle's center coordinates to the closest point inside the rectangle edges
        # mx1 is left (min x), mx2 is right (max x)
        closest_x = max(mx1, min(circle.h, mx2))
        # my2 is bottom (min y), my1 is top (max y)
        closest_y = max(my2, min(circle.k, my1))
        
        # Calculate the Euclidean distance from the closest point to the circle center
        distance_x = circle.h - closest_x
        distance_y = circle.k - closest_y
        distance = math.sqrt((distance_x ** 2) + (distance_y ** 2))
        
        # Return True if the distance is smaller than the circle's radius
        return distance <= circle.r

    def draw(self, canvas, w, h, grid):
        mx1, my1, mx2, my2 = self.get_corners()
        px1, py1 = grid.to_pixels(mx1, my1, w, h)
        px2, py2 = grid.to_pixels(mx2, my2, w, h)
        
        canvas.create_rectangle(
            px1, py1, px2, py2, 
            fill=self.color, 
            outline=self.outline, 
            width=self.width
        )


class MathEllipse(Shape):
    def __init__(self, h, k, a_semi, b_semi, steps=100, **kwargs):
        """
        Defines an Ellipse locked to Cartesian Math Space.
        (h, k)  = Center point coordinates
        a_semi  = Horizontal semi-axis radius length
        b_semi  = Vertical semi-axis radius length
        """
        super().__init__(**kwargs)
        self.h = h
        self.k = k
        self.a_semi = a_semi
        self.b_semi = b_semi
        self.steps = steps

    def draw(self, canvas, w, h, grid):
        pixel_points = []
        for i in range(self.steps + 1):
            t = (2 * math.pi * i) / self.steps
            # Parametric Ellipse Equation: x = h + a*cos(t), y = k + b*sin(t)
            mx = self.h + self.a_semi * math.cos(t)
            my = self.k + self.b_semi * math.sin(t)
            px, py = grid.to_pixels(mx, my, w, h)
            pixel_points.extend([px, py])
        canvas.create_polygon(pixel_points, fill=self.color, outline=self.outline, width=self.width)
