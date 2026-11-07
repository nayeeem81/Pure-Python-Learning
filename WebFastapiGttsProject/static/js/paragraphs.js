// ==========================================
// 6. PARAGRAPH State Management
// ==========================================

// PAGING VARIABLES
let currentSkip = 0;
const recordsPerPage = 10;
let totalRecords = 0;

// Track active transaction contexts securely across modules
window.currentSentenceId = null;

// 🛠️ FIX 1: Move these references to the global scope so both fetchSentences() 
// and the DOMContentLoaded listeners can see them reliably.
let userTableBody;
let deleteSelectedBtn;
let selectedCountSpan;
let selectAllCheckbox;

// PAGING RELATED
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
// Inside /static/js/paragraphs.js

async function fetchSentences() {
    if (!userTableBody) userTableBody = document.getElementById('userTableBody');
    userTableBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">Querying ORM...</td></tr>';

    try {
        const response = await fetch(`/api/sentences?skip=${currentSkip}&limit=${recordsPerPage}`);
        if (!response.ok) throw new Error(`Server connection failed: ${response.status}`);

        const result = await response.json();
        const sentences = result.data;

        // 🛠️ OPTIMIZATION ALIGNMENT: 
        // Only update totalRecords if the server returns a valid count (not -1)
        if (result.total !== -1) {
            totalRecords = result.total;
        }

        userTableBody.innerHTML = '';

        if (!sentences || sentences.length === 0) {
            userTableBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">No database rows found.</td></tr>';
            updatePaginationUI();
            updateDeleteButtonState();
            return;
        }

        sentences.forEach((sentence, index) => {
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
                    <td>${duration}</td>
                    <td><span class="status-indicator ready">Ready</span></td>
                </tr>
            `;
            userTableBody.insertAdjacentHTML('beforeend', rowHtml);
        });

        updatePaginationUI();
        updateDeleteButtonState();

    } catch (error) {
        console.error(error);
        userTableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: red;">Error: ${error.message}</td></tr>`;
    }
}

// PAGING OF THE GRID DATA
function updatePaginationUI() {
    const currentPage = Math.floor(currentSkip / recordsPerPage) + 1;
    const totalPages = Math.ceil(totalRecords / recordsPerPage) || 1;

    console.log(`Pagination Diagnostics -> Total Rows: ${totalRecords}, Current Skip: ${currentSkip}`);

    document.getElementById('pageInfo').innerText = `Page ${currentPage} of ${totalPages} (Total: ${totalRecords})`;

    const prevBtn = document.getElementById('prevPageBtn');
    const nextBtn = document.getElementById('nextPageBtn');

    prevBtn.disabled = (currentSkip === 0);
    nextBtn.disabled = (currentSkip + recordsPerPage >= totalRecords);
}

// 🛠️ FIX 1 Continued: Declared standard visibility function globally so events can target it cleanly
function updateDeleteButtonState() {
    if (!userTableBody || !deleteSelectedBtn || !selectedCountSpan) return;

    const checkedBoxes = userTableBody.querySelectorAll('.row-checkbox:checked');
    const count = checkedBoxes.length;

    if (count > 0) {
        deleteSelectedBtn.style.display = 'inline-block';
        selectedCountSpan.textContent = count;
    } else {
        deleteSelectedBtn.style.display = 'none';
    }

    const allBoxes = userTableBody.querySelectorAll('.row-checkbox');
    if (allBoxes.length > 0 && selectAllCheckbox) {
        selectAllCheckbox.checked = (checkedBoxes.length === allBoxes.length);
    }
}


// ==========================================
// DOM LOADED BLOCK
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
    // Bind the global variables to DOM items securely on window configuration
    selectAllCheckbox = document.getElementById('selectAllCheckbox');
    userTableBody = document.getElementById('userTableBody');
    deleteSelectedBtn = document.getElementById('deleteSelectedBtn');
    selectedCountSpan = document.getElementById('selectedCount');

    // Run once on load to ensure button matches empty check state
    updateDeleteButtonState();

    // Master Checkbox Event (Toggle all rows)
    selectAllCheckbox.addEventListener('change', () => {
        const rowCheckboxes = userTableBody.querySelectorAll('.row-checkbox');
        rowCheckboxes.forEach(cb => {
            cb.checked = selectAllCheckbox.checked;
        });
        updateDeleteButtonState();
    });

    // Delegated Listener for row checkboxes (supports dynamically added rows)
    userTableBody.addEventListener('change', (e) => {
        if (e.target.classList.contains('row-checkbox')) {
            updateDeleteButtonState();
        }
    });

    // Executing Bulk Deletion against your FastAPI backend
    deleteSelectedBtn.addEventListener('click', async () => {
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
                // UI Cleanup: Remove matching rows locally from the DOM tree
                checkedBoxes.forEach(cb => {
                    const row = cb.closest('tr');
                    if (row) row.remove();
                });
                // Recalculate button visibility state after removal
                updateDeleteButtonState();
            }
        } catch (error) {
            console.error('Bulk deletion structural failure:', error);
            alert(`Deletion failed: ${error.message}`);
        }
    });
});
