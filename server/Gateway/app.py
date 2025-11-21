from flask import Flask, jsonify, render_template, session, send_from_directory, request, redirect
from dotenv import load_dotenv
import os
import requests
import json
from dotenv import load_dotenv
from modeles.role import ROLE
from modeles.department import Department

load_dotenv()
app = Flask(__name__)

AUTH_server = os.getenv('AUTH_SERVER')
SAVING_server = os.getenv('SAVING_server')

@app.route('/login',methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    print(email,password)
    

    
    if (email is None) or (password is None):
        return jsonify({"Text": "missing content"}), 401
    else :
        return requests.post(f'http://{AUTH_server}/login',json=data).json() , 200
    
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
    
    response_from_auth_service = requests.get(f'http://{AUTH_server}/signup',json={
        "email":email,
        "Password":Password
    })

    if (response_from_auth_service.status_code == 200) :
        
        response_from_auth_service_data = response_from_auth_service.json()
            
            # Check if it's a string (might be double-encoded)
        if isinstance(response_from_auth_service_data, str):
                response_from_auth_service_data = json.loads(response_from_auth_service_data)
            
        print("Parsed data:", response_from_auth_service_data)
            
        id = response_from_auth_service_data.get("id")
        user_data = {
                "email": email,
                "password": "temp_password_not_used",  
                "role": ROLE.EMPLOYER.value,
                "first_name": firstName,
                "last_name": lastName,
                "address": address,
                "department": "hadhi n3amerha mba3ed",
                "userID": id,  
                "date_of_birth":DateOfBirth
            }
        response_from_saving_service = requests.post(f'http://{SAVING_server}/auth/register',json=user_data)
        if (response_from_saving_service.status_code == 200):
            return jsonify({"AuthToken": {response_from_auth_service.json().get("Token")}}), 200
        else : 
            return jsonify({"error": "we get an error from saving error"}), 500
    else : 
        return jsonify({"error": "we get an error from auth service"}), 500
    

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=7050, debug=False)
   
            