// Global variables
let webSocket = null;
let imageWebSocket = null;
let isConnected = false;
let startTime = null;
let snapshotCounter = 0;
let fpsUpdateInterval = null;

// DOM elements
const videoStream = document.getElementById('video-stream');
const connectionStatus = document.getElementById('connection-status');
const statusValue = document.getElementById('status-value');
const fpsValue = document.getElementById('fps-value');
const resolutionValue = document.getElementById('resolution-value');
const detectionsValue = document.getElementById('detections-value');
const uptimeValue = document.getElementById('uptime-value');
const loadingOverlay = document.getElementById('loading-overlay');
const snapshotBtn = document.getElementById('snapshot-btn');
const fullscreenBtn = document.getElementById('fullscreen-btn');
const confidenceThreshold = document.getElementById('confidence-threshold');
const confidenceValue = document.getElementById('confidence-value');
const aiModel = document.getElementById('ai-model');
const displayFps = document.getElementById('display-fps');
const applySettings = document.getElementById('apply-settings');
const snapshotsGrid = document.getElementById('snapshots-grid');
const snapshotModal = document.getElementById('snapshot-modal');
const modalImage = document.getElementById('modal-image');
const downloadSnapshotBtn = document.getElementById('download-snapshot');
const closeButton = document.querySelector('.close-button');

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

// Initialize the application
function initializeApp() {
    // Update confidence value display
    confidenceThreshold.addEventListener('input', () => {
        confidenceValue.textContent = confidenceThreshold.value;
    });

    // Apply settings button
    applySettings.addEventListener('click', () => {
        applySettingsToServer();
    });

    // Snapshot button
    snapshotBtn.addEventListener('click', () => {
        takeSnapshot();
    });

    // Fullscreen button
    fullscreenBtn.addEventListener('click', () => {
        toggleFullscreen();
    });

    // Modal close button
    closeButton.addEventListener('click', () => {
        snapshotModal.style.display = 'none';
    });

    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === snapshotModal) {
            snapshotModal.style.display = 'none';
        }
    });

    // Download snapshot button
    downloadSnapshotBtn.addEventListener('click', () => {
        downloadSnapshot();
    });

    // Connect to the server
    connectToServer();

    // Start the uptime counter
    startTime = new Date();
    setInterval(updateUptime, 1000);
}

// Connect to the WebSocket server
function connectToServer() {
    // Control WebSocket for sending commands and receiving status updates
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname || 'localhost';
    const port = 8888; // Should match the server port

    // Show loading overlay
    loadingOverlay.style.display = 'flex';
    
    // Create WebSocket connection
    webSocket = new WebSocket(`${protocol}//${host}:${port}/control`);
    
    // WebSocket event handlers
    webSocket.onopen = () => {
        console.log('Control WebSocket connected');
        // Request initial settings
        webSocket.send(JSON.stringify({ command: 'get_settings' }));
    };
    
    webSocket.onclose = () => {
        console.log('Control WebSocket disconnected');
        handleDisconnection();
        
        // Try to reconnect after 5 seconds
        setTimeout(connectToServer, 5000);
    };
    
    webSocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        handleDisconnection();
    };
    
    webSocket.onmessage = (event) => {
        handleWebSocketMessage(event);
    };

    // Image WebSocket for receiving video frames
    imageWebSocket = new WebSocket(`${protocol}//${host}:${port}/video`);
    
    imageWebSocket.onopen = () => {
        console.log('Image WebSocket connected');
    };
    
    imageWebSocket.onclose = () => {
        console.log('Image WebSocket disconnected');
    };
    
    imageWebSocket.onerror = (error) => {
        console.error('Image WebSocket error:', error);
    };
    
    imageWebSocket.onmessage = (event) => {
        handleImageMessage(event);
    };
}

// Handle WebSocket messages
function handleWebSocketMessage(event) {
    try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'status') {
            updateStatus(data);
        } else if (data.type === 'settings') {
            updateSettingsUI(data);
        } else if (data.type === 'stats') {
            updateStats(data);
        } else if (data.type === 'detections') {
            updateDetections(data);
        } else if (data.type === 'error') {
            console.error('Server error:', data.message);
        }
    } catch (error) {
        console.error('Error parsing WebSocket message:', error);
    }
}

// Handle image messages
function handleImageMessage(event) {
    // Convert blob to image URL
    const imageUrl = URL.createObjectURL(event.data);
    
    // Update the video stream
    videoStream.src = imageUrl;
    
    // Hide loading overlay if it's visible
    if (loadingOverlay.style.display === 'flex') {
        loadingOverlay.style.display = 'none';
        
        // Enable controls
        snapshotBtn.disabled = false;
        fullscreenBtn.disabled = false;
        
        // Update connection status
        updateConnectionStatus(true);
    }
    
    // Clean up the object URL to avoid memory leaks
    videoStream.onload = () => {
        URL.revokeObjectURL(imageUrl);
        
        // Update resolution value
        resolutionValue.textContent = `${videoStream.naturalWidth} × ${videoStream.naturalHeight}`;
    };
}

// Update connection status
function updateConnectionStatus(connected) {
    isConnected = connected;
    
    if (connected) {
        connectionStatus.textContent = 'Connected';
        connectionStatus.className = 'status-online';
        statusValue.textContent = 'Connected';
    } else {
        connectionStatus.textContent = 'Disconnected';
        connectionStatus.className = 'status-offline';
        statusValue.textContent = 'Disconnected';
    }
}

// Handle disconnection
function handleDisconnection() {
    updateConnectionStatus(false);
    
    // Disable controls
    snapshotBtn.disabled = true;
    fullscreenBtn.disabled = true;
    
    // Show loading overlay
    loadingOverlay.style.display = 'flex';
    
    // Reset stats
    fpsValue.textContent = '0';
    detectionsValue.textContent = '0';
}

// Update status information
function updateStatus(data) {
    if (data.connected !== undefined) {
        updateConnectionStatus(data.connected);
    }
}

// Update settings UI
function updateSettingsUI(data) {
    if (data.ai_model) {
        aiModel.value = data.ai_model;
    }
    
    if (data.confidence_threshold) {
        confidenceThreshold.value = data.confidence_threshold;
        confidenceValue.textContent = data.confidence_threshold;
    }
    
    if (data.display_fps !== undefined) {
        displayFps.checked = data.display_fps;
    }
}

// Update statistics
function updateStats(data) {
    if (data.fps) {
        fpsValue.textContent = data.fps;
    }
}

// Update detections count
function updateDetections(data) {
    if (data.count !== undefined) {
        detectionsValue.textContent = data.count;
    }
}

// Apply settings to server
function applySettingsToServer() {
    if (!webSocket || webSocket.readyState !== WebSocket.OPEN) {
        console.error('WebSocket not connected');
        return;
    }
    
    const settings = {
        command: 'update_settings',
        ai_model: aiModel.value,
        confidence_threshold: parseFloat(confidenceThreshold.value),
        display_fps: displayFps.checked
    };
    
    webSocket.send(JSON.stringify(settings));
}

// Take a snapshot
function takeSnapshot() {
    if (!isConnected) return;
    
    // Create a canvas element
    const canvas = document.createElement('canvas');
    canvas.width = videoStream.naturalWidth;
    canvas.height = videoStream.naturalHeight;
    
    // Draw the current frame on the canvas
    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoStream, 0, 0, canvas.width, canvas.height);
    
    // Convert canvas to data URL
    const dataUrl = canvas.toDataURL('image/jpeg');
    
    // Create timestamp
    const now = new Date();
    const timestamp = now.toLocaleTimeString();
    
    // Create snapshot item
    const snapshotItem = document.createElement('div');
    snapshotItem.className = 'snapshot-item';
    snapshotItem.innerHTML = `
        <img src="${dataUrl}" alt="Snapshot ${++snapshotCounter}">
        <div class="snapshot-timestamp">${timestamp}</div>
    `;
    
    // Add click event to open modal
    snapshotItem.addEventListener('click', () => {
        modalImage.src = dataUrl;
        snapshotModal.style.display = 'block';
    });
    
    // Add to snapshots grid
    snapshotsGrid.prepend(snapshotItem);
}

// Download snapshot
function downloadSnapshot() {
    if (!modalImage.src) return;
    
    const link = document.createElement('a');
    link.href = modalImage.src;
    link.download = `snapshot_${new Date().toISOString().replace(/:/g, '-')}.jpg`;
    link.click();
}

// Toggle fullscreen
function toggleFullscreen() {
    if (!document.fullscreenElement) {
        if (videoStream.requestFullscreen) {
            videoStream.requestFullscreen();
        } else if (videoStream.webkitRequestFullscreen) {
            videoStream.webkitRequestFullscreen();
        } else if (videoStream.msRequestFullscreen) {
            videoStream.msRequestFullscreen();
        }
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
    }
}

// Update uptime
function updateUptime() {
    if (!startTime) return;
    
    const now = new Date();
    const diff = now - startTime;
    
    // Convert to hours, minutes, seconds
    const hours = Math.floor(diff / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);
    
    // Format as HH:MM:SS
    const formattedTime = [
        hours.toString().padStart(2, '0'),
        minutes.toString().padStart(2, '0'),
        seconds.toString().padStart(2, '0')
    ].join(':');
    
    uptimeValue.textContent = formattedTime;
}
