# Quick Start Guide

## ✅ All Bugs Fixed!

Your Flask HR Management API is now fully functional with all critical bugs resolved.

---

## 🚀 Getting Started

### 1. Activate Virtual Environment (if not already active)

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 2. Verify Installation

```bash
python test_fixes.py
```

You should see all tests passing ✓

### 3. Start the Server

```bash
python app.py
```

Server will start on: **http://0.0.0.0:6021**

---

## 📡 API Endpoints

### **Public Endpoints** (No Authentication Required)

#### 1. **Signup** - Create New User
```http
POST http://localhost:6021/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "FirstName": "John",
  "LastName": "Doe",
  "Password": "SecurePassword123",
  "DateOfBirth": "1990-01-15",
  "Address": "123 Main Street"
}
```

**Success Response:**
```json
{
  "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error Response (Duplicate Email):**
```json
{
  "Text": "email already used"
}
```

---

#### 2. **Login** - Authenticate User
```http
POST http://localhost:6021/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Success Response:**
```json
{
  "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error Responses:**

Missing credentials:
```json
{
  "Text": "missing content"
}
```

User not found:
```json
{
  "Text": "user not found"
}
```

Wrong password:
```json
{
  "Text": "credentials are wrong"
}
```

---

### **Protected Endpoints** (Require JWT Token)

Use the access token in the Authorization header:
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

#### 3. **Get All Employers** (HR Only)
```http
GET http://localhost:6021/hr/getallemp
Authorization: Bearer <your_jwt_token>
```

**Response:**
```json
[
  {
    "ID": "uuid-here",
    "FirstName": "Jane",
    "LastName": "Smith",
    "Email": "jane@example.com",
    "Role": "EMPLOYER",
    "Department": "IT",
    "EmployeesList": [],
    ...
  }
]
```

---

#### 4. **Get All Managers** (HR Only)
```http
GET http://localhost:6021/hr/getallang
Authorization: Bearer <your_jwt_token>
```

**Response:** Same format as employers

---

#### 5. **Assign Employee to Manager** (HR Only)
```http
POST http://localhost:6021/hr/assemployee
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "empId": "employee@example.com",
  "managerId": "manager@example.com"
}
```

**Success Response:**
```json
{
  "Text": "employee assigned successfully"
}
```

**Error Responses:**

Not authorized (non-HR user):
```json
{
  "Text": "not authorized"
}
```

User not found:
```json
{
  "Text": "user not found"
}
```

Invalid roles:
```json
{
  "Text": "invalid roles"
}
```

---

## 🧪 Testing with cURL

### Signup:
```bash
curl -X POST http://localhost:6021/signup \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@test.com\",\"FirstName\":\"Test\",\"LastName\":\"User\",\"Password\":\"password123\",\"DateOfBirth\":\"2000-01-01\",\"Address\":\"Test Address\"}"
```

### Login:
```bash
curl -X POST http://localhost:6021/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@test.com\",\"password\":\"password123\"}"
```

### Get Employers (replace TOKEN):
```bash
curl -X GET http://localhost:6021/hr/getallemp \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🧪 Testing with PowerShell

### Signup:
```powershell
Invoke-WebRequest -Uri "http://localhost:6021/signup" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"test@test.com","FirstName":"Test","LastName":"User","Password":"password123","DateOfBirth":"2000-01-01","Address":"Test Address"}'
```

### Login:
```powershell
$response = Invoke-WebRequest -Uri "http://localhost:6021/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"test@test.com","password":"password123"}'
  
$response.Content
```

---

## 🔐 User Roles

- **GUEST** - Default role (no special permissions)
- **EMPLOYER** - Regular employee
- **MANAGER** - Can manage employees
- **HR** - Can access all HR endpoints
- **ADMIN** - (Not yet implemented)

---

## 📝 What Was Fixed

1. ✅ **getUserByEmail bug** - Now returns `None` instead of `"ejjaw"`
2. ✅ **Password saving** - Passwords now saved on signup
3. ✅ **Real JWT tokens** - Signup returns valid tokens
4. ✅ **Department serialization** - No more crashes
5. ✅ **Duplicate emails** - Prevented
6. ✅ **Error messages** - Fixed typos
7. ✅ **Login error handling** - Handles missing users
8. ✅ **Employee assignment** - Saves both records
9. ✅ **Password security** - Upgraded to bcrypt
10. ✅ **Import errors** - Removed unused imports

See **BUG_FIXES.md** for detailed information.

---

## ⚠️ Important Notes

### Password Migration
Existing users in `userJson.json` have old SHA-512 hashes and **won't be able to login**. 

Solutions:
1. Create new test users using `/signup`
2. Delete old users and re-register them
3. Implement password migration (contact for help)

### Current Test Users
The existing users in your JSON files:
- Email: `eerf` (HR role)
- Email: `eerf.tr` (EMPLOYER role)
- Email: `eerf.tr.cd` (MANAGER role)
- Email: `yqssin;qssss.655` (HR role)

**These users have old password hashes and won't work until you migrate them.**

---

## 🎯 Next Steps

1. **Create a new HR user:**
   ```bash
   # Signup as HR (you'll need to manually edit userJson.json to set Role to "HR")
   # Or create regular user and test employer/manager features
   ```

2. **Test the endpoints** using Postman, cURL, or your frontend

3. **Consider improvements:**
   - Move to a real database (PostgreSQL, MongoDB)
   - Add input validation (email format, password strength)
   - Implement environment variables for secrets
   - Add rate limiting
   - Add CORS for frontend integration
   - Add logging and monitoring

---

## 🆘 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "Permission denied" errors
Make sure you're in the virtual environment:
```bash
.venv\Scripts\activate
```

### Can't login with existing users
Create new users with `/signup` - old passwords are incompatible with bcrypt.

### Port already in use
Change the port in `app.py`:
```python
app.run(host='0.0.0.0', port=6021, debug=False)  # Change 6021 to another port
```

---

**Your application is now ready to use! 🎉**

For detailed bug fix information, see: **BUG_FIXES.md**
