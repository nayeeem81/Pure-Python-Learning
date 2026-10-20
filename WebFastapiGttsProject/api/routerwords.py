# api/routerwords.py
import os
import json
import re
from io import BytesIO
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from pydub import AudioSegment
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Database dependencies and ORM Models
from data.database import get_db
from data.model import Sentence, Word, SentenceHistory, WordHistory

router_words = APIRouter(prefix="/words", tags=["Word Frequency & Amplitude Customizer"])

WORKSPACE_DIR = os.path.abspath("./project")
GENERATED_DIR = os.path.join(WORKSPACE_DIR, "generated")

class WordAdjustment(BaseModel):
    word_index: int
    pitch_shift: float  # Represented in octaves/semitones
    volume_db: float    # Represented in Decibels adjustment (+/- dB)

class ConsolidateRequest(BaseModel):
    sentence_id: int    # Linked to relational primary keys
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

@router_words.post("/parse/{sentence_id}", status_code=status.HTTP_201_CREATED)
async def parse_sentence_into_words(sentence_id: int, db: AsyncSession = Depends(get_db)):
    """
    Finds a sentence, parses its string into clean sequential words,
    and saves them to the 'words' table mapped to their exact chronological order index.
    """
    try:
        stmt = select(Sentence).where(Sentence.id == sentence_id)
        result = await db.execute(stmt)
        sentence = result.scalar_one_or_none()
        
        if not sentence:
            raise HTTPException(status_code=404, detail=f"Sentence ID {sentence_id} not found.")

        # Clear out any existing parsed words for this sentence to prevent duplicates
        clear_stmt = select(Word).where(Word.sentence_id == sentence_id)
        clear_res = await db.execute(clear_stmt)
        existing_words = clear_res.scalars().all()
        for w in existing_words:
            await db.delete(w)

        raw_tokens = re.findall(r'\b\w+\b', sentence.text_content)
        if not raw_tokens:
            raise HTTPException(status_code=400, detail="Sentence string contains no parseable words.")

        new_words = []
        for index, token in enumerate(raw_tokens, start=1):
            word_item = Word(
                sentence_id=sentence.id,
                text_content=token,
                word_order=index,
                audio_bytes=None,  
                mp3_file_path=None 
            )
            new_words.append(word_item)
        
        db.add_all(new_words)
        await db.commit() # Ensure commits save word allocations safely
        return {"message": f"Successfully compiled {len(new_words)} words for Sentence #{sentence_id}."}

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while parsing the text layout: {str(e)}"
        )

# --- 2. UPDATED AUDIO PROCESSING & DATABASE INTEGRATION ENGINE ---
@router_words.post("/consolidate-modifications")
async def consolidate_modifications(payload: ConsolidateRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Fetch targeting parent sentence from database context
        sentence_stmt = select(Sentence).where(Sentence.id == payload.sentence_id)
        sentence_res = await db.execute(sentence_stmt)
        sentence = sentence_res.scalar_one_or_none()
        
        if not sentence:
            raise HTTPException(status_code=404, detail=f"Sentence ID {payload.sentence_id} missing in DB.")

        # Target the unique dynamic sentence JSON file instead of global metadata.json
        dynamic_json_path = os.path.join(GENERATED_DIR, f"metadata_{payload.sentence_id}.json")
        if not os.path.exists(dynamic_json_path):
            raise HTTPException(status_code=404, detail=f"Original analysis metadata map missing for sentence {payload.sentence_id}")

        with open(dynamic_json_path, "r", encoding="utf-8") as f:
            original_data = json.load(f)

        adj_map = {item.word_index: item for item in payload.adjustments}
        modified_timeline = []
        consolidated_track = AudioSegment.empty()

        # --- ARCHIVE RUN: SAVE HISTORICAL SNAPSHOT BEFORE MODIFICATION ---
        sentence_hist_stmt = select(SentenceHistory).where(SentenceHistory.sentence_id == sentence.id)
        s_hist_res = await db.execute(sentence_hist_stmt)
        next_s_version = len(s_hist_res.scalars().all()) + 1

        # 💡 FIX: Removed fields that were causing mapping crashes since they don't exist in SentenceHistory
        old_sentence_snapshot = SentenceHistory(
            sentence_id=sentence.id,
            text_content=sentence.text_content,
            version=next_s_version
        )
        db.add(old_sentence_snapshot)

        # Ensure individual word target folders exist safely
        segments_dir = os.path.join(WORKSPACE_DIR, "generated", "segments")
        os.makedirs(segments_dir, exist_ok=True)

        # --- CONSOLIDATION LOOP ---
        for word_meta in original_data["words_timeline"]:
            idx = word_meta["word_index"]
            word_wav_path = os.path.join(WORKSPACE_DIR, word_meta["segment_file"])
            
            if not os.path.exists(word_wav_path):
                raise HTTPException(status_code=404, detail=f"Fragment missing: {word_wav_path}")
                
            raw_word_audio = AudioSegment.from_wav(word_wav_path)
            
            pitch_val = adj_map[idx].pitch_shift if idx in adj_map else 0.0
            volume_val = adj_map[idx].volume_db if idx in adj_map else 0.0
            
            processed_word_audio = apply_dsp_tweaks(raw_word_audio, pitch_val, volume_val)
            consolidated_track += processed_word_audio
            
            # Build raw binary outputs for individual database records
            word_buffer = BytesIO()
            processed_word_audio.export(word_buffer, format="wav")
            word_raw_bytes = word_buffer.getvalue()

            # Update specific child word entries in database or archive if modified
            word_stmt = select(Word).where(Word.sentence_id == sentence.id, Word.word_order == idx)
            word_res = await db.execute(word_stmt)
            live_word = word_res.scalar_one_or_none()
            
            if live_word:
                # Archive old word configuration fields before rewriting
                word_hist_stmt = select(WordHistory).where(WordHistory.word_id == live_word.id)
                w_hist_res = await db.execute(word_hist_stmt)
                next_w_version = len(w_hist_res.scalars().all()) + 1

                # 💡 FIX: Matches exact WordHistory schema properties from model.py safely
                old_word_snapshot = WordHistory(
                    word_id=live_word.id,
                    text_content=live_word.text_content,
                    version=next_w_version
                )
                db.add(old_word_snapshot)

                # Assign new operational metrics to live table record row
                live_word.audio_bytes = word_raw_bytes
                live_word.mp3_file_path = f"generated/segments/word_{idx:03d}_mod.wav"

                # Export modified segment file back out to local drive
                word_absolute_path = os.path.join(WORKSPACE_DIR, live_word.mp3_file_path)
                processed_word_audio.export(word_absolute_path, format="wav")

            # Footprint logging adjustments for JSON configuration mappings
            modified_word_entry = word_meta.copy()
            modified_word_entry["applied_frequency_shift_hz"] = pitch_val
            modified_word_entry["applied_amplitude_db"] = volume_val
            modified_timeline.append(modified_word_entry)

        # 💡 FIX: Completed the missing file export and data persistence block here
        dynamic_mp3_path = os.path.join(GENERATED_DIR, f"sentence_{payload.sentence_id}.mp3")
        consolidated_track.export(dynamic_mp3_path, format="mp3")

        # Build raw binary memory segment bytes for parent model updates
        sentence_buffer = BytesIO()
        consolidated_track.export(sentence_buffer, format="mp3")
        
        # Update main operational tracking values inside your parent Sentence table context
        sentence.audio_bytes = sentence_buffer.getvalue()
        sentence.version += 1
        sentence.modified_sentence_json = {"words_timeline": modified_timeline}

        # Write fresh updated JSON metadata back out to disk map configs securely
        with open(dynamic_json_path, "w", encoding="utf-8") as f:
            json.dump({"words_timeline": modified_timeline}, f, indent=4, ensure_ascii=False)

        # Save all transaction changes to PostgreSQL database instances safely
        await db.commit()
        return {"status": "success", "message": f"Sentence ID {payload.sentence_id} consolidated and updated successfully."}

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database transaction operations returned error statuses: {str(e)}"
        )
