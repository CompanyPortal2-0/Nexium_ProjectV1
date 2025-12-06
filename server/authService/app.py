from flask import Flask, jsonify, render_template, session, send_from_directory, request, redirect
from dotenv import load_dotenv
import os
import json
import requests
from Helper import authHelper
from supaBase.supaBase import dataBaseAuth

load_dotenv()

app = Flask(__name__)
authenter = dataBaseAuth(os.getenv("SUPABASE_URL"),os.getenv("SUPABASE_KEY"))
auth_helper = authHelper(authenter)
SAVING_server = os.getenv('SAVING_server')



@app.route("/signup",methods=['POST'])
def signUp():
    data = request.get_json()

    email = data.get('email')
    firstName = data.get('FirstName')
    lastName = data.get('LastName')
    Password = data.get('Password')
    DateOfBirth = data.get('DateOfBirth')
    address = data.get('Address')
    ManagerCode = data.get('managercode')

    result = auth_helper.CreateUser(email,Password)
    result = json.loads(result)
    Token = result.get("Token")
    id = result.get("id")
    user_data = {
            "email": email,
            "password": Password,  
            "role": "employee",
            "first_name": firstName,
            "last_name": lastName,
            "address": address,
            "department": "hadhi n3amerha mba3ed",
            "userID": id,  
            "date_of_birth": DateOfBirth
        }
    HEADERS = {"X-Internal-Key": "nexus-internal-secret-key-123"}

    try:
        response_from_saving_service = requests.post(
            f'http://{SAVING_server}/users/', 
            json=user_data, 
            headers=HEADERS
        )
    except Exception as e:
        delResult = auth_helper.deleteUser(id)
        return jsonify({"message":"error creating in the saving server","del result":delResult}),500

    if response_from_saving_service.status_code == 200 or response_from_saving_service.status_code == 201 : 
        print("from app :")
    
        #response = json.dumps()
        if(result is not None) :
            return jsonify({
            "Token":result.get("Token"),
            "id": result.get("id")
        }) , 200
        else :
            return jsonify({"error":"error in auth_helper.CreateUser(email,Password)"}) , 500
    else:
        delResult = auth_helper.deleteUser(id)
        return jsonify({"message":"error creating in the saving server"}),500
        

@app.route("/login",methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    Password = data.get('password')
    
    # Get result from auth helper
    login_result = auth_helper.login(email, Password)
    
    # Check if login_result is None (failed)
    if login_result is None:
        return jsonify({"error": "Login failed. Invalid credentials or service error."}), 401
    
    # Parse the JSON result
    try:
        result = json.loads(login_result)
        return jsonify({
            "Token": result.get("Token"),
            "firstname": result.get("firstname"),
            "lastname": result.get("lastname"),
            "role": result.get("role")
        }), 200
    except Exception as e:
        print(f"Error parsing login result: {e}")
        return jsonify({"error": "Error processing login response"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=7051, debug=False)
