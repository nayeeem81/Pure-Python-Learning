# audio.py
import os
import threading
from gtts import gTTS
import pygame

pygame.mixer.init()

def _speak_worker(text: str, on_complete_callback=None):
    """Internal worker that runs on a background thread."""
    try:
        filename = "temp_voice.mp3"
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(filename)
        
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
        pygame.mixer.music.unload()
        if os.path.exists(filename):
            os.remove(filename)
            
    except Exception as e:
        print(f"[AUDIO ERROR] {e}")
    finally:
        # Trigger the callback on the main UI thread to turn off the wave
        if on_complete_callback:
            on_complete_callback()

def speak_sentence(text: str, on_complete_callback=None):
    """Safely triggers speech and runs a callback when done."""
    thread = threading.Thread(
        target=_speak_worker, 
        args=(text, on_complete_callback), 
        daemon=True
    )
    thread.start()
