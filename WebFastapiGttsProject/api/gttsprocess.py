import os
import json
import traceback
from io import BytesIO
from gtts import gTTS
from pydub import AudioSegment
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

# Database connections
from data.database import get_db, async_session
from data.model import Sentence, Word

router_gttsprocess = APIRouter(prefix="/process", tags=["Gtts Processor"]) 

# ==========================================================================
# D: DRIVE DECOUPLED STORAGE CORE INITIALIZATION
# ==========================================================================
STORAGE_ROOT = "D:\\StudioStorage"
GENERATED_DIR = os.path.join(STORAGE_ROOT, "generated")
SEGMENTS_BASE_DIR = os.path.join(GENERATED_DIR, "segments")

os.makedirs(GENERATED_DIR, exist_ok=True)
os.makedirs(SEGMENTS_BASE_DIR, exist_ok=True)

class TTSRequest(BaseModel):
    text: str

import os
import json
import traceback
from io import BytesIO
from gtts import gTTS
from pydub import AudioSegment
from sqlmodel import select

# Database connections
from data.database import async_session
from data.model import Sentence, Word

async def generate_tts_and_metadata_task(sentence_id: int, text: str):
    """
    🛠️ AUTO-HEALING WORKER: Compiles TTS audio tracks, saves physical assets to D drive,
    and commits sentence and word metadata structures cleanly without transaction lockups.
    """
    try:
        # Define D Drive Absolute Execution Targets
        STORAGE_ROOT = "D:\\StudioStorage"
        GENERATED_DIR = os.path.join(STORAGE_ROOT, "generated")
        SEGMENTS_BASE_DIR = os.path.join(GENERATED_DIR, "segments")
        
        absolute_mp3_path = os.path.normpath(os.path.join(GENERATED_DIR, f"sentence_{sentence_id}.mp3"))
        absolute_json_path = os.path.normpath(os.path.join(GENERATED_DIR, f"metadata_{sentence_id}.json"))
        sentence_segments_dir = os.path.join(SEGMENTS_BASE_DIR, f"sentence_{sentence_id}")
        
        os.makedirs(sentence_segments_dir, exist_ok=True)

        # 1. Download full sentence track off Google TTS engine node
        tts = gTTS(text=text, lang='en')
        tts.save(absolute_mp3_path)
        
        # 2. Slice into sub-words (Using PyDub)
        sound = AudioSegment.from_mp3(absolute_mp3_path)
        words = text.split()
        
        total_duration = sound.duration_seconds
        duration_per_word = total_duration / len(words) if words else 0
        
        words_timeline = []
        current_time = 0.0
        
        with open(absolute_mp3_path, "rb") as audio_file:
            master_mp3_bytes = audio_file.read()
            
        # Open fresh isolated async session tracker
        async with async_session() as session:
            # Query parent sentence row object out of PostgreSQL container safely
            stmt = select(Sentence).where(Sentence.id == sentence_id)
            res = await session.execute(stmt)
            sentence_row = res.scalars().first()
            
            if not sentence_row:
                print(f"❌ Background Error: Sentence ID {sentence_id} not found in DB.")
                return

            # Loop through individual text assets to provision structural word instances
            for idx, word in enumerate(words, start=1):
                start_ms = int(current_time * 1000)
                end_ms = int((current_time + duration_per_word) * 1000)
                
                word_segment = sound[start_ms:end_ms]
                
                clean_word = "".join(c for c in word if c.isalnum()).lower()
                segment_filename = f"word_{idx:03d}_{clean_word}.wav"
                
                # Assign fully qualified absolute paths directly on system storage drive partition
                word_absolute_path = os.path.normpath(os.path.join(sentence_segments_dir, segment_filename))
                word_segment.export(word_absolute_path, format="wav")
                
                word_buffer = BytesIO()
                word_segment.export(word_buffer, format="wav")
                word_raw_bytes = word_buffer.getvalue()

                # 💡 ENHANCEMENT: Provision child Word logs safely bound to parent ID key parameters
                db_word = Word(
                    sentence_id=sentence_id,
                    text_content=word,
                    word_order=idx,
                    audio_bytes=word_raw_bytes,
                    mp3_file_path=word_absolute_path
                )
                session.add(db_word)
                
                words_timeline.append({
                    "word_index": idx,
                    "text": word,
                    "start_time": round(current_time, 2),
                    "end_time": round(current_time + duration_per_word, 2),
                    "segment_file": word_absolute_path,
                    "applied_frequency_shift_hz": 0.0,
                    "applied_amplitude_db": 0.0
                })
                current_time += duration_per_word

            # Compile layout tracking blueprint metadata dictionaries
            project_data = {
                "original_sentence": text,
                "master_mp3_path": absolute_mp3_path,
                "total_duration_seconds": round(total_duration, 2),
                "words_timeline": words_timeline
            }
            
            # Export blueprint configuration file straight onto disk drive space
            with open(absolute_json_path, "w", encoding="utf-8") as f:
                json.dump(project_data, f, indent=4)
                
            # Assign values back to model tracking fields securely
            sentence_row.audio_bytes = master_mp3_bytes
            sentence_row.mp3_file_path = absolute_mp3_path
            sentence_row.original_sentence_json = project_data
            
            # Flush changes locally inside the transactional frame context before firing commit triggers
            await session.flush()
            
            # Fire final processing commit tracking command
            await session.commit()
            print(f"✅ Transaction settled successfully! Row entries and absolute file assets initialized for ID #{sentence_id}")
        
    except Exception as e:
        print(f"❌ Core background compilation crash details: {str(e)}")
        traceback.print_exc()

@router_gttsprocess.post("/generate-speech-processing", status_code=status.HTTP_201_CREATED)
async def generate_speech(payload: TTSRequest, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """
    Receives sentence text, provisions primary database row entry instantly, 
    hands off generation workloads over to background tasks loops, and cleanly returns data properties.
    """
    try:
        new_sentence = Sentence(
            text_content=payload.text,
            audio_bytes=None,  
            mp3_file_path=None,
            original_sentence_json=None,
            modified_sentence_json=None
        )
        db.add(new_sentence)
        
        # 💡 FIX: Flush to calculate and populate the auto-increment ID field right away
        await db.flush()
        
        # 💡 FIX: Immediately read the integer value into a isolated local Python variable
        sentence_id = int(new_sentence.id)
        
        # Commit the transaction safely while keeping our local variable intact
        await db.commit()
        
        # Pass the plain, stable integer variable over to our background worker task thread safely
        background_tasks.add_task(generate_tts_and_metadata_task, sentence_id, payload.text)
        
        # 🛠️ FIXED: Aligned the expected path strings to return the precise absolute paths on the D Drive
        return {
            "status": "processing",
            "sentence_id": sentence_id,  
            "message": "Speech tracking record provisioned. Core asset engine initialized in background.",
            "expected_paths": {
                "audio": os.path.normpath(os.path.join(GENERATED_DIR, f"sentence_{sentence_id}.mp3")),
                "json": os.path.normpath(os.path.join(GENERATED_DIR, f"metadata_{sentence_id}.json"))
            }
        }
    except Exception as e:
        await db.rollback()
        print(f"❌ Route Crash Error Details: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database initialization failure: {str(e)}")
