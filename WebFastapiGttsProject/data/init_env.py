# init_env.py
import os
import sys

# 1. Base directory where you extracted your ffmpeg zip package
base_lookup_dir = r"C:\ffmpeg"
detected_bin_dir = None

# 2. Automatically walk through the folder structure to find the actual bin path
if os.path.exists(base_lookup_dir):
    for root, dirs, files in os.walk(base_lookup_dir):
        if "ffmpeg.exe" in files and "ffprobe.exe" in files:
            detected_bin_dir = root
            break

# 3. Apply the runtime environment overrides if found
if detected_bin_dir:
    print(f"[FFmpeg Engine] Dynamically targeted binary path at: {detected_bin_dir}")
    
    # Inject directly into the OS runtime path execution array
    if detected_bin_dir not in os.environ["PATH"]:
        os.environ["PATH"] = detected_bin_dir + os.pathsep + os.environ["PATH"]
        
    # Explicitly register hook paths on pydub properties before modules run
    try:
        import pydub
        pydub.AudioSegment.converter = os.path.join(detected_bin_dir, "ffmpeg.exe")
        pydub.AudioSegment.ffprobe = os.path.join(detected_bin_dir, "ffprobe.exe")
    except ImportError:
        pass
else:
    print(f"❌ [FFmpeg Error] Could not locate 'ffmpeg.exe' or 'ffprobe.exe' anywhere inside '{base_lookup_dir}'.")
    print("Please make sure you have downloaded and extracted the archive correctly to that directory.")

