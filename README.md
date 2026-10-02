# PurePythonApp

## Array & Variables


## Wave (Python)

Yes, the total number of frames divided by the sample rate creates the exact duration (time) of the audio file. [1, 2] 

However, your assumption about the sample rate being an "average" because some seconds have more or fewer frames is incorrect. 

In standard uncompressed audio formats like WAV (PCM), the distribution is not an average—it is completely fixed and constant throughout the entire file.
------------------------------
## 1. Frame vs. Sample vs. Sample Rate
To clear up the confusion, it helps to look at exactly how these terms connect:

* 
* Sample: A single data point representing the amplitude of the audio at a precise moment in time. [3] 

* Frame: A collection of samples captured at the exact same instant across all audio channels.

* In a Mono (1-channel) file: 1 Frame = 1 Sample.

* In a Stereo (2-channel) file: 1 Frame = 2 Samples 
(one for the left channel, one for the right). [4, 5] 

* Sample Rate (Framerate): The exact number of frames captured per second. It never fluctuates. If a WAV file has a sample rate of 44,100 Hz, it means every single second contains exactly 44,100 frames, without exception. [2, 4, 5, 6] 
* 

## 2. Does the Sample Rate give us total samples?
Not directly, but it gives us the total frames per second. You can easily calculate the total number of samples using the channels: [2, 5] 

$$\text{Total Samples} = \text{Total Frames (\texttt{getnframes()})} \times \text{Number of Channels}$$ 

## 3. Calculating the Audio Duration
Because the playback speed (sample rate) is perfectly constant, the math to find the exact length of your audio file is straightforward:

$$\text{Duration (seconds)} = \frac{\text{Total Frames}}{\text{Sample Rate}}$$ 

Here is how you can visualize this in Python code:

import wave
with wave.open("audio.wav", "rb") as wav_file:
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

Are you planning to process the raw audio data (like converting it to a NumPy array), or do you just need to extract metadata like duration and file properties? Let me know your main goal so I can provide the right snippet! [2, 7] 

[1] [https://stackoverflow.com](https://stackoverflow.com/questions/65729661/what-does-n-mean-in-readframesn-wave-python)
[2] [https://stackoverflow.com](https://stackoverflow.com/questions/7833807/get-wav-file-length-or-duration)
[3] [https://stackoverflow.com](https://stackoverflow.com/questions/34257434/understanding-frames-samples-for-audio)
[4] [https://sound.stackexchange.com](https://sound.stackexchange.com/questions/46353/what-is-the-real-time-from-sample-number)
[5] [https://stackoverflow.com](https://stackoverflow.com/questions/19589496/frame-rate-vs-sample-rate)
[6] [https://raspberrypi.stackexchange.com](https://raspberrypi.stackexchange.com/questions/39865/getting-frequency-of-an-audio-file-per-second-in-raspberry-pi)
[7] [https://stackoverflow.com](https://stackoverflow.com/questions/45893013/python-wav-processing-nframe-not-equal-to-actual-number-of-frame)
