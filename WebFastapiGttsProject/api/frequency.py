# api/frequency.py
import os
import json  
import io
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from pydub import AudioSegment
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Database dependencies and ORM Models
from data.database import get_db
from data.model import Sentence, Word, SentenceHistory, WordHistory

frequency_router = APIRouter(prefix="/frequency", tags=["Sentence Frequency Analyzer"])

WORKSPACE_DIR = os.path.abspath("./project")
GENERATED_DIR = os.path.join(WORKSPACE_DIR, "generated")
SEGMENTS_DIR = os.path.join(GENERATED_DIR, "segments")

os.makedirs(SEGMENTS_DIR, exist_ok=True)

class FrequencyUpdate(BaseModel):
    sentence_id: int  # 💡 Required to isolate paths and database records
    word_index: int
    new_frequency_shift: float 
    
def apply_frequency_pitch_shift(audio_segment: AudioSegment, shift_amount: float) -> AudioSegment:
    """Shifts the core pitch (frequencies) of a word segment."""
    if shift_amount == 0:
        return audio_segment
    new_sample_rate = int(audio_segment.frame_rate * (2.0 ** shift_amount))
    shifted_audio = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_sample_rate})
    return shifted_audio.set_frame_rate(audio_segment.frame_rate)


@frequency_router.post("/update-frequency", status_code=status.HTTP_200_OK)
async def update_frequency(data: FrequencyUpdate, db: AsyncSession = Depends(get_db)):
    """
    Shifts the frequency of a word fragment, re-consolidates the specific track on disk,
    and updates both primary rows and modification histories in PostgreSQL.
    """
    # 1. Fetch matching primary records from PostgreSQL
    sentence_stmt = select(Sentence).where(Sentence.id == data.sentence_id)
    sentence_res = await db.execute(sentence_stmt)
    sentence = sentence_res.scalar_one_or_none()
    
    if not sentence:
        raise HTTPException(status_code=404, detail=f"Sentence ID {data.sentence_id} not found in DB.")

    # 💡 CRUCIAL INTEGRATION FIX: Generate unique paths tied to this specific sentence ID
    dynamic_json_path = os.path.join(GENERATED_DIR, f"metadata_{data.sentence_id}.json")
    dynamic_master_mp3_path = os.path.join(GENERATED_DIR, f"sentence_{data.sentence_id}.mp3")

    # Fallback to legacy file checking if dynamic file generation hasn't fully migrated yet
    active_json_path = dynamic_json_path if os.path.exists(dynamic_json_path) else os.path.join(GENERATED_DIR, "metadata.json")
    
    if not os.path.exists(active_json_path):
        raise HTTPException(status_code=404, detail=f"Project metadata mapping missing on disk for sentence {data.sentence_id}")
        
    with open(active_json_path, "r", encoding="utf-8") as f:
        project_data = json.load(f)
        
    target_word_meta = None
    for word in project_data["words_timeline"]:
        if word["word_index"] == data.word_index:
            target_word_meta = word
            break
            
    if not target_word_meta:
        raise HTTPException(status_code=404, detail=f"Word index {data.word_index} mismatch in project JSON template.")

    # 2. Log Parent Sentence Snapshot to History Table before making edits
    s_hist_stmt = select(SentenceHistory).where(SentenceHistory.sentence_id == sentence.id)
    s_hist_res = await db.execute(s_hist_stmt)
    next_s_version = len(s_hist_res.scalars().all()) + 1

    old_sentence_snapshot = SentenceHistory(
        sentence_id=sentence.id,
        text_content=sentence.text_content,
        audio_bytes=sentence.audio_bytes,
        mp3_file_path=sentence.mp3_file_path,
        original_sentence_json=sentence.original_sentence_json,
        modified_sentence_json=sentence.modified_sentence_json,
        version=next_s_version,
        modified_by="frequency_tweak_engine"
    )
    db.add(old_sentence_snapshot)

    # Apply configuration change to JSON tracking framework memory tree
    target_word_meta["applied_frequency_shift_hz"] = data.new_frequency_shift
    
    consolidated_sentence = AudioSegment.empty()
    
    # 3. Audio Consolidation Loop
    for word_item in project_data["words_timeline"]:
        idx = word_item["word_index"]
        word_wav_path = os.path.join(WORKSPACE_DIR, word_item["segment_file"])
        
        if not os.path.exists(word_wav_path):
            raise HTTPException(status_code=404, detail=f"Missing word fragment file: {word_wav_path}")       
            
        word_audio = AudioSegment.from_wav(word_wav_path)
        modified_word_audio = apply_frequency_pitch_shift(
            word_audio, 
            word_item["applied_frequency_shift_hz"]
        )
        consolidated_sentence += modified_word_audio

        # If this is the specific word being modified, generate its new bytes and log histories
        if idx == data.word_index:
            word_stmt = select(Word).where(Word.sentence_id == sentence.id, Word.word_order == idx)
            word_res = await db.execute(word_stmt)
            live_word = word_res.scalar_one_or_none()
            
            if live_word:
                # Capture Word History snapshot
                w_hist_stmt = select(WordHistory).where(WordHistory.word_id == live_word.id)
                w_hist_res = await db.execute(w_hist_stmt)
                next_w_version = len(w_hist_res.scalars().all()) + 1

                old_word_snapshot = WordHistory(
                    word_id=live_word.id,
                    text_content=live_word.text_content,
                    word_order=live_word.word_order,
                    audio_bytes=live_word.audio_bytes,
                    mp3_file_path=live_word.mp3_file_path,
                    version=next_w_version
                )
                db.add(old_word_snapshot)

                # Export single word memory buffer directly to database column
                word_buffer = io.BytesIO()
                modified_word_audio.export(word_buffer, format="wav")
                live_word.audio_bytes = word_buffer.getvalue()

    # 4. Export Consolidated Output to local drive (Isolated Path)
    consolidated_sentence.export(dynamic_master_mp3_path, format="mp3")
    
    # Package master sentence file buffer for parent row update
    master_buffer = io.BytesIO()
    consolidated_sentence.export(master_buffer, format="mp3")
    
    # Write structural updates out to local JSON file (Isolated Path)
    with open(dynamic_json_path, "w", encoding="utf-8") as f:
        json.dump(project_data, f, indent=4)

    # 5. Synchronize primary parent sentence metrics in PostgreSQL
    sentence.audio_bytes = master_buffer.getvalue()
    sentence.mp3_file_path = f"generated/sentence_{data.sentence_id}.mp3"
    sentence.modified_sentence_json = project_data
    
    return {
        "status": "success", 
        "database_sync": "complete",
        "sentence_id": data.sentence_id,
        "mp3_relative_path": sentence.mp3_file_path,
        "message": f"Successfully shifted frequency of word index {data.word_index} and consolidated assets."
    }
