# api/routerwords.py

# 1. Standard Library Imports
from datetime import datetime, timezone  
from io import BytesIO
import json
import os
import re
from typing import List, Optional

# 2. Third-Party Imports
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from pydub import AudioSegment
from sqlmodel import select  # 💡 Import select from sqlmodel uniformly to keep driver calls safe
from sqlmodel.ext.asyncio.session import AsyncSession

# 3. Local Application Imports (Database dependencies and ORM Models)
from data.database import get_db
from data.model import Sentence, SentenceHistory, Word, WordHistory

router_gttsword = APIRouter(prefix="/words", tags=["Word Frequency & Amplitude Customizer"])

# 💡 MATCHED: Utilizing your exact pre-declared Pydantic schema structures
class WordAdjustment(BaseModel):
    word_index: int
    pitch_shift: float  # Represented in octaves/semitones
    volume_db: float    # Represented in Decibels adjustment (+/- dB)

class ConsolidateRequest(BaseModel):
    sentence_id: int    # Linked to relational primary keys
    adjustments: List[WordAdjustment]

# ==========================================================================
# UNIFIED DECOUPLED STORAGE VARIABLES FOR D: DRIVE PARAMS
# ==========================================================================
STORAGE_ROOT = "D:\\StudioStorage"
GENERATED_DIR = os.path.normpath(os.path.join(STORAGE_ROOT, "generated"))
SEGMENTS_BASE_DIR = os.path.normpath(os.path.join(GENERATED_DIR, "segments"))

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

@router_gttsword.post("/parse/{sentence_id}", status_code=status.HTTP_201_CREATED)
async def parse_sentence_into_words(sentence_id: int, db: AsyncSession = Depends(get_db)):
    """
    Finds a sentence, parses its string into clean sequential words,
    and saves them to the 'words' table mapped to their exact chronological order index.
    """
    try:
        stmt = select(Sentence).where(Sentence.id == sentence_id)
        result = await db.exec(stmt)
        sentence = result.one_or_none() 
        
        if not sentence:
            raise HTTPException(status_code=404, detail=f"Sentence ID {sentence_id} not found.")

        # Clear out any existing parsed words for this sentence to prevent duplicates
        clear_stmt = select(Word).where(Word.sentence_id == sentence_id)
        clear_res = await db.exec(clear_stmt)
        existing_words = clear_res.all()
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
        await db.commit() 
        return {"message": f"Successfully compiled {len(new_words)} words for Sentence #{sentence_id}."}

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while parsing the text layout: {str(e)}"
        )


@router_gttsword.post("/consolidate-modifications")
async def consolidate_modifications(payload: ConsolidateRequest, db: AsyncSession = Depends(get_db)):
    """
    🛠️ OPTIMIZED DSP ENGINE: Reads raw word fragments right off the D: Drive storage volume,
    applies real-time pitch/volume modifiers, archives snapshots, and flushes database changes cleanly.
    """
    try:
        # Fetch targeting parent sentence from database context
        sentence_stmt = select(Sentence).where(Sentence.id == payload.sentence_id)
        sentence_res = await db.execute(sentence_stmt)  
        sentence = sentence_res.scalars().first()  
        
        if not sentence:
            raise HTTPException(status_code=404, detail=f"Sentence ID {payload.sentence_id} missing in DB.")

        # Resolve strict absolute D: Drive tracking strings
        dynamic_json_path = os.path.normpath(os.path.join(GENERATED_DIR, f"metadata_{payload.sentence_id}.json"))
        dynamic_master_mp3_path = os.path.normpath(os.path.join(GENERATED_DIR, f"sentence_{payload.sentence_id}.mp3"))
        sentence_segments_dir = os.path.normpath(os.path.join(SEGMENTS_BASE_DIR, f"sentence_{payload.sentence_id}"))
        
        if not os.path.exists(dynamic_json_path):
            raise HTTPException(status_code=404, detail=f"Original analysis metadata map missing for sentence {payload.sentence_id}")

        with open(dynamic_json_path, "r", encoding="utf-8") as f:
            original_data = json.load(f)

        # 🛠️ ALIGNED DICTIONARY MAP: Safely maps WordAdjustment models
        adj_map = {item.word_index: item for item in payload.adjustments}
        modified_timeline = []
        consolidated_track = AudioSegment.empty()

        # --- ARCHIVE RUN: SAVE HISTORICAL SNAPSHOT BEFORE MODIFICATION ---
        sentence_hist_stmt = select(SentenceHistory).where(SentenceHistory.sentence_id == sentence.id)
        s_hist_res = await db.execute(sentence_hist_stmt)  
        next_s_version = len(s_hist_res.scalars().all()) + 1

        old_sentence_snapshot = SentenceHistory(
            sentence_id=sentence.id,
            text_content=sentence.text_content,
            version=next_s_version
        )
        db.add(old_sentence_snapshot)

        # --- CONSOLIDATION LOOP ---
        for word_meta in original_data["words_timeline"]:
            idx = word_meta["word_index"]
            
            # Target path parsed directly from the database string layer
            word_wav_path = os.path.normpath(word_meta["segment_file"])
            
            if not os.path.exists(word_wav_path):
                raise HTTPException(status_code=404, detail=f"Fragment missing at location: {word_wav_path}")
                
            raw_word_audio = AudioSegment.from_wav(word_wav_path)
            
            # Read alignment numbers from the WordAdjustment parameter map
            pitch_val = adj_map[idx].pitch_shift if idx in adj_map else 0.0
            volume_val = adj_map[idx].volume_db if idx in adj_map else 0.0
            
            # Execute your custom DSP frequency/amplitude modifiers
            processed_word_audio = apply_dsp_tweaks(raw_word_audio, pitch_val, volume_val)
            consolidated_track += processed_word_audio
            
            word_buffer = BytesIO()
            processed_word_audio.export(word_buffer, format="wav")
            word_raw_bytes = word_buffer.getvalue()

            # Query matching Word entry to update its values
            word_stmt = select(Word).where(Word.sentence_id == sentence.id, Word.word_order == idx)
            word_res = await db.execute(word_stmt)
            live_word = word_res.scalars().first()

            if live_word:
                # Track and archive historical modification state profiles
                word_hist_stmt = select(WordHistory).where(WordHistory.word_id == live_word.id)
                w_hist_res = await db.execute(word_hist_stmt)  
                next_w_version = len(w_hist_res.scalars().all()) + 1

                old_word_snapshot = WordHistory(
                    word_id=live_word.id,
                    text_content=live_word.text_content,
                    version=next_w_version
                )
                db.add(old_word_snapshot)

                # Overwrites the target modified word file inside sentence directory on D: Drive
                word_mod_filename = f"word_{idx:03d}_mod.wav"
                word_absolute_mod_path = os.path.normpath(os.path.join(sentence_segments_dir, word_mod_filename))
                
                processed_word_audio.export(word_absolute_mod_path, format="wav")

                # Map data columns accurately
                live_word.audio_bytes = word_raw_bytes
                live_word.mp3_file_path = word_absolute_mod_path  

            # Footprint logging adjustments for JSON configuration mappings
            modified_word_entry = word_meta.copy()
            modified_word_entry["applied_frequency_shift_hz"] = pitch_val
            modified_word_entry["applied_amplitude_db"] = volume_val
            modified_word_entry["segment_file"] = live_word.mp3_file_path if live_word else word_meta["segment_file"]
            modified_timeline.append(modified_word_entry)

        # Complete file writers and commit layout tree elements safely
        original_data["words_timeline"] = modified_timeline
        with open(dynamic_json_path, "w", encoding="utf-8") as f:
            json.dump(original_data, f, indent=4)

        # Export completed soundscape track out to D: Drive storage volume
        consolidated_track.export(dynamic_master_mp3_path, format="mp3")
        master_buffer = BytesIO()
        consolidated_track.export(master_buffer, format="mp3")

        # Sync changes back down onto PostgreSQL tables
        sentence.audio_bytes = master_buffer.getvalue()
        sentence.modified_sentence_json = original_data
        
        # Bind timezone-aware clock wrapper to clear value errors
        sentence.modified_at = datetime.now(timezone.utc)
        sentence.version += 1

        await db.commit()
        
        return {
            "status": "success",
            "code": status.HTTP_200_OK,
            "message": "DSP pipeline rendering complete. Database synchronized successfully.",
            "data": {
                "sentence_id": payload.sentence_id,
                "version": sentence.version,
                "total_words_processed": len(modified_timeline),
                "modified_at": sentence.modified_at.isoformat(),
                "assets": {
                    "master_mp3": f"generated/sentence_{payload.sentence_id}.mp3",
                    "metadata_json": f"generated/metadata_{payload.sentence_id}.json"
                }
            }
        }

    except Exception as e:
        await db.rollback()
        print(f"❌ Consolidation Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Database transaction operations failure: {str(e)}"
        )
