from flask import Flask, jsonify, render_template, session, send_from_directory, request, redirect
from dotenv import load_dotenv
import os
import json
from flask_jwt_extended import jwt_required
import requests

load_dotenv()

app = Flask(__name__)

@app.route('/getCodeForManager',methods=['GET'])

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

