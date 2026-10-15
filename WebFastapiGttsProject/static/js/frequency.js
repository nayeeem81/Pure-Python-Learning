 // 1. Initialize Wavesurfer
// Load the consolidated master track from the media route
const ws = WaveSurfer.create({
    container: '#waveform',
    waveColor: '#4F4A85',
    progressColor: '#383351',
    url: '/media/full_sentence.mp3', // <-- Updated path
});

// Force hot-reload target when a word frequency shifts
ws.load(`/media/full_sentence.mp3?t=${new Date().getTime()}`);


// 2. Initialize the Regions plugin
const wsRegions = ws.registerPlugin(WaveSurfer.plugins.regions.create());

// 3. Fetch your backend's metadata mapping file
fetch('/api/project')
    .then(res => res.json())
    .then(projectData => {
        renderWordRegions(projectData.words_timeline);
        buildEditorUI(projectData.words_timeline);
    });

// 4. Map words to the visual waveform timeline
function renderWordRegions(words) {
    words.forEach(word => {
        wsRegions.addRegion({
            start: word.start_time,
            end: word.end_time,
            content: word.text,
            color: 'rgba(0, 180, 216, 0.2)',
            drag: false, // Prevent dragging the word boundaries visually
            resize: false
        });
    });
}

// 5. Generate UI sliders to manipulate word frequencies
function buildEditorUI(words) {
    const panel = document.getElementById('word-editor-panel');
    words.forEach(word => {
        const div = document.createElement('div');
        div.className = 'word-controls';
        div.innerHTML = `
            <h3>"${word.text}"</h3>
            <label>Shift (Hz): </label>
            <input type="range" min="-500" max="500" value="${word.applied_frequency_shift_hz}" id="slide-${word.word_index}">
            <button onclick="saveWordFreq(${word.word_index})">Apply & Recompile</button>
        `;
        panel.appendChild(div);
    });
}

// 6. Send user changes back to FastAPI
function saveWordFreq(index) {
    const newVal = document.getElementById(`slide-${index}`).value;
    fetch('/api/update-frequency', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ word_index: index, new_frequency_shift: parseFloat(newVal) })
    })
    .then(res => res.json())
    .then(data => {
        if(data.status === 'success') {
            // Force wavesurfer to reload the newly generated consolidated mp3 file without refreshing the page
            ws.load(`/media/full_sentence.mp3?t=${new Date().getTime()}`);
        }
    });
}