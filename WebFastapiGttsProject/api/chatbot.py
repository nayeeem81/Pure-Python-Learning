import os
import uuid
from typing import Optional
from fastapi import APIRouter, Request, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import Session, select
from google import genai
from google.genai import types
from gtts import gTTS

from data.database import get_db
from data.model import ChatSession, ChatMessage  
from config import config

router_chatbot = APIRouter(prefix="/chat", tags=["Chatbot"])

print("DEBUG GEMINI KEY:", repr(config.GEMINI_API_KEY))
GEMINI_API_KEY = (os.getenv("GEMINI_API_KEY") or "AIzaSy...your_39_char_key...").strip()

gemini_client = genai.Client(api_key=config.GEMINI_API_KEY)

CHAT_DIR = config.CHAT_AUDIO_DIR
os.makedirs(CHAT_DIR, exist_ok=True)


# 1. Make helper async and await db calls
async def get_or_create_session_record(request: Request, db: AsyncSession) -> ChatSession:
	session_token = request.session.get("chat_session_token")

	if session_token:
		statement = select(ChatSession).where(ChatSession.session_token == session_token)
		result = await db.exec(statement)
		existing_session = result.first()
		if existing_session:
			return existing_session

	new_token = str(uuid.uuid4())
	request.session["chat_session_token"] = new_token

	new_session = ChatSession(session_token=new_token)
	db.add(new_session)
	await db.commit()
	await db.refresh(new_session)
	return new_session


@router_chatbot.post("/send")
async def send_and_save_chat(
	request: Request,
	text: Optional[str] = Form(None),
	audio: Optional[UploadFile] = File(None),
	want_audio_reply: bool = Form(True),
	db: AsyncSession = Depends(get_db)
):
	if not text and not audio:
		raise HTTPException(status_code=400, detail="Provide text or an audio file.")

	# 2. Await the async helper
	chat_session = await get_or_create_session_record(request, db)

	# 3. Await db.exec() before calling .all()
	history_stmt = (
		select(ChatMessage)
		.where(ChatMessage.session_id == chat_session.id)
		.order_by(ChatMessage.created_at.asc())
	)
	history_result = await db.exec(history_stmt)
	past_messages = history_result.all()

	gemini_contents = [
		types.Content(
			role=msg.role,
			parts=[types.Part.from_text(text=msg.content)]
		)
		for msg in past_messages
	]

	if audio:
		audio_bytes = await audio.read()
		mime_type = audio.content_type or "audio/webm"
		gemini_contents.append(
			types.Content(
				role="user",
				parts=[
					types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
					types.Part.from_text(text="Listen to this voice message and reply clearly in English.")
				]
			)
		)
		user_saved_text = "🎤 [Voice Message]"
	else:
		gemini_contents.append(
			types.Content(
				role="user",
				parts=[types.Part.from_text(text=text)]
			)
		)
		user_saved_text = text.strip()

	try:
		response = gemini_client.models.generate_content(
			model="gemini-3.8-flash",
			contents=gemini_contents,
			config=types.GenerateContentConfig(
				system_instruction="You are a helpful, concise assistant speaking English."
			)
		)
		bot_reply_text = response.text.strip()
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")

	audio_url = None
	if want_audio_reply:
		audio_filename = f"tts_{uuid.uuid4()}.mp3"
		mp3_path = config.CHAT_AUDIO_DIR / audio_filename

		# 1. Save the MP3 file to your D:\StudioStorage\chat_audio folder
		tts = gTTS(text=bot_reply_text, lang="en")
		tts.save(str(mp3_path))

		# 2. Return the HTTP endpoint URL (NEVER the D:\ local file path!)
		audio_url = f"/api/chat/audio/{audio_filename}"

	# 4. Await commit, refresh, and rollback
	try:
		user_record = ChatMessage(
			session_id=chat_session.id,
			role="user",
			content=user_saved_text
		)
		bot_record = ChatMessage(
			session_id=chat_session.id,
			role="model",
			content=bot_reply_text
		)

		db.add(user_record)
		db.add(bot_record)
		await db.commit()
		await db.refresh(user_record)
		await db.refresh(bot_record)
	except Exception as e:
		await db.rollback()
		raise HTTPException(status_code=500, detail=f"Database save failed: {str(e)}")

	return {
		"session_id": chat_session.id,
		"user_message": {
			"id": user_record.id,
			"role": user_record.role,
			"content": user_record.content
		},
		"bot_message": {
			"id": bot_record.id,
			"role": bot_record.role,
			"content": bot_record.content,
			"audio_url": audio_url
		}
	}


@router_chatbot.get("/history")
async def get_saved_chat_history(request: Request, db: AsyncSession = Depends(get_db)):
	chat_session = await get_or_create_session_record(request, db)
	statement = (
		select(ChatMessage)
		.where(ChatMessage.session_id == chat_session.id)
		.order_by(ChatMessage.created_at.asc())
	)
	# 5. Await db.exec() here as well
	result = await db.exec(statement)
	records = result.all()

	return [
		{
			"id": r.id,
			"role": r.role,
			"content": r.content,
			"created_at": r.created_at.isoformat()
		}
		for r in records
	]


@router_chatbot.get("/audio/{filename}")
async def serve_chat_audio(filename: str):
	file_path = config.CHAT_AUDIO_DIR / filename
	if not file_path.exists():
		raise HTTPException(status_code=404, detail="Audio file not found.")
	return FileResponse(file_path, media_type="audio/mpeg")

