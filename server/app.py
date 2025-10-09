from flask import Flask, jsonify, render_template, session, send_from_directory, request, redirect
from Helperes.userHelper import userHelper

app = Flask(__name__)
app.secret_key = '12354681353415'


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if request.method == 'POST':
        email = data.get('email')
        password = data.get('password')
        if (email is None) or (password is None):
            return jsonify({"Text": "missing content"}), 401
        user = userHelper.getUserByEmail(email)
        if user is not None:
            return jsonify({"RedirectionLink": "test.test", "accessToken": "testtttt"}), 200
        else:
            return jsonify({"Text": "cordinates are wring"}), 400

    return jsonify({"message": "wrong method"}), 402


if __name__ == '__main__':
    app.run(debug=True)
