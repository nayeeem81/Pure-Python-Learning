import os
import struct
import time
import tkinter as tk
import wave
import winsound

# Fix root execution directory routing inside Visual Studio
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except Exception:
    pass

input_filename = "vs_audio_mix.wav"

# ==========================================
# 1. PARSE & ISOLATE THE AUDIO SEGMENT
# ==========================================
if not os.path.exists(input_filename):
    print(f"Error: '{input_filename}' not found. Please ensure it exists in your project directory.")
    exit()

with wave.open(input_filename, "rb") as wav:
    num_channels = wav.getnchannels()
    sample_width = wav.getsampwidth()
    sample_rate = wav.getframerate()
    num_frames = wav.getnframes()
    raw_bytes = wav.readframes(num_frames)

# Unpack signed 16-bit integers
total_samples = len(raw_bytes) // sample_width
all_samples = struct.unpack(f"<{total_samples}h", raw_bytes)

# Split stereo streams. If mono, handle identical extraction channels
if num_channels == 2:
    left_channel = all_samples[0::2]
    right_channel = all_samples[1::2]
else:
    left_channel = list(all_samples)
    right_channel = list(all_samples)

# --- TRACKING CONSTRAINTS ---
# Total time duration of the file in seconds
total_duration = num_frames / sample_rate 

# Select a precise chunk window layout to plot on screen
view_start_sample = 0
view_length_samples = int(sample_rate * total_duration)  # Display whole file length
left_window = left_channel[view_start_sample:view_start_sample + view_length_samples]
right_window = right_channel[view_start_sample:view_start_sample + view_length_samples]

# ==========================================
# 2. APPLICATION WINDOW SETUP
# ==========================================
root = tk.Tk()
root.title("Interactive Waveform Visualizer & Live Tracking Cursor")

window_width = 850
window_height = 550
canvas = tk.Canvas(root, width=window_width, height=window_height, bg="#121212")
canvas.pack()

# Spatial layout constants
chart_width = 720
margin_left = 70
left_center_y = 150
right_center_y = 380

# Structural background labels
canvas.create_text(425, 25, text="REAL-TIME PLAYBACK TIMELINE CHANNELS", fill="#ffffff", font=("Arial", 13, "bold"))
canvas.create_text(margin_left, left_center_y - 90, text="LEFT SPEAKER (CH 1)", fill="#00ffcc", anchor="w", font=("Arial", 9, "bold"))
canvas.create_text(margin_left, right_center_y - 90, text="RIGHT SPEAKER (CH 2)", fill="#ff3366", anchor="w", font=("Arial", 9, "bold"))

# Draw dashed baseline zero-voltage registers
canvas.create_line(margin_left, left_center_y, margin_left + chart_width, left_center_y, fill="#333333", dash=(4, 2))
canvas.create_line(margin_left, right_center_y, margin_left + chart_width, right_center_y, fill="#333333", dash=(4, 2))

# ==========================================
# 3. STATIC WAVEFORM RENDER PIPELINE
# ==========================================
def render_static_waves(samples, center_y, color):
    points = []
    num_points = len(samples)
    if num_points < 2: return
    
    # Sub-sampling data step calculation to prevent UI lag on huge files
    step = max(1, num_points // chart_width)
    
    for idx in range(0, num_points, step):
        x = margin_left + (idx / (num_points - 1)) * chart_width
        sample_val = samples[idx]
        normalized_y = (sample_val / 32768.0) * 80
        y = center_y - normalized_y
        points.append((x, y))
        
    for i in range(len(points) - 1):
        canvas.create_line(points[i], points[i+1], fill=color, width=1.2)

# Run static plotting sweeps
render_static_waves(left_window, left_center_y, "#00ffcc")
render_static_waves(right_window, right_center_y, "#ff3366")

# ==========================================
# 4. LIVE CURSOR CORE ENGINE PROPERTIES
# ==========================================
# Draw the actual dynamic cursor component line across the canvas vertically
cursor_id = canvas.create_line(margin_left, 40, margin_left, 480, fill="#ffffff", width=2)

# Playback state tracking anchors
start_timestamp = 0.0
is_playing = False

def start_playback_routine():
    global start_timestamp, is_playing
    if is_playing: return  # Guard clause against overlapping play calls
    
    is_playing = True
    start_timestamp = time.time()
    
    # SND_ASYNC forces Windows to play the audio stream on an independent background thread. 
    # This prevents the application window frame from freezing.
    winsound.PlaySound(input_filename, winsound.SND_FILENAME | winsound.SND_ASYNC)
    
    # Trigger the tick tracking manager immediately
    update_cursor_tick()

def update_cursor_tick():
    global start_timestamp, is_playing
    if not is_playing: return
    
    # Calculate how many seconds have slipped by since the play button was hit
    elapsed_time = time.time() - start_timestamp
    
    if elapsed_time >= total_duration:
        # File has hit the terminal end boundary line
        canvas.coords(cursor_id, margin_left + chart_width, 40, margin_left + chart_width, 480)
        is_playing = False
        print("Playback finished.")
        return
        
    # Translate elapsed time percentage into an absolute screen X coordinate matching the static plot width
    progress_ratio = elapsed_time / total_duration
    current_x = margin_left + (progress_ratio * chart_width)
    
    # Move the vertical coordinate line to its new horizontal position vector
    canvas.coords(cursor_id, current_x, 40, current_x, 480)
    
    # Enqueue a redraw event step to run again in 16 milliseconds (~60 Frames Per Second refresh rate)
    root.after(16, update_cursor_tick)

# ==========================================
# 5. UI BUTTON LAYER CONSTRUCTS
# ==========================================
# Build a native panel anchor button at the bottom of the layout structure
play_btn = tk.Button(
    root, 
    text="▶ START LIVE TRACKING AUDIO", 
    command=start_playback_routine, 
    bg="#222222", 
    fg="#ffffff", 
    activebackground="#444444", 
    activeforeground="#00ffcc",
    font=("Arial", 10, "bold"),
    padx=20,
    pady=8
)
play_btn.pack(pady=15)

# Display context markers at the footer base limits
canvas.create_text(margin_left, 500, text="0.0s (Start)", fill="#777777", anchor="w")
canvas.create_text(margin_left + chart_width, 500, text=f"{total_duration:.2f}s (End)", fill="#777777", anchor="e")

print("Application frame deployment successful.")
root.mainloop()





