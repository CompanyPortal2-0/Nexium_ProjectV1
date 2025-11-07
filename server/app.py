from flask import Flask, jsonify, render_template, session, send_from_directory, request, redirect


from Helperes.userHelper import userHelper
from Helperes.passwordHelper import passwordHelper
from Helperes.Code_helper import codeHelper
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from modeles.role import ROLE
from testStore.userJson import JsonUserStore

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
    Code = data.get('Code')
    ManagerId = codeHelper.getManagerMAILByCode(Code)
    NewUser = userHelper.CreateUser(email,firstName,lastName,DateOfBirth,address,Password)
    if NewUser is not None :
        Manager=userHelper.getUserByEmail(ManagerId)
        userHelper.addEmployee(Manager, NewUser)

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


@app.route('/hr/generatecode', methods=['GET'])
@jwt_required()
def generatecode():
    current_employer = userHelper.getUserByEmail(get_jwt_identity())
    if current_employer is None or current_employer.getRole() != ROLE.HR:
        return jsonify({"Text": "not authorized"}), 401
    code = codeHelper.generateCode()
    data = request.get_json()
    manager_mail = data.get('manager_mail')
    codeHelper().saveCode(code, manager_mail)

    return jsonify({"invitationCode": code}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=6021, debug=False)
