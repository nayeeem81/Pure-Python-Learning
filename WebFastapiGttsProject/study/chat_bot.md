To build a multi-modal chatbot supporting Text/Voice input and Text/Audio output, the best approach is a 3-stage pipeline (STT → LLM → TTS) integrated into your existing FastAPI + Vanilla JS stack. Since you are already building a FastAPI project (WebFastapiGttsProject), you can connect browser audio recording directly to FastAPI endpoints that handle transcription, AI responses, and speech synthesis.

1. System Architecture Overview

text
[Browser: Mic / Text Input] 
       │
       ▼ (Audio Blob or Text via fetch)
[FastAPI Backend]
  ├── 1. Speech-to-Text (STT): Whisper / Google Speech (if audio input)
  ├── 2. Brain (LLM): Gemini / OpenAI / Ollama (generates text reply)
  └── 3. Text-to-Speech (TTS): gTTS / Edge-TTS / OpenAI TTS (creates MP3)
       │
       ▼ (JSON with text reply + audio URL/base64)
[Browser: Displays Text + Plays <audio>]
Use code with caution.

2. Choosing Your Tools (Local vs. Cloud)


Stage	Fast & Free (Python/Local)	High Quality (Cloud APIs)
Speech-to-Text (STT)	faster-whisper (runs locally) or Browser Web Speech API	OpenAI Whisper API / Google Cloud STT
AI Brain (LLM)	Ollama (Llama 3 / Mistral locally)	Google Gemini API (google-genai) / OpenAI API
Text-to-Speech (TTS)	gTTS (Google TTS) or edge-tts (natural voices, free)	ElevenLabs / OpenAI TTS


3. FastAPI Backend Example (main.py)

This example combines gTTS (for voice output) and an LLM response function, accepting either text or an uploaded audio file and returning both text and an audio response.
bash
pip install fastapi uvicorn python-multipart gTTS openai
Use code with caution.
python
import os
import uuid
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from gtts import gTTS
# from openai import OpenAI  # Uncomment if using OpenAI Whisper + GPT

app = FastAPI()
AUDIO_DIR = "chat_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# client = OpenAI(api_key="YOUR_API_KEY")

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/chat")
async def chat_endpoint(
    text: str = Form(None),
    audio: UploadFile = File(None),
    want_audio_reply: bool = Form(True)
):
    user_message = text

    # 1. VOICE-TO-TEXT (If user sent an audio recording)
    if audio:
        temp_in = os.path.join(AUDIO_DIR, f"in_{uuid.uuid4()}.webm")
        with open(temp_in, "wb") as f:
            f.write(await audio.read())
        
        # Replace with Whisper / faster-whisper transcription:
        # transcript = client.audio.transcriptions.create(model="whisper-1", file=open(temp_in, "rb"))
        # user_message = transcript.text
        user_message = "[Transcribed voice message placeholder]"

    if not user_message:
        raise HTTPException(status_code=400, detail="Provide either text or audio.")

    # 2. LLM RESPONSE (Replace with Gemini / OpenAI / Ollama call)
    bot_reply_text = f"You said: {user_message}. Here is your AI response!"

    # 3. TEXT-TO-VOICE (If user wants spoken audio back)
    audio_url = None
    if want_audio_reply:
        out_filename = f"out_{uuid.uuid4()}.mp3"
        out_path = os.path.join(AUDIO_DIR, out_filename)
        tts = gTTS(text=bot_reply_text, lang="en")
        tts.save(out_path)
        audio_url = f"/api/audio/{out_filename}"

    return {
        "user_text": user_message,
        "bot_text": bot_reply_text,
        "audio_url": audio_url
    }

@app.get("/api/audio/{filename}")
async def get_audio(filename: str):
    return FileResponse(os.path.join(AUDIO_DIR, filename), media_type="audio/mpeg")
Use code with caution.

4. Frontend HTML + Vanilla JS (index.html)

This frontend uses the browser's built-in MediaRecorder API to capture microphone audio and sends either text or audio to /api/chat.
html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Voice & Text AI Chatbot</title>
</head>
<body>
    <h2>Multi-Modal AI Chatbot</h2>
    <div id="chatBox" style="border:1px solid #ccc; padding:10px; height:250px; overflow-y:auto;"></div>
    <br>
    <input type="text" id="textInput" placeholder="Type a message...">
    <button onclick="sendText()">Send Text</button>
    <button id="recordBtn" onclick="toggleRecording()">Hold / Click to Record Voice</button>
    <label><input type="checkbox" id="voiceReplyCheck" checked> Speak Reply</label>
    <audio id="botAudio" hidden></audio>

    <script>
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;

        async function sendText() {
            const input = document.getElementById("textInput");
            if (!input.value.trim()) return;

            const formData = new FormData();
            formData.append("text", input.value);
            formData.append("want_audio_reply", document.getElementById("voiceReplyCheck").checked);
            
            appendMessage("You", input.value);
            input.value = "";
            await sendToBackend(formData);
        }

        async function toggleRecording() {
            const btn = document.getElementById("recordBtn");
            if (!isRecording) {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];

                mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
                    const formData = new FormData();
                    formData.append("audio", audioBlob, "voice.webm");
                    formData.append("want_audio_reply", document.getElementById("voiceReplyCheck").checked);
                    await sendToBackend(formData);
                };

                mediaRecorder.start();
                isRecording = true;
                btn.innerText = "Stop Recording";
            } else {
                mediaRecorder.stop();
                isRecording = false;
                btn.innerText = "Click to Record Voice";
            }
        }

        async function sendToBackend(formData) {
            const res = await fetch("/api/chat", { method: "POST", body: formData });
            const data = await res.json();

            appendMessage("Bot", data.bot_text);
            if (data.audio_url) {
                const player = document.getElementById("botAudio");
                player.src = data.audio_url;
                player.play();
            }
        }

        function appendMessage(sender, text) {
            const box = document.getElementById("chatBox");
            box.innerHTML += `<p><strong>${sender}:</strong> ${text}</p>`;
            box.scrollTop = box.scrollHeight;
        }
    </script>
</body>
</html>
Use code with caution.

5. Key Tips for Smooth Performance

• Zero-Cost Browser Alternative: If you don't want to process audio files on the server, you can use the browser's native window.SpeechRecognition (for Voice-to-Text) and window.speechSynthesis (for Text-to-Voice) directly in JavaScript, sending only plain JSON text to FastAPI.
• Conversation Memory: Store the chat history list in request.session["history"] (or SQLModel database) so the LLM remembers previous turns in the conversation.
• Real-Time Low Latency: For instant, phone-call-like voice conversations without waiting for full audio files to render, look into WebSockets paired with the Gemini Multimodal Live API or OpenAI Realtime API.
Sharing your preferred setup will help me tailor the exact Speech-to-Text, LLM, and Text-to-Speech integration code for your project.

Which AI & speech stack do you want to use?

Free local / gTTS + Ollama
Google Gemini API + gTTS
OpenAI (Whisper + GPT + TTS)
Browser Web Speech API only

How should the bot remember chat history?

Single session (in-memory)
Database (SQLModel / SQLite)
No memory needed

What languages does the chatbot need to support?

English
Bengali (Bangla)
Other languages
2 of 3
Skip

