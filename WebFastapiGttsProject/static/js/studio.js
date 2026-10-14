 // Reference to our master audio element
const player = document.getElementById('masterPlayer');

// EVENT A: User wants to generate live speech
function handleLiveTTS() {
    const textValue = document.getElementById('ttsText').value;

    // Direct call to FastAPI router under the hood
    // encodeURIComponent ensures spaces/punctuation don't break the web URL
    player.src = "/agent/generate-tts?text=${encodeURIComponent(textValue)}";
    player.play();
}

// EVENT B: User wants to load a pre-existing file from the server disk
function handlePlayExisting(filename) {
    // Direct call to FastAPI file reader stream
    player.src = "/agent/play-file/${filename}";
    player.play();
}