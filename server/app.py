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
import os
import secrets
import string

load_dotenv()
app = Flask(__name__)
app.secret_key = '12354681353415'
app.config["JWT_SECRET_KEY"] = "1358415380351515"  # Change this in production
jwt = JWTManager(app)
authenter = dataBaseAuth(os.getenv("SUPABASE_URL"),os.getenv("SUPABASE_KEY"))
auth_helper = authHelper(authenter)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=6021, debug=False, request_handler=CustomRequestHandler)
