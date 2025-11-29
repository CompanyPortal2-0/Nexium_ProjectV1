from meeting import Meeting
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_cors import CORS
from flask import Flask, jsonify, render_template, session, send_from_directory, request, redirect
from dotenv import load_dotenv
from Helper import MeetHelper
import logging
import os

load_dotenv()
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Socket.IO with explicit CORS settings
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Keep track of users in rooms
rooms = {}

signalingServer = os.getenv("SIGNALING_SERVER")

@app.route("/create-meet", methods=["POST"])
def create_meet():
    try:
        meet_data = request.json
        
        # Extract data from request
        title = meet_data.get("title")
        obj = meet_data.get("object")
        description = meet_data.get("description")
        invited_employees = meet_data.get("invitedEmployeesList", [])
        password = meet_data.get("password", "")
        
        # Validate required fields
        if not title or not obj or not description:
            return jsonify({"error": "Title, object, and description are required"}), 400
        
        # Create new meeting
        new_meeting = Meeting(
            title=title,
            obj=obj,
            description=description,
            invited_employees=invited_employees,
            password=password
        )
        
        # Add meeting to helper
        MeetHelper.addMeeting(new_meeting)
        
        # Return meeting details
        return jsonify({
            "success": True,
            "meeting": {
                "id": new_meeting.getID(),
                "title": new_meeting.getTitle(),
                "object": new_meeting.getObject(),
                "description": new_meeting.getDescription(),
                "invitationLink": new_meeting.getInvitationLink(),
                "createdAt": new_meeting.getCreatedAt(),
                "invitedEmployees": new_meeting.getInvitedEmployeesList()
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating meeting: {str(e)}")
        return jsonify({"error": "Failed to create meeting"}), 500

@app.route("/join-meet", methods=["POST"])
def join_meet():
    print("d5al")
    meet_data = request.json
    meet_id = meet_data.get("meet_id")
    password = meet_data.get("password")
    user_email = meet_data.get("user_email")
   
    if not(MeetHelper.verifyMeetingPassword(meet_id, password)):
        return jsonify({"error": "Invalid credentials"}), 401

    MeetHelper.addUserToMeeting(meet_id, user_email)
    return jsonify({
        "success": True,
        "redirectUrl": f"https://192.168.100.183:7053/room/{meet_id}/{user_email}"
    }), 200

@app.route("/room/<meet_id>/<user_email>")
def room(meet_id, user_email):
    userMail = user_email
    meet = MeetHelper.getMeetingByID(meet_id)
    
    if not meet:
        return "Meeting not found", 404

    participants = meet.getInvitedEmployeesList()

    if userMail not in participants:
        return "You are not a member of this meet", 403

    return render_template("video.html", meet_id=meet_id, user_mail=userMail, server="https://192.168.100.190:5001")

@socketio.on('connect')
def handle_connect():
    user_email = request.args.get("user_email")
    logger.info(f'Client connected: {request.sid} user_email: {user_email}')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f'Client disconnected: {request.sid}')

    # Find and remove user from any rooms they were in
    for room_id in list(rooms.keys()):
        if request.sid in rooms[room_id]:
            rooms[room_id].pop(request.sid)
            emit('peer-disconnected', {'peerId': request.sid}, room=room_id, skip_sid=request.sid)
            
            if len(rooms[room_id]) == 0:
                del rooms[room_id]

@socketio.on('join')
def handle_join(data):
    room_id = data['room']
    user_id = request.sid
    user_email = data.get('user_email')

    logger.info(f'User {user_id} (email: {user_email}) joining room: {room_id}')

    # Create room if it doesn't exist
    if room_id not in rooms:
        rooms[room_id] = {}

    # Add user to room
    join_room(room_id)
    rooms[room_id][user_id] = {'user_email': user_email, 'joined': True}

    # Get peer info with emails
    peer_info = [{'id': peer_id, 'user_email': peer_data.get('user_email')} 
                 for peer_id, peer_data in rooms[room_id].items() if peer_id != user_id]

    # Confirm room joined
    emit('room-joined', {
        'room': room_id,
        'peers': list(rooms[room_id].keys()),
        'peerInfo': peer_info
    })

    # Notify others that a new peer joined
    emit('new-peer', {
        'peerId': user_id,
        'user_email': user_email
    }, room=room_id, skip_sid=user_id)

@socketio.on('leave')
def handle_leave(data):
    room_id = data['room']
    user_id = request.sid

    logger.info(f'User {user_id} leaving room: {room_id}')

    # Remove user from room
    if room_id in rooms and user_id in rooms[room_id]:
        leave_room(room_id)
        del rooms[room_id][user_id]

        # Notify others that peer left
        emit('peer-disconnected', {'peerId': user_id}, room=room_id)

        # Delete room if empty
        if len(rooms[room_id]) == 0:
            del rooms[room_id]

@socketio.on('offer')
def handle_offer(data):
    room_id = data['room']
    target_id = data['targetId']
    offer = data['offer']
    user_email = data.get('user_email')

    logger.info(f'Relaying offer from {request.sid} (email: {user_email}) to {target_id}')

    # Send the offer to the target peer
    emit('offer', {
        'peerId': request.sid,
        'offer': offer,
        'user_email': user_email
    }, room=target_id)

@socketio.on('answer')
def handle_answer(data):
    room_id = data['room']
    target_id = data['targetId']
    answer = data['answer']
    user_email = data.get('user_email')

    logger.info(f'Relaying answer from {request.sid} (email: {user_email}) to {target_id}')

    # Send the answer to the target peer
    emit('answer', {
        'peerId': request.sid,
        'answer': answer,
        'user_email': user_email
    }, room=target_id)

@socketio.on('ice-candidate')
def handle_ice_candidate(data):
    room_id = data['room']
    target_id = data['targetId']
    candidate = data['candidate']

    # Send the ICE candidate to the target peer
    emit('ice-candidate', {
        'peerId': request.sid,
        'candidate': candidate
    }, room=target_id)

if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',
        port=7053,
        certfile='meetingService\\certifs\\cert.pem',
        keyfile='meetingService\\certifs\\key.pem',
        debug=True, allow_unsafe_werkzeug=True
     )
