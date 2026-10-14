import math
import wave
import struct
import tkinter as tk
from tkinter import ttk
import winsound  # Built-in sound engine for Windows

class WaveInterferenceChordApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wave Interference & Chord Visualizer")
        self.root.geometry("640x650")
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
        amp1_slider = tk.Scale(amp1_row, from_=0.0, to=2.0, resolution=0.1, orient="horizontal", variable=self.amp1, command=lambda e: self.update_graph(), showvalue=False, bg="#1e1e24", fg="#00adb5", highlightthickness=0, troughcolor="#444", activebackground="#00adb5")
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
        amp2_slider = tk.Scale(amp2_row, from_=0.0, to=2.0, resolution=0.1, orient="horizontal", variable=self.amp2, command=lambda e: self.update_graph(), showvalue=False, bg="#1e1e24", fg="#ff79c6", highlightthickness=0, troughcolor="#444", activebackground="#ff79c6")
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
        points_sum = []  # To hold the combined interference wave coordinates

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

            # --- INTERFERENCE MATH ---
            # Sum the values of both mathematical equations together
            y_sum = y1 + y2
            pixel_y_sum = center_y - (y_sum * 40.0)
            points_sum.append((pixel_x, pixel_y_sum))

        flat_w1 = [coord for pt in points_wave1 for coord in pt]
        flat_w2 = [coord for pt in points_wave2 for coord in pt]
        flat_sum = [coord for pt in points_sum for coord in pt]

        # Draw the original two wave lines
        self.canvas.create_line(flat_w1, fill="#00adb5", width=2, smooth=True)
        self.canvas.create_line(flat_w2, fill="#ff79c6", width=2, smooth=True)
        
        # Draw the new combined interference wave line (Thicker Green line)
        self.canvas.create_line(flat_sum, fill="#50fa7b", width=3, smooth=True)

    def generate_and_play_wav(self):
        SAMPLE_RATE = 44100
        DURATION = 1.5  # Play length in seconds
        filename = "interference_chord.wav"
        
        hz1 = self.freq1.get() * 100.0
        hz2 = self.freq2.get() * 100.0
        
        vol1 = self.amp1.get() / 2.0  # Normalized to new max bound boundaries
        vol2 = self.amp2.get() / 2.0

        num_samples = int(SAMPLE_RATE * DURATION)
        byte_array = bytearray()

        for i in range(num_samples):
            t = i / SAMPLE_RATE
            
            wave1_sample = math.sin(2 * math.pi * hz1 * t) * vol1
            wave2_sample = math.sin(2 * math.pi * hz2 * t) * vol2
            
            # The audio mixing code mirrors the visual green line perfectly!
            combined_sample = (wave1_sample + wave2_sample) / 2.0  
            
            integer_value = int(combined_sample * 32767 * 0.7)
            byte_array.extend(struct.pack('<h', integer_value))

        with wave.open(filename, 'wb') as wav_file:
            wav_file.setparams((1, 2, SAMPLE_RATE, len(byte_array), 'NONE', 'not compressed'))
            wav_file.writeframes(byte_array)

        winsound.PlaySound(filename, winsound.SND_FILENAME | winsound.SND_ASYNC)

if __name__ == "__main__":
    root = tk.Tk()
    app = WaveInterferenceChordApp(root)
    root.mainloop()

