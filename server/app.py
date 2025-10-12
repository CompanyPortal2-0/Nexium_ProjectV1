from flask import Flask, jsonify, render_template, session, send_from_directory, request, redirect


from Helperes.userHelper import userHelper
from Helperes.passwordHelper import passwordHelper
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from modeles.role import ROLE
app = Flask(__name__)
app.secret_key = '12354681353415'
app.config["JWT_SECRET_KEY"] = "1358415380351515"  # Change this in production
jwt = JWTManager(app)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    print(email,password)
    if (email is None) or (password is None):
        return jsonify({"Text": "missing content"}), 401
    user = userHelper.getUserByEmail(email)

    access_token = create_access_token(identity=email)
    if passwordHelper.isPasswordTrueForUser(user.getId(), password):
        return jsonify({"accessToken": f"{access_token}"}), 200
    else:
        return jsonify({"Text": "cordinates are wring"}), 400



@app.route('/signup', methods=['POST'])
def signUp():
    data = request.get_json()

    email = data.get('email')
    firstName=data.get('FirstName')
    lastName = data.get('LastName')
    Password = data.get('Password')
    DateOfBirth = data.get('DateOfBirth')
    address = data.get('Address')
    if userHelper.CreateUser(email,firstName,lastName,DateOfBirth,address,Password) is not None :
        return jsonify({"RedirectionLink": "testStore.testStore", "accessToken": "testtttt"}), 200
    else :
        return jsonify({"Text": "mail used"}), 401


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

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=6021, debug=False)
