Let’s shift from straight algebra to trigonometry and sound waves!
We are going to transition the line into a sine wave function: $y = A \cdot \sin(B \cdot x)$.
To give you complete visual control over this new wave shape, our two sliders will now control:

* Amplitude (A): The height of the wave. Dragging this makes the peaks taller and the valleys deeper.
* Frequency (B): How tightly packed the wave cycles are. Dragging this squishes the wave horizontally or stretches it out wide.

Here is the updated Python code to run your new interactive wave grid:

import mathimport tkinter as tkfrom tkinter import ttk
class InteractiveSineWaveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Sine Wave: y = A * sin(B * x)")
        self.root.geometry("640x480")
        self.root.configure(bg="#121214")

        # 1. Initialize variables for Amplitude (height) and Frequency (horizontal compression)
        self.amplitude = tk.DoubleVar(value=1.5)  # Default wave height
        self.frequency = tk.DoubleVar(value=2.0)  # Default wave cycles

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
        controls_frame = tk.Frame(self.root, bg="#1e1e24", bd=10)
        controls_frame.pack(fill="x", padx=20, pady=5)
        
        # --- SLIDER 1: AMPLITUDE (Wave Height) ---
        amp_row = tk.Frame(controls_frame, bg="#1e1e24")
        amp_row.pack(fill="x", pady=5)
        
        amp_lbl = tk.Label(amp_row, text="Amplitude (Height):", fg="#e1e1e6", bg="#1e1e24", font=("Arial", 10, "bold"), width=18, anchor="w")
        amp_lbl.pack(side="left", padx=5)
        
        amp_slider = tk.Scale(
            amp_row, from_=0.0, to=3.0, resolution=0.1, orient="horizontal", 
            variable=self.amplitude, command=lambda e: self.update_graph(), 
            showvalue=False, bg="#1e1e24", fg="#ff79c6", highlightthickness=0, 
            troughcolor="#444", activebackground="#ff79c6"
        )
        amp_slider.pack(side="left", fill="x", expand=True, padx=10)
        
        self.amp_val_lbl = tk.Label(amp_row, text="1.5", width=6, fg="#ff79c6", bg="#1e1e24", font=("Courier", 12, "bold"))
        self.val_lbl_1 = self.amp_val_lbl  # Reference tracker
        self.amp_val_lbl.pack(side="right", padx=5)

        # --- SLIDER 2: FREQUENCY (Wave Tightness) ---
        freq_row = tk.Frame(controls_frame, bg="#1e1e24")
        freq_row.pack(fill="x", pady=5)
        
        freq_lbl = tk.Label(freq_row, text="Frequency (Cycles):", fg="#e1e1e6", bg="#1e1e24", font=("Arial", 10, "bold"), width=18, anchor="w")
        freq_lbl.pack(side="left", padx=5)
        
        freq_slider = tk.Scale(
            freq_row, from_=0.5, to=8.0, resolution=0.1, orient="horizontal", 
            variable=self.frequency, command=lambda e: self.update_graph(), 
            showvalue=False, bg="#1e1e24", fg="#00adb5", highlightthickness=0, 
            troughcolor="#444", activebackground="#00adb5"
        )
        freq_slider.pack(side="left", fill="x", expand=True, padx=10)
        
        self.freq_val_lbl = tk.Label(freq_row, text="2.0", width=6, fg="#00adb5", bg="#1e1e24", font=("Courier", 12, "bold"))
        self.freq_val_lbl.pack(side="right", padx=5)

    def update_graph(self):
        # Clean canvas before redrawing a new line variation frame
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

        # Fetch active variable state values
        current_amp = self.amplitude.get()
        current_freq = self.frequency.get()
        
        # Display current values on text labels
        self.amp_val_lbl.config(text=f"{current_amp:.1f}")
        self.freq_val_lbl.config(text=f"{current_freq:.1f}")

        # Compute wave shape values using trigonometry: y = A * sin(B * x)
        points = []
        for pixel_x in range(w):
            # Scale factor: 40 pixels = 1 math grid unit distance
            x = (pixel_x - center_x) / 40.0
            
            # Apply our interactive wave formula
            y = current_amp * math.sin(current_freq * x)
            
            # Invert coordinates to map cleanly back onto screen Y-pixels
            pixel_y = center_y - (y * 40.0)
            points.append((pixel_x, pixel_y))

        # Flatten list configurations out for standard Tkinter lines processing blocks
        flat_points = [coord for pt in points for coord in pt]
        self.canvas.create_line(flat_points, fill="#00adb5", width=3, smooth=True)
if __name__ == "__main__":
    root = tk.Tk()
    app = InteractiveSineWaveApp(root)
    root.mainloop()

## Try Testing These Variations:

* Drop Amplitude to 0.0: The wave flattens instantly into a dead straight horizontal line.
* Crank Frequency up to 8.0: The wave compresses tightly together, displaying a rapid, high-frequency oscillation across the screen.

Now that we have successfully transitioned the line into an interactive wave, what would you like to build next?
Would you like to:

* Add a second wave line to the canvas grid to see how they cross paths?
* Connect a Play button that converts this exact wave shape into a playable WAV sound byte array?
* Introduce a circle shape onto this same grid?


