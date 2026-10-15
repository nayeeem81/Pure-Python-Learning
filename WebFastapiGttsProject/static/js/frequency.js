// 1. Initialize Wavesurfer
// Points to your mounted audio workspace route folder
const ws = WaveSurfer.create({
    container: '#waveform',
    waveColor: '#4F4A85',
    progressColor: '#383351',
    url: '/project/generated/full_sentence.mp3', 
});

// 2. Initialize the Regions plugin
const wsRegions = ws.registerPlugin(WaveSurfer.plugins.regions.create());

// 3. Fetch your backend's metadata mapping file directly from your disk mount
fetch('/project/generated/metadata.json') // <-- UPDATED to match your main.py mount
    .then(res => {
        if (!res.ok) throw new Error("Metadata file not found yet.");
        return res.json();
    })
    .then(projectData => {
        renderWordRegions(projectData.words_timeline);
        buildEditorUI(projectData.words_timeline);
    })
    .catch(err => console.log("Waiting for background task to write files:", err));

// 4. Force hot-reload target when a word frequency shifts
function reloadWaveform() {
    ws.load(`/project/generated/full_sentence.mp3?t=${new Date().getTime()}`); // <-- UPDATED
}