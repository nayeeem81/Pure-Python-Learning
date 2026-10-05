# app_window.py
import tkinter as tk
# Import our clean custom shape modules
from shapes import Rectangle, Circle 

class DynamicCanvasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modular Shape Canvas")
        self.root.geometry("800x600")
        
        self.canvas = tk.Canvas(self.root, bg="#fbfbfb", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.render_scene)
        
        # Instantiate your custom shape objects
        self.shapes = [
            Rectangle(w_pct=0.7, h_pct=0.7, color="#e3f2fd", outline="#2196f3"),
            Circle(h_offset=0, k_offset=0, r_pct=0.2, color="#ffe082", outline="#ffb300")
        ]
        
    def render_scene(self, event):
        self.canvas.delete("all")
        for shape in self.shapes:
            shape.draw(self.canvas, event.width, event.height)
