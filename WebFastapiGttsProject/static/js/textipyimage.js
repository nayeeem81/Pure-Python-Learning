
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

const applyButton = document.querySelector('#textipy-update-button');
const undoButton = document.querySelector('#textipy-undo-button');
let currentMetadata = { title: '', short_brief: '' };

let tensor;
let tensorStack = [];

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

function setTensorStack(tensornew) {
    // 2. Initialize the historical tracking stack array with version 0
    tensorStack = [cloneTensor(tensornew)];
    // 3. Set the operational display pointer to the latest array matrix
    tensor = tensorStack[tensorStack.length - 1];
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
    if (!tensor) return;
    const { width, height, pixels } = tensor;
    // 1. Set canvas dimensions to match the tensor
    const sourceCanvas = document.createElement('canvas');
    sourceCanvas.width = width;
    sourceCanvas.height = height;
    const sourceContext = sourceCanvas.getContext('2d', { willReadFrequently: true });
    const image = sourceContext.createImageData(width, height);
    // 2. Copy RGB values from tensor.pixels into ImageData
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
    // 3. Use putImageData (NOT drawImage) for ImageData objects
    sourceContext.putImageData(image, 0, 0);
    // 4. Send the rendered canvas to your visible <img> element
    const imgElement = document.getElementById("sessionImage"); // Replace with your <img> ID
    if (imgElement) {
        imgElement.src = sourceCanvas.toDataURL("image/png");
    }
}

document.querySelector('#textipy-undo-button').addEventListener('click', () => {
    if (tensorStack.length <= 1) return;
    tensorStack.pop();
    tensor = tensorStack[tensorStack.length - 1];
    updateTensorReadout();
    render();
});


document.addEventListener('keydown', (event) => {
    const isTyping = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName);
    const key = event.key ? event.key.toLowerCase() : "";
    if (key === 't' && !isTyping) {
        event.preventDefault();
        if (floatingPanel) floatingPanel.classList.toggle('hidden');
    }
});

if (closePanelButton) {
    closePanelButton.addEventListener('click', () => {
        if (floatingPanel) floatingPanel.classList.add('hidden');
    });
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
            console.log('Metadata cleared');
        } else {
            alert('Failed to clear metadata');
        }
    } catch (error) {
        console.error('Metadata clear error:', error);
        alert('Error clearing metadata: ' + error.message);
    }
}

if (applyButton) {
    applyButton.addEventListener('click', async () => {
        try {
            const originalText = applyButton.innerHTML;
            applyButton.disabled = true;
            applyButton.innerHTML = "⚡ Baking Tensor...";

            const title = titleInput ? titleInput.value.trim() : '';
            const short_brief = briefInput ? briefInput.value.trim() : '';

            const payload = {
                title: title,
                short_brief: short_brief
            };
            
            const response = await fetch('/api/bake-text', {
                method: 'POST',
                headers: {
                    "Content-Type": "application/json" 
                },
                credentials: "include",
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                console.error("FastAPI Error Detail:", errorData.detail);
                throw new Error(errorData.detail || `Server error: ${response.status}`);
            }

            const updatedTensorData = await response.json();
            tensorStack.push(cloneTensor(updatedTensorData));
            tensor = tensorStack[tensorStack.length - 1];
            currentMetadata = { title: '', short_brief: '' };
            updateTensorReadout();
            render();
            applyButton.disabled = false;
            applyButton.innerHTML = originalText;
            console.log("Tensor updated from backend engine cleanly.");
            titleInput.value = '';
            briefInput.value = '';
        } catch (error) {
            console.error('Tensor apply modification error:', error);
            alert('Error updating image tensor from backend: ' + error.message);
            applyButton.disabled = false;
            applyButton.innerHTML = "⚡ Apply";
        }
    });
}


if (downloadButton) {
    downloadButton.addEventListener('click', () => {
        if (!tensor) return;
        const outputCanvas = document.createElement('canvas');
        outputCanvas.width = tensor.width;
        outputCanvas.height = tensor.height;
        const outputContext = outputCanvas.getContext('2d', { alpha: false });
        const image = outputContext.createImageData(tensor.width, tensor.height);
        tensor.pixels.forEach((row, y) => row.forEach((pixel, x) => {
            const index = (y * tensor.width + x) * 4;
            image.data[index] = pixel[0];
            image.data[index + 1] = pixel[1];
            image.data[index + 2] = pixel[2];
            image.data[index + 3] = 255;
        }));
        outputContext.putImageData(image, 0, 0);
        outputCanvas.toBlob((blob) => {
            if (!blob) return;
            const link = document.createElement('a');
            link.download = 'tensor-text-adjusted.png';
            link.href = URL.createObjectURL(blob);
            link.click();
            URL.revokeObjectURL(link.href);
        }, 'image/png');
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

// Function to load the image tied to the current browser session
function loadSessionImage() {
    const imgElement = document.getElementById("sessionImage");
    // Append timestamp (?t=...) to prevent browser from showing a cached old image
    imgElement.src = "/api/my-session-image?t=" + new Date().getTime();
    imgElement.onload = () => { imgElement.style.display = "block"; };
    imgElement.onerror = () => { imgElement.style.display = "none"; };
}

// Function to upload the selected file using JS fetch
async function uploadImage() {
    const fileInput = document.getElementById("imageInput");
    const statusText = document.getElementById("status");
    if (!fileInput.files.length) {
        statusText.innerText = "Please select an image first.";
        return;
    }
    // 1. Pack the file into FormData (Do NOT set Content-Type header manually)
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    statusText.innerText = "Uploading...";
    try { 
        const response = await fetch("/api/upload-image", {
            method: "POST",
            body: formData
        });
        const result = await response.json();
        if (response.ok) {
            statusText.innerText = result.message;
            loadSessionImage(); 
        } else {
            statusText.innerText = "Error: " + result.detail;
        }
    } catch (err) {
        statusText.innerText = "Network error occurred.";
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadSessionImage();
});