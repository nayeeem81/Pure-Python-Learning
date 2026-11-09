const canvas = document.querySelector('#textipy-tensor-canvas');
const context = canvas.getContext('2d', { alpha: false });
const shape = document.querySelector('#textipy-shape');
const position = document.querySelector('#textipy-pixel-position');
const pixelValues = document.querySelector('#textipy-pixel-values');
const downloadButton = document.querySelector('#textipy-download-button');
const imageUpload = document.querySelector('#textipy-image-upload');
const imageName = document.querySelector('#textipy-image-name');

const floatingPanel = document.querySelector('#textipy-floating-panel');
const closePanelButton = document.querySelector('#textipy-close-panel-button');
const titleInput = document.querySelector('#textipy-title-input');
const briefInput = document.querySelector('#textipy-brief-input');
const saveMetadataButton = document.querySelector('#textipy-save-metadata-button');
const clearMetadataButton = document.querySelector('#textipy-clear-metadata-button');
let textOverlayCanvas = document.querySelector('#textipy-text-overlay-canvas');

let uploadedTensor;
const applyButton = document.querySelector('#textipy-update-button');
const undoButton = document.querySelector('#textipy-undo-button');
let textOverlayContext;
let currentMetadata = { title: '', short_brief: '' };

let tensor;
let originalTensor;
let tensorStack = [];
let dots = [];

function clamp(value) {
    return Math.max(0, Math.min(255, value));
}

function cloneTensor(source) {
    return {
        width: source.width,
        height: source.height,
        channels: [...source.channels],
        pixels: source.pixels.map((row) => row.map((pixel) => [...pixel])),
    };
}

// ==========================================================================
// TENSOR ENGINE TRACKING HELPERS
// ==========================================================================

function setTensorStack(initialTensor) {
    // 1. Establish the absolute baseline original image
    originalTensor = cloneTensor(initialTensor);

    // 2. Initialize the historical tracking stack array with version 0
    tensorStack = [cloneTensor(initialTensor)];

    // 3. Set the operational display pointer to the latest array matrix
    tensor = tensorStack[0];

    updateTensorReadout();
}

function updateTensorReadout() {
    if (!tensor) return;

    // Update the row size dimensions readout string (e.g. 720 × 1280 × 3 uint8)
    shape.textContent = `${tensor.height} × ${tensor.width} × 3 uint8`;

    // Update the layout tracking counter text UI label element
    const stackCounter = document.querySelector('#textipy-tensor-count');
    if (stackCounter) {
        stackCounter.textContent = `Stack: ${tensorStack.length}`;
    }

    // Safely enable/disable your Undo button based on stack size history
    const undoBtn = document.querySelector('#textipy-undo-button');
    if (undoBtn) {
        undoBtn.disabled = tensorStack.length <= 1;
    }
}

function render() {
    if (!originalTensor) return; // Guard against running before an image is available

    const { width, height, pixels } = originalTensor; // 🚀 Uses the active stack layer

    // Allocate imageData canvas array channel buffers
    const image = context.createImageData(width, height);

    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            const pixel = pixels[y][x];
            const index = (y * width + x) * 4;

            image.data[index] = clamp(pixel[0]); // R
            image.data[index + 1] = clamp(pixel[1]); // G
            image.data[index + 2] = clamp(pixel[2]); // B
            image.data[index + 3] = 255;             // Alpha
        }
    }

    context.putImageData(image, 0, 0);

    // Render client text layouts over the top canvas layer
    // renderTextOverlay();
}

async function loadTensor() {
    const response = await fetch('/api/tensor');
    if (!response.ok) throw new Error('Tensor request failed');

    setTensorStack(await response.json());

    canvas.width = originalTensor.width;
    canvas.height = originalTensor.height;

    render();
}

function readImageAsTensor(file) {
    return new Promise((resolve, reject) => {
        const image = new Image();
        const objectUrl = URL.createObjectURL(file);

        image.onload = () => {
            const sourceCanvas = document.createElement('canvas');
            const sourceContext = sourceCanvas.getContext('2d', { willReadFrequently: true });
            sourceCanvas.width = image.naturalWidth;
            sourceCanvas.height = image.naturalHeight;
            sourceContext.drawImage(image, 0, 0);
            const pixels = sourceContext.getImageData(0, 0, image.naturalWidth, image.naturalHeight).data;
            const tensorPixels = [];

            for (let y = 0; y < image.naturalHeight; y += 1) {
                const row = [];
                for (let x = 0; x < image.naturalWidth; x += 1) {
                    const index = (y * image.naturalWidth + x) * 4;
                    row.push([pixels[index], pixels[index + 1], pixels[index + 2]]);
                }
                tensorPixels.push(row);
            }

            URL.revokeObjectURL(objectUrl);
            resolve({ width: image.naturalWidth, height: image.naturalHeight, channels: ['r', 'g', 'b'], pixels: tensorPixels });
        };

        image.onerror = () => {
            URL.revokeObjectURL(objectUrl);
            reject(new Error('The selected file is not a readable image'));
        };

        image.src = objectUrl;
    });
}
// ==========================================================================
// FILE UPLOAD AND BASE TENSOR SYNCHRONIZATION
// ==========================================================================

// 1. Trigger the hidden file input when clicking the styled "Select image" button
const uploadBtn = document.querySelector('#textipy-upload-button');
if (uploadBtn) {
    uploadBtn.addEventListener('click', () => imageUpload.click());
}

// 2. Handle the file upload action safely and refresh all operational matrix pointers
if (imageUpload) {
    imageUpload.addEventListener('change', async () => {
        const [file] = imageUpload.files;
        if (!file) return;

        try {
            // A. Process the local raw file directly into an H x W x 3 array payload
            const localTensor = await readImageAsTensor(file);

            // B. Re-initialize your history tracking array stack with this new image asset
            setTensorStack(localTensor);

            // C. Synchronize the dimensions of BOTH canvas layers to match the new tensor shape boundaries
            if (canvas && originalTensor) {
                canvas.width = originalTensor.width;
                canvas.height = originalTensor.height;
            }

            if (textOverlayCanvas && originalTensor) {
                textOverlayCanvas.width = originalTensor.width;
                textOverlayCanvas.height = originalTensor.height;
            }

            // D. Display the clean filename to the user interface tracking label row
            if (imageName) {
                imageName.textContent = file.name;
            }

            // E. Clear out any lingering temporary typing inputs from the previous image state
            currentMetadata = { title: '', short_brief: '' };
            if (titleInput) titleInput.value = '';
            if (briefInput) briefInput.value = '';

            // F. Paint the fresh image pixels cleanly onto your workspace viewports
            render();

        } catch (error) {
            console.error('File upload execution error:', error);
            if (imageName) {
                imageName.textContent = `Upload error: ${error.message}`;
            }
        }
    });
}

// ====================================================================
// FLOATING PANEL AND TEXT OVERLAY FUNCTIONALITY
// ====================================================================

async function loadTensor() {
    const response = await fetch('/api/tensor');
    if (!response.ok) throw new Error('Tensor request failed');
    setTensorStack(await response.json());
    canvas.width = tensor.width;
    canvas.height = tensor.height;
    render();
}

document.addEventListener('keydown', (event) => {
    const isTyping = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName);
    if (event.key.toLowerCase() === 't' && !isTyping) {
        event.preventDefault();
        if (floatingPanel) floatingPanel.classList.toggle('hidden');
    }
});

if (closePanelButton) {
    closePanelButton.addEventListener('click', () => {
        if (floatingPanel) floatingPanel.classList.add('hidden');
    });
}


async function loadCurrentMetadata() {
    try {
        const response = await fetch('/api/current'); // Standardize endpoint URL
        if (response.ok) {
            const data = await response.json();
            currentMetadata = {
                title: data.title || '',
                short_brief: data.short_brief || ''
            };
            // Seed the inputs with saved values
            if (titleInput) titleInput.value = currentMetadata.title;
            if (briefInput) briefInput.value = currentMetadata.short_brief;
            // renderTextOverlay();
        }
    } catch (error) {
        console.warn('Initial metadata preload skipped or endpoint unavailable:', error);
    }
}

// Save or update metadata
async function saveMetadata() {
    if (!titleInput || !briefInput) return;
    const title = titleInput.value.trim();
    const short_brief = briefInput.value.trim();

    try {
        const response = await fetch('/api/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, short_brief })
        });

        if (response.ok) {
            const data = await response.json();
            currentMetadata = {
                title: data.title,
                short_brief: data.short_brief
            };
            // renderTextOverlay();
            console.log('Metadata saved successfully');
        } else {
            alert('Failed to save metadata');
        }
    } catch (error) {
        console.error('Metadata save error:', error);
        alert('Error saving metadata: ' + error.message);
    }
}

// Clear metadata
async function clearMetadata() {
    try {
        const response = await fetch('/api/clear', { method: 'POST' });

        if (response.ok) {
            currentMetadata = { title: '', short_brief: '' };
            if (titleInput) titleInput.value = '';
            if (briefInput) briefInput.value = '';
            // renderTextOverlay();
            console.log('Metadata cleared');
        } else {
            alert('Failed to clear metadata');
        }
    } catch (error) {
        console.error('Metadata clear error:', error);
        alert('Error clearing metadata: ' + error.message);
    }
}
// ==========================================================================
// 3. CANVAS TEXT OVERLAY RENDERING ENGINE
// ==========================================================================

function renderTextOverlay() {
    // 🚀 FIX: Match your actual global variable tracking naming structure (originalTensor)
    if (!originalTensor || !textOverlayCanvas) return;

    // 🚀 FIX: Auto-initialize the canvas context on-demand if it hasn't been configured yet
    if (!textOverlayContext) {
        textOverlayContext = textOverlayCanvas.getContext('2d');
        if (!textOverlayContext) return;
    }

    textOverlayCanvas.width = canvas.width;
    textOverlayCanvas.height = canvas.height;

    if (!currentMetadata.title && !currentMetadata.short_brief) {
        textOverlayContext.clearRect(0, 0, textOverlayCanvas.width, textOverlayCanvas.height);
        return;
    }

    textOverlayContext.clearRect(0, 0, textOverlayCanvas.width, textOverlayCanvas.height);

    const width = textOverlayCanvas.width;
    const height = textOverlayCanvas.height;
    const marginX = Math.max(20, width / 20);
    const marginY = Math.max(40, height / 12);

    const titleFontSize = Math.max(24, Math.floor(height / 12));
    const briefFontSize = Math.max(16, Math.floor(height / 18));

    textOverlayContext.save();
    let yPos = marginY;

    // Draw title
    if (currentMetadata.title) {
        textOverlayContext.font = `bold ${titleFontSize}px Arial`;
        textOverlayContext.fillStyle = '#f5c451';
        textOverlayContext.shadowColor = 'rgba(0, 0, 0, 0.7)';
        textOverlayContext.shadowBlur = 8;
        textOverlayContext.shadowOffsetX = 2;
        textOverlayContext.shadowOffsetY = 2;
        textOverlayContext.fillText(currentMetadata.title, marginX, yPos);
        yPos += titleFontSize + 32;
        textOverlayContext.shadowColor = 'transparent';
    }

    // Draw short brief
    if (currentMetadata.short_brief) {
        textOverlayContext.font = `${briefFontSize}px Arial`;
        textOverlayContext.fillStyle = '#ffffff';
        textOverlayContext.shadowColor = 'rgba(0, 0, 0, 0.7)';
        textOverlayContext.shadowBlur = 6;
        textOverlayContext.shadowOffsetX = 1;
        textOverlayContext.shadowOffsetY = 1;

        const maxWidth = width - (2 * marginX);
        const lineHeight = briefFontSize + 12;
        const lines = wrapText(currentMetadata.short_brief, maxWidth, briefFontSize);

        lines.forEach((line) => {
            textOverlayContext.fillText(line, marginX, yPos);
            yPos += lineHeight;
        });
    }

    textOverlayContext.restore();
}

function wrapText(text, maxWidth, fontSize) {
    const canvas_temp = document.createElement('canvas');
    const ctx_temp = canvas_temp.getContext('2d');
    ctx_temp.font = `${fontSize}px Arial`;

    const paragraphs = text.split('\n');
    const lines = [];

    paragraphs.forEach((paragraph) => {
        if (!paragraph.trim()) {
            lines.push('');
            return;
        }

        const words = paragraph.split(' ');
        let currentLine = '';

        words.forEach((word) => {
            const testLine = currentLine + (currentLine ? ' ' : '') + word;
            const metrics = ctx_temp.measureText(testLine);

            if (metrics.width > maxWidth && currentLine) {
                lines.push(currentLine);
                currentLine = word;
            } else {
                currentLine = testLine;
            }
        });

        if (currentLine) {
            lines.push(currentLine);
        }
    });

    return lines;
}

// ==========================================================================
// 4. USER INTERACTION EVENT LISTENERS
// ==========================================================================
// ==========================================================================
// 4. APPLY BUTTON EVENT HANDLER (Fetch Updated Tensor Matrix from Backend)
// ==========================================================================


if (applyButton) {
    applyButton.addEventListener('click', async () => {
        try {
            // 1. Visually guide the user by setting a loading state on the button
            const originalText = applyButton.innerHTML;
            applyButton.disabled = true;
            applyButton.innerHTML = "⚡ Baking Tensor...";

            // 2. Prepare the text fields to tell the server what to bake into the pixels
            const title = titleInput ? titleInput.value.trim() : '';
            const short_brief = briefInput ? briefInput.value.trim() : '';

            // 3. Make an API call to a tensor processing endpoint on your FastAPI backend
            const response = await fetch('/api/bake-text', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, short_brief })
            });

            if (!response.ok) {
                throw new Error(`Server tensor processing failed with status: ${response.status}`);
            }

            // Inside your applyButton listener block...
            const updatedTensorData = await response.json();

            // 🚀 Safe Push: Add the backend-baked image as a new historical layer
            tensorStack.push(cloneTensor(updatedTensorData));

            // Point your operational references to this latest baked layer version
            tensor = tensorStack[tensorStack.length - 1];
            originalTensor = cloneTensor(tensor); // Syncs baseline matrix tracking

            // Clear out local temporary client overlays since it's hard baked down now
            currentMetadata = { title: '', short_brief: '' };

            // Refresh layout tracking statistics and redraw the image viewport
            updateTensorReadout();

            render();

            // Restore button layout states
            applyButton.disabled = false;

            applyButton.innerHTML = originalText;

            console.log("Tensor updated from backend engine cleanly.");

        } catch (error) {

            console.error('Tensor apply modification error:', error);

            alert('Error updating image tensor from backend: ' + error.message);

            // Re-enable button on error states
            applyButton.disabled = false;

            applyButton.innerHTML = "⚡ Apply";
        }
    });
}

if (downloadButton) {
    downloadButton.addEventListener('click', async () => {
        try {
            // 1. Show a loading state on the button to guide the user
            const originalText = downloadButton.innerHTML;
            downloadButton.disabled = true;
            downloadButton.innerHTML = "⏳ Processing Text...";

            // 2. Fetch the server-baked composite image stream directly from FastAPI
            // This path hits your new @router_magiclens endpoint
            const response = await fetch('/api/download-baked');

            if (!response.ok) {
                throw new Error(`Server processing failed with status: ${response.status}`);
            }

            // 3. Convert the response stream into a binary Blob object
            const imageBlob = await response.blob();

            // 4. Create an ephemeral memory URL for the downloaded blob asset
            const downloadUrl = URL.createObjectURL(imageBlob);

            // 5. Instantly instantiate an off-screen link anchor to trigger the browser save dialog
            const downloadLink = document.createElement('a');
            downloadLink.href = downloadUrl;
            downloadLink.download = `textipy_baked_presentation_${Date.now()}.png`;

            document.body.appendChild(downloadLink);
            downloadLink.click();

            // 6. Housekeeping: Remove the anchor link and release memory buffers right away
            document.body.removeChild(downloadLink);
            URL.revokeObjectURL(downloadUrl);

            // Restore the download button text
            downloadButton.disabled = false;
            downloadButton.innerHTML = originalText;

        } catch (error) {
            console.error('Server-side baking download error:', error);
            alert('Error downloading baked image from server: ' + error.message);

            // Reset button state in case of unexpected errors
            downloadButton.disabled = false;
            downloadButton.innerHTML = "Download PNG";
        }
    });
}

if (saveMetadataButton) saveMetadataButton.addEventListener('click', saveMetadata);

if (clearMetadataButton) {
    clearMetadataButton.addEventListener('click', async () => {
        if (confirm('Are you sure you want to clear all text?')) {
            await clearMetadata();
        }
    });
}

function resizeCanvasToDisplay() {
    if (!textOverlayCanvas) return;
    if (textOverlayCanvas.width !== textOverlayCanvas.clientWidth ||
        textOverlayCanvas.height !== textOverlayCanvas.clientHeight) {
            textOverlayCanvas.width = textOverlayCanvas.clientWidth;
        textOverlayCanvas.height = textOverlayCanvas.clientHeight;
        renderTextOverlay(); // 🚀 FIX: Safely re-triggers the text pass mapping loop
    }
}
// ==========================================================================
// 5. DOM CONTENT COMPLIANCE WRAPPER LOOP
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
    textOverlayCanvas = document.querySelector('#textipy-text-overlay-canvas');
    if (textOverlayCanvas) {
        textOverlayContext = textOverlayCanvas.getContext('2d');
        console.log("Canvas context loaded successfully!");
        resizeCanvasToDisplay();
        window.addEventListener('resize', resizeCanvasToDisplay);
    }
    // 🚀 FIX: Cleanly close code and execute server metadata queries
    loadTensor();
});
