
import tkinter as tk
from tkinter import ttk

class InteractiveLineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Linear Graph: y = 2x + b")
        self.root.geometry("640x420")
        self.root.configure(bg="#121214")

        # Create a variable to hold our changing Y-intercept value (b)
        self.b_value = tk.DoubleVar(value=1.0)

        # Create drawing canvas
        self.canvas = tk.Canvas(
            self.root, 
            width=600, 
            height=250, 
            bg="#141416", 
            highlightthickness=1, 
            highlightbackground="#333"
        )
        self.canvas.pack(pady=20)

        # Setup the UI control layout frame at the bottom
        self.setup_controls()
        
        # Initial render of the grid and the line
        self.update_graph()

    def setup_controls(self):
        # A container box for the slider elements
        controls_frame = tk.Frame(self.root, bg="#1e1e24", bd=10)
        controls_frame.pack(fill="x", padx=20, pady=5)
        
        # Label to show what the slider does
        lbl = tk.Label(controls_frame, text="Y-Intercept (b):", fg="#e1e1e6", bg="#1e1e24", font=("Arial", 10, "bold"))
        lbl.pack(side="left", padx=5)
        
        # The interactive slider tool
        # Every time it moves, it triggers 'self.update_graph()' automatically
        slider = tk.Scale(
            controls_frame, 
            from_=-3.0, 
            to=3.0, 
            resolution=0.1,
            orient="horizontal", 
            variable=self.b_value, 
            command=lambda e: self.update_graph(), 
            showvalue=False, 
            bg="#1e1e24", 
            fg="#00adb5", 
            highlightthickness=0, 
            troughcolor="#444", 
            activebackground="#00adb5"
        )
        slider.pack(side="left", fill="x", expand=True, padx=10)
        
        # Dynamic label to output the exact numeric value on screen
        self.val_lbl = tk.Label(controls_frame, text="1.0", width=6, fg="#00adb5", bg="#1e1e24", font=("Courier", 12, "bold"))
        self.val_lbl.pack(side="right", padx=5)

    def update_graph(self):
        # 1. Wipe the canvas completely clean so we don't draw lines on top of old lines
        self.canvas.delete("all")
        
        w, h = 600, 250
        center_y = h / 2
        center_x = w / 2

        # 2. Redraw Background Grid Lines
        for x in range(0, w, 40):
            self.canvas.create_line(x, 0, x, h, fill="#252529", width=1)
        for y in range(0, h, 40):
            self.canvas.create_line(0, y, w, y, fill="#252529", width=1)

        # 3. Redraw Main Axes
        self.canvas.create_line(0, center_y, w, center_y, fill="#888", width=2) # X Axis
        self.canvas.create_line(center_x, 0, center_x, h, fill="#888", width=2) # Y Axis

        # Update the live value label text on screen
        current_b = self.b_value.get()
        self.val_lbl.config(text=f"{current_b:.1f}")

        # 4. Calculate and Plot the new Line Position
        points = []
        for pixel_x in range(w):
            x = (pixel_x - center_x) / 40.0
            
            # Use our dynamic variable 'current_b' inside our math equation!
            y = 2 * x + current_b
            
            pixel_y = center_y - (y * 40.0)
            points.append((pixel_x, pixel_y))

        flat_points = [coord for pt in points for coord in pt]
        self.canvas.create_line(flat_points, fill="#00adb5", width=3)

if __name__ == "__main__":
    root = tk.Tk()
    app = InteractiveLineApp(root)
    root.mainloop()
