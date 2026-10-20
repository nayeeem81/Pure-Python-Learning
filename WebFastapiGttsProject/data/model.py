# data/model.py
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Text, LargeBinary, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB  
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Import the Base instance from database.py to maintain the shared metadata loop
from data.database import Base

class Sentence(Base):
    __tablename__ = "sentence"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Structural fields 
    text_content: Mapped[str] = mapped_column(Text, nullable=False)
    audio_bytes: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True) 
    mp3_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    original_sentence_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    modified_sentence_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    modified_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    modified_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships linked properly to the singular table name context
    words: Mapped[List["Word"]] = relationship("Word", back_populates="sentence", cascade="all, delete-orphan")
    history_records: Mapped[List["SentenceHistory"]] = relationship("SentenceHistory", back_populates="sentence", cascade="all, delete-orphan")

class Word(Base):
    __tablename__ = "words"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sentence_id: Mapped[int] = mapped_column(ForeignKey("sentence.id", ondelete="CASCADE"), nullable=False) # 💡 Fixed to 'sentence.id'
    text_content: Mapped[str] = mapped_column(String(100), nullable=False)
    word_order: Mapped[int] = mapped_column(Integer, nullable=False)
    audio_bytes: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    mp3_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Relationships
    sentence: Mapped["Sentence"] = relationship("Sentence", back_populates="words")
    history_records: Mapped[List["WordHistory"]] = relationship("WordHistory", back_populates="word", cascade="all, delete-orphan")

class SentenceHistory(Base):
    __tablename__ = "sentence_history"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sentence_id: Mapped[int] = mapped_column(ForeignKey("sentence.id", ondelete="CASCADE"), nullable=False) # 💡 Fixed to 'sentence.id'
    text_content: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    # Relationships
    sentence: Mapped["Sentence"] = relationship("Sentence", back_populates="history_records")

class WordHistory(Base):
    __tablename__ = "word_history"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id", ondelete="CASCADE"), nullable=False)
    text_content: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    # Relationships
    word: Mapped["Word"] = relationship("Word", back_populates="history_records")
