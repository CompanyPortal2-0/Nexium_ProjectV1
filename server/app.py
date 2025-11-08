from flask import Flask, jsonify, render_template, session, send_from_directory, request, redirect
import os
import sys

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded .env file")
except ImportError:
    print("⚠️  python-dotenv not installed, loading .env manually")
    # Manual .env loading if dotenv not installed
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("✅ Manually loaded .env file")

from Helperes.userHelper import userHelper
from Helperes.passwordHelper import passwordHelper
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from modeles.role import ROLE
from testStore.userJson import JsonUserStore
from supaBase.supaBase import SupabaseConnectionSingleton, SupabaseConfig

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "12354681353415")  # Use env var or default
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "1358415380351515")  # Use env var or default
jwt = JWTManager(app)

# Initialize Supabase connection
try:
    print("\n" + "="*60)
    print("🔍 SUPABASE CONFIGURATION CHECK")
    print("="*60)
    
    SUPABASE_URL = os.getenv("SUPABASE_URL", None)
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", None)
    
    print(f"📋 SUPABASE_URL: {SUPABASE_URL if SUPABASE_URL else '❌ NOT SET'}")
    print(f"📋 SUPABASE_KEY: {SUPABASE_KEY[:20] + '...' if SUPABASE_KEY else '❌ NOT SET'}")
    
    # Supabase is REQUIRED - no fallback mode
    if not SUPABASE_URL or not SUPABASE_KEY:
        print(f"\n❌ ERROR: Supabase credentials are REQUIRED!")
        print(f"   This app uses ONLY Supabase authentication.")
        print(f"\n   Please create a .env file with:")
        print(f"   SUPABASE_URL=http://localhost:9999 (for local Docker)")
        print(f"   SUPABASE_KEY=your-anon-key")
        print(f"\n   Get the key with: supabase status")
        print("="*60 + "\n")
        sys.exit(1)
    
    # Detect if using local Supabase (Docker) or cloud
    is_local_supabase = "localhost" in SUPABASE_URL or "127.0.0.1" in SUPABASE_URL
    
    if is_local_supabase:
        print(f"\n🐳 Local Supabase (Docker) detected!")
        print(f"   URL: {SUPABASE_URL}")
    else:
        print(f"\n☁️  Cloud Supabase detected!")
        print(f"   URL: {SUPABASE_URL}")
    
    print(f"✅ Supabase credentials found!")
    supabase_config = SupabaseConfig(url=SUPABASE_URL, key=SUPABASE_KEY)
    supabase_connection = SupabaseConnectionSingleton(supabase_config)
    print(f"✅ Supabase connection initialized successfully")
    print(f"🔥 AUTHENTICATION MODE: SUPABASE ONLY")
    
    # Initialize userHelper with Supabase connection (no local auth)
    user_helper = userHelper(supabase_connection)
    print(f"✅ userHelper initialized (Supabase-only authentication)")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"❌ CRITICAL ERROR: Failed to initialize Supabase connection: {e}")
    print("  The app CANNOT start without Supabase.")
    import traceback
    traceback.print_exc()
    print("\n" + "="*60)
    print("Please configure Supabase in .env file:")
    print("SUPABASE_URL=http://localhost:9999")
    print("SUPABASE_KEY=your-anon-key")
    print("="*60 + "\n")
    sys.exit(1)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    print(email, password)
    if (email is None) or (password is None):
        return jsonify({"Text": "missing content"}), 401
    
    # Use Supabase authentication
    user = user_helper.authenticateUser(email, password)
    if user is None:
        return jsonify({"Text": "invalid credentials"}), 401

    # Generate JWT token
    access_token = create_access_token(identity=email)
    return jsonify({"accessToken": f"{access_token}"}), 200



@app.route('/signup', methods=['POST'])
def signUp():
    data = request.get_json()

    email = data.get('email')
    firstName = data.get('FirstName')
    lastName = data.get('LastName')
    Password = data.get('Password')
    DateOfBirth = data.get('DateOfBirth')
    address = data.get('Address')
    
    # Create user with Supabase authentication
    new_user = user_helper.CreateUser(email, firstName, lastName, DateOfBirth, address, Password)
    if new_user is not None:
        # Generate real JWT token
        access_token = create_access_token(identity=email)
        return jsonify({"accessToken": access_token}), 200
    else:
        return jsonify({"Text": "email already used or signup failed"}), 401


@app.route('/hr/getallemp', methods=['GET'])
@jwt_required()
def getAllEmp():
    current_employer = user_helper.getUserByEmail(get_jwt_identity())
    if current_employer is None or current_employer.getRole() != ROLE.HR:
        return jsonify({"Text": "not authorized"}), 401
    employeresList = user_helper.getAllUsers(ROLE.EMPLOYER)
    # Convert each User object to a dictionary for JSON serialization
    employeresList_dicts = [user.to_dict() for user in employeresList]
    return jsonify(employeresList_dicts), 200


@app.route('/hr/getallang', methods=['GET'])
@jwt_required()
def getAllAng():
    current_employer = user_helper.getUserByEmail(get_jwt_identity())
    if current_employer is None or current_employer.getRole() != ROLE.HR:
        return jsonify({"Text": "not authorized"}), 401
    employeresList = user_helper.getAllUsers(ROLE.MANAGER)
    # Convert each User object to a dictionary for JSON serialization
    employeresList_dicts = [user.to_dict() for user in employeresList]
    return jsonify(employeresList_dicts), 200

@app.route('/hr/assemployee', methods=['POST'])
@jwt_required()
def assemployee():
    current_employer = user_helper.getUserByEmail(get_jwt_identity())
    if current_employer is None or current_employer.getRole() != ROLE.HR:
        return jsonify({"Text": "not authorized"}), 401
    data = request.get_json()
    empId = data.get('empId')
    managerId = data.get('managerId')
    emp = user_helper.getUserByEmail(empId)
    manager = user_helper.getUserByEmail(managerId)
    if emp is None or manager is None:
        return jsonify({"Text": "user not found"}), 404
    if emp.getRole() != ROLE.EMPLOYER or manager.getRole() != ROLE.MANAGER:
        return jsonify({"Text": "invalid roles"}), 400
    
    # Add employee to manager's list
    user_helper.addEmployee(manager, empId)
    
    # Save both updated records
    JsonUserStore("./userJson.json").add_user(manager)
    JsonUserStore("./userJson.json").add_user(emp)
    
    return jsonify({"Text": "employee assigned successfully"}), 200
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=6021, debug=False)
