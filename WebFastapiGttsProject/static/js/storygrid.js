// ==========================================
// 6. Text Editor & DSP State Management
// ==========================================
// 🛠️ ADD THESE LINES AT THE VERY TOP OF THE FILE:
let currentSkip = 0;
const recordsPerPage = 10;
let totalRecords = 0;
const selectAllCheckbox = document.getElementById('selectAllCheckbox');
const userTableBody = document.getElementById('userTableBody');
const chapterSelectedBtn = document.getElementById('chapterSelectedBtn');
const selectedCountSpan = document.getElementById('selectedCount');

// Dom Reference Cache
const newStoryModal = document.getElementById('newStoryModal');
const newChapterModal = document.getElementById('newChapterModal');
const createStoryBtn = document.getElementById('createStoryBtn'); 
const createChapterBtn = document.getElementById('createChapterBtn');
const cancelStoryBtn = document.getElementById('cancelStoryBtn');
const closeModalCross = document.getElementById('closeModalCross');
const submitStoryBtn = document.getElementById('submitStoryBtn');
const storyTitleInput = document.getElementById('storyTitleInput');
const submitChapterBtn = document.getElementById('submitChapterBtn');
const chapterTitleInput = document.getElementById('chapterTitleInput');

// 1. Open Native Modal with Backdrop backdrop styling automatically handled by browser
createStoryBtn.addEventListener('click', () => {
    newStoryModal.showModal();
    storyTitleInput.focus(); // Good accessibility UX focus placement
});

// 2. Local Modular Modal Closures
const closeAndResetModal = () => {
    newStoryModal.close();
    storyTitleInput.value = ''; // Clean field for subsequent openings
};

cancelStoryBtn.addEventListener('click', closeAndResetModal);
closeModalCross.addEventListener('click', closeAndResetModal);
// =========================================================================
// RULE 2: Save metadata during the async REST API fetch return loop
// =========================================================================
submitStoryBtn.addEventListener('click', async () => {
    const storyTitle = storyTitleInput.value.trim();
    if (!storyTitle) return;

    submitStoryBtn.disabled = true;

    // Inside your /static/js/storygrid.js -> submitStoryBtn Event Listener
    try {
        const response = await fetch('/api/stories', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ story_name: storyTitle })
        });

        if (!response.ok) {
            throw new Error(`Server returned error status: ${response.status}`);
        }

        const data = await response.json(); // Explicit properties: data.id and data.story_name
        console.log('Story generated successfully:', data);

        // 1. Hide the dialog input modal form safely
        closeAndResetModal();

        // ====================================================
        // UPDATE PERMANENT UI CONTEXT LABEL
        // ====================================================
        const activeStoryLabel = document.getElementById('activeStoryLabel');
        const loadStoryGridDataBtn = document.getElementById('loadStoryGridDataBtn');

        // 2. Inject the newly processed model string properties permanently into the DOM
        activeStoryLabel.innerHTML = `📖 <span style="color: #007bff;">${data.story_name}</span> <span style="font-size: 12px; color: #6c757d; font-weight: 400; margin-left: 10px;">(Database ID: ${data.id})</span>`;

        // 3. Automatically enable your 'Load Sentences' table grid logic hook
        if (loadStoryGridDataBtn) {
            loadStoryGridDataBtn.disabled = false;
        }

    } catch (error) {
        console.error('Failed to submit new story context payload:', error);
        alert('Could not save your new story right now. Please try again.');
    } finally {
        submitStoryBtn.disabled = false;
    }
});

// Track active transaction contexts securely across modules
window.currentSentenceId = null;

// Initialize layout elements as soon as the DOM loads
document.addEventListener("DOMContentLoaded", () => {

    const savedStoryName = localStorage.getItem('activeStoryName');
    const savedStoryId = localStorage.getItem('activeStoryId');

    if (savedStoryName && savedStoryId) {
        updatePermanentUI(savedStoryName, savedStoryId);
    }

    // Helper component function to manage structural view states cleanly
    function updatePermanentUI(name, id) {
        activeStoryLabel.innerHTML = `📖 <span style="color: #007bff; font-weight: 700;">${name}</span> <span style="font-size: 12px; color: #6c757d; margin-left: 8px;">(Database ID: ${id})</span>`;

        // Enable the matching data matrix loading triggers automatically
        if (loadStoryGridDataBtn) {
            loadStoryGridDataBtn.disabled = false;
        }
    }

    // 1. Dynamic visibility toggle & count calculation
    function updateChapterButtonState() {
        const checkedBoxes = userTableBody.querySelectorAll('.row-checkbox:checked');
        const count = checkedBoxes.length;

        if (count > 0) {
            chapterSelectedBtn.style.display = 'inline-block';
            selectedCountSpan.textContent = count;
        } else {
            chapterSelectedBtn.style.display = 'none';
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
    chapterSelectedBtn.addEventListener('click', async () => {
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
                updateChapterButtonState();

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


// 💡 Helper function to update the slider numerical value text dynamically
function updateLabel(elementId, value) {
    const label = document.getElementById(elementId);
    if (label) label.innerText = value;
}

// Connect the main action button
document.getElementById('loadStoryGridDataBtn').addEventListener('click', () => {
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

document.getElementById('loadStoryGridDataBtn').addEventListener('click', fetchSentences);

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
