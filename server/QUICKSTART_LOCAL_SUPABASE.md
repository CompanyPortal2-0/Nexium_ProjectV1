# 🚀 QUICK START - Local Supabase Configuration

## TL;DR - Get Running in 2 Minutes

You're using **Local Supabase in Docker** on `http://localhost:9999`. Here's how to enable it:

### 1. Create `.env` File

Create a file named `.env` in the server directory:

```env
SUPABASE_URL=http://localhost:9999
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0
SECRET_KEY=dev-secret-123
JWT_SECRET_KEY=dev-jwt-456
```

> 💡 **Note:** The key above is the **default Supabase local anon key**. If you've customized your Supabase setup, get your key with `supabase status`.

### 2. Verify Configuration

```bash
python check_env.py
```

**Expected output:**
```
✅ SUPABASE_URL: http://localhost:9999
   🐳 LOCAL Supabase (Docker) detected!
✅ SUPABASE_KEY: eyJhbGciOiJIUzI1NiI...

🐳 Local Supabase (Docker) is configured!
```

### 3. Start Flask App

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
============================================================
```

### 4. Test It

**Create a user:**
```bash
curl -X POST http://localhost:6021/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "role": "GUEST"}'
```

**Console shows:**
```
🔵 [SUPABASE] Attempting to create user: test@example.com
✅ [SUPABASE] User created successfully, ID: abc-123
```

**Done!** 🎉

---

## 🔍 What If My Supabase Key is Different?

### Get Your Local Supabase Key

Run this command:
```bash
supabase status
```

**Output shows:**
```
API URL: http://localhost:9999
anon key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Copy the `anon key` and use it in your `.env` file.

**Or check Docker logs:**
```bash
docker logs <container-name> | grep "anon key"
```

---

## ✅ Checklist

Before starting the Flask app, verify:

- [ ] Supabase Docker container is running
  ```bash
  docker ps | grep supabase
  # or
  supabase status
  ```

- [ ] Supabase auth is accessible
  ```bash
  curl http://localhost:9999/auth/v1/health
  # Should return: {"message":"ok"}
  ```

- [ ] `.env` file exists with correct values
  ```bash
  cat .env
  ```

- [ ] Flask app shows 🐳 Docker detection
  ```bash
  python app.py
  # Look for: 🐳 Local Supabase (Docker) detected!
  ```

---

## 🐛 Common Issues

### "Connection refused" to localhost:9999

**Fix:**
```bash
# Start Supabase
supabase start

# Or restart Docker container
docker-compose restart
```

### "Invalid API key" or Auth failures

**Fix:**
```bash
# Get the correct key
supabase status

# Update .env with the anon key shown
```

### Still showing "LOCAL-ONLY mode"

**Fix:**
```bash
# Check if .env is loaded
python check_env.py

# Make sure both SUPABASE_URL and SUPABASE_KEY are set
```

---

## 📁 File Structure

Your `.env` file should be here:
```
server/
├── .env          ← Create this file
├── app.py
├── main.go
├── modeles/
└── ...
```

---

## 🎯 What Changed

I fixed the code that was **blocking localhost URLs**:

**Before:** ❌
- Code rejected `http://localhost:9999` as invalid
- App ran in LOCAL-ONLY mode (no Supabase)

**After:** ✅
- Code accepts local Supabase URLs
- Detects and labels as 🐳 Docker instance
- Enables Supabase authentication

---

## 📚 More Information

- **Full setup guide:** `LOCAL_SUPABASE_SETUP.md`
- **Debugging guide:** `SUPABASE_DEBUGGING.md`
- **General solution:** `THIS_IS_THE_SOLUTION.md`

---

**That's it!** Create the `.env` file and you're ready to go! 🚀
