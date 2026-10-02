import struct

file_path = "fully_processed.wav"

with open(file_path, "rb") as f:
    # Read exactly the first 44 bytes of the file
    header = f.read(44)

# Unpack the binary header according to the RIFF spec layout
# Format string guide:
# 4s = 4-byte string, I = 4-byte unsigned int, H = 2-byte unsigned short
elements = struct.unpack("<4sI4s4sIHHIIHH4sI", header)

# Map unpacked data to clear variables
chunk_id          = elements[0].decode('ascii')
file_size_minus_8 = elements[1]
format_tag        = elements[2].decode('ascii')
subchunk_1_id     = elements[3].decode('ascii')
subchunk_1_size   = elements[4]
audio_format      = elements[5]
num_channels      = elements[6]
sample_rate       = elements[7]
byte_rate         = elements[8]
block_align       = elements[9]
bits_per_sample   = elements[10]
subchunk_2_id     = elements[11].decode('ascii')
data_size         = elements[12]

# Display our extracted metadata
print("=" * 45)
print("       RAW WAV HEADER METADATA             ")
print("=" * 45)
print(f"File Type Marker:     {chunk_id}")
print(f"Format Marker:        {format_tag}")
print(f"Audio Format Type:    {audio_format} (1 = Uncompressed PCM)")
print(f"Channels:             {num_channels} ({'Stereo' if num_channels == 2 else 'Mono'})")
print(f"Sample Rate:          {sample_rate} Hz ({sample_rate / 1000} kHz)")
print(f"Bit Depth:            {bits_per_sample}-bit")
print(f"Frame Size Alignment: {block_align} bytes per frame")
print(f"Data Subchunk Marker: {subchunk_2_id}")
print(f"Raw Audio Data Size:  {data_size} bytes")
print("=" * 45)
