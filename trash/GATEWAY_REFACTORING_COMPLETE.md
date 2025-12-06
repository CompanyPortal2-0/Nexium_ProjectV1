# ✅ Gateway Refactoring Complete

## Summary of Changes

### Gateway/app.py

#### **Removed Direct Imports**
- ❌ Removed: `from Helperes.userHelper import userHelper`
- ✅ Added: JWT integration with `get_jwt_identity`
- ✅ Added: `secrets` and `string` for code generation

#### **Updated `/getCodeForManager` Endpoint**

**Before:**
```python
@app.route('/getCodeForManager', methods=['GET'])
@jwt_required()
def getCode():
    current_employer = userHelper.getUserByEmail(get_jwt_identity())
    if current_employer is None or current_employer.getRole() != ROLE.HR:
        return jsonify({"Text": "not authorized"}), 401
    data = request.get_json()
    managerMail = data.get('managermail')
    user = userHelper.getUserByEmail(managerMail)
    if user is None:
        return jsonify({"Text": "user not found"}), 404
    code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    userHelper.assignCodeToManager(user, code)
    return jsonify({"code": code})
```

**After:**
```python
@app.route('/getCodeForManager', methods=['POST'])
@jwt_required()
def getCode():
    """Generate manager invitation code - Only HR users can generate codes"""
    try:
        # 1. Get email from JWT token
        current_user_email = get_jwt_identity()
        
        # 2. Fetch current user from UserServices API
        current_user_response = requests.get(
            f'http://{UserServices}/users/by-email/{current_user_email}',
            timeout=10
        )
        
        if current_user_response.status_code != 200:
            return jsonify({"Text": "Current user not found"}), 404
        
        current_user = current_user_response.json()
        
        # 3. Check if current user is HR
        if current_user.get('Role') != ROLE.HR.value:
            return jsonify({"Text": "not authorized"}), 401
        
        # 4. Get manager email from request
        data = request.get_json()
        manager_email = data.get('managermail')
        
        if not manager_email:
            return jsonify({"Text": "Manager email is required"}), 400
        
        # 5. Fetch manager details from UserServices API
        manager_response = requests.get(
            f'http://{UserServices}/users/by-email/{manager_email}',
            timeout=10
        )
        
        if manager_response.status_code != 200:
            return jsonify({"Text": "Manager not found"}), 404
        
        manager_user = manager_response.json()
        
        # 6. Generate random code
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        
        # 7. Send code to UserServices for storage
        code_response = requests.post(
            f'http://{UserServices}/assign-code',
            json={
                "manager_email": manager_email,
                "manager_id": manager_user.get('ID'),
                "code": code
            },
            timeout=10
        )
        
        if code_response.status_code == 200:
            return jsonify({"code": code}), 200
        else:
            return jsonify({"Text": "Failed to assign code"}), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({"Text": f"Service communication error: {str(e)}"}), 503
    except Exception as e:
        return jsonify({"Text": f"Internal error: {str(e)}"}), 500
```

---

### UserServices/app.py

#### **New Endpoint: `/assign-code`**

```python
@app.route('/assign-code', methods=['POST'])
def assign_code():
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
        
        NEXUS_API_URL = os.getenv('SAVING_server', 'http://127.0.0.1:5001')
        response = requests.post(
            f"{NEXUS_API_URL}/invites/",
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
```

---

## Key Improvements

### 🔐 Security
- JWT-based authentication with role validation
- Token-based user identification (no password passing)
- Role-based access control (only HR can generate codes)

### 🏗️ Architecture
- **Microservices Pattern**: Gateway doesn't import from other services
- **HTTP Communication**: Services communicate via REST API
- **Separation of Concerns**: Each service has clear responsibilities

### 🛡️ Error Handling
- Comprehensive try-catch blocks
- Specific HTTP status codes
- Timeout on all HTTP requests (10 seconds)
- Service communication error handling

### 📊 Flow Control
- Step-by-step validation
- Early returns for error cases
- Clear success/failure paths

---

## Service Responsibilities

### Gateway (Port 7050)
- **Authentication Gateway**: Validates JWT tokens
- **Request Router**: Routes requests to appropriate services
- **Authorization**: Checks user roles and permissions
- **No Business Logic**: Just orchestrates service calls

### UserServices (Port 7052)
- **User Data Management**: Fetches and converts user data
- **Code Management**: Assigns codes to managers
- **Data Persistence**: Communicates with Saving Server

### AuthService (Port 7051)
- **Authentication**: Login/Signup with Supabase
- **JWT Token Issuing**: Creates tokens with user claims
- **Password Security**: Handled by Supabase

### Saving Server (Port 5001)
- **Data Storage**: Stores user data, codes, invites
- **CRUD Operations**: Create, Read, Update, Delete

---

## Request Flow Example

```
Client Request:
POST /getCodeForManager
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Body: {"managermail": "manager@example.com"}

↓

Gateway:
1. Validates JWT token
2. Extracts email from token: "hr@example.com"
3. GET http://localhost:7052/users/by-email/hr@example.com
   ← {"Email": "hr@example.com", "Role": "hr", ...}
4. Validates: Role == "hr" ✓
5. GET http://localhost:7052/users/by-email/manager@example.com
   ← {"Email": "manager@example.com", "ID": "mgr-123", ...}
6. Generates code: "XYZ98765"
7. POST http://localhost:7052/assign-code
   Body: {"manager_email": "...", "manager_id": "mgr-123", "code": "XYZ98765"}
   
↓

UserServices:
8. POST http://127.0.0.1:5001/invites/
   Body: {"manager_id": "mgr-123", "code": "XYZ98765", "max_uses": 1}
9. ← 201 Created

↓

Response to Client:
200 OK
{"code": "XYZ98765"}
```

---

## Testing Commands

### 1. Start All Services

```powershell
# Terminal 1 - Saving Server (if not running)
cd saving_server
python app.py

# Terminal 2 - Auth Service
cd authService
python app.py

# Terminal 3 - User Services
cd userServices
python app.py

# Terminal 4 - Gateway
cd Gateway
python app.py
```

### 2. Test Login

```powershell
curl -X POST http://localhost:7050/login `
  -H "Content-Type: application/json" `
  -d '{"email": "hr@example.com", "password": "Password123"}'
```

### 3. Test Get Manager Code

```powershell
curl -X POST http://localhost:7050/getCodeForManager `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" `
  -d '{"managermail": "manager@example.com"}'
```

---

## Next Steps

1. ✅ Gateway communicates with UserServices via HTTP
2. ✅ No direct imports between services
3. ✅ JWT-based authentication
4. ⬜ Implement JWT token creation in AuthService
5. ⬜ Add request logging middleware
6. ⬜ Add rate limiting
7. ⬜ Add API documentation (Swagger)
8. ⬜ Write integration tests

---

## Benefits Achieved

✅ **True Microservices**: Services are independently deployable
✅ **Scalability**: Can scale each service independently
✅ **Maintainability**: Clear separation of concerns
✅ **Testability**: Each service can be tested in isolation
✅ **Security**: JWT-based authentication with role validation
✅ **Resilience**: Proper error handling and timeouts
