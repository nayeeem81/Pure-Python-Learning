# api/process.py
import os
import json
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, status
from pydantic import BaseModel
from gtts import gTTS
from pydub import AudioSegment
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Database dependencies and ORM Models
from data.database import get_db
from data.model import Sentence, Word

# ALWAYS DECLARE THE ROUTER FIRST AT THE TOP
process_router = APIRouter(prefix="/process", tags=["TTS Processor"]) 

WORKSPACE_DIR = os.path.abspath("./project")
GENERATED_DIR = os.path.join(WORKSPACE_DIR, "generated")
SEGMENTS_DIR = os.path.join(GENERATED_DIR, "segments")

# Auto-ensure directories exist on startup
os.makedirs(SEGMENTS_DIR, exist_ok=True)


class TTSRequest(BaseModel):
    text: str


async def generate_tts_and_metadata_task(sentence_id: int, text: str):
    """
    Background worker that downloads the speech file from Google TTS,
    segments it into words, compiles the project map file, and synchronizes database fields.
    """
    # Since this runs inside an unmanaged background thread task context, 
    # we open an isolated context session dynamically to execute database writes.
    from data.database import async_session
    
    try:
        # 💡 FIX 1: Generate dynamic paths securely inside the function context
        dynamic_mp3_path = os.path.join(GENERATED_DIR, f"sentence_{sentence_id}.mp3")
        dynamic_json_path = os.path.join(GENERATED_DIR, f"metadata_{sentence_id}.json")
        
        # 1. Download and save full sentence via gTTS using the dynamic path
        tts = gTTS(text=text, lang='en')
        tts.save(dynamic_mp3_path)
        
        # 2. Slice into words for editing (Using PyDub)
        sound = AudioSegment.from_mp3(dynamic_mp3_path)
        words = text.split()
        
        # Calculate duration footprints
        total_duration = sound.duration_seconds
        duration_per_word = total_duration / len(words) if words else 0
        
        words_timeline = []
        current_time = 0.0
        
        # Read the newly compiled MP3 file back as raw binary data for database persistence
        with open(dynamic_mp3_path, "rb") as audio_file:
            master_mp3_bytes = audio_file.read()
            
        async with async_session() as session:
            # Fetch the parent row created by the route endpoint
            stmt = select(Sentence).where(Sentence.id == sentence_id)
            res = await session.execute(stmt)
            sentence_row = res.scalar_one_or_none()
            
            if not sentence_row:
                print(f"❌ Background Error: Sentence ID {sentence_id} not found in DB.")
                return

            for idx, word in enumerate(words, start=1):
                start_ms = int(current_time * 1000)
                end_ms = int((current_time + duration_per_word) * 1000)
                
                # Isolate the segment chunk
                word_segment = sound[start_ms:end_ms]
                
                # Form clean strings for storage mapping keys
                clean_word = "".join(c for c in word if c.isalnum()).lower()
                segment_filename = f"word_{idx:03d}_{clean_word}.wav"
                
                segment_relative_path = f"generated/segments/{segment_filename}"
                segment_absolute_path = os.path.join(SEGMENTS_DIR, segment_filename)
                
                # Save lossless chunk to local drive
                word_segment.export(segment_absolute_path, format="wav")
                
                # Extract word segment audio raw data as a byte stream array
                from io import BytesIO
                word_buffer = BytesIO()
                word_segment.export(word_buffer, format="wav")
                word_raw_bytes = word_buffer.getvalue()

                # DB WRITE: Populate the relational 'words' table rows synchronously
                db_word = Word(
                    sentence_id=sentence_id,
                    text_content=word,
                    word_order=idx,
                    audio_bytes=word_raw_bytes,
                    mp3_file_path=segment_relative_path
                )
                session.add(db_word)
                
                # Add to JSON sequence map array for disk file tracking
                words_timeline.append({
                    "word_index": idx,
                    "text": word,
                    "start_time": round(current_time, 2),
                    "end_time": round(current_time + duration_per_word, 2),
                    "segment_file": segment_relative_path,
                    "applied_frequency_shift_hz": 0.0,
                    "applied_amplitude_db": 0.0
                })
                
                current_time += duration_per_word

            # 3. Output structural config map profile onto hard drive
            project_data = {
                "original_sentence": text,
                "master_mp3_path": f"generated/sentence_{sentence_id}.mp3",
                "total_duration_seconds": round(total_duration, 2),
                "words_timeline": words_timeline
            }
            
            with open(dynamic_json_path, "w", encoding="utf-8") as f:
                json.dump(project_data, f, indent=4)
                
            # Update parent fields with metadata mapping definitions
            sentence_row.audio_bytes = master_mp3_bytes
            sentence_row.mp3_file_path = f"generated/sentence_{sentence_id}.mp3"
            sentence_row.original_sentence_json = project_data
            
            await session.commit()
            print(f"✅ Successfully compiled & synchronized assets for Sentence ID #{sentence_id}: '{text}'")
        
    except Exception as e:
        print(f"❌ Error compiling background audio tasks: {str(e)}")

# Inside api/process.py
@process_router.post("/generate-speech-processing", status_code=status.HTTP_201_CREATED)
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
        
        # 💡 FIX: Change 'await db.flush()' to 'await db.commit()'
        # This pushes the record permanently out of the sandbox transaction into the real database right now!
        await db.commit()
        
        # Capture the newly verified identity primary key safely
        sentence_id = new_sentence.id
        
        # Pass work over to background task routine loop safely
        background_tasks.add_task(generate_tts_and_metadata_task, sentence_id, payload.text)
        
        return {
            "status": "processing",
            "sentence_id": sentence_id,  
            "message": "Speech tracking record provisioned. Core asset engine initialized in background.",
            "expected_paths": {
                "audio": f"generated/sentence_{sentence_id}.mp3",
                "json": f"generated/metadata_{sentence_id}.json"
            }
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database initialization failure: {str(e)}")
