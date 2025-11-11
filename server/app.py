from flask import Flask, jsonify, render_template, session, send_from_directory, request, redirect
from dotenv import load_dotenv
from Helperes.userHelper import userHelper
from Helperes.passwordHelper import passwordHelper
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from modeles.role import ROLE
from testStore.userJson import JsonUserStore
from supaBase.supaBase import dataBaseAuth
from werkzeug.serving import WSGIRequestHandler
from Helperes.authHelper import authHelper
from Helperes.meetHelper import meetHelper
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import os
import secrets
import string
import logging

load_dotenv()
app = Flask(__name__)
app.secret_key = '12354681353415'
app.config["JWT_SECRET_KEY"] = "1358415380351515"  # Change this in production

# Enable CORS for the app
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize JWT
jwt = JWTManager(app)

# Initialize SocketIO with CORS support
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database authentication
authenter = dataBaseAuth(os.getenv("SUPABASE_URL"),os.getenv("SUPABASE_KEY"))
auth_helper = authHelper(authenter)

# Store active meeting rooms and participants
active_rooms = {}  # {room_id: {user_id: {sid: socket_id, email: user_email, username: display_name}}}

class CustomRequestHandler(WSGIRequestHandler):
    def setup(self):
        self.request.settimeout(10)  # Set a 0.5-second read timeout
        super().setup()

@app.route('/hr/getCodeForManager',methods=['GET'])
@jwt_required()
def getCode():
    current_employer = userHelper.getUserByEmail(get_jwt_identity())
    if current_employer is None or current_employer.getRole() != ROLE.HR:
        return jsonify({"Text": "not authorized"}), 401
    data = request.get_json()
    managerMail=data.get('managermail')
    user = userHelper.getUserByEmail(managerMail)
    if user is None:
        return jsonify({"Text": "user not found"}), 404
    code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    userHelper.assignCodeToManager(user,code)

    return jsonify({"code": code})


    




@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    print(email,password)
    
    if (email is None) or (password is None):
        return jsonify({"Text": "missing content"}), 401
    
    try:
        user = userHelper.getUserByEmail(email)
        if user is None:
            return jsonify({"Text": "user not found"}), 404
        
        if passwordHelper.isPasswordTrueForUser(user.getId(), password) and auth_helper.login(email,password):
            access_token = create_access_token(identity=email)
            return jsonify({"accessToken": f"{access_token}"}), 200
        else:
            return jsonify({"Text": "coordinates are wrong"}), 400
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({"Text": "Login failed, please try again later"}), 503



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
    
    try:
        # First, create user in Supabase Auth
        if not auth_helper.CreateUser(email, Password):
            return jsonify({"Text": "Failed to create authentication account"}), 500
        
        # Then, create user locally
        success, new_user = userHelper.CreateUser(email, firstName, lastName, DateOfBirth, address, Password)
        
        if success and new_user:
            access_token = create_access_token(identity=email)
            
            # If manager code provided, link to manager
            if ManagerCode:
                managerMail = userHelper.getManagerFromCode(ManagerCode)
                if managerMail:
                    manager = userHelper.getUserByEmail(managerMail)
                    if manager:
                        userHelper.addemployerTomanager(manager, new_user)
            
            return jsonify({
                "accessToken": access_token,
                "message": "User created successfully"
            }), 200
        else:
            return jsonify({"Text": "Failed to create user profile"}), 500
            
    except Exception as e:
        print(f"Signup error: {str(e)}")
        import traceback
        traceback.print_exc()  # ✅ Print full stack trace for debugging
        return jsonify({"Text": "Registration failed, please try again later"}), 503


@app.route('/hr/getallemp', methods=['GET'])
@jwt_required()
def getAllEmp():
    current_employer = userHelper.getUserByEmail(get_jwt_identity())
    if current_employer is None or current_employer.getRole() != ROLE.HR:
        return jsonify({"Text": "not authorized"}), 401
    employeresList = userHelper.getAllUsers(ROLE.EMPLOYER)
    # Convert each User object to a dictionary for JSON serialization
    employeresList_dicts = [user.to_dict() for user in employeresList]
    return jsonify(employeresList_dicts), 200


@app.route('/hr/getallang', methods=['GET'])
@jwt_required()
def getAllAng():
    current_employer = userHelper.getUserByEmail(get_jwt_identity())
    if current_employer is None or current_employer.getRole() != ROLE.HR:
        return jsonify({"Text": "not authorized"}), 401
    employeresList = userHelper.getAllUsers(ROLE.MANAGER)
    # Convert each User object to a dictionary for JSON serialization
    employeresList_dicts = [user.to_dict() for user in employeresList]
    return jsonify(employeresList_dicts), 200

@app.route('/manager/createMeeting', methods=['POST'])
@jwt_required()
def createMeeting():
    """
    Create a new meeting (Manager only)
    """
    # Check if user is a manager
    current_user = userHelper.getUserByEmail(get_jwt_identity())
    if current_user is None or current_user.getRole() != ROLE.MANAGER:
        return jsonify({"Text": "not authorized"}), 401
    
    # Get meeting data from request
    data = request.get_json()
    title = data.get('title')
    object_text = data.get('object')
    description = data.get('description')
    
    # Validate required fields
    if not all([title, object_text, description]):
        return jsonify({"Text": "Missing required fields"}), 400
    
    try:
        # Create meeting using meetHelper
        
        
        new_meeting = meetHelper.create_meet(
            title=title,
            object=object_text,
            Description=description,
            CreterMail=current_user.Email
        )
        
        if new_meeting:
            return jsonify({
                "Text": "Meeting created successfully",
                "meetingID": new_meeting.getID(),
                "invitationLink": new_meeting.getInvitationLink()
            }), 200
        else:
            return jsonify({"Text": "Failed to create meeting"}), 500
            
    except Exception as e:
        print(f"Create meeting error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"Text": "Failed to create meeting"}), 503

@app.route('/joinMeeting', methods=['POST'])
@jwt_required()
def joinMeeting():
    """
    Join a meeting by adding the current user to the invited list
    """
    # Get current user from JWT token
    current_user = userHelper.getUserByEmail(get_jwt_identity())
    if current_user is None:
        return jsonify({"Text": "User not found"}), 404
    
    # Get meeting ID from request
    data = request.get_json()
    meeting_id = data.get('meetingID')
    
    # Validate required fields
    if not meeting_id:
        return jsonify({"Text": "Meeting ID is required"}), 400
    
    try:
        # Add user to meeting using meetHelper
        success = meetHelper.joinMeet(current_user.Email, meeting_id)
        
        if success:
            return jsonify({
                "Text": "Successfully joined meeting",
                "meetingID": meeting_id,
                "userEmail": current_user.Email
            }), 200
        else:
            return jsonify({"Text": "Failed to join meeting"}), 500
            
    except Exception as e:
        print(f"Join meeting error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"Text": "Failed to join meeting"}), 503

# ============================================
# MEETING ROOM ROUTES
# ============================================

@app.route('/meeting/<meeting_id>')
def meeting_room(meeting_id):
    """
    Serve the meeting room HTML interface
    """
    # Verify meeting exists
    meeting = meetHelper.get_meeting(meeting_id)
    if meeting is None:
        return jsonify({"Text": "Meeting not found"}), 404
    
    return send_from_directory('meetfiles', 'index.html')

@app.route('/meetfiles/<path:filename>')
def serve_meeting_files(filename):
    """
    Serve static files for meeting (JS, CSS, etc.)
    """
    return send_from_directory('meetfiles', filename)

@app.route('/api/meeting/<meeting_id>/details', methods=['GET'])
@jwt_required()
def get_meeting_details(meeting_id):
    """
    Get meeting details (authenticated)
    """
    current_user = userHelper.getUserByEmail(get_jwt_identity())
    if current_user is None:
        return jsonify({"Text": "User not found"}), 404
    
    meeting = meetHelper.get_meeting(meeting_id)
    if meeting is None:
        return jsonify({"Text": "Meeting not found"}), 404
    
    # Check if user is authorized (invited or creator)
    if not meetHelper.is_user_in_meeting(current_user.Email, meeting_id):
        return jsonify({"Text": "Not authorized to view this meeting"}), 403
    
    return jsonify({
        "meetingID": meeting.getID(),
        "title": meeting.getTitle(),
        "object": meeting.getObject(),
        "description": meeting.getDescription(),
        "creator": meeting.getCreator(),
        "invitationLink": meeting.getInvitationLink(),
        "invitedUsers": meeting.getInvitedEmployeesList()
    }), 200

@app.route('/api/my-meetings', methods=['GET'])
@jwt_required()
def get_my_meetings():
    """
    Get all meetings for the current user
    """
    current_user = userHelper.getUserByEmail(get_jwt_identity())
    if current_user is None:
        return jsonify({"Text": "User not found"}), 404
    
    meetings = meetHelper.get_user_meetings(current_user.Email)
    
    meetings_data = [{
        "meetingID": m.getID(),
        "title": m.getTitle(),
        "object": m.getObject(),
        "description": m.getDescription(),
        "creator": m.getCreator(),
        "invitationLink": m.getInvitationLink(),
        "isCreator": m.getCreator() == current_user.Email
    } for m in meetings]
    
    return jsonify({"meetings": meetings_data}), 200

# ============================================
# WEBSOCKET HANDLERS FOR WEBRTC SIGNALING
# ============================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    user_id = request.args.get('customId', request.sid)
    username = request.args.get('username', 'Anonymous')
    
    logger.info(f'Client connected: {request.sid} | User ID: {user_id} | Username: {username}')
    emit('connected', {'message': 'Connected to signaling server', 'sid': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f'Client disconnected: {request.sid}')
    
    # Remove user from all rooms they were in
    for room_id in list(active_rooms.keys()):
        users_in_room = active_rooms[room_id]
        for user_id, user_data in list(users_in_room.items()):
            if user_data.get('sid') == request.sid:
                # Leave the room
                leave_room(room_id)
                del active_rooms[room_id][user_id]
                
                # Notify others in the room
                emit('peer-disconnected', {
                    'peerId': request.sid,
                    'userId': user_id
                }, room=room_id)
                
                logger.info(f'User {user_id} removed from room {room_id}')
                
                # Clean up empty rooms
                if len(active_rooms[room_id]) == 0:
                    del active_rooms[room_id]
                    logger.info(f'Room {room_id} is now empty and has been deleted')
                
                break

@socketio.on('join')
def handle_join(data):
    """Handle user joining a meeting room"""
    room_id = data.get('room')
    user_email = data.get('userEmail')
    username = data.get('username', 'Anonymous')
    
    if not room_id:
        emit('error', {'message': 'Room ID is required'})
        return
    
    logger.info(f'User {username} ({user_email}) joining room: {room_id}')
    
    # Verify meeting exists
    meeting = meetHelper.get_meeting(room_id)
    if meeting is None:
        emit('error', {'message': 'Meeting not found'})
        return
    
    # Verify user is authorized (optional - can be enforced)
    # if user_email and not meetHelper.is_user_in_meeting(user_email, room_id):
    #     emit('error', {'message': 'Not authorized to join this meeting'})
    #     return
    
    # Create room if it doesn't exist
    if room_id not in active_rooms:
        active_rooms[room_id] = {}
    
    # Add user to room
    join_room(room_id)
    active_rooms[room_id][request.sid] = {
        'sid': request.sid,
        'email': user_email,
        'username': username
    }
    
    # Get list of existing peers in the room
    existing_peers = []
    peer_info = []
    
    for peer_sid, peer_data in active_rooms[room_id].items():
        if peer_sid != request.sid:
            existing_peers.append(peer_sid)
            peer_info.append({
                'id': peer_sid,
                'username': peer_data.get('username', 'Anonymous'),
                'email': peer_data.get('email')
            })
    
    # Confirm room joined to the joining user
    emit('room-joined', {
        'room': room_id,
        'peers': existing_peers,
        'peerInfo': peer_info
    })
    
    # Notify existing users about the new peer
    emit('new-peer', {
        'peerId': request.sid,
        'username': username,
        'email': user_email
    }, room=room_id, skip_sid=request.sid)
    
    logger.info(f'Room {room_id} now has {len(active_rooms[room_id])} users')

@socketio.on('leave')
def handle_leave(data):
    """Handle user leaving a meeting room"""
    room_id = data.get('room')
    
    if not room_id:
        return
    
    logger.info(f'User {request.sid} leaving room: {room_id}')
    
    if room_id in active_rooms and request.sid in active_rooms[room_id]:
        # Leave the room
        leave_room(room_id)
        user_data = active_rooms[room_id][request.sid]
        del active_rooms[room_id][request.sid]
        
        # Notify others in the room
        emit('peer-disconnected', {
            'peerId': request.sid,
            'username': user_data.get('username')
        }, room=room_id)
        
        # Clean up empty rooms
        if len(active_rooms[room_id]) == 0:
            del active_rooms[room_id]
            logger.info(f'Room {room_id} is now empty and has been deleted')
        else:
            logger.info(f'Room {room_id} now has {len(active_rooms[room_id])} users')

@socketio.on('offer')
def handle_offer(data):
    """Forward WebRTC offer to target peer"""
    room_id = data.get('room')
    target_id = data.get('targetId')
    offer = data.get('offer')
    
    logger.info(f'Forwarding offer from {request.sid} to {target_id} in room {room_id}')
    
    # Get sender info
    sender_username = 'Anonymous'
    if room_id in active_rooms and request.sid in active_rooms[room_id]:
        sender_username = active_rooms[room_id][request.sid].get('username', 'Anonymous')
    
    # Forward the offer to the target peer
    emit('offer', {
        'offer': offer,
        'peerId': request.sid,
        'username': sender_username
    }, room=target_id)

@socketio.on('answer')
def handle_answer(data):
    """Forward WebRTC answer to target peer"""
    room_id = data.get('room')
    target_id = data.get('targetId')
    answer = data.get('answer')
    
    logger.info(f'Forwarding answer from {request.sid} to {target_id} in room {room_id}')
    
    # Get sender info
    sender_username = 'Anonymous'
    if room_id in active_rooms and request.sid in active_rooms[room_id]:
        sender_username = active_rooms[room_id][request.sid].get('username', 'Anonymous')
    
    # Forward the answer to the target peer
    emit('answer', {
        'answer': answer,
        'peerId': request.sid,
        'username': sender_username
    }, room=target_id)

@socketio.on('ice-candidate')
def handle_ice_candidate(data):
    """Forward ICE candidate to target peer"""
    room_id = data.get('room')
    target_id = data.get('targetId')
    candidate = data.get('candidate')
    
    logger.info(f'Forwarding ICE candidate from {request.sid} to {target_id} in room {room_id}')
    
    # Forward the ICE candidate to the target peer
    emit('ice-candidate', {
        'candidate': candidate,
        'peerId': request.sid
    }, room=target_id)

if __name__ == '__main__':
    # Use socketio.run instead of app.run for WebSocket support
    logger.info("Starting Flask-SocketIO server on port 6021...")
    socketio.run(app, host='0.0.0.0', port=6021, debug=False, allow_unsafe_werkzeug=True)
