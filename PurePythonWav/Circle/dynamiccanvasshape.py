import tkinter as tk
import math

# ==========================================
# 1. THE BASE SHAPE CLASS & SUBCLASSES
# ==========================================

class Shape:
    """Abstract base class that all canvas shapes will inherit from."""
    def __init__(self, color="blue", outline="black", width=2):
        self.color = color
        self.outline = outline
        self.width = width

    def draw(self, canvas, window_width, window_height):
        """Must be implemented by subclasses to handle responsive rendering."""
        raise NotImplementedError("Subclasses must implement the draw method")


class Rectangle(Shape):
    def __init__(self, w_pct, h_pct, **kwargs):
        super().__init__(**kwargs)
        self.w_pct = w_pct  # Width as a fraction of the screen (0.0 to 1.0)
        self.h_pct = h_pct  # Height as a fraction of the screen (0.0 to 1.0)

    def draw(self, canvas, w, h):
        # Center the rectangle in the window dynamically
        x1 = (w - (w * self.w_pct)) / 2
        y1 = (h - (h * self.h_pct)) / 2
        x2 = x1 + (w * self.w_pct)
        y2 = y1 + (h * self.h_pct)
        
        canvas.create_rectangle(x1, y1, x2, y2, fill=self.color, outline=self.outline, width=self.width)


class Circle(Shape):
    def __init__(self, h_offset, k_offset, r_pct, **kwargs):
        super().__init__(**kwargs)
        self.h_offset = h_offset  # Horizontal offset from window center
        self.k_offset = k_offset  # Vertical offset from window center
        self.r_pct = r_pct        # Radius as a fraction of smaller window dimension

    def draw(self, canvas, w, h):
        # Calculate dynamic center (h, k)
        center_x = (w / 2) + self.h_offset
        center_y = (h / 2) + self.k_offset
        radius = min(w, h) * self.r_pct
        
        # Tkinter requires top-left and bottom-right bounding box coordinates
        canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            fill=self.color, outline=self.outline, width=self.width
        )


class RegularPolygon(Shape):
    def __init__(self, n, r_pct, rotation_deg=0, **kwargs):
        super().__init__(**kwargs)
        self.n = max(3, n)        # Number of sides (minimum 3)
        self.r_pct = r_pct        # Radius of bounding circle as window fraction
        self.rotation = math.radians(rotation_deg)

    def draw(self, canvas, w, h):
        center_x = w / 2
        center_y = h / 2
        radius = min(w, h) * self.r_pct
        points = []

        # Generate math coordinates using parametric step loops
        for i in range(self.n):
            angle = (2 * math.pi * i / self.n) + self.rotation
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.extend([x, y])

        canvas.create_polygon(points, fill=self.color, outline=self.outline, width=self.width)


# ==========================================
# 2. THE APP WINDOW CLASS (MANAGEMENT)
# ==========================================

class DynamicCanvasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Polymorphic Shape Canvas")
        self.root.geometry("800x600")
        
        self.canvas = tk.Canvas(self.root, bg="#fbfbfb", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.render_scene)
        
        # Store shape instances polymorphically in a standard list container
        self.shapes = [
            Rectangle(w_pct=0.7, h_pct=0.7, color="#e3f2fd", outline="#2196f3"),
            Circle(h_offset=-100, k_offset=0, r_pct=0.15, color="#ffe082", outline="#ffb300"),
            RegularPolygon(n=6, r_pct=0.12, rotation_deg=15, color="#c8e6c9", outline="#4caf50")
        ]
        
    def render_scene(self, event):
        """Fires systematically whenever the canvas resizes."""
        self.canvas.delete("all")
        w = event.width
        h = event.height
        
        # Clean execution flow: loop over elements and let them manage their layout
        for shape in self.shapes:
            shape.draw(self.canvas, w, h)


if __name__ == "__main__":
    # Handle OS-level window crispness natively
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

    root = tk.Tk()
    app = DynamicCanvasApp(root)
    root.mainloop()
