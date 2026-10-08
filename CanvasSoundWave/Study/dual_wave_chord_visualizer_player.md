Here is the updated Python code that adds a "Play Chord" button below the wave controls!
When you click the button, Python takes the mathematical values of both waves from your sliders, blends them together to create a 2-note chord, converts the resulting wave shapes into a raw WAV byte array, and streams it directly to your speakers using Windows' built-in audio system.

import mathimport waveimport structimport tkinter as tkfrom tkinter import ttkimport winsound  # Built-in sound engine for Windows
class DualWaveChordApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dual Wave Chord Visualizer & Player")
        self.root.geometry("640x630")
        self.root.configure(bg="#121214")

        # Initialize variables for Wave 1 (Teal)
        self.amp1 = tk.DoubleVar(value=1.5)
        self.freq1 = tk.DoubleVar(value=2.0)

        # Initialize variables for Wave 2 (Pink)
        self.amp2 = tk.DoubleVar(value=1.0)
        self.freq2 = tk.DoubleVar(value=4.0)

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

        # Setup UI controls and layout
        self.setup_controls()
        
        # Initial draw execution
        self.update_graph()

    def setup_controls(self):
        # Slider Container Panel
        controls_frame = tk.Frame(self.root, bg="#1e1e24", bd=10)
        controls_frame.pack(fill="x", padx=20, pady=5)
        
        # ------------------ WAVE 1 CONTROLS (TEAL) ------------------
        tk.Label(controls_frame, text="WAVE 1 (TEAL)", fg="#00adb5", bg="#1e1e24", font=("Arial", 9, "bold")).pack(anchor="w", pady=(0, 5))
        
        amp1_row = tk.Frame(controls_frame, bg="#1e1e24")
        amp1_row.pack(fill="x", pady=2)
        tk.Label(amp1_row, text="Amplitude 1:", fg="#e1e1e6", bg="#1e1e24", font=("Arial", 10), width=15, anchor="w").pack(side="left")
        amp1_slider = tk.Scale(amp1_row, from_=0.0, to=3.0, resolution=0.1, orient="horizontal", variable=self.amp1, command=lambda e: self.update_graph(), showvalue=False, bg="#1e1e24", fg="#00adb5", highlightthickness=0, troughcolor="#444", activebackground="#00adb5")
        amp1_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.amp1_val = tk.Label(amp1_row, text="1.5", width=6, fg="#00adb5", bg="#1e1e24", font=("Courier", 12, "bold"))
        self.amp1_val.pack(side="right")

        freq1_row = tk.Frame(controls_frame, bg="#1e1e24")
        freq1_row.pack(fill="x", pady=2)
        tk.Label(freq1_row, text="Frequency 1:", fg="#e1e1e6", bg="#1e1e24", font=("Arial", 10), width=15, anchor="w").pack(side="left")
        freq1_slider = tk.Scale(freq1_row, from_=0.5, to=8.0, resolution=0.1, orient="horizontal", variable=self.freq1, command=lambda e: self.update_graph(), showvalue=False, bg="#1e1e24", fg="#00adb5", highlightthickness=0, troughcolor="#444", activebackground="#00adb5")
        freq1_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.freq1_val = tk.Label(freq1_row, text="2.0", width=6, fg="#00adb5", bg="#1e1e24", font=("Courier", 12, "bold"))
        self.freq1_val.pack(side="right")

        # Separator Line
        ttk.Separator(controls_frame, orient='horizontal').pack(fill='x', pady=10)

        # ------------------ WAVE 2 CONTROLS (PINK) ------------------
        tk.Label(controls_frame, text="WAVE 2 (PINK)", fg="#ff79c6", bg="#1e1e24", font=("Arial", 9, "bold")).pack(anchor="w", pady=(0, 5))

        amp2_row = tk.Frame(controls_frame, bg="#1e1e24")
        amp2_row.pack(fill="x", pady=2)
        tk.Label(amp2_row, text="Amplitude 2:", fg="#e1e1e6", bg="#1e1e24", font=("Arial", 10), width=15, anchor="w").pack(side="left")
        amp2_slider = tk.Scale(amp2_row, from_=0.0, to=3.0, resolution=0.1, orient="horizontal", variable=self.amp2, command=lambda e: self.update_graph(), showvalue=False, bg="#1e1e24", fg="#ff79c6", highlightthickness=0, troughcolor="#444", activebackground="#ff79c6")
        amp2_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.amp2_val = tk.Label(amp2_row, text="1.0", width=6, fg="#ff79c6", bg="#1e1e24", font=("Courier", 12, "bold"))
        self.amp2_val.pack(side="right")

        freq2_row = tk.Frame(controls_frame, bg="#1e1e24")
        freq2_row.pack(fill="x", pady=2)
        tk.Label(freq2_row, text="Frequency 2:", fg="#e1e1e6", bg="#1e1e24", font=("Arial", 10), width=15, anchor="w").pack(side="left")
        freq2_slider = tk.Scale(freq2_row, from_=0.5, to=8.0, resolution=0.1, orient="horizontal", variable=self.freq2, command=lambda e: self.update_graph(), showvalue=False, bg="#1e1e24", fg="#ff79c6", highlightthickness=0, troughcolor="#444", activebackground="#ff79c6")
        freq2_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.freq2_val = tk.Label(freq2_row, text="4.0", width=6, fg="#ff79c6", bg="#1e1e24", font=("Courier", 12, "bold"))
        self.freq2_val.pack(side="right")

        # ------------------ PLAY BUTTON INTERFACE ------------------
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 11, "bold"), padding=8)
        
        play_btn = ttk.Button(self.root, text="Play Combined Chord", command=self.generate_and_play_wav)
        play_btn.pack(pady=15, fill="x", padx=20)

    def update_graph(self):
        self.canvas.delete("all")
        w, h = 600, 250
        center_y = h / 2
        center_x = w / 2

        # Redraw Background Mesh Grid
        for x in range(0, w, 40):
            self.canvas.create_line(x, 0, x, h, fill="#252529", width=1)
        for y in range(0, h, 40):
            self.canvas.create_line(0, y, w, y, fill="#252529", width=1)

        # Redraw Main X and Y Axes
        self.canvas.create_line(0, center_y, w, center_y, fill="#888", width=2)
        self.canvas.create_line(center_x, 0, center_x, h, fill="#888", width=2)

        # Update text strings on status boxes
        self.amp1_val.config(text=f"{self.amp1.get():.1f}")
        self.freq1_val.config(text=f"{self.freq1.get():.1f}")
        self.amp2_val.config(text=f"{self.amp2.get():.1f}")
        self.freq2_val.config(text=f"{self.freq2.get():.1f}")

        points_wave1 = []
        points_wave2 = []

        for pixel_x in range(w):
            x = (pixel_x - center_x) / 40.0
            
            # Draw Wave 1
            y1 = self.amp1.get() * math.sin(self.freq1.get() * x)
            pixel_y1 = center_y - (y1 * 40.0)
            points_wave1.append((pixel_x, pixel_y1))

            # Draw Wave 2
            y2 = self.amp2.get() * math.sin(self.freq2.get() * x)
            pixel_y2 = center_y - (y2 * 40.0)
            points_wave2.append((pixel_x, pixel_y2))

        flat_w1 = [coord for pt in points_wave1 for coord in pt]
        flat_w2 = [coord for pt in points_wave2 for coord in pt]

        self.canvas.create_line(flat_w1, fill="#00adb5", width=3, smooth=True)
        self.canvas.create_line(flat_w2, fill="#ff79c6", width=3, smooth=True)

    def generate_and_play_wav(self):
        SAMPLE_RATE = 44100
        DURATION = 1.5  # Play length in seconds
        filename = "dual_wave_chord.wav"
        
        # Audio needs higher audible numbers than the visual grid space (e.g. 200 Hz to 600 Hz tones)
        # We multiply our small visual slider scale by 100 to map it cleanly to audible frequencies
        hz1 = self.freq1.get() * 100.0
        hz2 = self.freq2.get() * 100.0
        
        # Get relative volume levels from the amplitudes
        vol1 = self.amp1.get() / 3.0  # Normalize to 0.0 - 1.0 range
        vol2 = self.amp2.get() / 3.0

        num_samples = int(SAMPLE_RATE * DURATION)
        byte_array = bytearray()

        for i in range(num_samples):
            t = i / SAMPLE_RATE
            
            # --- THE SOUND CHORD EQUATION ---
            # Generate both audio waves independently, scale by volume, and mix them together
            wave1_sample = math.sin(2 * math.pi * hz1 * t) * vol1
            wave2_sample = math.sin(2 * math.pi * hz2 * t) * vol2
            combined_sample = (wave1_sample + wave2_sample) / 2.0  # Avoid audio clipping distortion
            
            # Map structural decimals (-1.0 to 1.0) into standard signed 16-bit sound boundary space
            integer_value = int(combined_sample * 32767 * 0.7)
            
            # Package into Little Endian binary bytes and stream to the array buffer
            byte_array.extend(struct.pack('<h', integer_value))

        # Write data structural headers onto file payload blocks
        with wave.open(filename, 'wb') as wav_file:
            wav_file.setparams((1, 2, SAMPLE_RATE, len(byte_array), 'NONE', 'not compressed'))
            wav_file.writeframes(byte_array)

        # Broadcast raw array blocks directly over Windows output engines asynchronously
        winsound.PlaySound(filename, winsound.SND_FILENAME | winsound.SND_ASYNC)
if __name__ == "__main__":
    root = tk.Tk()
    app = DualWaveChordApp(root)
    root.mainloop()

## How the Math Mixes Into Sound:

* The Pitch Shift (* 100.0): In the visual grid, a frequency value of 2.0 looks great, but 2 Hz is way too low for human ears to hear as sound. Inside generate_and_play_wav, we multiply it by 100 so that a visual value of 2.6 becomes an audible 260 Hz tone (close to a Middle C note).
* The Mixing Loop: Inside the loop, it calculates wave1_sample and wave2_sample at the exact same slice of time t, adds them together, and divides by 2 so the volume doesn't clip or distort.

Now that we have successfully rendered the separate wave lines and generated a mixed audio chord from them, what would you like to explore next?
Would you like to add a third line onto the canvas grid that visually shows the mathematical combination of both waves (showing wave interference), or would you like to introduce a circle equation to the mix?
Tell me if you prefer to:

* Add a third visual line to the grid showing the combined sum wave (wave interference)
* Introduce a circle shape to this same graph environment
* Change the tool to handle a three-note musical chord instead of two


