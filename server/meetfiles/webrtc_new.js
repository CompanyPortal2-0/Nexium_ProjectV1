// Global variables
let localStream = null;
let peerConnections = {};
let socket = null;
let roomId = null;
let userEmail = null;
let username = null;
let participantCount = 0;
let isVideoEnabled = true;
let isAudioEnabled = true;

// DOM elements
const localVideo = document.getElementById('localVideo');
const videoGrid = document.getElementById('videoGrid');
const toggleVideoButton = document.getElementById('toggleVideoButton');
const toggleAudioButton = document.getElementById('toggleAudioButton');
const hangupButton = document.getElementById('hangupButton');
const statusMessage = document.getElementById('statusMessage');
const participantCountElement = document.getElementById('participantCount');
const meetingIdElement = document.getElementById('meetingId');
const loadingElement = document.getElementById('loading');

// WebRTC configuration
const configuration = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' },
        {
            urls: 'turn:openrelay.metered.ca:80',
            username: 'openrelayproject',
            credential: 'openrelayproject'
        },
        {
            urls: 'turn:openrelay.metered.ca:443',
            username: 'openrelayproject',
            credential: 'openrelayproject'
        }
    ],
    iceCandidatePoolSize: 10
};

// Initialize the meeting
async function initMeeting() {
    try {
        // Get meeting ID from URL
        const pathParts = window.location.pathname.split('/');
        roomId = pathParts[pathParts.length - 1];
        
        if (!roomId) {
            showStatus('Error: No meeting ID provided', true);
            return;
        }
        
        meetingIdElement.textContent = `Meeting: ${roomId}`;
        
        // Get user info from localStorage or prompt
        userEmail = localStorage.getItem('userEmail') || prompt('Enter your email:');
        username = localStorage.getItem('username') || prompt('Enter your name:');
        
        if (!userEmail || !username) {
            showStatus('Error: User information required', true);
            return;
        }
        
        // Store for future use
        localStorage.setItem('userEmail', userEmail);
        localStorage.setItem('username', username);
        
        // Get local media stream
        await getLocalStream();
        
        // Connect to signaling server
        connectToSignalingServer();
        
    } catch (error) {
        console.error('Error initializing meeting:', error);
        showStatus('Error: Could not initialize meeting', true);
    }
}

// Get local media stream
async function getLocalStream() {
    try {
        // Check if getUserMedia is supported
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error('getUserMedia is not supported. Please use HTTPS or localhost, or try a different browser.');
        }
        
        localStream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 }
            },
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true
            }
        });
        
        localVideo.srcObject = localStream;
        showStatus('Camera and microphone ready');
        
    } catch (error) {
        console.error('Error accessing media devices:', error);
        
        // Provide detailed error message
        let errorMsg = 'Error: Could not access camera/microphone. ';
        if (error.name === 'NotAllowedError') {
            errorMsg += 'Permission denied. Please allow camera/microphone access.';
        } else if (error.name === 'NotFoundError') {
            errorMsg += 'No camera or microphone found.';
        } else if (error.message.includes('getUserMedia')) {
            errorMsg += 'Please use HTTPS, localhost, or 127.0.0.1 instead of IP address.';
        } else {
            errorMsg += error.message;
        }
        
        showStatus(errorMsg, true);
        throw error;
    }
}

// Connect to signaling server
function connectToSignalingServer() {
    // Use the current page's protocol and host
    const protocol = window.location.protocol === 'https:' ? 'https' : 'http';
    const serverUrl = `${protocol}://${window.location.host}`;
    
    console.log('Connecting to signaling server:', serverUrl);
    
    socket = io(serverUrl, {
        query: {
            customId: userEmail,
            username: username
        },
        transports: ['polling', 'websocket'],  // Try polling first, then upgrade to websocket
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        reconnectionAttempts: 5
    });
    
    // Socket event handlers
    socket.on('connect', () => {
        console.log('Connected to signaling server');
        showStatus('Connected to server');
        
        // Join the meeting room
        socket.emit('join', {
            room: roomId,
            userEmail: userEmail,
            username: username
        });
    });
    
    socket.on('connected', (data) => {
        console.log('Server connection confirmed:', data);
    });
    
    socket.on('room-joined', (data) => {
        console.log('Joined room:', data);
        showStatus(`Joined meeting: ${data.room}`);
        loadingElement.style.display = 'none';
        
        updateParticipantCount(data.peers.length + 1);
        
        // Create peer connections for existing participants
        if (data.peers && data.peers.length > 0) {
            data.peers.forEach((peerId, index) => {
                setTimeout(() => {
                    createPeerConnection(peerId, true);
                }, index * 500); // Stagger connection creation
            });
        }
    });
    
    socket.on('new-peer', (data) => {
        console.log('New peer joined:', data);
        showStatus(`${data.username} joined the meeting`);
        
        // Create peer connection (don't send offer, wait for it)
        createPeerConnection(data.peerId, false);
        updateParticipantCount(participantCount + 1);
    });
    
    socket.on('peer-disconnected', (data) => {
        console.log('Peer disconnected:', data);
        showStatus(`${data.username || 'Participant'} left the meeting`);
        
        removePeerConnection(data.peerId);
        updateParticipantCount(participantCount - 1);
    });
    
    socket.on('offer', async (data) => {
        console.log('Received offer from:', data.peerId);
        
        if (!peerConnections[data.peerId]) {
            createPeerConnection(data.peerId, false);
        }
        
        await handleOffer(data.peerId, data.offer);
    });
    
    socket.on('answer', async (data) => {
        console.log('Received answer from:', data.peerId);
        await handleAnswer(data.peerId, data.answer);
    });
    
    socket.on('ice-candidate', async (data) => {
        console.log('Received ICE candidate from:', data.peerId);
        await handleIceCandidate(data.peerId, data.candidate);
    });
    
    socket.on('error', (data) => {
        console.error('Socket error:', data);
        showStatus(`Error: ${data.message}`, true);
    });
    
    socket.on('disconnect', () => {
        console.log('Disconnected from signaling server');
        showStatus('Disconnected from server', true);
    });
    
    socket.on('connect_error', (error) => {
        console.error('Connection error:', error);
        showStatus('Failed to connect to server. Please check your connection.', true);
    });
    
    socket.on('reconnect', (attemptNumber) => {
        console.log('Reconnected after', attemptNumber, 'attempts');
        showStatus('Reconnected to server');
    });
    
    socket.on('reconnect_failed', () => {
        console.error('Failed to reconnect');
        showStatus('Could not reconnect to server. Please refresh the page.', true);
    });
}

// Create peer connection
function createPeerConnection(peerId, shouldCreateOffer) {
    console.log(`Creating peer connection for: ${peerId}`);
    
    const pc = new RTCPeerConnection(configuration);
    peerConnections[peerId] = pc;
    
    // Add local stream tracks
    localStream.getTracks().forEach(track => {
        pc.addTrack(track, localStream);
    });
    
    // Handle incoming tracks
    pc.ontrack = (event) => {
        console.log('Received remote track from:', peerId);
        addRemoteVideo(peerId, event.streams[0]);
    };
    
    // Handle ICE candidates
    pc.onicecandidate = (event) => {
        if (event.candidate) {
            socket.emit('ice-candidate', {
                room: roomId,
                targetId: peerId,
                candidate: event.candidate
            });
        }
    };
    
    // Handle connection state changes
    pc.onconnectionstatechange = () => {
        console.log(`Peer ${peerId} connection state:`, pc.connectionState);
        
        if (pc.connectionState === 'disconnected' || pc.connectionState === 'failed') {
            console.log(`Peer ${peerId} connection failed, removing...`);
            removePeerConnection(peerId);
        }
    };
    
    // Create offer if this peer should initiate
    if (shouldCreateOffer) {
        setTimeout(() => {
            createOffer(peerId);
        }, 100);
    }
}

// Create and send offer
async function createOffer(peerId) {
    try {
        const pc = peerConnections[peerId];
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);
        
        socket.emit('offer', {
            room: roomId,
            targetId: peerId,
            offer: offer
        });
        
        console.log('Sent offer to:', peerId);
    } catch (error) {
        console.error('Error creating offer:', error);
    }
}

// Handle incoming offer
async function handleOffer(peerId, offer) {
    try {
        const pc = peerConnections[peerId];
        await pc.setRemoteDescription(new RTCSessionDescription(offer));
        
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);
        
        socket.emit('answer', {
            room: roomId,
            targetId: peerId,
            answer: answer
        });
        
        console.log('Sent answer to:', peerId);
    } catch (error) {
        console.error('Error handling offer:', error);
    }
}

// Handle incoming answer
async function handleAnswer(peerId, answer) {
    try {
        const pc = peerConnections[peerId];
        await pc.setRemoteDescription(new RTCSessionDescription(answer));
        console.log('Set remote description from answer');
    } catch (error) {
        console.error('Error handling answer:', error);
    }
}

// Handle ICE candidate
async function handleIceCandidate(peerId, candidate) {
    try {
        const pc = peerConnections[peerId];
        if (pc) {
            await pc.addIceCandidate(new RTCIceCandidate(candidate));
        }
    } catch (error) {
        console.error('Error adding ICE candidate:', error);
    }
}

// Add remote video to UI
function addRemoteVideo(peerId, stream) {
    // Check if video already exists
    let videoElement = document.getElementById(`video-${peerId}`);
    
    if (!videoElement) {
        const videoContainer = document.createElement('div');
        videoContainer.className = 'video-item';
        videoContainer.id = `video-${peerId}`;
        
        const video = document.createElement('video');
        video.autoplay = true;
        video.playsInline = true;
        video.srcObject = stream;
        
        const nameLabel = document.createElement('div');
        nameLabel.className = 'peer-name';
        nameLabel.textContent = peerId.substring(0, 8) + '...';
        
        videoContainer.appendChild(video);
        videoContainer.appendChild(nameLabel);
        videoGrid.appendChild(videoContainer);
    } else {
        // Update existing video
        const video = videoElement.querySelector('video');
        if (video) {
            video.srcObject = stream;
        }
    }
}

// Remove peer connection
function removePeerConnection(peerId) {
    // Close peer connection
    if (peerConnections[peerId]) {
        peerConnections[peerId].close();
        delete peerConnections[peerId];
    }
    
    // Remove video element
    const videoElement = document.getElementById(`video-${peerId}`);
    if (videoElement) {
        videoElement.remove();
    }
}

// Toggle video
function toggleVideo() {
    isVideoEnabled = !isVideoEnabled;
    
    localStream.getVideoTracks().forEach(track => {
        track.enabled = isVideoEnabled;
    });
    
    if (isVideoEnabled) {
        toggleVideoButton.textContent = '📹 Video On';
        toggleVideoButton.classList.remove('off');
    } else {
        toggleVideoButton.textContent = '📹 Video Off';
        toggleVideoButton.classList.add('off');
    }
}

// Toggle audio
function toggleAudio() {
    isAudioEnabled = !isAudioEnabled;
    
    localStream.getAudioTracks().forEach(track => {
        track.enabled = isAudioEnabled;
    });
    
    if (isAudioEnabled) {
        toggleAudioButton.textContent = '🎤 Audio On';
        toggleAudioButton.classList.remove('off');
    } else {
        toggleAudioButton.textContent = '🎤 Audio Off';
        toggleAudioButton.classList.add('off');
    }
}

// Leave meeting
function leaveMeeting() {
    // Stop all tracks
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
    }
    
    // Close all peer connections
    Object.values(peerConnections).forEach(pc => pc.close());
    peerConnections = {};
    
    // Leave room via socket
    if (socket) {
        socket.emit('leave', { room: roomId });
        socket.disconnect();
    }
    
    // Redirect or show goodbye message
    showStatus('You have left the meeting', true);
    setTimeout(() => {
        window.location.href = '/';
    }, 2000);
}

// Update participant count
function updateParticipantCount(count) {
    participantCount = count;
    participantCountElement.textContent = `👥 ${count}`;
}

// Show status message
function showStatus(message, isError = false) {
    statusMessage.textContent = message;
    statusMessage.className = 'status-message show';
    statusMessage.style.backgroundColor = isError ? 'rgba(231, 76, 60, 0.9)' : 'rgba(46, 204, 113, 0.9)';
    
    setTimeout(() => {
        statusMessage.classList.remove('show');
    }, 3000);
}

// Event listeners
toggleVideoButton.addEventListener('click', toggleVideo);
toggleAudioButton.addEventListener('click', toggleAudio);
hangupButton.addEventListener('click', leaveMeeting);

// Handle page unload
window.addEventListener('beforeunload', () => {
    leaveMeeting();
});

// Initialize when page loads
window.addEventListener('load', initMeeting);
