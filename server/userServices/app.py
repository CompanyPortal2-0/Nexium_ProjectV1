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


    """Assign invitation code to a manager"""
    try:
        data = request.get_json()
        manager_email = data.get('manager_email')
        manager_id = data.get('manager_id')
        code = data.get('code')
        
        if not all([manager_email, manager_id, code]):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Save code to NEXUS/Saving Server
        payload = {
            "manager_id": manager_id,
            "code": code,
            "max_uses": 1
        }
        
        response = requests.post(
            f"{SAVING_server}/invites/",
            json=payload,
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            return jsonify({"success": True, "code": code}), 200
        else:
            return jsonify({"error": "Failed to save code"}), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Service communication error: {str(e)}"}), 503
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
        #current_user_email = data.get('current_user_email')
        manager_email = data.get('manager_email')
        
        #if not current_user_email or not manager_email:
        #    return jsonify({"Text": "Missing required fields"}), 400
        #
        ## 1. Get current user and verify they are authorized
        #current_user = userHelper.getUserByEmail(current_user_email)
        #if current_user is None:
        #    return jsonify({"Text": "Current user not found"}), 404
        #
        ## Check if current user is Manager (adjust role as needed)
        #if current_user.Role not in ROLE.MANAGER.value:
        #    return jsonify({"Text": "not authorized"}), 401
        #
        # 2. Get manager user
        manager_user = userHelper.getUserByEmail(manager_email)
        if manager_user is None:
            return jsonify({"Text": "Manager not found"}), 404
        
        # 3. Generate code
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        print("el code : ",code)
        # 4. Save code to Saving Server
        payload = {
            "manager_id": manager_user.ID,
            "code": code,
            "max_uses": 1
        }
        
        response = requests.post(
            f"{SAVING_server}/invites/",
            json=payload,
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            return jsonify({"code": code}), 200
        else:
            return jsonify({"Text": "Failed to save code to database"}), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({"Text": f"Database communication error: {str(e)}"}), 503
    except Exception as e:
        return jsonify({"Text": f"Internal error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7052, debug=False)

