let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

// 1. Load saved PostgreSQL chat history when page loads
window.addEventListener("DOMContentLoaded", async () => {
    try {
        const res = await fetch("/api/chat/history", { credentials: "include" });
        if (!res.ok) return;

        const history = await res.json();
        history.forEach(msg => {
            const sender = msg.role === "user" ? "You" : "Bot";
            addMessage(sender, msg.content, msg.role);
        });
    } catch (err) {
        console.error("Failed to load chat history:", err);
    }
});

// 2. Send text input (called by <button onclick="sendText()">)
async function sendText() {
    const input = document.getElementById("textInput");
    const text = input.value.trim();
    if (!text) return;

    const wantAudio = document.getElementById("voiceReplyCheck").checked;

    addMessage("You", text, "user");
    input.value = "";

    const formData = new FormData();
    formData.append("text", text);
    formData.append("want_audio_reply", wantAudio);

    await postChat(formData);
}

// Allow pressing Enter inside #textInput to send
document.getElementById("textInput")?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        sendText();
    }
});

// 3. Record voice input (called by <button id="recordBtn" onclick="toggleRecording()">)
async function toggleRecording() {
    const btn = document.getElementById("recordBtn");

    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) audioChunks.push(e.data);
            };

            mediaRecorder.onstop = async () => {
                // Stop microphone tracks so browser recording icon turns off
                stream.getTracks().forEach(track => track.stop());

                const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
                const wantAudio = document.getElementById("voiceReplyCheck").checked;

                addMessage("You", "🎤 [Voice Message]", "user");

                const formData = new FormData();
                formData.append("audio", audioBlob, "voice.webm");
                formData.append("want_audio_reply", wantAudio);

                await postChat(formData);
            };

            mediaRecorder.start();
            isRecording = true;
            btn.innerText = "Stop Recording";
        } catch (err) {
            console.error("Microphone access error:", err);
            addMessage("Error", "Could not access microphone.", "model");
        }
    } else {
        mediaRecorder.stop();
        isRecording = false;
        btn.innerText = "Hold / Click to Record Voice";
    }
}

// 4. Send FormData to FastAPI and handle reply + audio playback
async function postChat(formData) {
    try {
        const res = await fetch("/api/chat/send", {
            method: "POST",
            body: formData,
            credentials: "include"
        });

        const data = await res.json();

        if (!res.ok) {
            console.error("Server Error:", data.detail);
            addMessage("Error", data.detail || `Server error (${res.status})`, "model");
            return;
        }

        // Display Gemini's text reply
        addMessage("Bot", data.bot_message.content, "model");

        // Play gTTS MP3 audio using <audio id="botAudio" hidden>
        if (data.bot_message.audio_url) {
            const player = document.getElementById("botAudio");
            player.src = data.bot_message.audio_url;
            player.play().catch(err => console.warn("Autoplay blocked:", err));
        }
    } catch (err) {
        console.error("Network error:", err);
        addMessage("Error", "Network error connecting to server.", "model");
    }
}

// 5. Render message inside <div id="chatBox" class="chatbox">
function addMessage(sender, text, roleClass) {
    const box = document.getElementById("chatBox");
    if (!box) return;

    const div = document.createElement("div");
    div.className = `msg ${roleClass}`;
    div.innerHTML = `<strong>${sender}:</strong> ${text}`;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}
