from flask import Flask, jsonify, render_template, session, send_from_directory, request, redirect
from dotenv import load_dotenv
import os
from Helperes.userHelper import userHelper
from Helperes.passwordHelper import passwordHelper
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from modeles.role import ROLE
from testStore.userJson import JsonUserStore
from supaBase.supaBase import dataBaseAuth
from werkzeug.serving import WSGIRequestHandler
from Helperes.authHelper import authHelper



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
    firstName=data.get('FirstName')
    lastName = data.get('LastName')
    Password = data.get('Password')
    DateOfBirth = data.get('DateOfBirth')
    address = data.get('Address')
    
    # Validate required fields
    if not all([email, firstName, lastName, Password, DateOfBirth, address]):
        return jsonify({"Text": "Missing required fields"}), 400
    
    try:
        # First, create user in Supabase Auth
        if not auth_helper.CreateUser(email, Password):
            return jsonify({"Text": "Failed to create authentication account"}), 500
        
        # Then, create user locally
        if userHelper.CreateUser(email, firstName, lastName, DateOfBirth, address, Password):
            access_token = create_access_token(identity=email)
            return jsonify({
                "RedirectionLink": "testStore.testStore", 
                "accessToken": access_token
            }), 200
        else:
            return jsonify({"Text": "Failed to create user profile"}), 500
            
    except Exception as e:
        print(f"Signup error: {str(e)}")
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

@app.route('/hr/assemployee', methods=['POST'])
@jwt_required()
def assemployee():
    current_employer = userHelper.getUserByEmail(get_jwt_identity())
    if current_employer is None or current_employer.getRole() != ROLE.HR:
        return jsonify({"Text": "not authorized"}), 401
    data = request.get_json()
    empId = data.get('empId')
    managerId = data.get('managerId')
    emp = userHelper.getUserByEmail(empId)
    manager = userHelper.getUserByEmail(managerId)
    if emp is None or manager is None:
        return jsonify({"Text": "user not found"}), 404
    if emp.getRole() != ROLE.EMPLOYER or manager.getRole() != ROLE.MANAGER:
        return jsonify({"Text": "invalid roles"}), 400
    userHelper.addEmployee(manager, empId)


    JsonUserStore("./userJson.json").add_user(manager)
    return jsonify({"Text": "employee assigned"}), 200
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=6021, debug=False, request_handler=CustomRequestHandler)
