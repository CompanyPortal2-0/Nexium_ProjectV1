from flask import Flask, render_template, session ,send_from_directory, request, redirect
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import logging
from werkzeug.utils import secure_filename
import os

from models.user_model import User
from models.Helpers.userHelper import UserHelper
from models.message_model import Message
from models.Helpers.messageHelper import MessageHelper
from models.ressource_model import Ressource
from models.Helpers.ressource_helper import RessourceHelper
from models.meet import Meet
from models.Helpers.meet_helper import MeetHelper


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

@app.route("/meet")
def meet_home():
    user = session.get("user")
    if not user:
        return redirect("/")
    return render_template("meet.html", user=user)


@app.route("/create-meet", methods=["POST"])
def create_meet():
    meet_id = request.form["meet_id"]
    password = request.form["password"]

    existing = MeetHelper.import_meets()
    if meet_id in existing:
        return "Meet ID already exists. <a href='/meet'>Try again</a>"

    meet = Meet(meet_id, password)
    MeetHelper.save_meet(meet)
    MeetHelper.add_user_to_meet(meet_id, session["user"]["id"])
    return redirect(f"/room/{meet_id}")


@app.route("/join-meet", methods=["POST"])
def join_meet():
    meet_id = request.form["meet_id"]
    password = request.form["password"]
    meets = MeetHelper.import_meets()

    if meet_id not in meets or meets[meet_id]["password"] != password:
        return "Invalid credentials. <a href='/meet'>Try again</a>"

    MeetHelper.add_user_to_meet(meet_id, session["user"]["name"])
    return redirect(f"/room/{meet_id}")