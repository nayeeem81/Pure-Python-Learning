import os
import json
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from gtts import gTTS
from pydub import AudioSegment
# 🔥 FIX: Inject the FFmpeg binary path directly into the Python running environment
FFMPEG_PATH = r"C:\ffmpeg\bin"
if FFMPEG_PATH not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + FFMPEG_PATH
# Tell PyDub the exact hard disk location of your downloaded FFmpeg binaries
AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe"
AudioSegment.ffprobe = r"C:\ffmpeg\bin\ffprobe.exe"
# ALWAYS DECLARE THE ROUTER FIRST AT THE TOP
process_router = APIRouter(prefix="/process", tags=["TTS Processor"]) 

class TTSRequest(BaseModel):
    text: str

# Resolve paths matching your target directory schema
WORKSPACE_DIR = os.path.abspath("./project")
GENERATED_DIR = os.path.join(WORKSPACE_DIR, "generated")
SEGMENTS_DIR = os.path.join(GENERATED_DIR, "segments")
JSON_PATH = os.path.join(GENERATED_DIR, "metadata.json")
MASTER_MP3_PATH = os.path.join(GENERATED_DIR, "full_sentence.mp3")

# Auto-ensure directories exist on startup
os.makedirs(SEGMENTS_DIR, exist_ok=True)


def generate_tts_and_metadata(text: str):
    """
    Background worker that downloads the speech file from Google TTS,
    segments it into words, and compiles the project map file.
    """
    try:
        # 1. Download and save full sentence via gTTS
        tts = gTTS(text=text, lang='en')
        tts.save(MASTER_MP3_PATH)
        
        # 2. Slice into words for editing (Using PyDub)
        sound = AudioSegment.from_mp3(MASTER_MP3_PATH)
        words = text.split()
        
        # Calculate duration footprints
        total_duration = sound.duration_seconds
        duration_per_word = total_duration / len(words) if words else 0
        
        words_timeline = []
        current_time = 0.0
        
        for idx, word in enumerate(words):
            start_ms = int(current_time * 1000)
            end_ms = int((current_time + duration_per_word) * 1000)
            
            # Isolate the segment chunk
            word_segment = sound[start_ms:end_ms]
            
            # Form clean strings for storage mapping keys
            clean_word = "".join(c for c in word if c.isalnum()).lower()
            segment_filename = f"word_{idx:03d}_{clean_word}.wav"
            
            # 'segment_file' should match your workspace schema for relative lookup
            segment_relative_path = f"generated/segments/{segment_filename}"
            segment_absolute_path = os.path.join(SEGMENTS_DIR, segment_filename)
            
            # Save lossless chunk to local drive
            word_segment.export(segment_absolute_path, format="wav")
            
            # Add to the JSON alignment sequence map
            words_timeline.append({
                "word_index": idx,
                "text": word,
                "start_time": round(current_time, 2),
                "end_time": round(current_time + duration_per_word, 2),
                "segment_file": segment_relative_path,
                "applied_frequency_shift_hz": 0.0
            })
            
            current_time += duration_per_word

        # 3. Output structural config map profile onto hard drive
        project_data = {
            "original_sentence": text,
            "master_mp3_path": "generated/full_sentence.mp3",
            "total_duration_seconds": round(total_duration, 2),
            "words_timeline": words_timeline
        }
        
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(project_data, f, indent=4)
            
        print(f"✅ Successfully compiled raw audio assets for: '{text}'")
        
    except Exception as e:
        print(f"❌ Error compiling background audio tasks: {str(e)}")


@process_router.post("/generate-speech-processing")
async def generate_speech(payload: TTSRequest, background_tasks: BackgroundTasks):
    """
    Receives sentence text, passes processing workloads over to system background loops,
    and cleanly unblocks the UI immediately.
    """
    # Trigger background audio processing task immediately on local disk
    background_tasks.add_task(generate_tts_and_metadata, payload.text)
    
    return {
        "status": "processing",
        "message": "Speech generation started in background.",
        "expected_paths": {
            "audio": "generated/full_sentence.mp3",
            "json": "generated/metadata.json"
        }
    }
