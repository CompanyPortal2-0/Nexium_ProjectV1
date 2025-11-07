# Supabase Integration Guide

## Overview

The `userHelper` class has been refactored to support **Supabase authentication** while maintaining backward compatibility with local JSON storage.

---

## 🔄 What Changed

### Before (Static Class):
```python
class userHelper:
    @staticmethod
    def getUserByEmail(email: str) -> User:
        # ...
```

### After (Instance-Based with Constructor):
```python
class userHelper:
    def __init__(self, supabase_connection: SupabaseConnectionSingleton):
        self.supabase = supabase_connection
        self.json_store = JsonUserStore("./userJson.json")
    
    def getUserByEmail(self, email: str) -> Optional[User]:
        # ...
```

---

## 🏗️ Architecture

```
┌─────────────────┐
│   Flask App     │
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
    ┌────▼─────┐    ┌─────▼──────────┐
    │userHelper│────│ Supabase Auth  │
    └────┬─────┘    └────────────────┘
         │
    ┌────▼─────────┐
    │ JSON Storage │
    └──────────────┘
```

### Flow:
1. **Signup**: Creates user in Supabase Auth → Stores user data in JSON with Supabase ID
2. **Login**: Authenticates via Supabase → Retrieves user data from JSON
3. **User ID**: Uses Supabase user ID (UUID) instead of generating a new one

---

## 📝 New Methods

### 1. `__init__(supabase_connection)`
Initialize userHelper with Supabase connection.

```python
from supaBase.supaBase import SupabaseConnectionSingleton, SupabaseConfig

config = SupabaseConfig(url="https://xxx.supabase.co", key="your-key")
supabase = SupabaseConnectionSingleton(config)
user_helper = userHelper(supabase)
```

### 2. `getUserBySupabaseId(supabase_id)`
Get user by their Supabase authentication ID.

```python
user = user_helper.getUserBySupabaseId("uuid-from-supabase")
```

### 3. `CreateUser()` - Updated
Now creates user in **both** Supabase Auth and local storage.

```python
new_user = user_helper.CreateUser(
    Email="user@example.com",
    FirstName="John",
    LastName="Doe",
    DateOfBirth="1990-01-01",
    Address="123 Main St",
    password="SecurePassword123"
)
# Returns User object if successful, None if failed
```

**What happens:**
1. Checks if email exists locally
2. Creates user in Supabase Auth (returns Supabase ID)
3. Stores user in JSON with Supabase ID as primary key
4. Stores password hash locally as backup (bcrypt)

### 4. `authenticateUser(email, password)` - New
Authenticate user via Supabase Auth.

```python
user = user_helper.authenticateUser("user@example.com", "password123")
if user:
    print("Login successful!")
else:
    print("Invalid credentials")
```

**What happens:**
1. Authenticates with Supabase
2. Retrieves user data from local JSON
3. Returns User object if successful

---

## ⚙️ Configuration

### 1. Set up Supabase Project

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Create a new project
3. Get your credentials from **Settings → API**:
   - `Project URL` (SUPABASE_URL)
   - `anon public` key (SUPABASE_KEY)

### 2. Configure Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3. Load Environment Variables (Optional)

Install python-dotenv:
```bash
pip install python-dotenv
```

Update `app.py`:
```python
from dotenv import load_dotenv
load_dotenv()  # Load .env file
```

---

## 🔐 Security Features

### Dual Authentication System

1. **Primary**: Supabase handles password hashing and authentication
2. **Backup**: Local bcrypt hashing for fallback

### Benefits:
- ✅ Supabase handles secure password storage (bcrypt by default)
- ✅ Local backup allows offline development
- ✅ Can migrate to Supabase-only authentication later
- ✅ User IDs are globally unique (Supabase UUIDs)

---

## 📊 Data Flow Examples

### Signup Flow:

```
User submits signup form
         ↓
POST /signup
         ↓
user_helper.CreateUser()
         ↓
    ┌────┴────┐
    │         │
Supabase   Check local
Auth       storage for
creates    duplicate email
user       
    │         │
    └────┬────┘
         ↓
   Get Supabase ID
         ↓
   Store in JSON
   (ID = Supabase ID)
         ↓
   Store password
   locally (backup)
         ↓
  Return JWT token
```

### Login Flow:

```
User submits login form
         ↓
POST /login
         ↓
user_helper.authenticateUser()
         ↓
Supabase.sign_in_user()
         ↓
   Returns Supabase ID
         ↓
user_helper.getUserBySupabaseId()
         ↓
   Fetch from JSON
         ↓
  Return JWT token
```

---

## 🧪 Testing

### Test Signup with Supabase:

```python
# Make sure Supabase credentials are configured
import requests

response = requests.post("http://localhost:6021/signup", json={
    "email": "test@example.com",
    "FirstName": "Test",
    "LastName": "User",
    "Password": "SecurePass123!",
    "DateOfBirth": "1990-01-01",
    "Address": "123 Test St"
})

print(response.json())
# {"accessToken": "eyJ0eXAiOi..."}
```

### Test Login with Supabase:

```python
response = requests.post("http://localhost:6021/login", json={
    "email": "test@example.com",
    "password": "SecurePass123!"
})

print(response.json())
# {"accessToken": "eyJ0eXAiOi..."}
```

---

## 🔄 Migration from Old System

### Old Users (UUID-based IDs):
If you have existing users with random UUIDs, they won't work with Supabase authentication.

**Options:**

1. **Keep Both Systems** (Recommended for now):
   - Old users use local bcrypt authentication
   - New users use Supabase authentication
   - Gradually migrate users

2. **Force Password Reset**:
   - Delete old users
   - Users re-register via `/signup`
   - Gets Supabase ID automatically

3. **Manual Migration Script** (Advanced):
   ```python
   # Create Supabase users for existing local users
   for user in old_users:
       supabase_id = supabase.sign_up_user(user.email, new_password)
       user.ID = supabase_id
       json_store.add_user(user)
   ```

---

## ⚠️ Important Notes

### 1. Supabase Email Confirmation

By default, Supabase requires email confirmation. To disable for testing:

1. Go to **Authentication → Settings** in Supabase
2. Uncheck "Enable email confirmations"
3. Save

### 2. Password Requirements

Supabase enforces minimum password strength. Default: 6 characters

Configure in **Authentication → Settings → Password Requirements**

### 3. Rate Limiting

Supabase has built-in rate limiting for auth endpoints:
- Default: 30 requests/hour per IP for signup
- 30 requests/hour per IP for login

### 4. Local Development Without Supabase

If you don't want to use Supabase yet:

**Option 1**: Use dummy credentials (app will fail on auth)

**Option 2**: Add fallback to local auth:

```python
def authenticateUser(self, email: str, password: str) -> Optional[User]:
    # Try Supabase first
    try:
        supabase_user_id = self.supabase.sign_in_user(email, password)
        if supabase_user_id:
            return self.getUserBySupabaseId(supabase_user_id)
    except:
        pass
    
    # Fallback to local authentication
    user = self.getUserByEmail(email)
    if user and passwordHelper.isPasswordTrueForUser(user.ID, password):
        return user
    
    return None
```

---

## 📦 Updated Dependencies

Add to `requirements.txt`:
```txt
Flask==3.0.0
flask-jwt-extended==4.6.0
bcrypt==4.1.2
supabase==2.3.0
python-dotenv==1.0.0  # For .env file support
```

Install:
```bash
pip install -r requirements.txt
```

---

## 🎯 Benefits of This Approach

✅ **Scalable**: Supabase handles millions of users  
✅ **Secure**: Industry-standard authentication  
✅ **Features**: Email verification, password reset, OAuth (Google, GitHub, etc.)  
✅ **Real-time**: Supabase provides real-time subscriptions  
✅ **Database**: Can extend to use Supabase PostgreSQL instead of JSON  
✅ **Backup**: Local authentication as fallback  

---

## 🚀 Next Steps

1. ✅ Set up Supabase project
2. ✅ Configure environment variables
3. ✅ Test signup/login with Supabase
4. 📋 Optional: Migrate to Supabase database (instead of JSON)
5. 📋 Optional: Add OAuth providers (Google, GitHub)
6. 📋 Optional: Enable email verification
7. 📋 Optional: Add password reset functionality

---

## 🆘 Troubleshooting

### "Invalid API key" error:
- Check your `SUPABASE_KEY` in environment variables
- Make sure you're using the `anon public` key, not the `service_role` key

### "Email already registered" in Supabase:
- Email exists in Supabase Auth but not in local JSON
- Check Supabase dashboard → Authentication → Users
- Delete user from Supabase or use different email

### Users can't login after migration:
- Old users have local UUIDs, not Supabase IDs
- Implement fallback authentication (see "Local Development" section)

---

**Your application now uses enterprise-grade authentication! 🎉**
