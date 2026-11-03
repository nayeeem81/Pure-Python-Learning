// ==========================================
// Story Grid Editor & DSP State Management
// ==========================================
let currentSkip = 0;
const recordsPerPage = 10;
let totalRecords = 0;

const selectAllCheckbox = document.getElementById('selectAllCheckbox');
const userTableBody = document.getElementById('userTableBody');
const chapterSelectedBtn = document.getElementById('chapterSelectedBtn');
const selectedCountSpan = document.getElementById('selectedCount');

// Track active transaction contexts securely across modules
window.currentSentenceId = null;

const createStoryBtn = document.getElementById('createStoryBtn');
// Story Modal Elements
const newStoryModal = document.getElementById('newStoryModal');
const cancelStoryBtn = document.getElementById('cancelStoryBtn');
const closeModalCross = document.getElementById('closeModalCross');
const submitStoryBtn = document.getElementById('submitStoryBtn');
const storyTitleInput = document.getElementById('storyTitleInput');

// Local Storage (Story)
const activeStoryLabel = document.getElementById('activeStoryLabel');
const haveActiveContext = localStorage.getItem('activeStoryName') && localStorage.getItem('activeStoryId');
// Local Storage (Chapter)
const activeChapterLabel = document.getElementById('activeChapterLabel');

const loadStoryGridDataBtn = document.getElementById('loadStoryGridDataBtn');
const createChapterBtn = document.getElementById('createChapterBtn');

// Chapter Modal Elements   
const newChapterModal = document.getElementById('newChapterModal');
const submitChapterBtn = document.getElementById('submitChapterBtn');
const chapterTitleInput = document.getElementById('chapterTitleInput');
const cancelChapterBtn = document.getElementById('cancelChapterBtn');
const closeChapterModalCross = document.getElementById('closeChapterModalCross');

// 1. Open Story Native Modal with Backdrop backdrop styling automatically handled by browser
createStoryBtn.addEventListener('click', () => {
    newStoryModal.showModal();
    storyTitleInput.focus(); 
});

const closeAndResetModal = () => {
    newStoryModal.close();
    storyTitleInput.value = '';
};

// 2. Local Modular Modal Closures (Story)
cancelStoryBtn.addEventListener('click', closeAndResetModal);
closeModalCross.addEventListener('click', closeAndResetModal);

// 1. Open Chapter Native Modal with Backdrop backdrop styling automatically handled by browser
createChapterBtn.addEventListener('click', () => {
    newChapterModal.showModal();
    chapterTitleInput.focus(); 
});

const closeAndResetChapterModal = () => {
    newChapterModal.close();
    chapterTitleInput.value = '';
};

// 2. Local Modular Modal Closures (Chapter)
cancelChapterBtn.addEventListener('click', closeAndResetChapterModal);
closeChapterModalCross.addEventListener('click', closeAndResetChapterModal);


// =========================================================================
// RULE 2: Save metadata during the async REST API fetch return loop (Create Story first)
// =========================================================================

// Helper component function to manage structural view states cleanly
function updatePermanentUI(name, id) {
    activeStoryLabel.innerHTML = `📖 <span style="color: #007bff; font-weight: 700;">${name}</span> <span style="font-size: 12px; color: #6c757d; margin-left: 8px;">(Database ID: ${id})</span>`;

    // Enable the matching data matrix loading triggers automatically
    if (loadStoryGridDataBtn) {
        loadStoryGridDataBtn.disabled = false;
    }
}

submitStoryBtn.addEventListener('click', async () => {

    const storyTitle = storyTitleInput.value.trim();

    if (!storyTitle) return;

    submitStoryBtn.disabled = true;

    try {
        const response = await fetch('/api/stories', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ story_name: storyTitle })
        });

        if (!response.ok) {
            throw new Error(`Server returned error status: ${response.status}`);
        }

        const data = await response.json(); 

        console.log('Story generated successfully:', data);

        // 1. Commit values securely into browser local storage
        localStorage.setItem('activeStoryName', data.story_name);
        localStorage.setItem('activeStoryId', data.id);

        // 2. Trigger instant component layout update
        updatePermanentUI(data.story_name, data.id);

        // 3. Clear window layer and close modal context
        closeAndResetModal();

        const activeStoryLabel = document.getElementById('activeStoryLabel');
        const loadStoryGridDataBtn = document.getElementById('loadStoryGridDataBtn');

        // 2. Inject the newly processed model string properties permanently into the DOM
        activeStoryLabel.innerHTML = `📖 <span style="color: #007bff;">${data.story_name}</span> <span style="font-size: 12px; color: #6c757d; font-weight: 400; margin-left: 10px;">(Database ID: ${data.id})</span>`;

        // 3. Automatically enable your 'Load Sentences' table grid logic hook
        if (loadStoryGridDataBtn) {
            loadStoryGridDataBtn.disabled = false;
            createChapterBtn.disabled = false;
        }

    } catch (error) {
        console.error('Failed to submit new story context payload:', error);
        alert('Could not save your new story right now. Please try again.');
    } finally {
        submitStoryBtn.disabled = true;
    }
});

// =========================================================================
// RULE 3: Save metadata during the async REST API fetch return loop (Create Chapter)
// =========================================================================
var arrChapters = []; // Initialize an empty array to hold chapter data

submitChapterBtn.addEventListener('click', async () => {

    const chapterTitle = chapterTitleInput.value.trim();

    if (!chapterTitle) return;

    submitChapterBtn.disabled = false;

    try {
        const rawStoryId = localStorage.getItem('activeStoryId');
        const activeStoryId = rawStoryId ? parseInt(rawStoryId, 10) : 0; 

        const payload = {
            chapter_name: chapterTitle,
            serial_number: 0, // Placeholder for future logic to auto-increment chapter numbers
            story_id: activeStoryId    
        };
      
        const response = await fetch('/api/chapters', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json' 
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Server returned error status: ${response.status}`);
        }

        var data = {};
        data = await response.json(); 

        // Commit values securely into browser local storage
        arrChapters.push(data); 

        localStorage.setItem('activeChapters', JSON.stringify(arrChapters));
 
        appendChapterToUI('activeChapterContainer');

        // Clear window layer and close modal context
        closeAndResetChapterModal();

        // Automatically enable your 'Load Sentences' table grid logic hook
        if (loadStoryGridDataBtn) {
            loadStoryGridDataBtn.disabled = false;
            createChapterBtn.disabled = false;
        }

    } catch (error) {
        console.error('Failed to submit new chapter context payload:', error);
        alert('Could not save your new chapter right now. Please try again.');
    } finally {
        submitChapterBtn.disabled = false;
    }
});

// Reusable utility function to append a new chapter element permanently to a container
function appendChapterToUI(containerId) {
    const targetContainer = document.getElementById(containerId);

    if (!targetContainer) {
        console.error(`Target container with ID "${containerId}" was not found.`);
        return;
    }

    // 1. Retrieve the raw JSON string from local storage
    const rawChapters = localStorage.getItem('activeChapters');

    // 2. Safely parse the string into a JS array object (fallback to an empty array if null)
    const arrChapters = rawChapters ? JSON.parse(rawChapters) : [];

    // 3. You can now use it as a normal array
    console.log("Your chapters array:", arrChapters);

    // 1. Clear out old entries to prevent UI duplication bugs
    targetContainer.innerHTML = '';

    for (let i = 0; i < arrChapters.length; i++) {
        const chapter = arrChapters[i];

        const newChapterHTML = `
    <div class="chapter-badge-item" data-id="${chapter.id}">
        <span class="chapter-badge-icon">📖</span>
        <span class="chapter-badge-title">${chapter.chapter_name}</span>
        <span class="chapter-badge-id">(Database ID: ${chapter.id})</span>
    </div>
    `;
        targetContainer.insertAdjacentHTML('beforeend', newChapterHTML);
    }
}

// Initialize layout elements as soon as the DOM loads
// Initialize layout elements as soon as the DOM loads
// Initialize layout elements as soon as the DOM loads
document.addEventListener("DOMContentLoaded", () => {
    const savedStoryName = localStorage.getItem('activeStoryName');
    const savedStoryId = localStorage.getItem('activeStoryId');

    if (haveActiveContext) {
        createStoryBtn.disabled = true; // Disable story creation if an active context exists
        loadStoryGridDataBtn.disabled = false; // Enable the load button if a story is active
        createChapterBtn.disabled = false; // Enable chapter creation if a story is active
    }

    if (savedStoryName && savedStoryId) {
        updatePermanentUI(savedStoryName, savedStoryId);
        appendChapterToUI('activeChapterContainer');
    }

    const container = document.getElementById('activeChapterContainer');

    if (container) {
        container.addEventListener('click', (event) => {
            const badge = event.target.closest('.chapter-badge-item');
            if (!badge) return;

            const chapterId = badge.dataset.id;
            console.log("Captured Chapter Database ID:", chapterId);

            handleChapterSelection(chapterId, badge);
        });
    }

    function handleChapterSelection(chapterId, badgeElement) {
        document.querySelector('.chapter-badge-item.active')?.classList.remove('active');
        badgeElement.classList.add('active');
        const activeChapterId = localStorage.setItem('activeChapterId', chapterId);
    }

    function updateChapterButtonState() {
        const checkedBoxes = userTableBody.querySelectorAll('.row-checkbox:checked');
        const count = checkedBoxes.length;

        if (count > 0) {
            chapterSelectedBtn.style.display = 'inline-block';
            selectedCountSpan.textContent = count;
        } else {
            chapterSelectedBtn.style.display = 'none';
        }

        const allBoxes = userTableBody.querySelectorAll('.row-checkbox');

        if (allBoxes.length > 0) {
            selectAllCheckbox.checked = (checkedBoxes.length === allBoxes.length);
        }
    }
    
    selectAllCheckbox.addEventListener('change', () => {
        const rowCheckboxes = userTableBody.querySelectorAll('.row-checkbox');
        rowCheckboxes.forEach(cb => {
            cb.checked = selectAllCheckbox.checked;
        });
        updateChapterButtonState();
    });

    userTableBody.addEventListener('change', (e) => {
        if (e.target.classList.contains('row-checkbox')) {
            updateChapterButtonState();
        }
    });

    chapterSelectedBtn.addEventListener('click', async () => {
        const checkedBoxes = userTableBody.querySelectorAll('.row-checkbox:checked');
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
                body: JSON.stringify({ ids: idsToDelete }) 
            });

            if (!response.ok) {
                const errData = await response.json();
                console.error('Validation details:', errData);
                throw new Error(errData.detail ? JSON.stringify(errData.detail) : 'Server rejected request');
            }

            const result = await response.json();
            if (result.status === 'success' || result.status === 'ignored') {
                checkedBoxes.forEach(cb => {
                    const row = cb.closest('tr');
                    row.remove();
                });
                
                selectAllCheckbox.checked = false;
                updateChapterButtonState();
                
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

function updateLabel(elementId, value) {
    const label = document.getElementById(elementId);
    if (label) label.innerText = value;
}

document.getElementById('loadStoryGridDataBtn').addEventListener('click', () => {
    currentSkip = 0; 
    fetchSentences();
});

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
    tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">Querying ORM...</td></tr>';

    try {
        const response = await fetch(`/api/sentences?skip=${currentSkip}&limit=${recordsPerPage}`);
        if (!response.ok) throw new Error(`Server connection failed: ${response.status}`);

        const result = await response.json();
        const sentences = result.data;
        totalRecords = result.total;
        tableBody.innerHTML = '';

        if (!sentences || sentences.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No database rows found.</td></tr>';
            updatePaginationUI();
            createChapterBtn.disabled = false; 
            return;
        }

        sentences.forEach((sentence, index) => {
            const row = document.createElement('tr');
            const duration = sentence.total_duration_seconds ? `${sentence.total_duration_seconds}s` : '2.88s';
            const mp3Url = sentence.master_mp3_path ? `/project/${sentence.master_mp3_path}` : '#';
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

function updatePaginationUI() {
    const currentPage = Math.floor(currentSkip / recordsPerPage) + 1;
    const totalPages = Math.ceil(totalRecords / recordsPerPage) || 1;
    console.log(`Pagination Diagnostics -> Total Rows: ${totalRecords}, Current Skip: ${currentSkip}`);
    document.getElementById('pageInfo').innerText = `Page ${currentPage} of ${totalPages} (Total: ${totalRecords})`;
    const prevBtn = document.getElementById('prevPageBtn');
    const nextBtn = document.getElementById('nextPageBtn');
    // FIX: Explicit boolean calculations
    prevBtn.disabled = (currentSkip === 0);
    nextBtn.disabled = (currentSkip + recordsPerPage >= totalRecords);
}
