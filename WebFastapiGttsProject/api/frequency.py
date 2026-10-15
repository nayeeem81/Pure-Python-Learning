import os
import json  
from fastapi import APIRouter, HTTPException 
from pydantic import BaseModel
from pydub import AudioSegment

frequency_router = APIRouter(prefix="/frequency", tags=["Sentence Frequency Analyzer"])

WORKSPACE_DIR = os.path.abspath("./project")
GENERATED_DIR = os.path.join(WORKSPACE_DIR, "generated")
SEGMENTS_DIR = os.path.join(GENERATED_DIR, "segments")
JSON_PATH = os.path.join(GENERATED_DIR, "metadata.json")
MASTER_MP3_PATH = os.path.join(GENERATED_DIR, "full_sentence.mp3")

os.makedirs(SEGMENTS_DIR, exist_ok=True)

class FrequencyUpdate(BaseModel):
    word_index: int
    new_frequency_shift: float 
    
def apply_frequency_pitch_shift(audio_segment: AudioSegment, shift_amount: float) -> AudioSegment:
    """Shifts the core pitch (frequencies) of a word segment.
    shift_amount: Use positive values (e.g., 0.5) to increase frequency/pitch, 
    negative values (e.g., -0.5) to decrease frequency/pitch."""
    if shift_amount == 0:
        return audio_segment
    new_sample_rate = int(audio_segment.frame_rate * (2.0 ** shift_amount))
    shifted_audio = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_sample_rate})
    return shifted_audio.set_frame_rate(audio_segment.frame_rate)

@frequency_router.post("/frequency")

@frequency_router.post("/update-frequency")
async def update_frequency(data: FrequencyUpdate):
    if not os.path.exists(JSON_PATH):
        raise HTTPException(status_code=404, detail="Project metadata.json file missing on disk.")
        
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        project_data = json.load(f)
    target_word = None
    for word in project_data["words_timeline"]:
        if word["word_index"] == data.word_index:
            target_word = word
            break
    if not target_word:
        raise HTTPException(status_code=404, detail="Word index mismatch.")
    target_word["applied_frequency_shift_hz"] = data.new_frequency_shift
    consolidated_sentence = AudioSegment.empty()
    
    for word in project_data["words_timeline"]:
        word_wav_path = os.path.join(WORKSPACE_DIR, word["segment_file"])
        if not os.path.exists(word_wav_path):
            raise HTTPException(status_code=404, detail=f"Missing word fragment file: {word_wav_path}")       
        word_audio = AudioSegment.from_wav(word_wav_path)
        modified_word_audio = apply_frequency_pitch_shift(
            word_audio, 
            word["applied_frequency_shift_hz"]
        )
        consolidated_sentence += modified_word_audio

    consolidated_sentence.export(MASTER_MP3_PATH, format="mp3")
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(project_data, f, indent=4)
    return {
        "status": "success", 
        "message": f"Successfully shifted frequency of word index {data.word_index} and consolidated."
    }
