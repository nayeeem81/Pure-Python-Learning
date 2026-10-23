# data/model.py
from datetime import datetime, timezone  # 💡 Added timezone import
from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import String, Text, LargeBinary, Column
from sqlalchemy.dialects.postgresql import JSONB  

# =====================================================================
# 1. SENTENCE MODEL
# =====================================================================
class Sentence(SQLModel, table=True): 
    __tablename__ = "sentence"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Text content mapped to PostgreSQL long Text type
    text_content: str = Field(sa_column=Column(Text, nullable=False))
    
    # Binary media and paths
    audio_bytes: Optional[bytes] = Field(default=None, sa_column=Column(LargeBinary, nullable=True)) 
    mp3_file_path: Optional[str] = Field(default=None, sa_column=Column(String(500), nullable=True))
    
    # Complex JSON trees mapped using native PostgreSQL JSONB columns
    original_sentence_json: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    modified_sentence_json: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    
    # Tracking parameters
    version: int = Field(default=1)
    
    # 💡 FIX: Force timezone tracking into the default factory loop to clear the ValueError
    modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    modified_by: Optional[str] = Field(default=None, max_length=100)

    # Relationships linked seamlessly across tables
    words: List["Word"] = Relationship(back_populates="sentence", cascade_delete=True)
    history_records: List["SentenceHistory"] = Relationship(back_populates="sentence", cascade_delete=True)


# =====================================================================
# 2. WORD MODEL (Verified & Unchanged)
# =====================================================================
class Word(SQLModel, table=True):
    __tablename__ = "words"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    sentence_id: int = Field(foreign_key="sentence.id", ondelete="CASCADE")
    
    text_content: str = Field(max_length=100, nullable=False)
    word_order: int = Field(nullable=False)
    audio_bytes: Optional[bytes] = Field(default=None, sa_column=Column(LargeBinary, nullable=True))
    mp3_file_path: Optional[str] = Field(default=None, sa_column=Column(String(500), nullable=True))
    
    # Relationships
    sentence: "Sentence" = Relationship(back_populates="words")
    history_records: List["WordHistory"] = Relationship(back_populates="word", cascade_delete=True)


# =====================================================================
# 3. SENTENCE HISTORY MODEL
# =====================================================================
class SentenceHistory(SQLModel, table=True):
    __tablename__ = "sentence_history"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    sentence_id: int = Field(foreign_key="sentence.id", ondelete="CASCADE")
    text_content: str = Field(sa_column=Column(Text, nullable=False))
    version: int = Field(default=1)
    
    # Relationships
    sentence: "Sentence" = Relationship(back_populates="history_records")


# =====================================================================
# 4. WORD HISTORY MODEL
# =====================================================================
class WordHistory(SQLModel, table=True):
    __tablename__ = "word_history"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    word_id: int = Field(foreign_key="words.id", ondelete="CASCADE")
    text_content: str = Field(max_length=100, nullable=False)
    version: int = Field(default=1)
    
    # Relationships
    word: "Word" = Relationship(back_populates="history_records")
