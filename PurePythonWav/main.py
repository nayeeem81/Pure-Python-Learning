# main.py
import asyncio

# Import the function from the Wav subfolder
from wav.app_metadata_reader import print_wav_file_header

async def main():
    print("🚀 Starting program from main.py...")
    await  print_wav_file_header()

if __name__ == "__main__":
    asyncio.run(main())
