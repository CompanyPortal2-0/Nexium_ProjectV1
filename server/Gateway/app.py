from flask import Flask, jsonify, render_template, session, send_from_directory, request, redirect
from dotenv import load_dotenv
import os
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import requests
import json
import secrets
import string
from dotenv import load_dotenv
from modeles.role import ROLE
from modeles.department import Department

from flask_cors import CORS
from flask_socketio import SocketIO, emit
import socketio

load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
GameServerSocket = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
MeetingServerSocket = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

client_connections_Game = {} 
client_connections_meeting = {}

AUTH_server = os.getenv('AUTH_SERVER')
SAVING_server = os.getenv('SAVING_server')
UserServices = os.getenv('UserServices_server')
Game_server = os.getenv('Game_server')
Meet_server = os.getenv('Meet_server')
app.secret_key = 'your-super-secret-jwt-token-with-at-least-32-characters-long'#hadhi nafesha fel .env ta3 image docker



jwt = JWTManager(app)




def create_GameServer_connection(client_sid):
    """Create a dedicated backend connection for a client"""
    backend = socketio.Client(logger=False, engineio_logger=False)
    
    # Setup event handlers for this specific backend connection
    @backend.on('matchCreated')
    def on_match_created(data):
        print(f"Backend -> Client {client_sid}: matchCreated {data}")
        GameServerSocket.emit('matchCreated', data, to=client_sid)
    
    @backend.on('matchJoined')
    def on_match_joined(data):
        print(f"Backend -> Client {client_sid}: matchJoined {data}")
        GameServerSocket.emit('matchJoined', data, to=client_sid)
    
    @backend.on('gameState')
    def on_game_state(data):
        print(f"Backend -> Client {client_sid}: gameState")
        GameServerSocket.emit('gameState', data, to=client_sid)
    
    @backend.on('error')
    def on_error(data):
        print(f"Backend -> Client {client_sid}: error {data}")
        GameServerSocket.emit('error', data, to=client_sid)
    
    try:
        backend.connect(Game_server)
        print(f"✅ Created backend connection for client {client_sid}")
        return backend
    except Exception as e:
        print(f"❌ Failed to connect to backend for client {client_sid}: {e}")
        return None


def create_MeetServer_connection(client_sid, user_email=None):
    """Create a dedicated backend connection for a client"""
    # Connect with user_email as query parameter if provided
    connection_url = Meet_server
    if user_email:
        connection_url = f"{Meet_server}?user_email={user_email}"
    
    backend = socketio.Client(
        logger=False, 
        engineio_logger=False,
        ssl_verify=False  # For self-signed certificates
    )
    
    # Setup event handlers for this specific backend connection
    @backend.on('room-joined')
    def on_room_joined(data):
        print(f"Backend -> Client {client_sid}: room-joined")
        MeetingServerSocket.emit('room-joined', data, to=client_sid)
    
    @backend.on('new-peer')
    def on_new_peer(data):
        print(f"Backend -> Client {client_sid}: new-peer {data.get('peerId')}")
        MeetingServerSocket.emit('new-peer', data, to=client_sid)
    
    @backend.on('peer-disconnected')
    def on_peer_disconnected(data):
        print(f"Backend -> Client {client_sid}: peer-disconnected {data.get('peerId')}")
        MeetingServerSocket.emit('peer-disconnected', data, to=client_sid)
    
    @backend.on('offer')
    def on_offer(data):
        print(f"Backend -> Client {client_sid}: offer from {data.get('peerId')}")
        MeetingServerSocket.emit('offer', data, to=client_sid)
    
    @backend.on('answer')
    def on_answer(data):
        print(f"Backend -> Client {client_sid}: answer from {data.get('peerId')}")
        MeetingServerSocket.emit('answer', data, to=client_sid)
    
    @backend.on('ice-candidate')
    def on_ice_candidate(data):
        print(f"Backend -> Client {client_sid}: ice-candidate from {data.get('peerId')}")
        MeetingServerSocket.emit('ice-candidate', data, to=client_sid)
    
    try:
        backend.connect(connection_url)
        print(f"✅ Created backend connection for client {client_sid}")
        return backend
    except Exception as e:
        print(f"❌ Failed to connect to backend for client {client_sid}: {e}")
        return None











# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    """
    Kubernetes health check endpoint
    Returns detailed health status of gateway and downstream services
    """
    health_status = {
        "status": "healthy",
        "service": "gateway",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "pod_name": os.getenv('POD_NAME', 'unknown'),
        "pod_ip": os.getenv('POD_IP', 'unknown'),
    }
    
    # Check if it's a liveness or readiness probe
    check_type = request.headers.get('X-Health-Check', 'general')
    
    if check_type == 'readiness':
        # For readiness probe, check downstream services
        downstream_services = {
            'auth-service': AUTH_SERVER,
            'user-service': USER_SERVICE,
            'saving-service': SAVING_SERVER
        }
        
        services_status = {}
        all_healthy = True
        
        for service_name, service_url in downstream_services.items():
            try:
                response = requests.get(
                    f"{service_url}/health",
                    timeout=2
                )
                services_status[service_name] = {
                    'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                    'response_time': response.elapsed.total_seconds()
                }
            except Exception as e:
                services_status[service_name] = {
                    'status': 'unreachable',
                    'error': str(e)
                }
                all_healthy = False
        
        health_status['downstream_services'] = services_status
        health_status['status'] = 'healthy' if all_healthy else 'degraded'
        
        if not all_healthy:
            return jsonify(health_status), 503
    
    return jsonify(health_status), 200

# Readiness check (simple version)
@app.route('/ready', methods=['GET'])
def ready():
    """Simple readiness check"""
    return jsonify({"status": "ready"}), 200

# Liveness check (simple version)
@app.route('/live', methods=['GET'])
def live():
    """Simple liveness check"""
    return jsonify({"status": "alive"}), 200

# Metrics endpoint (for Prometheus - optional)
@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    # TODO: Implement actual metrics collection
    return """# HELP gateway_requests_total Total requests
# TYPE gateway_requests_total counter
gateway_requests_total 0
""", 200, {'Content-Type': 'text/plain'}















@app.route('/login',methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    print(email,password)
    

    
    if (email is None) or (password is None):
        return jsonify({"Text": "missing content"}), 401
    else :
        return requests.post(f'http://{AUTH_server}/login',json=data).json() , 200
    
@app.route('/signup', methods=['POST'])
def signUp():
    data = request.get_json()

    email = data.get('email')
    firstName = data.get('FirstName')
    lastName = data.get('LastName')
    Password = data.get('Password')
    DateOfBirth = data.get('DateOfBirth')
    address = data.get('Address')
    ManagerCode = data.get('managercode')
    

    # Validate required fields
    if not all([email, firstName, lastName, Password, DateOfBirth, address]):
        return jsonify({"Text": "Missing required fields"}), 400
    
    response_from_auth_service = requests.get(f'http://{AUTH_server}/signup',json={
        "email":email,
        "Password":Password
    })

    if (response_from_auth_service.status_code == 200) :
        
        response_from_auth_service_data = response_from_auth_service.json()
            
            # Check if it's a string (might be double-encoded)
        if isinstance(response_from_auth_service_data, str):
                response_from_auth_service_data = json.loads(response_from_auth_service_data)
            
        print("Parsed data:", response_from_auth_service_data)
            
        id = response_from_auth_service_data.get("id")
        user_data = {
                "email": email,
                "password": "temp_password_not_us11447DDDD@@@ed",  
                "role": ROLE.EMPLOYER.value,
                "first_name": firstName,
                "last_name": lastName,
                "address": address,
                "department": "hadhi n3amerha mba3ed",
                "userID": id,  
                "date_of_birth":DateOfBirth
            }
        HEADERS = {"X-Internal-Key": "INTERNAL_API_KEY"} #INTERNAL_API_KEY badelha fe .env

        response_from_saving_service = requests.post(f'http://{SAVING_server}/users/',json=user_data,headers=HEADERS)
        if (response_from_saving_service.status_code == 200):
            return jsonify({"AuthToken": {response_from_auth_service.json().get("Token")}}), 200
        else : 
            return jsonify({"error": "we get an error from saving error"}), 500
    else : 
        return jsonify({"error": "we get an error from auth service"}), 500
    
   
@app.route('/getCodeForManager', methods=['POST'])
@jwt_required()
def getCode():
    """
    Gateway endpoint - forwards request to UserServices
    UserServices handles all business logic
    """
    try:
        # Get current user's email from JWT token
        current_user_email = get_jwt_identity()
        
        # Get manager email from request body
        data = request.get_json()
        manager_email = data.get('managermail')
        
        if not manager_email:
            return jsonify({"Text": "Manager email is required"}), 400
        
        # Forward entire request to UserServices
        response = requests.post(
            f'http://{UserServices}/getCodeForManager',
            json={
                "current_user_email": current_user_email,
                "manager_email": manager_email
            },
            timeout=10
        )
        
        # Return UserServices response directly
        return response.json(), response.status_code
        
    except requests.exceptions.RequestException as e:
        return jsonify({"Text": f"Service communication error: {str(e)}"}), 503
    except Exception as e:
        return jsonify({"Text": f"Internal error: {str(e)}"}), 500







####################GAME####################

@GameServerSocket.on('connect')
def handle_client_connect():
    """Client connected to gateway - create dedicated backend connection"""
    client_sid = request.sid
    print(f"✅ Client connected: {client_sid}")
    
    # Create a dedicated backend connection for this client
    backend = create_GameServer_connection(client_sid)
    if backend:
        client_connections_Game[client_sid] = backend
    else:
        emit('error', 'Failed to connect to game server')


@GameServerSocket.on('disconnect')
def handle_client_disconnect():
    """Client disconnected - cleanup backend connection"""
    client_sid = request.sid
    print(f"❌ Client disconnected: {client_sid}")
    
    # Disconnect and cleanup backend connection
    if client_sid in client_connections_Game:
        try:
            client_connections_Game[client_sid].disconnect()
        except:
            pass
        del client_connections_Game[client_sid]


@GameServerSocket.on('createMatch')
def handle_create_match():
    """Forward createMatch to backend"""
    client_sid = request.sid
    print(f"Client {client_sid} -> Backend: createMatch")
    
    if client_sid in client_connections_Game:
        client_connections_Game[client_sid].emit('createMatch')


@GameServerSocket.on('joinMatch')
def handle_join_match(match_code):
    """Forward joinMatch to backend"""
    client_sid = request.sid
    print(f"Client {client_sid} -> Backend: joinMatch {match_code}")
    
    if client_sid in client_connections_Game:
        client_connections_Game[client_sid].emit('joinMatch', match_code)


@GameServerSocket.on('makeMove')
def handle_make_move(data):
    """Forward makeMove to backend"""
    client_sid = request.sid
    print(f"Client {client_sid} -> Backend: makeMove")
    
    if client_sid in client_connections_Game:
        client_connections_Game[client_sid].emit('makeMove', data)


@GameServerSocket.on('restartGame')
def handle_restart_game(match_code):
    """Forward restartGame to backend"""
    client_sid = request.sid
    print(f"Client {client_sid} -> Backend: restartGame {match_code}")
    
    if client_sid in client_connections_Game:
        client_connections_Game[client_sid].emit('restartGame', match_code)



######### MEET #######################

@app.route('/create-meet', methods=['POST'])
def create_meet():
    """Forward create-meet request to backend"""
    try:
        print("Forwarding create-meet request to backend")
        response = requests.post(
            f"{Meet_server}/create-meet",
            json=request.json,
            verify=False  # For self-signed certificates
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        print(f"Error forwarding create-meet: {e}")
        return jsonify({"error": "Gateway error"}), 500

@app.route('/join-meet', methods=['POST'])
def join_meet():
    """Forward join-meet request to backend"""
    try:
        print("Forwarding join-meet request to backend")
        response = requests.post(
            f"{Meet_server}/join-meet",
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
        print(f"Error forwarding join-meet: {e}")
        return jsonify({"error": "Gateway error"}), 500


@app.route('/room/<meet_id>/<user_email>')
def room(meet_id, user_email):
    """Forward room page request to backend"""
    try:
        print(f"Forwarding room request for {meet_id}/{user_email}")
        response = requests.get(
            f"{Meet_server}/room/{meet_id}/{user_email}",
            verify=False  # For self-signed certificates
        )
        
        if response.status_code == 200:
            # Replace backend server URL with gateway URL in the HTML
            html_content = response.text
            html_content = html_content.replace(
                'server="https://{Meet_server}:7053"',
                'server="http://localhost:5001"'
            )
            return html_content, 200
        else:
            return response.text, response.status_code
            
    except Exception as e:
        print(f"Error forwarding room request: {e}")
        return "Gateway error", 500



@MeetingServerSocket.on('connect')
def handle_client_connect():
    """Client connected to gateway - create dedicated backend connection"""
    client_sid = request.sid
    user_email = request.args.get('user_email')
    print(f"✅ Client connected: {client_sid} (email: {user_email})")
    
    # Create a dedicated backend connection for this client
    backend = create_MeetServer_connection(client_sid, user_email)
    if backend:
        client_connections_meeting[client_sid] = {
            'backend': backend,
            'user_email': user_email
        }
    else:
        emit('error', 'Failed to connect to meeting server')


@MeetingServerSocket.on('disconnect')
def handle_client_disconnect():
    """Client disconnected - cleanup backend connection"""
    client_sid = request.sid
    print(f"❌ Client disconnected: {client_sid}")
    
    if client_sid in client_connections_meeting:
        try:
            client_connections_meeting[client_sid]['backend'].disconnect()
        except:
            pass
        del client_connections_meeting[client_sid]


@MeetingServerSocket.on('join')
def handle_join(data):
    """Forward join event to backend"""
    client_sid = request.sid
    print(f"Client {client_sid} -> Backend: join room {data.get('room')}")
    
    if client_sid in client_connections_meeting:
        client_connections_meeting[client_sid]['backend'].emit('join', data)


@MeetingServerSocket.on('leave')
def handle_leave(data):
    """Forward leave event to backend"""
    client_sid = request.sid
    print(f"Client {client_sid} -> Backend: leave room {data.get('room')}")
    
    if client_sid in client_connections_meeting:
        client_connections_meeting[client_sid]['backend'].emit('leave', data)


@MeetingServerSocket.on('offer')
def handle_offer(data):
    """Forward WebRTC offer to backend"""
    client_sid = request.sid
    print(f"Client {client_sid} -> Backend: offer to {data.get('targetId')}")
    
    if client_sid in client_connections_meeting:
        client_connections_meeting[client_sid]['backend'].emit('offer', data)


@MeetingServerSocket.on('answer')
def handle_answer(data):
    """Forward WebRTC answer to backend"""
    client_sid = request.sid
    print(f"Client {client_sid} -> Backend: answer to {data.get('targetId')}")
    
    if client_sid in client_connections_meeting:
        client_connections_meeting[client_sid]['backend'].emit('answer', data)


@MeetingServerSocket.on('ice-candidate')
def handle_ice_candidate(data):
    """Forward ICE candidate to backend"""
    client_sid = request.sid
    print(f"Client {client_sid} -> Backend: ice-candidate to {data.get('targetId')}")
    
    if client_sid in client_connections_meeting:
        client_connections_meeting[client_sid]['backend'].emit('ice-candidate', data)




if __name__ == '__main__':
    GameServerSocket.run(app, host='0.0.0.0', port=7050, debug=True, allow_unsafe_werkzeug=True)   
            