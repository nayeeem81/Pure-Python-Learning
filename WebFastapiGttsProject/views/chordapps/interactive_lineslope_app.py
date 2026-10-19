import tkinter as tk
from tkinter import ttk

class SlopeInterceptApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Graph: y = mx + b")
        self.root.geometry("640x480")
        self.root.configure(bg="#121214")

        # 1. Initialize variables for both Slope (m) and Y-intercept (b)
        self.m_value = tk.DoubleVar(value=2.0)  # Default slope of 2
        self.b_value = tk.DoubleVar(value=0.0)  # Default intercept at origin

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

        # Setup the UI controls frame
        self.setup_controls()
        
        # Initial draw execution
        self.update_graph()

    def setup_controls(self):
        # A container box for both sliders
        controls_frame = tk.Frame(self.root, bg="#1e1e24", bd=10)
        controls_frame.pack(fill="x", padx=20, pady=5)
        
        # --- SLIDER 1: SLOPE (m) ---
        m_row = tk.Frame(controls_frame, bg="#1e1e24")
        m_row.pack(fill="x", pady=5)
        
        m_lbl = tk.Label(m_row, text="Slope (m):", fg="#e1e1e6", bg="#1e1e24", font=("Arial", 10, "bold"), width=15, anchor="w")
        m_lbl.pack(side="left", padx=5)
        
        m_slider = tk.Scale(
            m_row, from_=-4.0, to=4.0, resolution=0.1, orient="horizontal", 
            variable=self.m_value, command=lambda e: self.update_graph(), 
            showvalue=False, bg="#1e1e24", fg="#ff79c6", highlightthickness=0, 
            troughcolor="#444", activebackground="#ff79c6"
        )
        m_slider.pack(side="left", fill="x", expand=True, padx=10)
        
        self.m_val_lbl = tk.Label(m_row, text="2.0", width=6, fg="#ff79c6", bg="#1e1e24", font=("Courier", 12, "bold"))
        self.m_val_lbl.pack(side="right", padx=5)

        # --- SLIDER 2: Y-INTERCEPT (b) ---
        b_row = tk.Frame(controls_frame, bg="#1e1e24")
        b_row.pack(fill="x", pady=5)
        
        b_lbl = tk.Label(b_row, text="Y-Intercept (b):", fg="#e1e1e6", bg="#1e1e24", font=("Arial", 10, "bold"), width=15, anchor="w")
        b_lbl.pack(side="left", padx=5)
        
        b_slider = tk.Scale(
            b_row, from_=-3.0, to=3.0, resolution=0.1, orient="horizontal", 
            variable=self.b_value, command=lambda e: self.update_graph(), 
            showvalue=False, bg="#1e1e24", fg="#00adb5", highlightthickness=0, 
            troughcolor="#444", activebackground="#00adb5"
        )
        b_slider.pack(side="left", fill="x", expand=True, padx=10)
        
        self.b_val_lbl = tk.Label(b_row, text="0.0", width=6, fg="#00adb5", bg="#1e1e24", font=("Courier", 12, "bold"))
        self.b_val_lbl.pack(side="right", padx=5)

    def update_graph(self):
        # Clean canvas before redrawing
        self.canvas.delete("all")
        
        w, h = 600, 250
        center_y = h / 2
        center_x = w / 2

        # Redraw Background Grid Lines
        for x in range(0, w, 40):
            self.canvas.create_line(x, 0, x, h, fill="#252529", width=1)
        for y in range(0, h, 40):
            self.canvas.create_line(0, y, w, y, fill="#252529", width=1)

        # Redraw Main Axes
        self.canvas.create_line(0, center_y, w, center_y, fill="#888", width=2) # X Axis
        self.canvas.create_line(center_x, 0, center_x, h, fill="#888", width=2) # Y Axis

        # Grab current variable inputs
        current_m = self.m_value.get()
        current_b = self.b_value.get()
        
        # Update text metrics on labels
        self.m_val_lbl.config(text=f"{current_m:.1f}")
        self.b_val_lbl.config(text=f"{current_b:.1f}")

        # Compute line using y = mx + b
        points = []
        for pixel_x in range(w):
            x = (pixel_x - center_x) / 40.0
            
            # Apply both variables directly into the linear function math rule
            y = (current_m * x) + current_b
            
            pixel_y = center_y - (y * 40.0)
            points.append((pixel_x, pixel_y))

        flat_points = [coord for pt in points for coord in pt]
        self.canvas.create_line(flat_points, fill="#00adb5", width=3)

if __name__ == "__main__":
    root = tk.Tk()
    app = SlopeInterceptApp(root)
    root.mainloop()
