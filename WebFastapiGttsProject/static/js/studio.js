// Reference to our master audio element
const player = document.getElementById('masterPlayer');

// EVENT A: User wants to generate live speech AND save assets for editing
function handleLiveTTS() {
    const textValue = document.getElementById('ttsText').value;
    
    if (!textValue.trim()) {
        alert("Please enter some text first!");
        return;
    }

    // 1. Play the live agent audio immediately in the speaker
    player.src = `/api/agent/generate-tts?text=${encodeURIComponent(textValue)}`;
    player.play();

    // 2. Trigger the background generation & file structure creation on your local disk
    fetch('/api/process/generate-speech-processing', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textValue })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Background file preparation tracking:", data);
        // Optional: You can trigger a visual "Loading Waveform..." indicator here
    })
    .catch(error => console.error("Error triggering background process:", error));
}

// EVENT B: User wants to load a pre-existing file from the server disk
function handlePlayExisting(filename) {
    // Correct URL targeting the agent router endpoint explicitly
    player.src = `/api/agent/play-file/${encodeURIComponent(filename)}`;
    player.play();
}