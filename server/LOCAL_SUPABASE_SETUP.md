# 🐳 Local Supabase (Docker) Configuration Guide

## Overview

You're running Supabase locally in Docker with auth on `http://localhost:9999`. This is perfect for development!

I've updated the code to **support local Supabase instances** (previously it was blocking localhost URLs).

---

## ✅ What Changed

### Fixed `app.py`

**Before:**
```python
if SUPABASE_URL and SUPABASE_KEY and SUPABASE_URL != "http://localhost:9999":
    # This blocked your local Supabase! ❌
```

**After:**
```python
if SUPABASE_URL and SUPABASE_KEY:
    # Now supports both cloud and local Supabase! ✅
    is_local_supabase = "localhost" in SUPABASE_URL or "127.0.0.1" in SUPABASE_URL
```

Now the app will:
- ✅ Accept `http://localhost:9999` as a valid Supabase URL
- 🐳 Detect and label it as "Local Supabase (Docker)"
- 🔥 Enable `use_supabase=True` flag
- ✅ Use Supabase for authentication

---

## 🔧 How to Configure

### Step 1: Create `.env` File

Create a `.env` file in the server directory with:

```env
# Local Supabase (Docker)
SUPABASE_URL=http://localhost:9999
SUPABASE_KEY=your-local-anon-key

# Flask secrets (generate random strings)
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

### Step 2: Get Your Local Supabase Key

If you're using Supabase CLI or Docker Compose, find your anon key:

**Option A: From Docker logs**
```bash
docker logs <your-supabase-container>
```

Look for the anon key in the output.

**Option B: From Supabase CLI**
```bash
supabase status
```

This will show:
```
API URL: http://localhost:9999
anon key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Option C: Default Supabase local key**

If using default Supabase local setup, the anon key is usually:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0
```

### Step 3: Update Your `.env`

```env
SUPABASE_URL=http://localhost:9999
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0
SECRET_KEY=dev-secret-key-123
JWT_SECRET_KEY=dev-jwt-secret-456
```

---

## 🧪 Test It

### 1. Start Your Local Supabase

Make sure your Supabase Docker container is running:

```bash
# If using Supabase CLI
supabase start

# Or if using docker-compose
docker-compose up -d
```

Verify it's running:
```bash
curl http://localhost:9999/auth/v1/health
```

Should return: `{"message":"ok"}`

### 2. Start the Flask App

```bash
python app.py
```

**Expected output:**
```
============================================================
🔍 SUPABASE CONFIGURATION CHECK
============================================================
📋 SUPABASE_URL: http://localhost:9999
📋 SUPABASE_KEY: eyJhbGciOiJIUzI1NiI...

🐳 Local Supabase (Docker) detected!
   URL: http://localhost:9999
✅ Supabase credentials found!
✅ Supabase connection initialized successfully
🔥 USE_SUPABASE FLAG = TRUE

✅ userHelper initialized with use_supabase=True
============================================================
```

### 3. Test Signup

```bash
curl -X POST http://localhost:6021/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "role": "GUEST"
  }'
```

**Expected console output:**
```
🔵 [SUPABASE] Attempting to create user: test@example.com
✅ [SUPABASE] User created successfully, ID: abc-123-def
✅ [LOCAL] User saved to JSON with Supabase ID
```

**Expected response:**
```json
{
  "message": "User created successfully!",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 4. Test Login

```bash
curl -X POST http://localhost:6021/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Expected console output:**
```
🔵 [SUPABASE] Attempting to authenticate user: test@example.com
✅ [SUPABASE] Authentication successful, ID: abc-123-def
✅ [LOCAL] Found user by email instead: local-uuid
```

**Expected response:**
```json
{
  "message": "Login successful!",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 🔍 Verify in Supabase Studio

Open Supabase Studio (usually at `http://localhost:54323` or similar) and check:

1. Go to **Authentication** → **Users**
2. You should see the user you just created
3. Email should be `test@example.com`
4. Status should be "Confirmed" (if email confirmation is disabled)

---

## 🐛 Troubleshooting

### Issue 1: "Connection refused" to localhost:9999

**Cause:** Supabase Docker container not running

**Solution:**
```bash
# Check if container is running
docker ps | grep supabase

# Start Supabase
supabase start
# or
docker-compose up -d
```

### Issue 2: "Invalid API key"

**Cause:** Wrong anon key in `.env`

**Solution:**
```bash
# Get the correct key
supabase status

# Update .env with the correct anon key
```

### Issue 3: "User already exists" error

**Cause:** Email already registered in Supabase

**Solution:**
```bash
# Delete the user from Supabase Studio
# Or use a different email address
```

### Issue 4: Still showing "LOCAL-ONLY mode"

**Cause:** `.env` file not loaded or missing variables

**Solution:**
```bash
# Check configuration
python check_env.py

# Make sure .env file exists and has correct format
cat .env
```

---

## 📊 Local vs Cloud Supabase

| Feature | Local (Docker) | Cloud |
|---------|----------------|-------|
| URL | `http://localhost:9999` | `https://xxx.supabase.co` |
| Setup | Docker/CLI required | Just sign up |
| Cost | Free | Free tier available |
| Data | Stored locally | Stored in cloud |
| Internet | Not required | Required |
| Best for | Development | Production |

---

## 🎯 Summary

**Before:**
- ❌ Code rejected `http://localhost:9999` as invalid
- 🔵 App ran in LOCAL-ONLY mode
- ❌ Supabase authentication disabled

**After:**
- ✅ Code accepts local Supabase URLs
- 🐳 Detects Docker/local instances
- 🔥 Supabase authentication enabled
- ✅ Verbose logging shows what's happening

---

## 🚀 Next Steps

1. **Create `.env` file** with your local Supabase credentials
2. **Restart Flask app** - look for the 🐳 Docker detection message
3. **Test signup/login** - watch the verbose logs
4. **Check Supabase Studio** - verify users are being created

Your local Supabase should now work perfectly! 🎉

---

## 💡 Pro Tips

### Tip 1: Reset Local Supabase

If you need to reset your local database:
```bash
supabase db reset
```

### Tip 2: View Logs

```bash
# Supabase logs
supabase logs

# Docker logs
docker logs <container-name> -f
```

### Tip 3: Seed Test Data

Create a seed file to populate test users automatically:
```bash
supabase db seed
```

### Tip 4: Switch to Cloud Later

When ready for production, just update `.env`:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-cloud-anon-key
```

No code changes needed! 🚀
