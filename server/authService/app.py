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



@app.route("/signup")
def signUp():
    data = request.get_json()
    email = data.get('email')
    Password = data.get('Password')
    result = auth_helper.CreateUser(email,Password)
    print("from app :")
    result = json.loads(result)
    response = json.dumps({
        "Token":result.get("Token"),
        "id": result.get("id")
    })
    if(result is not None) :
        return jsonify(response) , 200
    else :
        return jsonify({"error":"error in auth_helper.CreateUser(email,Password)"}) , 500

@app.route("/login",methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    Password = data.get('password')
    result = json.loads(auth_helper.login(email,Password))
    if(result is not None) :
        return jsonify({"Token":result.get("Token")}) , 200
    else :
        return jsonify({"error":"error in auth_helper.CreateUser(email,Password)"}) , 500


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=7051, debug=False)
