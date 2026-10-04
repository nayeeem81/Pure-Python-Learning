import wave

with wave.open("1.wav", "rb") as wav_file:
    total_frames = wav_file.getnframes()      
    # Total frames in the file

    sample_rate = wav_file.getframerate()     
    # Frames per second (e.g., 44100)

    channels = wav_file.getnchannels()        
    # 1 for mono, 2 for stereo
    
    # Calculate duration
    duration = total_frames / float(sample_rate)
    
    # Calculate total samples
    total_samples = total_frames * channels

    print(f"Duration: {duration:.2f} seconds")
    print(f"Total Samples: {total_samples}")

