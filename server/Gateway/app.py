from flask import Flask, jsonify, render_template, session, send_from_directory, request, redirect
from dotenv import load_dotenv
import os
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import requests
import json
import secrets
import string
from dotenv import load_dotenv
from modeles.role import ROLE
from modeles.department import Department

load_dotenv()
app = Flask(__name__)

AUTH_server = os.getenv('AUTH_SERVER')
SAVING_server = os.getenv('SAVING_server')
UserServices = os.getenv('UserServices_server')

app.secret_key = 'your-super-secret-jwt-token-with-at-least-32-characters-long'#hadhi nafesha fel .env ta3 image docker



jwt = JWTManager(app)












# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    """
    Kubernetes health check endpoint
    Returns detailed health status of gateway and downstream services
    """
    health_status = {
        "status": "healthy",
        "service": "gateway",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "pod_name": os.getenv('POD_NAME', 'unknown'),
        "pod_ip": os.getenv('POD_IP', 'unknown'),
    }
    
    # Check if it's a liveness or readiness probe
    check_type = request.headers.get('X-Health-Check', 'general')
    
    if check_type == 'readiness':
        # For readiness probe, check downstream services
        downstream_services = {
            'auth-service': AUTH_SERVER,
            'user-service': USER_SERVICE,
            'saving-service': SAVING_SERVER
        }
        
        services_status = {}
        all_healthy = True
        
        for service_name, service_url in downstream_services.items():
            try:
                response = requests.get(
                    f"{service_url}/health",
                    timeout=2
                )
                services_status[service_name] = {
                    'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                    'response_time': response.elapsed.total_seconds()
                }
            except Exception as e:
                services_status[service_name] = {
                    'status': 'unreachable',
                    'error': str(e)
                }
                all_healthy = False
        
        health_status['downstream_services'] = services_status
        health_status['status'] = 'healthy' if all_healthy else 'degraded'
        
        if not all_healthy:
            return jsonify(health_status), 503
    
    return jsonify(health_status), 200

# Readiness check (simple version)
@app.route('/ready', methods=['GET'])
def ready():
    """Simple readiness check"""
    return jsonify({"status": "ready"}), 200

# Liveness check (simple version)
@app.route('/live', methods=['GET'])
def live():
    """Simple liveness check"""
    return jsonify({"status": "alive"}), 200

# Metrics endpoint (for Prometheus - optional)
@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    # TODO: Implement actual metrics collection
    return """# HELP gateway_requests_total Total requests
# TYPE gateway_requests_total counter
gateway_requests_total 0
""", 200, {'Content-Type': 'text/plain'}















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
                "password": "temp_password_not_us11447DDDD@@@ed",  
                "role": ROLE.EMPLOYER.value,
                "first_name": firstName,
                "last_name": lastName,
                "address": address,
                "department": "hadhi n3amerha mba3ed",
                "userID": id,  
                "date_of_birth":DateOfBirth
            }
        HEADERS = {"X-Internal-Key": "INTERNAL_API_KEY"} #INTERNAL_API_KEY badelha fe .env

        response_from_saving_service = requests.post(f'http://{SAVING_server}/users/',json=user_data,headers=HEADERS)
        if (response_from_saving_service.status_code == 200):
            return jsonify({"AuthToken": {response_from_auth_service.json().get("Token")}}), 200
        else : 
            return jsonify({"error": "we get an error from saving error"}), 500
    else : 
        return jsonify({"error": "we get an error from auth service"}), 500
    

@app.route('/getCodeForManager', methods=['POST'])
@jwt_required()
def getCode():
    """
    Gateway endpoint - forwards request to UserServices
    UserServices handles all business logic
    """
    try:
        # Get current user's email from JWT token
        current_user_email = get_jwt_identity()
        
        # Get manager email from request body
        data = request.get_json()
        manager_email = data.get('managermail')
        
        if not manager_email:
            return jsonify({"Text": "Manager email is required"}), 400
        
        # Forward entire request to UserServices
        response = requests.post(
            f'http://{UserServices}/getCodeForManager',
            json={
                "current_user_email": current_user_email,
                "manager_email": manager_email
            },
            timeout=10
        )
        
        # Return UserServices response directly
        return response.json(), response.status_code
        
    except requests.exceptions.RequestException as e:
        return jsonify({"Text": f"Service communication error: {str(e)}"}), 503
    except Exception as e:
        return jsonify({"Text": f"Internal error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=7050, debug=False)
   
            