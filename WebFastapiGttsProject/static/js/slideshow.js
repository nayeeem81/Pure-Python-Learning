let images = [];
let currentIdx = 0;
const slides = [document.getElementById('slide1'), document.getElementById('slide2')];
let activeSlideIdx = 0;
let slideshowInterval = null;

// MP3 Playlist state
let mp3Playlist = [];
let currentTrackIdx = 0;
let isPlaylistMode = false;

const audioElement = document.getElementById('audio-element');

// Fetch current saved state configurations on load
async function loadCurrentConfig() {
    try {
        const res = await fetch('/api/config');
        const config = await res.json();
        if (config.image_folder) document.getElementById('img-path-input').value = config.image_folder;
        if (config.mp3_folder_path) document.getElementById('mp3-path-input').value = config.mp3_folder_path;

        if (config.image_folder || config.mp3_folder_path) {
            initializeMedia();
        }
    } catch (err) {
        console.error('Failed to load config:', err.message);
    }
}

// Post new folder layouts to FastAPI
async function savePaths() {
    const image_folder = document.getElementById('img-path-input').value;
    const mp3_folder_path = document.getElementById('mp3-path-input').value;

    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image_folder, mp3_folder_path })
        });

        if (response.ok) {
            alert("Paths initialized successfully!");
            initializeMedia();
        } else {
            const errData = await response.json();
            alert("Error: " + errData.detail);
        }
    } catch (err) {
        alert("Failed to connect to API: " + err.message);
    }
}

async function initializeMedia() {
    // Stop existing timeline loop if active
    if (slideshowInterval) clearInterval(slideshowInterval);

    // Stop audio playback
    audioElement.pause();
    audioElement.src = '';

    // 1. Boot up Audio Player and load playlist
    document.getElementById('floating-player').style.display = 'block';
    await loadMp3Playlist();

    // 2. Fetch and initialize image slideshow
    try {
        const response = await fetch('/api/images');
        const data = await response.json();
        images = data.images || [];

        if (images.length > 0) {
            // Fisher-Yates shuffle
            for (let i = images.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [images[i], images[j]] = [images[j], images[i]];
            }
            currentIdx = 0;
            changeImage();
            slideshowInterval = setInterval(changeImage, 5000);
        }
    } catch (err) {
        console.error("Error loading images:", err.message);
    }
}

// Load MP3 playlist from configured folder
async function loadMp3Playlist() {
    try {
        const response = await fetch('/api/mp3-files');
        const data = await response.json();
        mp3Playlist = data.files || [];
        isPlaylistMode = mp3Playlist.length > 0;
        currentTrackIdx = 0;

        if (isPlaylistMode) {
            loadNextTrack();
            updateTrackInfo();
        } else {
            document.getElementById('current-track-info').textContent = 'No MP3 files found';
        }
    } catch (err) {
        console.error("Error loading MP3 playlist:", err.message);
        document.getElementById('current-track-info').textContent = 'Failed to load playlist';
    }
}

// Load the current track in the audio element
function loadNextTrack() {
    if (!isPlaylistMode || mp3Playlist.length === 0) return;

    const filename = mp3Playlist[currentTrackIdx];
    audioElement.src = `/api/mp3/${encodeURIComponent(filename)}?t=${new Date().getTime()}`;
    updateTrackInfo();
}

// Update track info display
function updateTrackInfo() {
    if (!isPlaylistMode) return;
    const filename = mp3Playlist[currentTrackIdx];
    const info = `Track ${currentTrackIdx + 1}/${mp3Playlist.length}: ${filename}`;
    document.getElementById('current-track-info').textContent = info;
}

// Audio control functions
function playAudio() {
    if (isPlaylistMode && audioElement.src === '') {
        loadNextTrack();
    }
    audioElement.play().catch(err => console.error('Play error:', err));
}

function pauseAudio() {
    audioElement.pause();
}

function stopAudio() {
    audioElement.pause();
    audioElement.currentTime = 0;
}

// Advance to next track when current ends
audioElement.addEventListener('ended', () => {
    if (isPlaylistMode) {
        currentTrackIdx = (currentTrackIdx + 1) % mp3Playlist.length;
        loadNextTrack();
        playAudio();
    }
});

function changeImage() {
    if (images.length === 0) return;
    const nextSlideIdx = 1 - activeSlideIdx;
    const imgUrl = `/api/images/${encodeURIComponent(images[currentIdx])}?t=${new Date().getTime()}`;

    slides[nextSlideIdx].style.backgroundImage = `url('${imgUrl}')`;
    slides[nextSlideIdx].classList.add('active');
    slides[activeSlideIdx].classList.remove('active');

    activeSlideIdx = nextSlideIdx;
    currentIdx = (currentIdx + 1) % images.length;
}

// Generic panel dragging assignment utility logic
function makeElementDraggable(panel, header) {
    let isDragging = false, offsetX = 0, offsetY = 0;
    header.addEventListener('mousedown', (e) => {
        if (e.target.classList.contains('close-btn')) return;
        isDragging = true;
        offsetX = e.clientX - panel.offsetLeft;
        offsetY = e.clientY - panel.offsetTop;
    });
    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        panel.style.left = `${e.clientX - offsetX}px`;
        panel.style.top = `${e.clientY - offsetY}px`;
    });
    document.addEventListener('mouseup', () => isDragging = false);
}

makeElementDraggable(document.getElementById('config-panel'), document.getElementById('config-header'));
makeElementDraggable(document.getElementById('floating-player'), document.getElementById('player-header'));

function togglePlayer(show) {
    document.getElementById('floating-player').style.display = show ? 'block' : 'none';
}

// Fullscreen functionality
function requestFullscreen() {
    const container = document.getElementById('canvas-container');
    if (container.requestFullscreen) {
        container.requestFullscreen().catch(err => {
            console.error('Fullscreen request failed:', err.message);
        });
    } else if (container.webkitRequestFullscreen) {
        container.webkitRequestFullscreen();
    } else if (container.mozRequestFullScreen) {
        container.mozRequestFullScreen();
    } else if (container.msRequestFullscreen) {
        container.msRequestFullscreen();
    }
}

// Handle fullscreen change events
document.addEventListener('fullscreenchange', updateFullscreenUI);
document.addEventListener('webkitfullscreenchange', updateFullscreenUI);
document.addEventListener('mozfullscreenchange', updateFullscreenUI);
document.addEventListener('msfullscreenchange', updateFullscreenUI);

function updateFullscreenUI() {
    const exitBtn = document.getElementById('exit-fullscreen-btn');
    const isFullscreen = document.fullscreenElement || 
                        document.webkitFullscreenElement || 
                        document.mozFullScreenElement || 
                        document.msFullscreenElement;

    exitBtn.style.display = isFullscreen ? 'block' : 'none';
}

// Exit fullscreen handler
document.getElementById('exit-fullscreen-btn').addEventListener('click', () => {
    if (document.exitFullscreen) {
        document.exitFullscreen();
    } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
    } else if (document.mozCancelFullScreen) {
        document.mozCancelFullScreen();
    } else if (document.msExitFullscreen) {
        document.msExitFullscreen();
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Skip if user is typing in an input field
    const isInputElement = ['INPUT', 'TEXTAREA'].includes(e.target.tagName) || 
                          e.target.contentEditable === 'true';
    if (isInputElement) return;

    if (e.key.toLowerCase() === 'm') {
        const playerPanel = document.getElementById('floating-player');
        const configPanel = document.getElementById('config-panel');
        // Toggle both panels together
        const shouldShow = playerPanel.style.display === 'none';
        playerPanel.style.display = shouldShow ? 'block' : 'none';
        configPanel.style.display = shouldShow ? 'block' : 'none';
    }

    // ESC key exits fullscreen (browser handles this natively, but we ensure it works)
    if (e.key === 'Escape') {
        const isFullscreen = document.fullscreenElement || 
                            document.webkitFullscreenElement || 
                            document.mozFullScreenElement || 
                            document.msFullscreenElement;
        if (isFullscreen) {
            if (document.exitFullscreen) document.exitFullscreen();
        }
    }
});

loadCurrentConfig();