 // Reference to our master audio element
const player = document.getElementById('masterPlayer');

// EVENT A: User wants to generate live speech
function handleLiveTTS() {
    const textValue = document.getElementById('ttsText').value;
    // Direct call to FastAPI router under the hood
    // Correct FastAPI route string construction using backticks
    // MUST use backticks `` (found below the Esc key) and include /api
    player.src = `/api/agent/generate-tts?text=${encodeURIComponent(textValue)}`;
    player.play();
}

// EVENT B: User wants to load a pre-existing file from the server disk
function handlePlayExisting(filename) {
    // Correct URL targeting the agent router endpoint explicitly
    player.src = `/api/agent/play-file/${encodeURIComponent(filename)}`;
    player.play();
}