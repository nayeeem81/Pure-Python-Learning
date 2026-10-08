import math
import wave
import struct
import tkinter as tk
from tkinter import ttk
import winsound  # Built-in sound engine for Windows

class TriadChordInterferenceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3-Note Triad Chord & Interference Visualizer")
        self.root.geometry("640x720")
        self.root.configure(bg="#121214")

        # Initialize variables for Wave 1 (Teal) - Root Note
        self.amp1 = tk.DoubleVar(value=1.0)
        self.freq1 = tk.DoubleVar(value=2.6)  # ~261 Hz (Middle C)

        # Initialize variables for Wave 2 (Pink) - Third Note
        self.amp2 = tk.DoubleVar(value=1.0)
        self.freq2 = tk.DoubleVar(value=3.3)  # ~330 Hz (E)

        # Initialize variables for Wave 3 (Orange) - Fifth Note
        self.amp3 = tk.DoubleVar(value=1.0)
        self.freq3 = tk.DoubleVar(value=3.9)  # ~392 Hz (G)

        # Create drawing canvas
        self.canvas = tk.Canvas(
            self.root, 
            width=600, 
            height=220, 
            bg="#141416", 
            highlightthickness=1, 
            highlightbackground="#333"
        )
        self.canvas.pack(pady=15)

        # Setup UI controls and layout
        self.setup_controls()
        
        # Initial draw execution
        self.update_graph()

    def setup_controls(self):
        # Master scrollable/grouped slider container
        controls_frame = tk.Frame(self.root, bg="#1e1e24", bd=10)
        controls_frame.pack(fill="x", padx=20, pady=5)
        
        # ------------------ WAVE 1 CONTROLS (TEAL) ------------------
        tk.Label(controls_frame, text="WAVE 1 (TEAL) - Root", fg="#00adb5", bg="#1e1e24", font=("Arial", 9, "bold")).pack(anchor="w")
        self.create_wave_sliders(controls_frame, self.amp1, self.freq1, "#00adb5", "1")

        # ------------------ WAVE 2 CONTROLS (PINK) ------------------
        tk.Label(controls_frame, text="WAVE 2 (PINK) - Third", fg="#ff79c6", bg="#1e1e24", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 0))
        self.create_wave_sliders(controls_frame, self.amp2, self.freq2, "#ff79c6", "2")

        # ------------------ WAVE 3 CONTROLS (ORANGE) ------------------
        tk.Label(controls_frame, text="WAVE 3 (ORANGE) - Fifth", fg="#ffb86c", bg="#1e1e24", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 0))
        self.create_wave_sliders(controls_frame, self.amp3, self.freq3, "#ffb86c", "3")

        # ------------------ PLAY BUTTON INTERFACE ------------------
        play_btn = ttk.Button(self.root, text="Play Full 3-Note Triad Chord", command=self.generate_and_play_wav)
        play_btn.pack(pady=15, fill="x", padx=20)

    def create_wave_sliders(self, parent, amp_var, freq_var, color, suffix):
        # Helper to quickly generate amplitude and frequency row pairings
        row = tk.Frame(parent, bg="#1e1e24")
        row.pack(fill="x", pady=2)
        
        # Amplitude Slider Row
        amp_scale = tk.Scale(row, from_=0.0, to=1.5, resolution=0.1, orient="horizontal", variable=amp_var, command=lambda e: self.update_graph(), showvalue=False, bg="#1e1e24", fg=color, highlightthickness=0, troughcolor="#444", activebackground=color, label="Amp")
        amp_scale.pack(side="left", fill="x", expand=True, padx=5)
        
        # Frequency Slider Row
        freq_scale = tk.Scale(row, from_=0.5, to=8.0, resolution=0.1, orient="horizontal", variable=freq_var, command=lambda e: self.update_graph(), showvalue=False, bg="#1e1e24", fg=color, highlightthickness=0, troughcolor="#444", activebackground=color, label="Freq")
        freq_scale.pack(side="left", fill="x", expand=True, padx=5)

    def update_graph(self):
        self.canvas.delete("all")
        w, h = 600, 220
        center_y = h / 2
        center_x = w / 2

        # Redraw background grid and main axes
        for x in range(0, w, 40): self.canvas.create_line(x, 0, x, h, fill="#252529", width=1)
        for y in range(0, h, 40): self.canvas.create_line(0, y, w, y, fill="#252529", width=1)
        self.canvas.create_line(0, center_y, w, center_y, fill="#888", width=2)
        self.canvas.create_line(center_x, 0, center_x, h, fill="#888", width=2)

        # Grab slider states
        a1, f1 = self.amp1.get(), self.freq1.get()
        a2, f2 = self.amp2.get(), self.freq2.get()
        a3, f3 = self.amp3.get(), self.freq3.get()

        points_w1, points_w2, points_w3, points_sum = [], [], [], []

        for pixel_x in range(w):
            x = (pixel_x - center_x) / 40.0
            
            y1 = a1 * math.sin(f1 * x)
            y2 = a2 * math.sin(f2 * x)
            y3 = a3 * math.sin(f3 * x)
            y_sum = y1 + y2 + y3  # Triple wave intersection calculation

            points_w1.append((pixel_x, center_y - (y1 * 40.0)))
            points_w2.append((pixel_x, center_y - (y2 * 40.0)))
            points_w3.append((pixel_x, center_y - (y3 * 40.0)))
            points_sum.append((pixel_x, center_y - (y_sum * 40.0)))

        # Render paths onto Tkinter canvas windows
        self.canvas.create_line([c for pt in points_w1 for c in pt], fill="#00adb5", width=1, smooth=True)
        self.canvas.create_line([c for pt in points_w2 for c in pt], fill="#ff79c6", width=1, smooth=True)
        self.canvas.create_line([c for pt in points_w3 for c in pt], fill="#ffb86c", width=1, smooth=True)
        
        # Thick Green Composite Interference Line
        self.canvas.create_line([c for pt in points_sum for c in pt], fill="#50fa7b", width=3, smooth=True)

    def generate_and_play_wav(self):
        SAMPLE_RATE = 44100
        DURATION = 1.5
        filename = "triad_chord.wav"
        
        hz1, vol1 = self.freq1.get() * 100.0, self.amp1.get() / 1.5
        hz2, vol2 = self.freq2.get() * 100.0, self.amp2.get() / 1.5
        hz3, vol3 = self.freq3.get() * 100.0, self.amp3.get() / 1.5

        num_samples = int(SAMPLE_RATE * DURATION)
        byte_array = bytearray()

        for i in range(num_samples):
            t = i / SAMPLE_RATE
            
            # Synthesize and compress three sound waves safely to prevent harsh digital clipping
            s1 = math.sin(2 * math.pi * hz1 * t) * vol1
            s2 = math.sin(2 * math.pi * hz2 * t) * vol2
            s3 = math.sin(2 * math.pi * hz3 * t) * vol3
            combined_sample = (s1 + s2 + s3) / 3.0
            
            integer_value = int(combined_sample * 32767 * 0.7)
            byte_array.extend(struct.pack('<h', integer_value))

        with wave.open(filename, 'wb') as wav_file:
            wav_file.setparams((1, 2, SAMPLE_RATE, len(byte_array), 'NONE', 'not compressed'))
            wav_file.writeframes(byte_array)

        winsound.PlaySound(filename, winsound.SND_FILENAME | winsound.SND_ASYNC)

if __name__ == "__main__":
    root = tk.Tk()
    app = TriadChordInterferenceApp(root)
    root.mainloop()
