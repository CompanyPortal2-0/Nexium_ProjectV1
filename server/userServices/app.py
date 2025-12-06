import secrets
import string
from flask import Flask, jsonify, render_template, session, send_from_directory, request, redirect
from dotenv import load_dotenv
import os
import json
from flask_jwt_extended import jwt_required
import requests
from userHelper import userHelper
from modeles.role import ROLE

load_dotenv()
HEADERS = {"X-Internal-Key": "nexus-internal-secret-key-123"}
app = Flask(__name__)
SAVING_server = os.getenv('SAVING_server')


@app.route('/users/by-email/<email>', methods=['GET'])
def get_user_by_email(email):
    """Get user details by email"""
    try:
        user = userHelper.getUserByEmail(email)
        if user:
            return jsonify(user.to_dict()), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


   
@app.route('/getCodeForManager', methods=['POST'])
def getCode():
    """
    Handle code generation for manager
    - Verify current user is HR/Manager
    - Verify target user exists
    - Generate code
    - Save to Saving Server
    """
    try:
        data = request.get_json()
        manager_email = data.get('manager_email')

        manager_user = userHelper.getUserByEmail(manager_email)
        if manager_user is None:
            return jsonify({"Text": "Manager not found"}), 404
        
        # 3. Generate code
        code = userHelper.generateCode()
        print("el code : ",code)
        # 4. Save code to Saving Server
        payload = {
            "manager_id": manager_user.ID,
            "code": code,
            "max_uses": 1
        }
        
        userHelper.saveIntoSavingServer(payload,"managerCode")

        return jsonify({'code':code})
        

    except requests.exceptions.RequestException as e:
        return jsonify({"Text": f"Database communication error: {str(e)}"}), 503
    except Exception as e:
        return jsonify({"Text": f"Internal error: {str(e)}"}), 500


@app.route("/generateBecameManagerCode",methods=['GET'])
def becameManagerCode():
    code = userHelper.generateCode()
    payload= {
        'hrid':(request.get_json()).get("hrid"),
        'code':code,
        'max_uses':1
    }
    userHelper.saveIntoSavingServer(payload,"becameManagerCode")
    return jsonify({'code':code})

@app.route("/becameManger",methods=['POST'])
def becameManager():
    data= request.get_json()
    code=data.get("code")
    userMail=data.get("userMail")
    return jsonify ({"response":userHelper.make_employee_manager(code,userMail)})
    


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7052, debug=False)

