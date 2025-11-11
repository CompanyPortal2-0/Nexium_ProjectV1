from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_cors import CORS
import logging

app = Flask(__name__)
app.secret_key = "c1e4a8d92b3f4c1d823d9d7be1a0ad91"
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Socket.IO with explicit CORS settings
socketio = SocketIO(app,cors_allowed_origins="*")

# Keep track of users in rooms
rooms = {}


@app.route('/')
def index():
    return '<h1>serveur ye5dem</h1>'


@socketio.on('connect')
def handle_connect():
    x= request
    logger.info(f'Client connected: {request.sid} username: {request.args.get("username")} username: {request.args.get("customId")}')


@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f'Client disconnected: {request.sid}')

    # Find and remove user from any rooms they were in
    for room_id in list(rooms.keys()):
        if request.sid in rooms[room_id]:
            handle_leave({'room': room_id})


@socketio.on('join')
def handle_join(data):
    room_id = data['room']
    user_id = request.sid

    logger.info(f'User {user_id} joining room: {room_id}')

    # Create room if it doesn't exist
    if room_id not in rooms:
        rooms[room_id] = {}

    # Add user to room
    join_room(room_id)
    rooms[room_id][user_id] = {'joined': True}

    # Confirm room joined
    emit('room-joined', {
        'room': room_id,
        'peers': list(rooms[room_id].keys())
    })

    # Notify existing users about the new peer
    for peer_id in rooms[room_id]:
        if peer_id != user_id:
            emit('new-peer', {'peerId': user_id}, to=peer_id)

    logger.info(f'Room {room_id} now has {len(rooms[room_id])} users')


@socketio.on('leave')
def handle_leave(data):
    room_id = data['room']
    user_id = request.sid

    logger.info(f'User {user_id} leaving room: {room_id}')

    if room_id in rooms and user_id in rooms[room_id]:
        # Leave the room
        leave_room(room_id)
        del rooms[room_id][user_id]

        # Notify other users in the room
        emit('peer-disconnected', {'peerId': user_id}, to=room_id)

        # Clean up empty rooms
        if len(rooms[room_id]) == 0:
            del rooms[room_id]
            logger.info(f'Room {room_id} is now empty and has been deleted')
        else:
            logger.info(f'Room {room_id} now has {len(rooms[room_id])} users')


@socketio.on('offer')
def handle_offer(data):
    room_id = data['room']
    target_id = data['targetId']
    offer = data['offer']

    logger.info(f'Received offer from {request.sid} to {target_id} in room {room_id}')

    # Forward the offer to the target peer
    emit('offer', {
        'offer': offer,
        'peerId': request.sid
    }, to=target_id)


@socketio.on('answer')
def handle_answer(data):
    room_id = data['room']
    target_id = data['targetId']
    answer = data['answer']

    logger.info(f'Received answer from {request.sid} to {target_id} in room {room_id}')

    # Forward the answer to the target peer
    emit('answer', {
        'answer': answer,
        'peerId': request.sid
    }, to=target_id)


@socketio.on('ice-candidate')
def handle_ice_candidate(data):
    room_id = data['room']
    target_id = data['targetId']
    candidate = data['candidate']

    logger.info(f'Received ICE candidate from {request.sid} to {target_id} in room {room_id}')

    # Forward the ICE candidate to the target peer
    emit('ice-candidate', {
        'candidate': candidate,
        'peerId': request.sid
    }, to=target_id)


if __name__ == '__main__':
    # Specify the SSL certificate and key paths
    cert_path = '/home/ahml-47/integration/certifHTTPS/cert.pem'
    key_path = '/home/ahml-47/integration/certifHTTPS/key.pem'

    # Run the server with SSL/TLS
    socketio.run(app,host='0.0.0.0',port=5010,debug=True,ssl_context=("/home/ahml-47/integration/certifHTTPS/cert.pem", "/home/ahml-47/integration/certifHTTPS/key.pem"))
