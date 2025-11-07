# 🔍 Supabase Debugging Guide

## Current Status: Verbose Logging Enabled

I've re-enabled **verbose logging** for Supabase operations. You'll now see detailed messages about what's happening during authentication.

---

## 📋 What Changed

### 1. **Enhanced Logging in `userHelper.py`**

Both `CreateUser()` and `authenticateUser()` now show detailed debug messages:

- 🔵 **INFO** - General information
- ✅ **SUCCESS** - Successful operations  
- ❌ **ERROR** - Failed operations
- ⚠️ **WARNING** - Fallback or unexpected behavior

### 2. **Startup Configuration Check in `app.py`**

When you start the Flask app, you'll see:

```
============================================================
🔍 SUPABASE CONFIGURATION CHECK
============================================================
📋 SUPABASE_URL: [your URL or NOT SET]
📋 SUPABASE_KEY: [first 20 chars... or NOT SET]

✅ Valid Supabase credentials found!
   OR
⚠️  Running in LOCAL-ONLY mode (no Supabase)
   Reason: SUPABASE_URL not set (or other reason)

🔥 USE_SUPABASE FLAG = TRUE
   OR
🔵 USE_SUPABASE FLAG = FALSE

✅ userHelper initialized with use_supabase=True/False
============================================================
```

---

## 🔧 How to Debug Your Issue

### Issue: Authentication fails when `passJson.json` is empty

This means Supabase is **NOT** being used. Here's why:

1. **Check environment variables**

Run this command to see your configuration:
```bash
python check_env.py
```

This will show you:
- ✅ If `.env` file exists
- ✅ If `SUPABASE_URL` is set (and valid)
- ✅ If `SUPABASE_KEY` is set
- ⚠️ Any configuration issues

2. **Most likely cause**: `use_supabase` flag is `False`

This happens when:
- `SUPABASE_URL` is not set in environment
- `SUPABASE_KEY` is not set in environment
- `SUPABASE_URL` equals `"http://localhost:9999"` (invalid)

---

## ✅ How to Fix It

### Option 1: Configure Supabase (Recommended)

1. **Create a `.env` file** in the server directory:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-public-key-here
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

2. **Get your Supabase credentials:**
   - Go to https://supabase.com/dashboard
   - Select your project
   - Go to **Settings** → **API**
   - Copy **Project URL** → Use as `SUPABASE_URL`
   - Copy **anon/public key** → Use as `SUPABASE_KEY`

3. **Restart the Flask app**

You should now see:
```
✅ Valid Supabase credentials found!
🔥 USE_SUPABASE FLAG = TRUE
```

### Option 2: Use Local Authentication Only

If you want to use local authentication (without Supabase):

1. **Make sure `passJson.json` has password hashes:**

```json
{
  "user-uuid-here": "bcrypt-hash-here"
}
```

2. Don't set `SUPABASE_URL` or `SUPABASE_KEY` in environment

The app will run in local-only mode and use `passJson.json` for authentication.

---

## 🧪 Testing the Fix

### After configuring Supabase:

1. **Start the Flask app:**
```bash
python app.py
```

2. **Look for the startup banner:**
```
============================================================
🔍 SUPABASE CONFIGURATION CHECK
============================================================
📋 SUPABASE_URL: https://xxxxx.supabase.co
📋 SUPABASE_KEY: eyJhbGciOiJIUzI1NiI...
✅ Valid Supabase credentials found!
🔥 USE_SUPABASE FLAG = TRUE
```

3. **Try to create a user:**
```bash
curl -X POST http://localhost:6021/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "role": "GUEST"}'
```

4. **Watch the console output:**
```
🔵 [SUPABASE] Attempting to create user: test@example.com
✅ [SUPABASE] User created successfully, ID: xxxx-xxxx-xxxx
```

5. **Try to login:**
```bash
curl -X POST http://localhost:6021/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

6. **Watch the console output:**
```
🔵 [SUPABASE] Attempting to authenticate user: test@example.com
✅ [SUPABASE] Authentication successful, ID: xxxx-xxxx-xxxx
```

---

## 🐛 Common Issues

### 1. "SUPABASE_URL not set"

**Solution:** Create `.env` file with valid Supabase URL

### 2. "404 Not Found" errors to Supabase

**Cause:** Invalid Supabase URL (e.g., `http://localhost:9999`)

**Solution:** Use your real Supabase project URL from the dashboard

### 3. "getaddrinfo failed" errors

**Cause:** Network issues or invalid URL

**Solution:** 
- Check your internet connection
- Verify the Supabase URL is correct
- Make sure it's `https://` not `http://`

### 4. "Authentication failed - returned None"

**Cause:** Wrong credentials or user doesn't exist in Supabase

**Solution:**
- Make sure user is created in Supabase first (via signup)
- Check that Supabase Auth is enabled in dashboard
- Verify email/password are correct

### 5. "Password verification failed" (local mode)

**Cause:** `passJson.json` is empty or missing user's password hash

**Solution:**
- Either configure Supabase (recommended)
- Or create user again to generate password hash

---

## 📊 Understanding the Logs

### When Supabase is ENABLED (`use_supabase=True`):

**Signup:**
```
🔵 [SUPABASE] Attempting to create user: user@example.com
✅ [SUPABASE] User created successfully, ID: abc-123
✅ [LOCAL] User saved to JSON with Supabase ID
```

**Login:**
```
🔵 [SUPABASE] Attempting to authenticate user: user@example.com
✅ [SUPABASE] Authentication successful, ID: abc-123
✅ [LOCAL] Found user by email instead: local-uuid
```

### When Supabase is DISABLED (`use_supabase=False`):

**Signup:**
```
🔵 [LOCAL] Creating user with local UUID
✅ [LOCAL] User created with ID: local-uuid-here
```

**Login:**
```
🔵 [LOCAL] Using local authentication for: user@example.com
🔵 [LOCAL] Found user in JSON, checking password...
✅ [LOCAL] Password verified successfully
```

---

## 🎯 Quick Reference

| Scenario | `use_supabase` | Authentication Method | Requires `.env` |
|----------|----------------|----------------------|-----------------|
| Supabase configured | `True` | Supabase API | ✅ Yes |
| No `.env` file | `False` | Local bcrypt + JSON | ❌ No |
| Invalid Supabase URL | `False` | Local bcrypt + JSON | ❌ No |
| Supabase error occurs | `False` (fallback) | Local bcrypt + JSON | ⚠️ Partial |

---

## 📞 Next Steps

1. **Run `python check_env.py`** to diagnose configuration
2. **Start the Flask app** and look at the startup banner
3. **Test signup/login** and watch the verbose logs
4. **If Supabase still not working**, share the console output

The verbose logging will now show you exactly what's happening at each step! 🎉
