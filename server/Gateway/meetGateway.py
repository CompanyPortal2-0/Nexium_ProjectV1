from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import socketio
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Gateway SocketIO server (facing clients)
gateway_io = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Store separate backend connections for each client
client_connections = {}  # {gateway_client_sid: backend_socketio_client}

BACKEND_SERVER_URL = 'https://192.168.100.190:7053'


def create_backend_connection(client_sid, user_email=None):
    """Create a dedicated backend connection for a client"""
    # Connect with user_email as query parameter if provided
    connection_url = BACKEND_SERVER_URL
    if user_email:
        connection_url = f"{BACKEND_SERVER_URL}?user_email={user_email}"
    
    backend = socketio.Client(
        logger=False, 
        engineio_logger=False,
        ssl_verify=False  # For self-signed certificates
    )
    
    # Setup event handlers for this specific backend connection
    @backend.on('room-joined')
    def on_room_joined(data):
        logger.info(f"Backend -> Client {client_sid}: room-joined")
        gateway_io.emit('room-joined', data, to=client_sid)
    
    @backend.on('new-peer')
    def on_new_peer(data):
        logger.info(f"Backend -> Client {client_sid}: new-peer {data.get('peerId')}")
        gateway_io.emit('new-peer', data, to=client_sid)
    
    @backend.on('peer-disconnected')
    def on_peer_disconnected(data):
        logger.info(f"Backend -> Client {client_sid}: peer-disconnected {data.get('peerId')}")
        gateway_io.emit('peer-disconnected', data, to=client_sid)
    
    @backend.on('offer')
    def on_offer(data):
        logger.info(f"Backend -> Client {client_sid}: offer from {data.get('peerId')}")
        gateway_io.emit('offer', data, to=client_sid)
    
    @backend.on('answer')
    def on_answer(data):
        logger.info(f"Backend -> Client {client_sid}: answer from {data.get('peerId')}")
        gateway_io.emit('answer', data, to=client_sid)
    
    @backend.on('ice-candidate')
    def on_ice_candidate(data):
        logger.info(f"Backend -> Client {client_sid}: ice-candidate from {data.get('peerId')}")
        gateway_io.emit('ice-candidate', data, to=client_sid)
    
    try:
        backend.connect(connection_url)
        logger.info(f"✅ Created backend connection for client {client_sid}")
        return backend
    except Exception as e:
        logger.error(f"❌ Failed to connect to backend for client {client_sid}: {e}")
        return None


# ============= HTTP ROUTES (REST API FORWARDING) =============

@app.route('/create-meet', methods=['POST'])
def create_meet():
    """Forward create-meet request to backend"""
    try:
        logger.info("Forwarding create-meet request to backend")
        response = requests.post(
            f"{BACKEND_SERVER_URL}/create-meet",
            json=request.json,
            verify=False  # For self-signed certificates
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error forwarding create-meet: {e}")
        return jsonify({"error": "Gateway error"}), 500


@app.route('/join-meet', methods=['POST'])
def join_meet():
    """Forward join-meet request to backend"""
    try:
        logger.info("Forwarding join-meet request to backend")
        response = requests.post(
            f"{BACKEND_SERVER_URL}/join-meet",
            json=request.json,
            verify=False  # For self-signed certificates
        )
        
        # Modify the redirect URL to point to gateway instead of backend
        if response.status_code == 200:
            data = response.json()
            if 'redirectUrl' in data:
                # Replace backend URL with gateway URL
                original_url = data['redirectUrl']
                # Extract path after domain
                path = original_url.split('/', 3)[-1] if '/' in original_url else ''
                data['redirectUrl'] = f"http://localhost:5001/{path}"
            return jsonify(data), response.status_code
        
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error forwarding join-meet: {e}")
        return jsonify({"error": "Gateway error"}), 500


@app.route('/room/<meet_id>/<user_email>')
def room(meet_id, user_email):
    """Forward room page request to backend"""
    try:
        logger.info(f"Forwarding room request for {meet_id}/{user_email}")
        response = requests.get(
            f"{BACKEND_SERVER_URL}/room/{meet_id}/{user_email}",
            verify=False  # For self-signed certificates
        )
        
        if response.status_code == 200:
            # Replace backend server URL with gateway URL in the HTML
            html_content = response.text
            html_content = html_content.replace(
                'server="https://192.168.100.183:7053"',
                'server="http://localhost:5001"'
            )
            return html_content, 200
        else:
            return response.text, response.status_code
            
    except Exception as e:
        logger.error(f"Error forwarding room request: {e}")
        return "Gateway error", 500


# ============= WEBSOCKET EVENT HANDLERS =============

@gateway_io.on('connect')
def handle_client_connect():
    """Client connected to gateway - create dedicated backend connection"""
    client_sid = request.sid
    user_email = request.args.get('user_email')
    logger.info(f"✅ Client connected: {client_sid} (email: {user_email})")
    
    # Create a dedicated backend connection for this client
    backend = create_backend_connection(client_sid, user_email)
    if backend:
        client_connections[client_sid] = {
            'backend': backend,
            'user_email': user_email
        }
    else:
        emit('error', 'Failed to connect to meeting server')


@gateway_io.on('disconnect')
def handle_client_disconnect():
    """Client disconnected - cleanup backend connection"""
    client_sid = request.sid
    logger.info(f"❌ Client disconnected: {client_sid}")
    
    # Disconnect and cleanup backend connection
    if client_sid in client_connections:
        try:
            client_connections[client_sid]['backend'].disconnect()
        except:
            pass
        del client_connections[client_sid]


@gateway_io.on('join')
def handle_join(data):
    """Forward join event to backend"""
    client_sid = request.sid
    logger.info(f"Client {client_sid} -> Backend: join room {data.get('room')}")
    
    if client_sid in client_connections:
        client_connections[client_sid]['backend'].emit('join', data)


@gateway_io.on('leave')
def handle_leave(data):
    """Forward leave event to backend"""
    client_sid = request.sid
    logger.info(f"Client {client_sid} -> Backend: leave room {data.get('room')}")
    
    if client_sid in client_connections:
        client_connections[client_sid]['backend'].emit('leave', data)


@gateway_io.on('offer')
def handle_offer(data):
    """Forward WebRTC offer to backend"""
    client_sid = request.sid
    logger.info(f"Client {client_sid} -> Backend: offer to {data.get('targetId')}")
    
    if client_sid in client_connections:
        client_connections[client_sid]['backend'].emit('offer', data)


@gateway_io.on('answer')
def handle_answer(data):
    """Forward WebRTC answer to backend"""
    client_sid = request.sid
    logger.info(f"Client {client_sid} -> Backend: answer to {data.get('targetId')}")
    
    if client_sid in client_connections:
        client_connections[client_sid]['backend'].emit('answer', data)


@gateway_io.on('ice-candidate')
def handle_ice_candidate(data):
    """Forward ICE candidate to backend"""
    client_sid = request.sid
    logger.info(f"Client {client_sid} -> Backend: ice-candidate to {data.get('targetId')}")
    
    if client_sid in client_connections:
        client_connections[client_sid]['backend'].emit('ice-candidate', data)


@app.route('/health')
def health_check():
    """Health check endpoint"""
    active_connections = len(client_connections)
    connected_backends = sum(
        1 for c in client_connections.values() 
        if c['backend'].connected
    )
    
    return jsonify({
        "status": "ok",
        "gateway": "running",
        "active_clients": active_connections,
        "connected_backends": connected_backends,
        "backend_server": BACKEND_SERVER_URL
    })


if __name__ == '__main__':
    logger.info("🚀 Starting Meeting Gateway Server...")
    logger.info(f"📡 Backend server: {BACKEND_SERVER_URL}")
    logger.info(f"🌐 Gateway listening on port 5001")
    
    # Disable SSL warnings for self-signed certificates
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    gateway_io.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True , ssl_context=('meetingService\\certifs\\cert.pem', 'meetingService\\certifs\\key.pem'))