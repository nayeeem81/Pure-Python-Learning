import os
import struct
import tkinter as tk
import wave

# Fix working directory for Visual Studio
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except Exception:
    pass

input_filename = "vs_audio_mix.wav"

if not os.path.exists(input_filename):
    print(f"Error: '{input_filename}' not found. Please run your audio creation script first!")
    exit()

with wave.open(input_filename, "rb") as wav:
    num_channels = wav.getnchannels()
    sample_width = wav.getsampwidth()
    sample_rate = wav.getframerate()
    num_frames = wav.getnframes()
    # Read raw binary frames
    raw_bytes = wav.readframes(num_frames)

if num_channels != 2:
    print(f"💡 This script is designed for 2-channel Stereo. Your file has {num_channels} channel(s).")

    print("For demonstration, we will duplicate the mono channel as Left and Right.")

    num_channels = 2

    # Duplicate bytes to simulate stereo if file is mono
    if sample_width == 2:
        new_bytes = bytearray()
        for i in range(0, len(raw_bytes), 2):
            chunk = raw_bytes[i:i+2]
            new_bytes.extend(chunk * 2)
        raw_bytes = bytes(new_bytes)

# Unpack signed 16-bit integers
total_samples = len(raw_bytes) // sample_width
all_samples = struct.unpack(f"<{total_samples}h", raw_bytes)

# Separate Interleaved Channels
# Index 0, 2, 4... are Left channel | Index 1, 3, 5... are Right channel
left_channel = all_samples[0::2]
right_channel = all_samples[1::2]

# Displaying millions of points will freeze the UI, so we zoom into a 500-sample window
view_start = int(sample_rate * 0.1)  # Look 0.1 seconds into the audio
view_length = 500
view_end = view_start + view_length

left_window = left_channel[view_start:view_end]
right_window = right_channel[view_start:view_end]

root = tk.Tk()
root.title("Pure Python Stereo Waveform Chart (2-Channel)")

window_width = 800
window_height = 500
canvas = tk.Canvas(root, width=window_width, height=window_height, bg="#1e1e1e")
canvas.pack()

# Chart layout math constants
chart_width = 700
chart_height = 180
margin_left = 60

# Center lines (silence anchors) for both plots
left_center_y = 120
right_center_y = 360

# Draw backgrounds & Title text elements
canvas.create_text(400, 20, text="STEREO AUDIO WAVEFORM EXAMINER", fill="#ffffff", font=("Arial", 14, "bold"))

canvas.create_text(margin_left, left_center_y - 95, text="LEFT CHANNEL (Ch 1)", fill="#00ffcc", anchor="w", font=("Arial", 10, "bold"))

canvas.create_text(margin_left, right_center_y - 95, text="RIGHT CHANNEL (Ch 2)", fill="#ff4d4d", anchor="w", font=("Arial", 10, "bold"))

# Draw baseline center lines
canvas.create_line(margin_left, left_center_y, margin_left + chart_width, left_center_y, fill="#555555", dash=(4, 2))

canvas.create_line(margin_left, right_center_y, margin_left + chart_width, right_center_y, fill="#555555", dash=(4, 2))

# 4. PLOT SAMPLES METHODICAL PIPELINE
def draw_channel_wave(samples, center_y, color):
    points = []
    num_points = len(samples)
    
    if num_points < 2:
        return
        
    for idx, sample_val in enumerate(samples):
        # Step X: Calculate horizontal spacing step across pixel scale
        x = margin_left + (idx / (num_points - 1)) * chart_width
        
        # Step Y: Scale 16-bit integer (-32768 to 32767) into our pixel height bounds (max 85 pixels high)
        normalized_y = (sample_val / 32768.0) * 85
        y = center_y - normalized_y  # Subtract because pixel Y starts at 0 at the top
        
        points.append((x, y))
        
    # Draw linear connections between each continuous coordinates array point
    for i in range(len(points) - 1):
        canvas.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1], fill=color, width=1.5)

# Render Left Waveform (Cyan) and Right Waveform (Red)
draw_channel_wave(left_window, left_center_y, "#00ffcc")
draw_channel_wave(right_window, right_center_y, "#ff4d4d")

# Draw Time scale label indicators at the bottom
canvas.create_text(margin_left, 470, text=f"Window Start: {view_start} samples", fill="#aaaaaa", anchor="w")

canvas.create_text(margin_left + chart_width, 470, text=f"Window End: {view_end} samples", fill="#aaaaaa", anchor="e")

print("Displaying chart rendering window...")

root.mainloop()



