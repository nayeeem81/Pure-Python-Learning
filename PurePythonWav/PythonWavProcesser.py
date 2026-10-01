import math
import os
import struct

input_filename = "1.wav"
output_filename = "fully_processed.wav"

# ==========================================
# 1. PARSE THE RAW FILE & HEADER MANUALLY
# ==========================================
with open(input_filename, "rb") as f:
    # Read the explicit 44-byte header structure
    header_bytes = f.read(44)
    
    # Read all remaining raw audio stream bytes
    raw_audio_bytes = f.read()

    # Unpack header metadata fields to map our file constraints
    # Layout mapping: 4s=str, I=uint32, H=uint16
    header_data = struct.unpack("<4sI4s4sIHHIIHH4sI", header_bytes)

    num_channels = header_data[5]  
    # Index 5: Channels (1=Mono, 2=Stereo)

    sample_rate = header_data[6]  
    # Index 6: Sample Rate (e.g., 44100)

    bits_per_sample = header_data[9]  
    # Index 9: Bit Depth (e.g., 16)


    if bits_per_sample > 8:
        raise ValueError(f"This processing script requires 16-bit audio depth. Detected: {bits_per_sample}-bit")

    # Unpack raw bytes into list of mutable integers
    total_samples = len(raw_audio_bytes) // 2
    audio_samples = list(struct.unpack(f"<{total_samples}h", raw_audio_bytes))

    print(f"Loaded: {num_channels} channels at {sample_rate} Hz ({bits_per_sample}-bit)")
    print(f"Processing {len(audio_samples)} discrete audio points...")

# ==========================================
# 2. AUDIO PROCESSING PIPELINE
# ==========================================
# Find highest absolute peak in the track
    max_peak = max(abs(sample) for sample in audio_samples)
    max_allowed = 32767 
# Max limit for signed 16-bit short integers

    if max_peak > 0:
        gain_multiplier = max_allowed / max_peak
        # Apply standard multiplier gain to maximize the audio signal safely
        audio_samples = [int(s * gain_multiplier) for s in audio_samples]

# --- EFFECT B: LINEAR FADE-OUT (Last 2 Seconds) ---
# Calculate how many samples are packed inside 2 seconds of audio
    fade_duration_seconds = 2.0
    samples_to_fade = int(fade_duration_seconds * sample_rate * num_channels)

# Bound checking to prevent crashing if the track is shorter than 2 seconds
    if len(audio_samples) > samples_to_fade:
        fade_start_index = len(audio_samples) - samples_to_fade
    
    for i in range(samples_to_fade):
        current_index = fade_start_index + i
        # Linearly scale volume factor down from 1.0 down to 0.0
        fade_factor = 1.0 - (i / samples_to_fade)
        audio_samples[current_index] = int(audio_samples[current_index] * fade_factor)

# ==========================================
# 3. BUILD CUSTOM 44-BYTE HEADER FROM SCRATCH
# ==========================================
    processed_audio_bytes = struct.pack(f"<{len(audio_samples)}h", *audio_samples)

# Re-calculate size fields based on our new data footprint
    data_chunk_size = len(processed_audio_bytes)
    riff_chunk_size = 36 + data_chunk_size
    bytes_per_sample = 2
    byte_rate = sample_rate * num_channels * bytes_per_sample
    block_align = num_channels * bytes_per_sample

# Pack the variables directly into raw binary string chunks
    new_header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",           # ChunkID
        riff_chunk_size,   # ChunkSize
        b"WAVE",           # Format Tag
        b"fmt ",           # Subchunk1ID
        16,                # Subchunk1Size (16 for standard PCM)
        1,                 # AudioFormat (1 = Uncompressed PCM)
        num_channels,      # NumChannels
        sample_rate,       # SampleRate
        byte_rate,         # ByteRate
        block_align,       # BlockAlign
        16,                # BitsPerSample (16-bit resolution)
        b"data",           # Subchunk2ID
        data_chunk_size    # Subchunk2Size
    )

# ==========================================
# 4. EXPORT TO DISK
# ==========================================
with open(output_filename, "wb") as out_file:
    out_file.write(new_header)             # Write custom 44-byte header
    out_file.write(processed_audio_bytes)  # Append our modified audio matrix

    print(f"🎉 Success! Completely processed file saved to '{output_filename}'")
