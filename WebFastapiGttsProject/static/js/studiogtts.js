// ==========================================
// 1. GLOBAL INSTANCES & STATE CONTAINERS
// ==========================================
let wsOriginal = null;
let wsModified = null;
let wsRegionsOriginal = null;
let wordTimelineData = [];
// ==========================================
// 6. Text Editor & DSP State Management
// ==========================================
// 🛠️ ADD THESE LINES AT THE VERY TOP OF THE FILE:
let currentSkip = 0;
const recordsPerPage = 10;
let totalRecords = 0;

// Track active transaction contexts securely across modules
window.currentSentenceId = null;

// Initialize layout elements as soon as the DOM loads
document.addEventListener("DOMContentLoaded", () => {
    const originalContainer = document.getElementById('original-waveform');
    const modifiedContainer = document.getElementById('modified-waveform');

    if (originalContainer && modifiedContainer) {
        initWaveSurferEngines();
    } else {
        console.warn("WaveSurfer target container nodes missing in active DOM view layer.");
    }

    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    const userTableBody = document.getElementById('userTableBody');
    const deleteSelectedBtn = document.getElementById('deleteSelectedBtn');
    const selectedCountSpan = document.getElementById('selectedCount');

    // 1. Dynamic visibility toggle & count calculation
    function updateDeleteButtonState() {
        const checkedBoxes = userTableBody.querySelectorAll('.row-checkbox:checked');
        const count = checkedBoxes.length;

        if (count > 0) {
            deleteSelectedBtn.style.display = 'inline-block';
            selectedCountSpan.textContent = count;
        } else {
            deleteSelectedBtn.style.display = 'none';
        }

        // Auto-check/uncheck master header box based on individual row status
        const allBoxes = userTableBody.querySelectorAll('.row-checkbox');
        if (allBoxes.length > 0) {
            selectAllCheckbox.checked = (checkedBoxes.length === allBoxes.length);
        }
    }

    // 2. Master Checkbox Event (Toggle all rows)
    selectAllCheckbox.addEventListener('change', () => {
        const rowCheckboxes = userTableBody.querySelectorAll('.row-checkbox');
        rowCheckboxes.forEach(cb => {
            cb.checked = selectAllCheckbox.checked;
        });
        updateDeleteButtonState();
    });

    // 3. Delegated Listener for row checkboxes (supports dynamically added rows)
    userTableBody.addEventListener('change', (e) => {
        if (e.target.classList.contains('row-checkbox')) {
            updateDeleteButtonState();
        }
    });
    // 4. Executing Bulk Deletion against your FastAPI backend
    deleteSelectedBtn.addEventListener('click', async () => {
        const checkedBoxes = userTableBody.querySelectorAll('.row-checkbox:checked');

        // Match your grid template: Read value directly from the checked checkbox element
        const idsToDelete = Array.from(checkedBoxes).map(cb => parseInt(cb.value, 10)).filter(id => !isNaN(id));

        if (idsToDelete.length === 0) return;

        const confirmDelete = confirm(`Are you sure you want to delete ${idsToDelete.length} selected item(s)?`);
        if (!confirmDelete) return;

        try {
            const response = await fetch('/api/sentences/bulk-delete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ ids: idsToDelete }) // Sends: {"ids":}
            });

            if (!response.ok) {
                const errData = await response.json();
                console.error('Validation details:', errData);
                throw new Error(errData.detail ? JSON.stringify(errData.detail) : 'Server rejected request');
            }

            const result = await response.json();

            if (result.status === 'success' || result.status === 'ignored') {
                // UI Cleanup: Remove matching rows locally from the DOM tree
                checkedBoxes.forEach(cb => {
                    const row = cb.closest('tr');
                    row.remove();
                });

                // Reset master checkbox header state
                selectAllCheckbox.checked = false;
                updateDeleteButtonState();

                // Show grid placeholder text if the table has been fully cleared out
                if (userTableBody.querySelectorAll('.row-checkbox').length === 0) {
                    userTableBody.innerHTML = `
                        <tr>
                            <td colspan="7" style="text-align: center; color: #666;">
                                Click "Load Sentences" to populate grid.
                            </td>
                        </tr>`;
                }
            } else {
                alert(`Notice: ${result.message}`);
            }
        } catch (error) {
            console.error('Error during bulk deletion processing:', error);
            alert(`Failed to delete records: ${error.message}`);
        }
    });

});

// ==========================================
// 2. WAVESURFER INITIALIZATION LOGIC
// ==========================================
function initWaveSurferEngines() {
    // Primary Pristine Audio Wave Viewport
    wsOriginal = WaveSurfer.create({
        container: '#original-waveform',
        waveColor: '#4f4a85',
        progressColor: '#383351',
        height: 100
    });

    // 💡 Modern WaveSurfer v7+ Regions Plugin Initialization Fix
    if (window.WaveSurfer && window.WaveSurfer.Regions) {
        wsRegionsOriginal = wsOriginal.registerPlugin(window.WaveSurfer.Regions.create());
    } else {
        try {
            wsRegionsOriginal = wsOriginal.registerPlugin(WaveSurfer.plugins.regions.create());
        } catch (e) {
            console.warn("WaveSurfer Regions plugin not loaded natively. Check script tags.");
        }
    }

    // Modified Real-Time Processing Audio Output Viewport
    wsModified = WaveSurfer.create({
        container: '#modified-waveform',
        waveColor: '#00b4d8',
        progressColor: '#0077b6',
        height: 100
    });

    console.log("WaveSurfer processing layers provisioned successfully.");
}

// ==========================================
// 3. TTS SPEECH INPUT & WORKSPACE ROUTINES
// ==========================================
function handleLiveTTS() {
    const textInput = document.getElementById('ttsText');
    const player = document.getElementById('masterPlayer');

    if (!textInput || !textInput.value.trim()) {
        alert("Please enter some text first!");
        return;
    }

    const textValue = textInput.value;

    if (player) {
        player.src = `/api/agent/generate-tts?text=${encodeURIComponent(textValue)}`;
        player.play().catch(err => console.log("Direct audio streaming interrupted:", err));
    }

    fetch('/api/process/generate-speech-processing', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textValue })
    })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP transaction status error: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log("Background preparation complete:", data);
            if (data.sentence_id) {
                loadSentenceWorkspace(data.sentence_id, 0); // 💡 Explicit clean entry with retry track tracking
            }
        })
        .catch(error => console.error("Error executing background speech compiler:", error));
}


function loadSentenceWorkspace(sentenceId, retryCount = 0) {
    if (!sentenceId) return;
    window.currentSentenceId = sentenceId;

    const targetJsonPath = `/project/generated/metadata_${sentenceId}.json`;

    fetch(targetJsonPath)
        .then(res => {
            if (!res.ok) {
                // If backend file writing isn't complete, enter a retry block loop
                if (retryCount < 10) {
                    console.log(`⏳ File writing in progress... retrying connection mapping cycle (${retryCount + 1}/10)`);
                    throw new Error("building");
                }
                // If completely timed out, switch over to local default models fallback
                return fetch('/project/generated/metadata.json').then(fallback => fallback.json());
            }
            return res.json();
        })
        .then(projectData => {
            // Handle standard format vs fallback schema layouts safely
            wordTimelineData = projectData.words_timeline || projectData;

            // Mount the specific generated audio assets securely
            wsOriginal.load(`/project/generated/sentence_${sentenceId}.mp3`);
            wsModified.load(`/project/generated/sentence_${sentenceId}.mp3`);

            // Refresh UI grids and region canvases
            renderWordRegions(wordTimelineData);
            buildControlGrid(wordTimelineData);
        })
        .catch(err => {
            if (err.message === "building" && retryCount < 10) {
                setTimeout(() => loadSentenceWorkspace(sentenceId, retryCount + 1), 500);
            } else {
                console.error("❌ Workspace setup failed entirely:", err);
            }
        });
}

// ==========================================
// 4. UI ELEMENT LAYOUT BUILDERS & UTILITIES
// ==========================================
function renderWordRegions(words) {
    if (!wsRegionsOriginal) return;

    // 💡 FIX 1: Modern WaveSurfer v7 method to wipe out previous region entities safely
    try {
        const existingRegions = wsRegionsOriginal.getRegions();
        if (existingRegions && existingRegions.length > 0) {
            existingRegions.forEach(region => region.destroy());
        }
    } catch (e) {
        console.warn("Could not sweep previous regional vectors:", e);
    }

    // Map region blocks across the timeline canvas graph coordinates
    words.forEach(word => {
        // 💡 FIX 2: Modern WaveSurfer v7 layout declaration structure
        wsRegionsOriginal.addRegion({
            start: parseFloat(word.start_time),
            end: parseFloat(word.end_time),
            content: word.text,
            color: 'rgba(79, 74, 133, 0.2)',
            drag: false,
            resize: false,
            id: `region-${word.word_index}`
        });
    });
    console.log(`🎯 Rendered ${words.length} timeline word markers.`);
}

function buildControlGrid(words) {
    const grid = document.getElementById('control-grid');
    if (!grid) return;

    grid.innerHTML = ''; // Wipe panel container bounds cleanly

    words.forEach(word => {
        const card = document.createElement('div');
        card.className = 'word-card';
        card.innerHTML = `
            <strong style="font-size: 1.1em; display: inline-block; margin-bottom: 8px;">"${word.text}"</strong>
            <div class="slider-group">
                <div class="slider-item">
                    <label style="font-size: 0.85em; color: #aaa;">Tone (Pitch Shift)</label>
                    <input type="range" min="-1.0" max="1.0" step="0.1" 
                           value="${word.applied_frequency_shift_hz || 0.0}" 
                           id="pitch-${word.word_index}" 
                           oninput="updateLabel('p-val-${word.word_index}', this.value)">
                    <span id="p-val-${word.word_index}" style="font-size: 0.85em; font-weight: bold; margin-left: 5px;">
                        ${(word.applied_frequency_shift_hz || 0.0).toFixed(1)}
                    </span>
                </div>
                <div class="slider-item" style="margin-top: 5px;">
                    <label style="font-size: 0.85em; color: #aaa;">Amplitude (Volume dB)</label>
                    <input type="range" min="-20.0" max="20.0" step="1" 
                           value="${word.applied_amplitude_db || 0.0}" 
                           id="vol-${word.word_index}" 
                           oninput="updateLabel('v-val-${word.word_index}', this.value + ' dB')">
                    <span id="v-val-${word.word_index}" style="font-size: 0.85em; font-weight: bold; margin-left: 5px;">
                        ${word.applied_amplitude_db || 0} dB
                    </span>
                </div>
            </div>
        `; // 💡 FIXED: Added closing template literal strings and tags here
        grid.appendChild(card);
    });
}

// 💡 Helper function to update the slider numerical value text dynamically
function updateLabel(elementId, value) {
    const label = document.getElementById(elementId);
    if (label) label.innerText = value;
}
// ==========================================
// 5. DSP CONSOLIDATION POST TRANSFERS
// ==========================================
function compileNewAudio() {
    if (!window.currentSentenceId) {
        alert("Operation denied: No active sentence payload context is currently loaded.");
        return;
    }

    // Map matching parameters out of current grid configurations elements
    const adjustments = wordTimelineData.map(word => {
        const pitchEl = document.getElementById(`pitch-${word.word_index}`);
        const volEl = document.getElementById(`vol-${word.word_index}`);

        return {
            word_index: word.word_index,
            pitch_shift: pitchEl ? parseFloat(pitchEl.value) : 0.0,
            volume_db: volEl ? parseFloat(volEl.value) : 0.0
        };
    });

    const requestPayload = {
        sentence_id: parseInt(window.currentSentenceId, 10),
        adjustments: adjustments
    };

    fetch('/api/words/consolidate-modifications', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestPayload)
    })
        .then(res => {
            if (!res.ok) throw new Error("Database transaction operations returned error statuses.");
            return res.json();
        })
        .then(data => {
            if (data.status === 'success' || data.database_sync === 'complete') {
                alert("New custom processing track synchronized & rendered inside database successfully!");

                // 💡 FIX: Explicitly derive path from active context ID to bypass missing backend keys
                const freshTrackUrl = `/project/generated/sentence_${window.currentSentenceId}.mp3`;

                // Reload the modified waveform canvas view wrapper utilizing timestamp cache-busting keys
                wsModified.load(`${freshTrackUrl}?t=${new Date().getTime()}`);
            } else {
                alert("Error running background audio mixing pipelines.");
            }
        })
        .catch(err => console.error("DSP Pipeline processing failure error logs:", err));
}




// Connect the main action button
document.getElementById('loadDataBtn').addEventListener('click', () => {
    currentSkip = 0; // Reset to the first page on a fresh click
    fetchSentences();
});

// Connect Next/Previous Pagination Elements
document.getElementById('prevPageBtn').addEventListener('click', () => {
    if (currentSkip >= recordsPerPage) {
        currentSkip -= recordsPerPage;
        fetchSentences();
    }
});

document.getElementById('nextPageBtn').addEventListener('click', () => {
    if (currentSkip + recordsPerPage < totalRecords) {
        currentSkip += recordsPerPage;
        fetchSentences();
    }
});

document.getElementById('loadDataBtn').addEventListener('click', fetchSentences);

async function fetchSentences() {
    const tableBody = document.getElementById('userTableBody');
    // Updated colspan to match the 4 columns we are rendering
    tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">Querying ORM...</td></tr>';

    try {
        // Inside studio-engine.js - update these lines inside fetchSentences():

        const response = await fetch(`/api/sentences?skip=${currentSkip}&limit=${recordsPerPage}`);
        if (!response.ok) throw new Error(`Server connection failed: ${response.status}`);

        const result = await response.json();
        // 🛠️ FIX: Extract the actual array from the data property container
        const sentences = result.data;
        totalRecords = result.total;

        tableBody.innerHTML = ''; // Clear fallback loading row

        if (!sentences || sentences.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No database rows found.</td></tr>';
            updatePaginationUI();
            return;
        }

        // 🛠️ FIX: Loop through the 'sentences' array variable instead of the root 'data' object
        sentences.forEach((sentence, index) => {
            const row = document.createElement('tr');
            const duration = sentence.total_duration_seconds ? `${sentence.total_duration_seconds}s` : '2.88s';
            const mp3Url = sentence.master_mp3_path ? `/project/${sentence.master_mp3_path}` : '#';

            // Example of how your row template string should look when appending to userTableBody
            const rowHtml = `
                    <tr data-id="${sentence.id}">
                        <td style="text-align: center;">
                            <input type="checkbox" class="row-checkbox" value="${sentence.id}">
                        </td>
                        <td>${sentence.id}</td>
                        <td>#${currentSkip + index + 1}</td>
                        <td>${sentence.text_content || 'No Text'}</td>
                         <td>
                    <audio controls preload="none"><source src="${mp3Url}" type="audio/mpeg"></audio>
                  
                </td>
                        <td>${sentence.total_duration_seconds}s</td>
                        <td><span class="status-indicator ready">Ready</span></td>
                    </tr>
                `;
                 
           
            userTableBody.insertAdjacentHTML('beforeend', rowHtml);
        });
        updatePaginationUI();
    } catch (error) {
        console.error(error);
        tableBody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: red;">Error: ${error.message}</td></tr>`;
    }
}

// Pageing
function updatePaginationUI() {
    const currentPage = Math.floor(currentSkip / recordsPerPage) + 1;
    const totalPages = Math.ceil(totalRecords / recordsPerPage) || 1;

    // Log calculation data to your browser console to verify values
    console.log(`Pagination Diagnostics -> Total Rows: ${totalRecords}, Current Skip: ${currentSkip}`);

    // Update text node layout
    document.getElementById('pageInfo').innerText = `Page ${currentPage} of ${totalPages} (Total: ${totalRecords})`;

    // Select DOM nodes
    const prevBtn = document.getElementById('prevPageBtn');
    const nextBtn = document.getElementById('nextPageBtn');

    // 🛠️ FIX: Explicit boolean calculations
    prevBtn.disabled = (currentSkip === 0);
    nextBtn.disabled = (currentSkip + recordsPerPage >= totalRecords);
}
