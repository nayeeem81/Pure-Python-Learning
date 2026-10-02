

# How to display a waves of samples (2 channel) from total sample in a chart in python.

To display your 2-channel (Stereo) audio samples visually inside a chart, you can use Python's built-in tkinter module to draw a custom graph from scratch. This maintains your pure Python (zero-install) requirement without needing heavy external charting packages like Matplotlib or NumPy.
The solution below extracts a small window of samples from your stereo file, splits them into Left and Right data arrays, and renders them onto a visual dual-timeline chart.
## Pure Python Stereo Waveform Charting Script
Paste this code directly into your Visual Studio 2026 project. It will read vs_audio_mix.wav (or any stereo WAV file) and draw both channels in a native window.

import osimport structimport tkinter as tkimport wave
# Fix working directory for Visual Studiotry:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))except Exception:
    pass
input_filename = "vs_audio_mix.wav"
# ==========================================# 1. EXTRACT AND SEPARATE STEREO SAMPLES# ==========================================if not os.path.exists(input_filename):
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
# Unpack signed 16-bit integerstotal_samples = len(raw_bytes) // sample_widthall_samples = struct.unpack(f"<{total_samples}h", raw_bytes)
# Separate Interleaved Channels# Index 0, 2, 4... are Left channel | Index 1, 3, 5... are Right channelleft_channel = all_samples[0::2]right_channel = all_samples[1::2]
# ==========================================# 2. ISOLATE A VISUAL RANGE (e.g., 500 samples)# ==========================================# Displaying millions of points will freeze the UI, so we zoom into a 500-sample windowview_start = int(sample_rate * 0.1)  # Look 0.1 seconds into the audioview_length = 500view_end = view_start + view_length
left_window = left_channel[view_start:view_end]right_window = right_channel[view_start:view_end]
# ==========================================# 3. BUILD THE TKINTER CHART WINDOW# ==========================================root = tk.Tk()
root.title("Pure Python Stereo Waveform Chart (2-Channel)")
window_width = 800window_height = 500canvas = tk.Canvas(root, width=window_width, height=window_height, bg="#1e1e1e")
canvas.pack()
# Chart layout math constantschart_width = 700chart_height = 180margin_left = 60
# Center lines (silence anchors) for both plotsleft_center_y = 120right_center_y = 360
# Draw backgrounds & Title text elements
canvas.create_text(400, 20, text="STEREO AUDIO WAVEFORM EXAMINER", fill="#ffffff", font=("Arial", 14, "bold"))
canvas.create_text(margin_left, left_center_y - 95, text="LEFT CHANNEL (Ch 1)", fill="#00ffcc", anchor="w", font=("Arial", 10, "bold"))
canvas.create_text(margin_left, right_center_y - 95, text="RIGHT CHANNEL (Ch 2)", fill="#ff4d4d", anchor="w", font=("Arial", 10, "bold"))
# Draw baseline center lines
canvas.create_line(margin_left, left_center_y, margin_left + chart_width, left_center_y, fill="#555555", dash=(4, 2))
canvas.create_line(margin_left, right_center_y, margin_left + chart_width, right_center_y, fill="#555555", dash=(4, 2))
# ==========================================# 4. PLOT SAMPLES METHODICAL PIPELINE# ==========================================def draw_channel_wave(samples, center_y, color):
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

## 🧠 How the Coordinate Math Maps to the UI
Because standard graphics canvas environments map coordinates inversely (where (0,0) is the top-left corner of the window), the script translates the values as follows:

* The Center Line: We establish a center_y line (e.g., 120 pixels down from the top) to represent standard digital silence (0 amplitude).
* Positive Volts/Peaks: When a sample value is positive (climbing to 32767), center_y - normalized_y subtracts pixels from the baseline, drawing the line upward toward the top edge.
* Negative Volts/Troughs: When a sample drops below zero, the negative value turns the operation into an addition, extending the waveform downward into the lower valley.

The visual representation below shows how the multi-series tracking arrays match on the parallel timelines:
If you'd like to refine this interface, let me know:

* Would you like to add a horizontal scrollbar to browse back and forth across the entire duration of the file?
* Do you want to see how to code a live playback marker line that slides across the chart while the speakers play the music?

To take your app further, tell me:

* Would you like to add a scrollbar to scroll across the whole file?
* Do you want a live cursor line that moves while the file plays?


