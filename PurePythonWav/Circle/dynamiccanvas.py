import tkinter as tk
class DynamicCanvasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Best Practices Canvas")
        
        # Start window configuration at a flexible ratio
        # Correctly placed and indented inside the __init__ constructor block
        self.root.geometry("800x600")
      
        # Create canvas widget with custom focus borders
        self.canvas = tk.Canvas(
            self.root, 
            bg="white", 
            highlightthickness=0  # Eliminates uneven outer gray frames
        )
    
        # Fill the window frame natively and scale gracefully
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind the window resize trigger
        self.canvas.bind("<Configure>", self.draw_graphics)
    
    def draw_graphics(self, event):
        """Redraws canvas items relative to live window dimensions."""
        # Clean the previous frame to avoid stacking old graphics in memory
        self.canvas.delete("all")
        w = event.width
        h = event.height
    
        # 1. Best Practice: Draw a dynamic centered background rectangle
        # Coords system layout: (x1, y1, x2, y2) -> Top-Left to Bottom-Right
        self.canvas.create_rectangle(
            w * 0.1, h * 0.1,  # 10% margin padding
            w * 0.9, h * 0.9, 
            fill="#f0f0f0", 
            outline="blue", 
            width=2
        )
    
        # 2. Best Practice: Add dynamic responsive vector typography
        self.canvas.create_text(
            w / 2, h / 2, 
            text=f"Resizing Canvas: {w}x{h}", 
            fill="black", 
            font=("Helvetica", 16, "bold"),
            anchor=tk.CENTER
        )


# This block ONLY runs if you run dynamic_canvas.py directly.
# It will be ignored entirely when you import it into main.py.
if __name__ == "__main__":
	# Fix High-DPI text scaling blur strictly on Windows devices
	try:
		import ctypes
		ctypes.windll.shcore.SetProcessDpiAwareness(2)
	except Exception:
		pass  # Standard fallback safe execution for macOS / Linux environments


root = tk.Tk()
app = DynamicCanvasApp(root)
root.mainloop()

