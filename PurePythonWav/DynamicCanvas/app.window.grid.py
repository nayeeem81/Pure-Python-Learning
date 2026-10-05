# app_window.py
import tkinter as tk
# If grid.py is inside a folder named "shapes"
from Shapes.grid import GraphGrid
from Shapes.primitives import MathCircle, MathParabola

class DynamicCanvasGridApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Equation Coordinate Plotter")
        self.root.geometry("800x600")
        
        self.canvas = tk.Canvas(self.root, bg="#ffffff", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.render_scene)
        
        # 1. Establish the graph grid viewport domain boundaries
        self.grid = GraphGrid(x_min=-10, x_max=10, y_min=-10, y_max=10)
        
        # 2. Add structural math entities directly using formulas
        self.shapes = [
            MathCircle(h=2, k=3, r=4, outline="blue", width=2),       # Center at (2,3), Radius 4
            MathParabola(a=0.5, h=0, k=-4, outline="red", width=2)    # y = 0.5(x-0)^2 - 4
        ]
        
    def render_scene(self, event):
        self.canvas.delete("all")
        w = event.width
        h = event.height
        
        # First draw the background grid axis markers
        self.grid.draw(self.canvas, w, h)
        
        # Pass the grid engine into each shape element to transform positions
        for shape in self.shapes:
            shape.draw(self.canvas, w, h, self.grid)
            
            # Print coordinate tracking validation directly to terminal console logs
            if isinstance(shape, MathCircle):
                print(f"Circle mathematical coordinates sample: {shape.get_coordinates()[0]}")
