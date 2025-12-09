# Migration Guide: JSON Storage → Nexus API

## 🎯 **What Changed**

Your Flask application now uses **Nexus API** for user data storage instead of local JSON files (`userJson.json`).

### ✅ **What Stayed the Same:**
- **Supabase Authentication** - Still used for login/signup authentication
- **Password Storage** - Still stored locally using `passwordHelper`
- **Manager Codes** - Still stored in `codes.json`
- **Meeting Data** - Still stored in `meetings.json`

### 🔄 **What Changed:**
- **User Data Storage** - Now stored in Nexus API (port 5001) instead of `userJson.json`
- **User CRUD Operations** - Now go through `NexusApiHelper` class

---

## 📋 **Prerequisites**

### 1. **Start Nexus API Server**
The Nexus API must be running on `http://127.0.0.1:5001`

```powershell
# Navigate to Nexus API directory
cd path\to\nexus-api

# Start the server
python app.py
```

**Verify it's running:**
```powershell
curl http://127.0.0.1:5001/health
```

Expected response:
```json
{
  "status": 200,
  "message": "OK"
}
```

---

## 🚀 **How It Works Now**

### **Signup Flow:**
```
User sends signup request
    ↓
1. Create auth account in Supabase (authentication)
    ↓
2. Create user data in Nexus API (data storage)
    ↓
3. Store password locally (passwordHelper)
    ↓
4. Link to manager if code provided
    ↓
5. Return JWT token
```

### **Login Flow:**
```
User sends login request
    ↓
1. Verify credentials with Supabase (authentication)
    ↓
2. Verify password locally (passwordHelper)
    ↓
3. Fetch user data from Nexus API
    ↓
4. Return JWT token
```

---

## 🔧 **New Architecture**

### **File Structure:**
```
Helperes/
├── nexusApiHelper.py    # ✨ NEW - Handles all Nexus API interactions
├── userHelper.py         # ✅ UPDATED - Now uses NexusApiHelper
├── authHelper.py         # ✅ UNCHANGED - Still uses Supabase
├── passwordHelper.py     # ✅ UNCHANGED - Still uses local storage
└── meetHelper.py         # ✅ UNCHANGED
```

### **Data Storage Mapping:**

| Data Type | Old Storage | New Storage | Notes |
|-----------|-------------|-------------|-------|
| User Profile | `userJson.json` | Nexus API | ✅ Migrated |
| Passwords | `passJson.json` | `passJson.json` | ✅ Unchanged |
| Manager Codes | `codes.json` | `codes.json` | ✅ Unchanged |
| Meetings | `meetings.json` | `meetings.json` | ✅ Unchanged |
| Authentication | Supabase | Supabase | ✅ Unchanged |

---

## 📝 **Role Mapping**

Your internal roles are automatically converted to Nexus API format:

| Internal Role | Nexus API Role |
|---------------|----------------|
| `ROLE.HR` | `"hr"` |
| `ROLE.MANAGER` | `"manager"` |
| `ROLE.EMPLOYER` | `"employee"` |
| `ROLE.GUEST` | `"employee"` |

---

## 🧪 **Testing the Migration**

### **Test 1: Create New User**
```powershell
# Make sure Nexus API is running first!
curl http://127.0.0.1:5001/health

# Then test signup
curl -X POST http://localhost:6021/signup `
  -H "Content-Type: application/json" `
  -d '{
    "email": "testuser@example.com",
    "Password": "TestPass123",
    "FirstName": "Test",
    "LastName": "User",
    "DateOfBirth": "1990-01-01",
    "Address": "123 Test St"
  }'
```

**Expected Result:**
- ✅ User created in Supabase (auth)
- ✅ User created in Nexus API (data)
- ✅ Password stored locally
- ✅ JWT token returned

**Check in Nexus API:**
```powershell
curl http://127.0.0.1:5001/users/
```

### **Test 2: Login**
```powershell
curl -X POST http://localhost:6021/login `
  -H "Content-Type: application/json" `
  -d '{
    "email": "testuser@example.com",
    "password": "TestPass123"
  }'
```

**Expected Result:**
- ✅ Supabase authentication succeeds
- ✅ User data fetched from Nexus API
- ✅ JWT token returned

### **Test 3: Get All Employees (HR only)**
```powershell
# First login as HR to get token
$token = "YOUR_JWT_TOKEN_HERE"

curl -X GET http://localhost:6021/hr/getallemp `
  -H "Authorization: Bearer $token"
```

**Expected Result:**
- ✅ Employee list fetched from Nexus API
- ✅ Only employees with role "EMPLOYER" returned

---

## 🔍 **Logging & Debugging**

The new system has comprehensive logging:

```python
logger.info("✅ User created successfully")      # Success
logger.warning("⚠️ User already exists")         # Warning
logger.error("❌ Failed to create user")         # Error
```

**Check console output for:**
- `✅ User retrieved from Nexus API: email@example.com`
- `✅ User created in Nexus API: email@example.com`
- `❌ Failed to create user in Nexus API: 409 - Email already registered`

---

## ⚠️ **Important Notes**

### **1. Nexus API Must Be Running**
If Nexus API is down, user operations will fail. Make sure it's running on port 5001.

### **2. Existing JSON Data Won't Migrate Automatically**
Users in `userJson.json` are **NOT** automatically migrated to Nexus API. They need to:
- Create new accounts, OR
- You need to write a migration script

### **3. Password Storage Still Local**
Passwords are still stored in `passJson.json` because:
- Nexus API has its own password system (not used for auth)
- Supabase handles authentication
- This is intentional for security separation

### **4. Manager Codes Still in JSON**
Manager invitation codes are still in `codes.json` - this is intentional and doesn't need to change.

---

## 🐛 **Troubleshooting**

### **Error: "Failed to create user in Nexus API"**
**Solution:** Check if Nexus API is running:
```powershell
curl http://127.0.0.1:5001/health
```

### **Error: "Network error creating user in Nexus API"**
**Solution:** 
1. Verify Nexus API URL in `nexusApiHelper.py` line 14:
   ```python
   BASE_URL = "http://127.0.0.1:5001"
   ```
2. Check firewall/antivirus isn't blocking port 5001

### **Error: "User not found in Nexus API"**
**Solution:** User might only exist in old JSON file. Check:
```powershell
# Check JSON file
cat userJson.json

# Check Nexus API
curl http://127.0.0.1:5001/users/
```

### **Error: "409 - Email already registered"**
**Solution:** User already exists in Nexus API. This is handled gracefully and returns success.

---

## 📊 **Migration Script (Optional)**

If you want to migrate existing users from `userJson.json` to Nexus API:

```python
import json
from Helperes.nexusApiHelper import NexusApiHelper
from modeles.user import User

# Read existing users
with open('userJson.json', 'r') as f:
    users_data = json.load(f)

# Migrate each user
for user_id, user_data in users_data.items():
    user = User(
        Email=user_data['Email'],
        FirstName=user_data['FirstName'],
        LastName=user_data['LastName'],
        ID=user_id,
        DateOfBirth=user_data['DateOfBirth'],
        Address=user_data['Address'],
        EmployeesList=user_data.get('EmployeesList', [])
    )
    
    success = NexusApiHelper.create_user_in_nexus(user)
    if success:
        print(f"✅ Migrated: {user.Email}")
    else:
        print(f"❌ Failed: {user.Email}")
```

---

## ✅ **Success Checklist**

- [ ] Nexus API running on port 5001
- [ ] Supabase Auth running
- [ ] Flask app starts without errors
- [ ] Can create new users via `/signup`
- [ ] Can login via `/login`
- [ ] User data appears in Nexus API (`GET /users/`)
- [ ] HR can get employee list
- [ ] Manager codes still work

---

## 📞 **Support**

If you encounter issues:
1. Check Nexus API logs
2. Check Flask app console output for error messages
3. Verify all services are running (Nexus API, Supabase, Flask)
4. Check the comprehensive logging in console
