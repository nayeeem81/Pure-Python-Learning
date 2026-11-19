let mediaRecorder;
let audioChunks = [];
let isRecording = false;

async function sendText()
{
    const input = document.getElementById("textInput");

    if (!input.value.trim()) return;

    const formData = new FormData();

    formData.append("text", input.value);

    formData.append("want_audio_reply", document.getElementById("voiceReplyCheck").checked);

    appendMessage("You", input.value);

    input.value = "";

    await sendToBackend(formData);

}

async function toggleRecording() 
{
    const btn = document.getElementById("recordBtn");

    if (!isRecording)
    {
        const stream = await navigator.mediaDevices.getUserMedia({audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];   

        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

        mediaRecorder.onstop = async () =>
        {
            const audioBlob = new Blob(audioChunks, {type: "audio/webm" });
            const formData = new FormData();
            formData.append("audio", audioBlob, "voice.webm");
            formData.append("want_audio_reply", document.getElementById("voiceReplyCheck").checked);
                await sendToBackend(formData);
        };

        mediaRecorder.start();
        isRecording = true;
        btn.innerText = "Stop Recording";

    }
    else
    {

        mediaRecorder.stop();
        isRecording = false;
        btn.innerText = "Click to Record Voice";

    }

}

async function sendToBackend(formData)
{
    const res = await fetch("/api/chat", {method: "POST", body: formData });
    const data = await res.json();
    appendMessage("Bot", data.bot_text);

    if (data.audio_url)
    {
        const player = document.getElementById("botAudio");
        player.src = data.audio_url;
        player.play();
    }
}

function appendMessage(sender, text)
{
    const box = document.getElementById("chatBox");
    box.innerHTML += `<p><strong>${sender}:</strong> ${text}</p>`;
    box.scrollTop = box.scrollHeight;
}