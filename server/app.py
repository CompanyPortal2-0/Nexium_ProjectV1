from flask import Flask, jsonify, render_template, session, send_from_directory, request, redirect

from Helperes.employersHelper import EmployerHelper
from Helperes.userHelper import userHelper
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
    if (email is None) or (password is None):
        return jsonify({"Text": "missing content"}), 401
    user = userHelper.getUserByEmail(email)
    access_token = create_access_token(identity=email)
    if user is not None:
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
        return jsonify({"RedirectionLink": "test.test", "accessToken": "testtttt"}), 200
    else :
        return jsonify({"Text": "mail used"}), 401


@app.route('/hr/getallemp', methods=['GET'])
@jwt_required()
def getAllEmp():
    current_employer = EmployerHelper.getEmployerByEmail(get_jwt_identity())
    if current_employer is None or current_employer.getRole() != ROLE.HR:
        return jsonify({"Text": "not authorized"}), 401
    employeresList = EmployerHelper.getAllEmployers()
    return jsonify(employeresList), 200
if __name__ == '__main__':
    app.run(debug=True)
