let wsOriginal, wsModified;
let wordTimelineData = [];

// 1. Initialize Dual Waveforms layout
wsOriginal = WaveSurfer.create({
    container: '#original-waveform',
    waveColor: '#4f4a85',
    progressColor: '#383351',
    url: '/project/generated/full_sentence.mp3' // Always reads original structural tracking targets
});

wsModified = WaveSurfer.create({
    container: '#modified-waveform',
    waveColor: '#00b4d8',
    progressColor: '#0077b6',
    url: '/project/generated/full_sentence.mp3' // Initially loads original file as fallback preview baseline
});

// 2. Fetch the pristine original JSON map file reference array layout
fetch('/project/generated/metadata.json')
    .then(res => res.json())
    .then(data => {
        wordTimelineData = data.words_timeline;
        buildControlGrid(wordTimelineData);
    })
    .catch(err => console.error("Error retrieving base mapping matrices:", err));

// 3. Build controls inside UI display frame grid
function buildControlGrid(words) {
    const grid = document.getElementById('control-grid');
    grid.innerHTML = ''; // clear space frame

    words.forEach(word => {
        const card = document.createElement('div');
        card.className = 'word-card';
        card.innerHTML = `
            <strong style="font-size: 1.2em; min-width: 100px;">"${word.text}"</strong>
            <div class="slider-group">
                <div class="slider-item">
                    <label>Tone (Pitch Shift)</label>
                    <input type="range" min="-1.0" max="1.0" step="0.1" value="0.0" id="pitch-${word.word_index}" oninput="updateLabel('p-val-${word.word_index}', this.value)">
                    <span id="p-val-${word.word_index}">0.0</span>
                </div>
                <div class="slider-item">
                    <label>Amplitude (Volume dB)</label>
                    <input type="range" min="-20.0" max="20.0" step="1" value="0.0" id="vol-${word.word_index}" oninput="updateLabel('v-val-${word.word_index}', this.value)">
                    <span id="v-val-${word.word_index}">0 dB</span>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
}

function updateLabel(id, value) {
    document.getElementById(id).innerText = value;
}

// 4. Extract active state values matrix loops and send back to FastAPI server layers
function compileNewAudio() {
    const adjustments = wordTimelineData.map(word => {
        const pVal = parseFloat(document.getElementById(`pitch-${word.word_index}`).value);
        const vVal = parseFloat(document.getElementById(`vol-${word.word_index}`).value);
        return {
            word_index: word.word_index,
            pitch_shift: pVal,
            volume_db: vVal
        };
    });

    fetch('/api/words/consolidate-modifications', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ adjustments: adjustments })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            alert("New custom MP3 rendering compiled successfully on disk!");
            // Force the modified tracking wavesurfer to load the new target file with cache bust parameters
            wsModified.load(`${data.mp3_url}?t=${new Date().getTime()}`);
        } else {
            alert("Error rendering modification output tracks.");
        }
    })
    .catch(err => console.error("Error executing DSP consolidation processing:", err));
}
