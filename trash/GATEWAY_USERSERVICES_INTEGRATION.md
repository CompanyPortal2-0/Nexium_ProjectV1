# Gateway & UserServices Integration Guide

## Overview
The Gateway now communicates with UserServices via HTTP REST API instead of importing helpers directly. This follows proper microservices architecture.

---

## Architecture Changes

### Before (Monolithic)
```
Gateway → imports userHelper → Database
```

### After (Microservices)
```
Gateway → HTTP Request → UserServices API → userHelper → Database
```

---

## API Endpoints

### UserServices (Port 7052)

#### 1. Get User by Email
```http
GET /users/by-email/<email>
```

**Response:**
```json
{
  "Email": "user@example.com",
  "FirstName": "John",
  "LastName": "Doe",
  "ID": "user-id-123",
  "DateOfBirth": "1990-01-01",
  "Address": "123 Main St",
  "Role": "hr",
  "Department": "IT",
  "EmployeesList": []
}
```

**Status Codes:**
- `200` - User found
- `404` - User not found
- `500` - Server error

---

#### 2. Assign Code to Manager
```http
POST /assign-code
Content-Type: application/json

{
  "manager_email": "manager@example.com",
  "manager_id": "manager-id-123",
  "code": "ABC12345"
}
```

**Response:**
```json
{
  "success": true,
  "code": "ABC12345"
}
```

**Status Codes:**
- `200` - Code assigned successfully
- `400` - Missing required fields
- `500` - Failed to save code
- `503` - Service communication error

---

### Gateway (Port 7050)

#### Get Manager Code (Protected Route)
```http
POST /getCodeForManager
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "managermail": "manager@example.com"
}
```

**Flow:**
1. Validates JWT token
2. Extracts user email from token
3. Fetches current user from UserServices
4. Checks if current user is HR
5. Fetches manager details from UserServices
6. Generates random 8-character code
7. Sends code to UserServices for storage
8. Returns code to client

**Response:**
```json
{
  "code": "XYZ98765"
}
```

**Status Codes:**
- `200` - Code generated successfully
- `400` - Missing manager email
- `401` - Not authorized (user is not HR)
- `404` - User not found
- `500` - Failed to assign code
- `503` - Service communication error

---

## Gateway Implementation

### JWT Token Flow
```python
@app.route('/getCodeForManager', methods=['POST'])
@jwt_required()
def getCode():
    # 1. Extract email from JWT token
    current_user_email = get_jwt_identity()
    
    # 2. Fetch user from UserServices
    current_user_response = requests.get(
        f'http://{UserServices}/users/by-email/{current_user_email}'
    )
    
    # 3. Verify authorization
    current_user = current_user_response.json()
    if current_user.get('Role') != ROLE.HR.value:
        return jsonify({"Text": "not authorized"}), 401
    
    # 4. Process request...
```

---

## Configuration

### Environment Variables

**Gateway (.env):**
```env
AUTH_SERVER=localhost:7051
SAVING_server=http://127.0.0.1:5001
UserServices_server=localhost:7052
JWT_SECRET_KEY=your-super-secret-jwt-token-with-at-least-32-characters-long
```

**UserServices (.env):**
```env
SAVING_server=http://127.0.0.1:5001
INTERNAL_API_KEY=your-internal-api-key
```

**AuthService (.env):**
```env
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
JWT_SECRET_KEY=your-super-secret-jwt-token-with-at-least-32-characters-long
```

---

## Service Communication

### Request Flow Example

```
Client → Gateway → AuthService → Supabase
   ↓
Gateway → UserServices → Saving Server
```

1. **Client** sends login request to Gateway
2. **Gateway** forwards to AuthService
3. **AuthService** validates with Supabase and returns JWT
4. **Client** uses JWT for subsequent requests
5. **Gateway** validates JWT and extracts email
6. **Gateway** queries UserServices for user details
7. **UserServices** fetches from Saving Server
8. **UserServices** converts and returns data to Gateway

---

## Error Handling

All services implement consistent error handling:

```python
try:
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        return response.json(), 200
    else:
        return jsonify({"error": "Service error"}), response.status_code
        
except requests.exceptions.RequestException as e:
    return jsonify({"error": f"Service communication error: {str(e)}"}), 503
    
except Exception as e:
    return jsonify({"error": str(e)}), 500
```

---

## Testing

### Start All Services

```powershell
# Terminal 1 - Auth Service
cd authService
python app.py

# Terminal 2 - User Services
cd userServices
python app.py

# Terminal 3 - Gateway
cd Gateway
python app.py
```

### Test Flow

1. **Login** (get JWT token):
```bash
curl -X POST http://localhost:7050/login \
  -H "Content-Type: application/json" \
  -d '{"email": "hr@example.com", "password": "password123"}'
```

2. **Get Manager Code** (use JWT from step 1):
```bash
curl -X POST http://localhost:7050/getCodeForManager \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{"managermail": "manager@example.com"}'
```

---

## Benefits

✅ **Decoupled Services**: Each service can be developed/deployed independently
✅ **Scalable**: Services can scale horizontally
✅ **Maintainable**: Clear separation of concerns
✅ **Testable**: Each service can be tested in isolation
✅ **Secure**: JWT-based authentication with role-based access control

---

## Migration Checklist

- [x] Create `/users/by-email/<email>` endpoint in UserServices
- [x] Create `/assign-code` endpoint in UserServices
- [x] Update Gateway to use JWT tokens
- [x] Update Gateway to call UserServices API
- [x] Add proper error handling
- [x] Add timeout to requests
- [ ] Implement JWT token creation in AuthService
- [ ] Add request logging
- [ ] Add rate limiting
- [ ] Add API documentation (Swagger/OpenAPI)
- [ ] Add integration tests
