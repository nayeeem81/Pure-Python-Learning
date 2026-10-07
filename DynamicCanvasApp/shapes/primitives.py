# shapes/primitives.py
import math
import tkinter as tk
from .base import Shape  
# Relative import from the same package
# MathCircle and MathParabola primitives
# shapes/primitives.py

class MathCircle(Shape):
    def __init__(self, mx, my, r, steps=100, **kwargs):
        super().__init__(**kwargs)
        self.mx = mx        # Math X-center
        self.my = my        # Math Y-center
        self.r = r          # Math radius
        self.steps = steps

    def contains_math_point_circle(self, mx, my, r, grid):
        """Returns True if a mathematical coordinate point falls inside the circle bounds."""
        self.r = r
        math_points = self.get_coordinates()
        pixel_points = []
        # Transform every explicit coordinate point into screen pixels
        for mx, my in math_points:
            px, py = grid.to_pixels(mx, my)
            if px == mx and py == my:
                return True
        return False

    def get_coordinates(self):
        """Returns a comprehensive list of all raw (x, y) math points."""
        coords = []
        for i in range(self.steps + 1):
            t = (2 * math.pi * i) / self.steps
            # Parametric Circle Equation: x = mx + r*cos(t), y = my + r*sin(t)
            mx = self.mx + self.r * math.cos(t)
            my = self.my + self.r * math.sin(t)
            coords.append((mx, my))
        self.mathcoordinates.append({"MathCircle": coords})
        return coords

    def draw(self, canvas, w, h, grid):
        math_points = self.get_coordinates()
        pixel_points = []
        # Transform every explicit coordinate point into screen pixels
        for mx, my in math_points:
            px, py = grid.to_pixels(mx, my)
            pixel_points.extend([px, py])
        self.pixelcoordinates.append({"MathCircle": pixel_points, "fill": "", "outline": self.outline, "width": self.width})
        # Draw the collection as a continuous line loop
        canvas.create_polygon(pixel_points, fill="", outline=self.outline, width=self.width)


class MathParabola(Shape):
    def __init__(self, start, end, curve, mx, my, **kwargs):
        super().__init__(**kwargs)
        self.curve = curve          # Vertical shift factor (for parabolas)
        self.mx = mx        # Vertex X coordinate
        self.my = my        # Vertex Y coordinate
        self.start = start  # Start X coordinate for drawing
        self.end = end      # End X coordinate for drawing

    def get_coordinates(self, start, end, steps=100):
        """Generates explicit mathematical coordinates along the parabola curve."""
        coords = []
        step_size = (end - start) / steps
        for i in range(steps + 1):
            mx = start + (i * step_size)
            # Standard Vertex Form Equation: y = a(x - h)^2 + k
            my = self.curve * ((mx - self.mx) ** 2) + self.my
            coords.append((mx, my))
        return coords

    def draw(self, canvas, w, h, grid):
        # Calculate points over the visible grid viewport range
        math_points = self.get_coordinates(self.start, self.end)
        self.mathcoordinates.append({"MathParabola": math_points})
        pixel_points = []
        for mx, my in math_points:
            px, py = grid.to_pixels(mx, my)
            pixel_points.extend([px, py])
        self.pixelcoordinates.append({"MathParabola": pixel_points, "fill": "", "outline": self.outline, "width": self.width})
        canvas.create_line(pixel_points, fill=self.outline, width=self.width)


class MathRectangle(Shape):
    def __init__(self, mx, my, width, height, default_color="#e3f2fd", collision_color="#ffcdd2", **kwargs):
        super().__init__(**kwargs)
        # FIXED: Removed the extra 4 spaces of indentation below
        self.mx = mx
        self.my = my
        self.width = width
        self.height = height
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
        half_w = self.width / 2
        half_h = self.height / 2  # FIXED typo: changed self.hight to self.height
        return self.mx - half_w, self.my + half_h, self.mx + half_w, self.my - half_h

    def check_collision_with_circle(self, circle):
        """Calculates mathematical bounding box overlaps against a target circle."""
        mx1, my1, mx2, my2 = self.get_corners()
        # Clamp the circle's center coordinates to the closest point inside the rectangle edges
        closest_x = max(mx1, min(circle.mx, mx2))
        closest_y = max(my2, min(circle.my, my1))
        # Calculate the Euclidean distance from the closest point to the circle center
        distance_x = circle.mx - closest_x
        distance_y = circle.my - closest_y
        distance = math.sqrt((distance_x ** 2) + (distance_y ** 2))
        return distance <= circle.r

    def draw(self, canvas, w, h, grid):
        mx1, my1, mx2, my2 = self.get_corners()
        self.mathcoordinates.append({"MathRectangle": (mx1, my1, mx2, my2), "fill": self.color, "outline": self.outline, "width": self.width})
        px1, py1 = grid.to_pixels(mx1, my1)
        px2, py2 = grid.to_pixels(mx2, my2)
        self.pixelcoordinates.append({"MathRectangle": (px1, py1, px2, py2), "fill": self.color, "outline": self.outline, "width": self.width})
        canvas.create_rectangle(
            px1, py1, px2, py2, 
            fill=self.color, 
            outline=self.outline, 
            width=self.width
        )


class MathEllipse(Shape):
    def __init__(self, mx, my, a_semi, b_semi, steps=100, **kwargs):
        """ Defines an Ellipse locked to Cartesian Math Space. """
        super().__init__(**kwargs)
        self.mx = mx
        self.my = my
        self.a_semi = a_semi
        self.b_semi = b_semi
        self.steps = steps

    def draw(self, canvas, w, h, grid):
        pixel_points = []
        for i in range(self.steps + 1):
            t = (2 * math.pi * i) / self.steps
            mx = self.mx + self.a_semi * math.cos(t)
            my = self.my + self.b_semi * math.sin(t)
            px, py = grid.to_pixels(mx, my)
            pixel_points.extend([px, py])
        self.mathcoordinates.append({"MathEllipse": (self.mx, self.my, self.a_semi, self.b_semi), "fill": self.color, "outline": self.outline, "width": self.width})
        self.pixelcoordinates.append({"MathEllipse": pixel_points, "fill": self.color, "outline": self.outline, "width": self.width})
        canvas.create_polygon(pixel_points, fill=self.color, outline=self.outline, width=self.width)
