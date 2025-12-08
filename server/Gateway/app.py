"""
Gateway API - Main Application
==============================
This is the main entry point for the Gateway API.
It handles routing and delegates business logic to helper classes.
"""

from flask import Flask, jsonify, render_template, session, send_from_directory, request, redirect
from dotenv import load_dotenv
import os
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import requests
import json
import secrets
import string
from datetime import datetime
from modeles.role import ROLE
from modeles.department import Department
from namespace.GameNamespace import GameNamespace
from namespace.MeetingNamespace import MeetingNamespace
from flask_cors import CORS
from flask_socketio import SocketIO, emit, Namespace
import socketio

# Import helper classes
from helpers import AuthHelper, UserHelper, ActivityHelper, MeetingHelper, HealthHelper

load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Single SocketIO instance with multiple namespaces
socketio_app = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Separate connection dictionaries for each namespace
client_connections_game = {} 
client_connections_meeting = {}

# Server configurations
AUTH_server = os.getenv('AUTH_SERVER')
SAVING_server = os.getenv('SAVING_server')
UserServices = os.getenv('UserServices_server')
Game_server = os.getenv('Game_server')
Meet_server = os.getenv('Meet_server')
Activity_server = os.getenv('Activity_server', 'localhost:7056')
MYIP = os.getenv('myip', 'localhost:7056')
app.secret_key = 'your-super-secret-jwt-token-with-at-least-32-characters-long'

jwt = JWTManager(app)

# =================== WEBSOCKET HELPER FUNCTIONS ===================

def create_GameServer_connection(client_sid, namespace_instance):
    """Create a dedicated backend connection for a game client"""
    backend = socketio.Client(logger=False, engineio_logger=False)
    
    @backend.on('matchCreated')
    def on_match_created(data):
        print(f"Backend -> Client {client_sid}: matchCreated {data}")
        socketio_app.emit('matchCreated', data, to=client_sid, namespace='/game')
    
    @backend.on('matchJoined')
    def on_match_joined(data):
        print(f"Backend -> Client {client_sid}: matchJoined {data}")
        socketio_app.emit('matchJoined', data, to=client_sid, namespace='/game')
    
    @backend.on('gameState')
    def on_game_state(data):
        print(f"Backend -> Client {client_sid}: gameState")
        socketio_app.emit('gameState', data, to=client_sid, namespace='/game')
    
    @backend.on('error')
    def on_error(data):
        print(f"Backend -> Client {client_sid}: error {data}")
        socketio_app.emit('error', data, to=client_sid, namespace='/game')
    
    try:
        backend.connect(Game_server)
        print(f"✅ Created backend connection for game client {client_sid}")
        return backend
    except Exception as e:
        print(f"❌ Failed to connect to game backend for client {client_sid}: {e}")
        return None


def create_MeetServer_connection(client_sid, namespace_instance, user_email=None):
    """Create a dedicated backend connection for a meeting client"""
    connection_url = Meet_server
    if user_email:
        connection_url = f"{Meet_server}?user_email={user_email}"
    
    backend = socketio.Client(
        logger=False, 
        engineio_logger=False,
        ssl_verify=False,
        # Fix: Remove invalid parameters and use correct ones
        reconnection=True,
        reconnection_attempts=5,
        reconnection_delay=1,
        reconnection_delay_max=5,
        # Remove these invalid parameters:
        # ping_timeout=60000,
        # ping_interval=25000
    )
    
    @backend.on('room-joined')
    def on_room_joined(data):
        print(f"Backend -> Client {client_sid}: room-joined")
        socketio_app.emit('room-joined', data, to=client_sid, namespace='/meeting')
    
    @backend.on('new-peer')
    def on_new_peer(data):
        print(f"Backend -> Client {client_sid}: new-peer {data.get('peerId')}")
        socketio_app.emit('new-peer', data, to=client_sid, namespace='/meeting')
    
    @backend.on('peer-disconnected')
    def on_peer_disconnected(data):
        print(f"Backend -> Client {client_sid}: peer-disconnected {data.get('peerId')}")
        socketio_app.emit('peer-disconnected', data, to=client_sid, namespace='/meeting')
    
    @backend.on('offer')
    def on_offer(data):
        print(f"Backend -> Client {client_sid}: offer from {data.get('peerId')}")
        socketio_app.emit('offer', data, to=client_sid, namespace='/meeting')
    
    @backend.on('answer')
    def on_answer(data):
        print(f"Backend -> Client {client_sid}: answer from {data.get('peerId')}")
        socketio_app.emit('answer', data, to=client_sid, namespace='/meeting')
    
    @backend.on('ice-candidate')
    def on_ice_candidate(data):
        print(f"Backend -> Client {client_sid}: ice-candidate from {data.get('peerId')}")
        socketio_app.emit('ice-candidate', data, to=client_sid, namespace='/meeting')
    
    @backend.on('error')
    def on_error(data):
        print(f"Backend -> Client {client_sid}: error {data}")
        socketio_app.emit('error', data, to=client_sid, namespace='/meeting')
    
    @backend.on('room-full')
    def on_room_full(data):
        print(f"Backend -> Client {client_sid}: room-full")
        socketio_app.emit('room-full', data, to=client_sid, namespace='/meeting')
    
    try:
        backend.connect(connection_url)
        print(f"✅ Created backend connection for meeting client {client_sid}")
        return backend
    except Exception as e:
        print(f"❌ Failed to connect to meeting backend for client {client_sid}: {e}")
        return None

# Register namespaces
socketio_app.on_namespace(GameNamespace('/game', socketio_app, Game_server))
socketio_app.on_namespace(MeetingNamespace('/meeting', socketio_app, Meet_server))


# =================== HTTP ENDPOINTS ===================

# Health check endpoints
@app.route('/health', methods=['GET'])
def health():
    """Kubernetes health check endpoint"""
    health_status = {
        "status": "healthy",
        "service": "gateway",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "pod_name": os.getenv('POD_NAME', 'unknown'),
        "pod_ip": os.getenv('POD_IP', 'unknown'),
    }
    
    check_type = request.headers.get('X-Health-Check', 'general')
    
    if check_type == 'readiness':
        downstream_services = {
            'auth-service': AUTH_server,
            'user-service': UserServices,
            'saving-service': SAVING_server
        }
        
        services_status = {}
        all_healthy = True
        
        for service_name, service_url in downstream_services.items():
            try:
                response = requests.get(f"{service_url}/health", timeout=2)
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


@app.route('/ready', methods=['GET'])
def ready():
    """Simple readiness check"""
    return jsonify({"status": "ready"}), 200


@app.route('/live', methods=['GET'])
def live():
    """Simple liveness check"""
    return jsonify({"status": "alive"}), 200


@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    return """# HELP gateway_requests_total Total requests
# TYPE gateway_requests_total counter
gateway_requests_total 0
""", 200, {'Content-Type': 'text/plain'}


# Authentication endpoints
@app.route('/login', methods=['POST'])
def login():
    """Login endpoint - delegates to AuthHelper"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if (email is None) or (password is None):
        return jsonify({"Text": "missing content"}), 401
    
    result, status_code = AuthHelper.login(email, password)
    return jsonify(result) if isinstance(result, dict) else result, status_code


@app.route('/signup', methods=['POST'])
def signUp():
    """Signup endpoint - delegates to AuthHelper"""
    data = request.get_json()

    email = data.get('email')
    firstName = data.get('FirstName')
    lastName = data.get('LastName')
    Password = data.get('Password')
    DateOfBirth = data.get('DateOfBirth')
    address = data.get('Address')
    ManagerCode = data.get('managercode')
    
    if not all([email, firstName, lastName, Password, DateOfBirth, address]):
        return jsonify({"Text": "Missing required fields"}), 400
    
    result, status_code = AuthHelper.signup(
        email=email,
        password=Password,
        first_name=firstName,
        last_name=lastName,
        date_of_birth=DateOfBirth,
        address=address,
        manager_code=ManagerCode
    )
    return jsonify(result), status_code


@app.route('/getCodeForManager', methods=['GET'])
@jwt_required()
def getCode():
    """Gateway endpoint - get manager code using AuthHelper"""
    manager_email = AuthHelper.get_user_email_from_jwt_identity(get_jwt_identity())
    
    if not manager_email:
        return jsonify({"Text": "Manager email is required"}), 400
    
    result, status_code = AuthHelper.get_code_for_manager(manager_email)
    return jsonify(result), status_code


# Teammates endpoints
@app.route('/teammates', methods=['GET'])
@jwt_required()
def get_teammates():
    """Get teammates for the currently logged-in user using UserHelper"""
    current_user_email = AuthHelper.get_user_email_from_jwt_identity(get_jwt_identity())
    
    if not current_user_email:
        return jsonify({"success": False, "error": "Could not determine user email from token"}), 401
    
    include_details = request.args.get('include_details', 'true')
    include_manager = request.args.get('include_manager', 'true')
    
    result, status_code = UserHelper.get_teammates(current_user_email, include_details, include_manager)
    return jsonify(result), status_code


@app.route('/team', methods=['GET'])
@jwt_required()
def get_full_team():
    """Get full team information for the currently logged-in user using UserHelper"""
    current_user_email = AuthHelper.get_user_email_from_jwt_identity(get_jwt_identity())
    
    if not current_user_email:
        return jsonify({"success": False, "error": "Could not determine user email from token"}), 401
    
    result, status_code = UserHelper.get_full_team(current_user_email)
    return jsonify(result), status_code


# Activity endpoints
@app.route('/activities', methods=['POST'])
@jwt_required()
def create_activity():
    """Create a new activity using ActivityHelper"""
    current_user_email = AuthHelper.get_user_email_from_jwt_identity(get_jwt_identity())
    if not current_user_email:
        return jsonify({"success": False, "error": "Could not resolve user identity"}), 401
    
    data = request.json or {}
    result, status_code = ActivityHelper.create(data, current_user_email)
    return jsonify(result), status_code


@app.route('/activities', methods=['GET'])
@jwt_required()
def list_activities():
    """List all activities with optional filters using ActivityHelper"""
    result, status_code = ActivityHelper.list_all(dict(request.args))
    return jsonify(result), status_code


@app.route('/activities/<int:activity_id>', methods=['GET'])
@jwt_required()
def get_activity(activity_id):
    """Get a specific activity by ID using ActivityHelper"""
    result, status_code = ActivityHelper.get_by_id(activity_id)
    return jsonify(result), status_code


@app.route('/activities/<int:activity_id>', methods=['PUT'])
@jwt_required()
def update_activity(activity_id):
    """Update an activity using ActivityHelper"""
    current_user_email = AuthHelper.get_user_email_from_jwt_identity(get_jwt_identity())
    if not current_user_email:
        return jsonify({"success": False, "error": "Could not resolve user identity"}), 401
    
    data = request.json or {}
    result, status_code = ActivityHelper.update(activity_id, data, current_user_email)
    return jsonify(result), status_code


@app.route('/activities/<int:activity_id>', methods=['DELETE'])
@jwt_required()
def delete_activity(activity_id):
    """Delete an activity using ActivityHelper"""
    current_user_email = AuthHelper.get_user_email_from_jwt_identity(get_jwt_identity())
    if not current_user_email:
        return jsonify({"success": False, "error": "Could not resolve user identity"}), 401
    
    result, status_code = ActivityHelper.delete(activity_id, current_user_email)
    return jsonify(result), status_code


@app.route('/activities/<activity_id>/join', methods=['POST'])
@jwt_required()
def join_activity(activity_id):
    """Join an activity using ActivityHelper"""
    current_user_email = AuthHelper.get_user_email_from_jwt_identity(get_jwt_identity())
    if not current_user_email:
        return jsonify({"success": False, "error": "Could not resolve user identity"}), 401
    
    result, status_code = ActivityHelper.join(activity_id, current_user_email)
    return jsonify(result), status_code


@app.route('/activities/<int:activity_id>/leave', methods=['POST'])
@jwt_required()
def leave_activity(activity_id):
    """Leave an activity using ActivityHelper"""
    current_user_email = AuthHelper.get_user_email_from_jwt_identity(get_jwt_identity())
    if not current_user_email:
        return jsonify({"success": False, "error": "Could not resolve user identity"}), 401
    
    result, status_code = ActivityHelper.leave(activity_id, current_user_email)
    return jsonify(result), status_code


@app.route('/activities/<int:activity_id>/participants', methods=['POST'])
@jwt_required()
def add_participant(activity_id):
    """Add participants to an activity using ActivityHelper"""
    current_user_email = AuthHelper.get_user_email_from_jwt_identity(get_jwt_identity())
    if not current_user_email:
        return jsonify({"success": False, "error": "Could not resolve user identity"}), 401
    
    data = request.json or {}
    
    # Support both single email and multiple emails
    emails = data.get('emails', [])
    participant_email = data.get('participant_email')
    
    # If single participant_email provided, convert to list
    if participant_email and not emails:
        emails = [participant_email]
    
    if not emails:
        return jsonify({"success": False, "error": "emails or participant_email is required"}), 400
    
    result, status_code = ActivityHelper.add_participants(activity_id, emails)
    return jsonify(result), status_code


@app.route('/activities/<int:activity_id>/participants', methods=['GET'])
@jwt_required()
def get_participants(activity_id):
    """Get all participants of an activity using ActivityHelper"""
    result, status_code = ActivityHelper.get_participants(activity_id)
    return jsonify(result), status_code


@app.route('/activities/<int:activity_id>/participants/<participant_email>', methods=['DELETE'])
@jwt_required()
def remove_participant(activity_id, participant_email):
    """Remove a participant from an activity using ActivityHelper"""
    result, status_code = ActivityHelper.leave(activity_id, participant_email)
    return jsonify(result), status_code


@app.route('/my-activities', methods=['GET'])
@jwt_required()
def get_my_activities():
    """Get all activities for the current user using ActivityHelper"""
    current_user_email = AuthHelper.get_user_email_from_jwt_identity(get_jwt_identity())
    if not current_user_email:
        return jsonify({"success": False, "error": "Could not resolve user identity"}), 401
    
    filter_type = request.args.get('filter', 'all')
    result, status_code = ActivityHelper.get_my_activities(current_user_email, filter_type)
    return jsonify(result), status_code


# Meeting endpoints
@app.route('/create-meet', methods=['POST'])
@jwt_required()
def create_meet():
    """Create a new meeting using MeetingHelper"""
    created_by = AuthHelper.get_user_email_from_jwt_identity(get_jwt_identity())
    data = request.json or {}
    
    result, status_code = MeetingHelper.create_meeting(data, created_by)
    return jsonify(result), status_code


@app.route('/join-meet', methods=['POST'])
@jwt_required()
def join_meet():
    """Join a meeting using MeetingHelper"""
    user_email = AuthHelper.get_user_email_from_jwt_identity(get_jwt_identity())
    data = request.json or {}
    
    result, status_code = MeetingHelper.join_meeting(data, user_email)
    return jsonify(result), status_code


@app.route('/room/<meet_id>/<user_email>')
def room(meet_id, user_email):
    """Get room page for a meeting using MeetingHelper"""
    result, status_code = MeetingHelper.get_room_page(meet_id, user_email)
    
    if status_code == 200 and isinstance(result, str):
        return result, 200
    
    return jsonify(result) if isinstance(result, dict) else result, status_code


# user service 
@app.route('/becamemanager', methods=['POST'])
@jwt_required()
def becameManager():
    """Become a manager using UserHelper"""
    user_email = AuthHelper.get_user_email_from_jwt_identity(get_jwt_identity())
    
    if user_email is None:
        return jsonify({"error": "Could not resolve user identity"}), 401
    
    code = (request.get_json()).get("code")
    result, status_code = UserHelper.became_manager(code, user_email)
    return jsonify(result), status_code
    

@app.route('/generateBecameManagerCode', methods=['GET'])
def generate_became_manager_code():
    """Generate a became manager code using UserHelper"""
    data = request.get_json()
    result, status_code = UserHelper.generate_became_manager_code(data)
    return jsonify(result), status_code


@app.route('/user/identity', methods=['GET'])
@jwt_required()
def get_user_identity():
    """Get the current user's identity (email) from JWT token using UserHelper"""
    user_id = get_jwt_identity()
    result, status_code = UserHelper.get_user_identity(user_id)
    return jsonify(result), status_code


# =================== MEETING CRUD ENDPOINTS ===================

@app.route('/meetings', methods=['GET'])
@jwt_required()
def get_all_meetings():
    """Get all meetings using MeetingHelper"""
    user_email = request.args.get('user_email')
    is_active = request.args.get('is_active')
    
    result, status_code = MeetingHelper.get_all_meetings(user_email, is_active)
    return jsonify(result), status_code


@app.route('/meetings/<meeting_id>', methods=['GET'])
@jwt_required()
def get_meeting(meeting_id):
    """Get a specific meeting by ID using MeetingHelper"""
    result, status_code = MeetingHelper.get_meeting(meeting_id)
    return jsonify(result), status_code


@app.route('/meetings/<meeting_id>', methods=['PUT'])
@jwt_required()
def update_meeting(meeting_id):
    """Update a meeting using MeetingHelper"""
    data = request.json or {}
    result, status_code = MeetingHelper.update_meeting(meeting_id, data)
    return jsonify(result), status_code


@app.route('/meetings/<meeting_id>', methods=['DELETE'])
@jwt_required()
def delete_meeting(meeting_id):
    """Delete a meeting using MeetingHelper"""
    result, status_code = MeetingHelper.delete_meeting(meeting_id)
    return jsonify(result), status_code


@app.route('/meetings/<meeting_id>/start', methods=['POST'])
@jwt_required()
def start_meeting(meeting_id):
    """Start a meeting using MeetingHelper"""
    result, status_code = MeetingHelper.start_meeting(meeting_id)
    return jsonify(result), status_code


@app.route('/meetings/<meeting_id>/end', methods=['POST'])
@jwt_required()
def end_meeting(meeting_id):
    """End a meeting using MeetingHelper"""
    result, status_code = MeetingHelper.end_meeting(meeting_id)
    return jsonify(result), status_code


@app.route('/meetings/<meeting_id>/log', methods=['POST'])
@jwt_required()
def add_meeting_log(meeting_id):
    """Add a log entry to a meeting using MeetingHelper"""
    data = request.json or {}
    result, status_code = MeetingHelper.add_log(meeting_id, data)
    return jsonify(result), status_code


@app.route('/meetings/<meeting_id>/log', methods=['GET'])
@jwt_required()
def get_meeting_log(meeting_id):
    """Get meeting log using MeetingHelper"""
    download = request.args.get('download')
    result, status_code = MeetingHelper.get_log(meeting_id, download)
    
    # Handle file download
    if download and status_code == 200 and not isinstance(result, dict):
        return result, status_code
    
    return jsonify(result), status_code


# =================== USER MEETING ENDPOINTS ===================

@app.route('/meetings/my', methods=['GET'])
@jwt_required()
def get_my_meetings():
    """Get all meetings for the currently logged-in user using MeetingHelper"""
    current_user_email = AuthHelper.get_user_email_from_jwt_identity(get_jwt_identity())
    
    if not current_user_email:
        return jsonify({"success": False, "error": "Could not determine user email from token"}), 401
    
    filter_type = request.args.get('filter', 'all')
    is_active = request.args.get('is_active')
    include_details = request.args.get('include_details', 'false')
    
    result, status_code = MeetingHelper.get_my_meetings(
        current_user_email, filter_type, is_active, include_details
    )
    return jsonify(result), status_code


@app.route('/meetings/my/upcoming', methods=['GET'])
@jwt_required()
def get_my_upcoming_meetings():
    """Get all upcoming meetings for the currently logged-in user using MeetingHelper"""
    current_user_email = AuthHelper.get_user_email_from_jwt_identity(get_jwt_identity())
    
    if not current_user_email:
        return jsonify({"success": False, "error": "Could not determine user email from token"}), 401
    
    result, status_code = MeetingHelper.get_my_upcoming_meetings(current_user_email)
    return jsonify(result), status_code


@app.route('/meetings/user', methods=['GET'])
@jwt_required()
def get_user_meetings_by_email():
    """Get all meetings for a specific user by email using MeetingHelper"""
    email = AuthHelper.get_user_email_from_jwt_identity(get_jwt_identity())
    filter_type = request.args.get('filter', 'all')
    is_active = request.args.get('is_active')
    include_details = request.args.get('include_details', 'false')
    
    result, status_code = MeetingHelper.get_user_meetings(
        email, filter_type, is_active, include_details
    )
    return jsonify(result), status_code


@app.route('/meetings/user/<email>/upcoming', methods=['GET'])
@jwt_required()
def get_user_upcoming_meetings_by_email(email):
    """Get all upcoming meetings for a specific user by email using MeetingHelper"""
    result, status_code = MeetingHelper.get_user_upcoming_meetings(email)
    return jsonify(result), status_code


@app.route('/meetings/<meeting_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_meeting_by_user(meeting_id):
    """Soft delete a meeting using MeetingHelper"""
    current_user_email = AuthHelper.get_user_email_from_jwt_identity(get_jwt_identity())
    
    if not current_user_email:
        return jsonify({"success": False, "error": "Could not determine user email from token"}), 401
    
    result, status_code = MeetingHelper.delete_meeting_by_user(meeting_id, current_user_email)
    return jsonify(result), status_code


@app.route('/meetings/<meeting_id>/hard-delete', methods=['DELETE'])
@jwt_required()
def hard_delete_meeting_route(meeting_id):
    """Permanently delete a meeting using MeetingHelper"""
    current_user_email = AuthHelper.get_user_email_from_jwt_identity(get_jwt_identity())
    
    if not current_user_email:
        return jsonify({"success": False, "error": "Could not determine user email from token"}), 401
    
    data = request.json or {}
    confirm = data.get('confirm', False)
    
    result, status_code = MeetingHelper.hard_delete_meeting(meeting_id, current_user_email, confirm)
    return jsonify(result), status_code


# =================== MAIN ENTRY POINT ===================

if __name__ == '__main__':
    socketio_app.run(
        app, 
        host='0.0.0.0', 
        port=7050, 
        debug=True, 
        allow_unsafe_werkzeug=True,
        ssl_context=('meetingService\\certifs\\cert.pem', 'meetingService\\certifs\\key.pem')
    )