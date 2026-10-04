import sys
import os
import struct
import asyncio  

import aiofiles # <--- Import this for non-blocking file reads


# Expose both the runner function and the global configuration variable
__all__ = ['print_wav_file_header', 'extract_wav_file_header', 'global_file_path']


# Fix root execution directory routing inside Visual Studio
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except Exception:
    pass





global_file_path = "1.wav"



def initialize_path():
	global global_file_path



def initialize_debugging_arguments():
 
    global global_file_path

    try:
        # Check if a non-empty argument was passed
        if len(sys.argv) > 1 and sys.argv[1].strip():
            print(f"🐞 [VS 2026 Debugger Argument Caught]: {sys.argv[1]}")
        else:
            print(f"🏠 [No Arguments Passed]: Using fallback default -> {global_file_path}")


        if  len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
            # If the argument is a valid file path, set it as the global file path
            global_file_path = sys.argv[1]
        else:
            # Explicitly keep or set default
            initialize_path()
            print(f"⚠️ Error: '{sys.argv[1]}' not found in your folder.")
            print(f"🏠 Using fallback default -> {global_file_path}")
    
    except Exception:
        # Explicitly keep or set default
        initialize_path()
        print(f"⚠️ [Error Handling Debug Arguments]")
        print(f"🏠 Using fallback default -> {global_file_path}")
        pass



async def extract_wav_file_header(): 
    initialize_debugging_arguments()
    header = await _get_header(global_file_path)
    return header



async def print_wav_file_header(): 
    initialize_debugging_arguments()
    header = await _get_header(global_file_path)
    await _printheader(header)


async def _get_header(path):  
   async with aiofiles.open(path, "rb") as f:
        print()
        print(f"Reading WAV header from: {path}")
       
        # Read exactly the first 44 bytes of the file
        header = await f.read(44)
        # Unpack the binary header according to the RIFF spec layout
        
        # Format string guide:
        # 4s = 4-byte string, I = 4-byte unsigned int, H = 2-byte unsigned short
        elements = struct.unpack("<4sI4s4sIHHIIHH4sI", header)
        
        await asyncio.sleep(0.1)  
        # Simulate async operation
        
        return elements


async def _printheader(elements):
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

    await asyncio.sleep(0.1)  # Simulate async operation
 
    # Display our extracted metadata
    print()
    print()
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



async def main():
    await print_wav_file_header()


if __name__ == "__main__":
    asyncio.run(main())
