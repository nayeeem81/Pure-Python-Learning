import os
import json
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from gtts import gTTS
from pydub import AudioSegment

# Assuming this is attached to your existing router file
processor_router = APIRouter(prefix="/audio-processor", tags=["TTS Processor"])

WORKSPACE_DIR = os.path.abspath("./project")
GENERATED_DIR = os.path.join(WORKSPACE_DIR, "generated")
SEGMENTS_DIR = os.path.join(GENERATED_DIR, "segments")
JSON_PATH = os.path.join(GENERATED_DIR, "metadata.json")
MASTER_MP3_PATH = os.path.join(GENERATED_DIR, "full_sentence.mp3")

class TTSRequest(BaseModel):
    text: str

def generate_tts_and_metadata(text: str):
    """
    Background worker that runs right after a request comes in.
    Generates the master sentence and populates the project folder structures.
    """
    try:
        # 1. Generate full sentence audio using Google TTS
        tts = gTTS(text=text, lang='en')
        tts.save(MASTER_MP3_PATH)
        
        # 2. Slice into individual words for editing (Using PyDub)
        sound = AudioSegment.from_mp3(MASTER_MP3_PATH)
        words = text.split()
        
        # Basic chunking: divide total duration equally among words for the map framework
        # (For hyper-precise waveform alignment, a forced-aligner can replace this step later)
        total_duration = sound.duration_seconds
        duration_per_word = total_duration / len(words) if words else 0
        
        words_timeline = []
        current_time = 0.0
        
        for idx, word in enumerate(words):
            start_ms = int(current_time * 1000)
            end_ms = int((current_time + duration_per_word) * 1000)
            
            # Isolate word audio clip
            word_segment = sound[start_ms:end_ms]
            
            # Save the clean, lossless WAV segment locally on your disk
            segment_filename = f"word_{idx:03d}_{word.lower()}.wav"
            segment_relative_path = f"generated/segments/{segment_filename}"
            segment_absolute_path = os.path.join(SEGMENTS_DIR, segment_filename)
            
            word_segment.export(segment_absolute_path, format="wav")
            
            # Append structured analytics payload map
            words_timeline.append({
                "word_index": idx,
                "text": word,
                "start_time": round(current_time, 2),
                "end_time": round(current_time + duration_per_word, 2),
                "segment_file": segment_relative_path,
                "applied_frequency_shift_hz": 0.0
            })
            
            current_time += duration_per_word

        # 3. Save the project structure profile to metadata.json
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

@processor_router.post("/generate-speech")
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
