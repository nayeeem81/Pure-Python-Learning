import os
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pydub import AudioSegment

router_words = APIRouter(prefix="/words", tags=["Word Frequency & Amplitude Customizer"])

WORKSPACE_DIR = os.path.abspath("./project")
GENERATED_DIR = os.path.join(WORKSPACE_DIR, "generated")
ORIGINAL_JSON = os.path.join(GENERATED_DIR, "metadata.json")

# New isolated export outputs
MODIFIED_JSON = os.path.join(GENERATED_DIR, "modified_metadata.json")
MODIFIED_MP3 = os.path.join(GENERATED_DIR, "modified_sentence.mp3")

# Ensure environment paths are set for PyDub subprocess engines
FFMPEG_PATH = r"C:\ffmpeg\bin"
if FFMPEG_PATH not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + FFMPEG_PATH

class WordAdjustment(BaseModel):
    word_index: int
    pitch_shift: float  # Represented in octaves/semitones
    volume_db: float    # Represented in Decibels adjustment (+/- dB)

class ConsolidateRequest(BaseModel):
    adjustments: list[WordAdjustment]

def apply_dsp_tweaks(audio: AudioSegment, pitch: float, volume: float) -> AudioSegment:
    """Modifies the frequency profile and gain metrics of an audio fragment."""
    # 1. Apply Volume / Amplitude Adjustment (in Decibels)
    modified_audio = audio + volume
    
    # 2. Apply Tone / Frequency Pitch Shift
    if pitch != 0:
        new_sample_rate = int(modified_audio.frame_rate * (2.0 ** pitch))
        spawned = modified_audio._spawn(modified_audio.raw_data, overrides={'frame_rate': new_sample_rate})
        modified_audio = spawned.set_frame_rate(modified_audio.frame_rate)
        
    return modified_audio

@router_words.post("/consolidate-modifications")
async def consolidate_modifications(payload: ConsolidateRequest):
    if not os.path.exists(ORIGINAL_JSON):
        raise HTTPException(status_code=404, detail="Original analysis metadata maps missing.")

    # Load original asset template
    with open(ORIGINAL_JSON, "r", encoding="utf-8") as f:
        original_data = json.load(f)

    # Convert incoming payload array to a dictionary lookup table
    adj_map = {item.word_index: item for item in payload.adjustments}
    
    modified_timeline = []
    consolidated_track = AudioSegment.empty()

    for word in original_data["words_timeline"]:
        idx = word["word_index"]
        word_wav_path = os.path.join(WORKSPACE_DIR, word["segment_file"])
        
        if not os.path.exists(word_wav_path):
            raise HTTPException(status_code=404, detail=f"Fragment missing: {word_wav_path}")
            
        raw_word_audio = AudioSegment.from_wav(word_wav_path)
        
        # Pull slider tweaks if user changed them; default to zero neutral baseline
        pitch_val = adj_map[idx].pitch_shift if idx in adj_map else 0.0
        volume_val = adj_map[idx].volume_db if idx in adj_map else 0.0
        
        # Process audio data arrays
        processed_word_audio = apply_dsp_tweaks(raw_word_audio, pitch_val, volume_val)
        consolidated_track += processed_word_audio
        
        # Build new configuration footprint tracking metrics
        modified_word_entry = word.copy()
        modified_word_entry["applied_frequency_shift_hz"] = pitch_val
        modified_word_entry["applied_amplitude_db"] = volume_val
        modified_timeline.append(modified_word_entry)

    # Export out new isolated tracks to disk
    consolidated_track.export(MODIFIED_MP3, format="mp3")
    
    new_project_data = {
        "original_sentence": original_data["original_sentence"],
        "master_mp3_path": "generated/modified_sentence.mp3",
        "total_duration_seconds": consolidated_track.duration_seconds,
        "words_timeline": modified_timeline
    }
    
    with open(MODIFIED_JSON, "w", encoding="utf-8") as f:
        json.dump(new_project_data, f, indent=4)

    return {
        "status": "success",
        "mp3_url": "/project/generated/modified_sentence.mp3",
        "json_url": "/project/generated/modified_metadata.json"
    }

