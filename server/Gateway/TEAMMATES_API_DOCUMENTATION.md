# 📊 Gateway Analysis: How Users See Employees with the Same Manager

## Overview
The Gateway provides functionality for employees to see their teammates (other employees who share the same manager) through a well-structured endpoint system.

---

## 🔍 How It Works

### **Architecture Flow**

```
User with JWT Token
        ↓
Gateway: GET /teammates
        ↓
Gateway/helpers/user_helper.py → UserHelper.get_teammates()
        ↓
HTTP Request to UserService
        ↓
UserService: GET /users/{email}/teammates
        ↓
userServices/userHelper.py → get_teammates()
        ↓
1. Find the employee's manager
2. Get all employees under that manager
3. Filter out the requesting employee
4. Return teammates with details
        ↓
Response back to user
```

---

## 📍 Endpoint Details

### **Gateway Endpoint: `GET /teammates`**

**Location:** `Gateway/app.py` (lines 287-300)

```python
@app.route('/teammates', methods=['GET'])
@jwt_required()
def get_teammates():
    """Get teammates for the currently logged-in user using UserHelper"""
    current_user_email = AuthHelper.get_user_email_from_jwt_identity(get_jwt_identity())
    
    if not current_user_email:
        return jsonify({"success": False, "error": "Could not determine user email from token"}), 401
    
    include_details = request.args.get('include_details', 'true')
    include_manager = request.args.get('include_manager', 'true')
    
    result, status_code = UserHelper.get_teammates(current_user_email, include_details, include_manager)
    return jsonify(result), status_code
```

**Key Features:**
- ✅ Requires JWT authentication
- ✅ Automatically extracts user email from JWT token
- ✅ Supports query parameters for customization
- ✅ Delegates to UserHelper for business logic

---

## 🔧 Helper Method

### **Gateway Helper: `UserHelper.get_teammates()`**

**Location:** `Gateway/helpers/user_helper.py` (lines 33-65)

```python
@staticmethod
def get_teammates(
    user_email: str,
    include_details: str = 'true',
    include_manager: str = 'true'
) -> Tuple[Dict[str, Any], int]:
    """
    Get all teammates of an employee (other employees under the same manager).
    
    Args:
        user_email: The email of the user to get teammates for
        include_details: If 'true', returns full user objects instead of just emails
        include_manager: If 'true', includes manager information in response
        
    Returns:
        Tuple of (response_data, status_code)
    """
    try:
        response = requests.get(
            f'http://{UserHelper.USER_SERVICE}/users/{user_email}/teammates',
            params={
                'include_details': include_details,
                'include_manager': include_manager
            },
            timeout=UserHelper.TIMEOUT
        )
        return response.json(), response.status_code
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Get teammates service error: {e}")
        return {"success": False, "error": f"Service communication error: {str(e)}"}, 503
    except Exception as e:
        logger.error(f"Get teammates error: {e}")
        return {"success": False, "error": f"Internal error: {str(e)}"}, 500
```

**Features:**
- ✅ Communicates with UserService via HTTP
- ✅ Passes query parameters for customization
- ✅ Handles errors gracefully
- ✅ Returns structured response

---

## 🎯 Backend Logic

### **UserService Logic: `get_teammates()`**

**Location:** `userServices/userHelper.py` (lines 503-590)

**Algorithm:**
1. **Verify Employee Exists**
   - Fetch employee data from database
   - Return error if not found

2. **Find Manager**
   - Search all users to find who has this employee in their `employeesList`
   - If no manager found, return empty teammates list

3. **Get All Employees Under Manager**
   - Extract manager's `employeesList`
   - This list contains all employees managed by that manager

4. **Filter Teammates**
   - Remove the requesting employee from the list
   - Keep only their peers (teammates)

5. **Build Response**
   - If `include_details=true`: Fetch full user objects for each teammate
   - If `include_details=false`: Return only email addresses
   - If `include_manager=true`: Include manager information

---

## 📝 Request/Response Examples

### **Request Example**

```bash
curl -X GET "http://localhost:7050/teammates?include_details=true&include_manager=true" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### **Successful Response (with teammates)**

```json
{
  "success": true,
  "employee": "john.doe@example.com",
  "teammates_count": 2,
  "manager": {
    "email": "manager@example.com",
    "first_name": "Boss",
    "last_name": "Manager",
    "department": "IT",
    "role": "MANAGER"
  },
  "teammates": [
    {
      "id": "auth0_user1",
      "email": "jane.smith@example.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "role": "employee",
      "department": "IT",
      "address": "123 Street, City",
      "date_of_birth": "1990-05-15",
      "employeesList": []
    },
    {
      "id": "auth0_user2",
      "email": "bob.wilson@example.com",
      "first_name": "Bob",
      "last_name": "Wilson",
      "role": "employee",
      "department": "IT",
      "address": "456 Avenue, City",
      "date_of_birth": "1988-03-20",
      "employeesList": []
    }
  ]
}
```

### **Response (no manager - top-level manager)**

```json
{
  "success": true,
  "employee": "ceo@example.com",
  "message": "No manager found for this employee",
  "manager": null,
  "teammates": [],
  "teammates_count": 0
}
```

### **Response (minimal details)**

**Request:** `GET /teammates?include_details=false&include_manager=false`

```json
{
  "success": true,
  "employee": "john.doe@example.com",
  "teammates_count": 2,
  "teammates": [
    "jane.smith@example.com",
    "bob.wilson@example.com"
  ]
}
```

---

## 🔐 Authentication & Authorization

### **Authentication Flow:**

1. **User logs in** → Receives JWT token
2. **JWT contains:** User ID
3. **Gateway extracts:** User email from user ID (via AuthHelper)
4. **Authorization:** Only the authenticated user can see their own teammates

### **JWT Resolution:**

```python
# Get JWT identity
user_id = get_jwt_identity()

# Resolve to email
current_user_email = AuthHelper.get_user_email_from_jwt_identity(user_id)
```

---

## 📊 Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_details` | boolean | `true` | If true, returns full user objects; if false, only emails |
| `include_manager` | boolean | `true` | If true, includes manager information in response |

---

## 🔄 Related Endpoints

### **1. GET /team**
- **Purpose:** Get complete team structure (employee + manager + teammates)
- **Difference:** Returns more comprehensive information including the user themselves

### **2. GET /my-employees**
- **Purpose:** For managers to see their subordinates
- **Difference:** Shows employees managed BY the user (not peers)

---

## 💡 Key Concepts

### **Teammates vs Subordinates**

| Concept | Definition | Who Uses It | Endpoint |
|---------|------------|-------------|----------|
| **Teammates** | Other employees under the same manager (peers) | Employees | `/teammates` |
| **Subordinates** | Employees managed by you | Managers | `/my-employees` |
| **Team** | You + your manager + your teammates | Anyone | `/team` |

---

## 🏗️ Data Model

### **How Teammates Are Determined:**

```
Manager
  └── employeesList: [employee1@email, employee2@email, employee3@email]

When employee1 asks for teammates:
  → Find their manager
  → Get manager's employeesList
  → Remove employee1 from the list
  → Result: [employee2@email, employee3@email]
```

### **Manager Assignment:**

Employees are assigned to a manager when they:
1. Sign up with a manager's invitation code (`managercode` field)
2. The signup process adds their email to the manager's `employeesList`

---

## 🔍 Error Handling

### **Possible Responses:**

| Status Code | Scenario | Response |
|-------------|----------|----------|
| `200` | Success | Teammates list with details |
| `401` | No JWT token | `{"error": "Missing JWT token"}` |
| `401` | Invalid JWT | `{"error": "Could not determine user email"}` |
| `404` | Employee not found | `{"success": false, "error": "Employee not found"}` |
| `503` | Service unavailable | `{"error": "Service communication error"}` |
| `500` | Internal error | `{"error": "Internal error"}` |

---

## 📈 Complete User Journey

### **Scenario: Employee wants to see their teammates**

1. **Employee logs in:**
   ```
   POST /login
   → Receives JWT token
   ```

2. **Employee requests teammates:**
   ```
   GET /teammates?include_details=true&include_manager=true
   Authorization: Bearer <jwt_token>
   ```

3. **Gateway processes request:**
   - Validates JWT token
   - Extracts user email from token
   - Calls UserHelper.get_teammates()

4. **UserService processes:**
   - Finds employee in database
   - Locates their manager
   - Gets all employees under that manager
   - Filters out requesting employee
   - Fetches full details for each teammate

5. **Response returned:**
   - Manager information
   - List of teammates with full details
   - Count of teammates

---

## 🎯 Summary

**How users see other employees with the same manager:**

✅ **Endpoint:** `GET /teammates`  
✅ **Authentication:** JWT token required  
✅ **Automatic:** User email extracted from JWT  
✅ **Customizable:** Query parameters for details/manager info  
✅ **Response:** Full employee details including name, address, department  
✅ **Logic:** Finds manager → Gets all their employees → Filters out requester  

**The system is already fully implemented and working!** 🎉
