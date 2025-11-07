# Supabase Configuration Guide

## Current Issue

You're seeing this error:
```
⚠ Supabase error during signup: Client error '404 Not Found' for url 'http://localhost:9999/auth/v1/signup'
```

This happens because the app is trying to connect to a local Supabase instance at `http://localhost:9999` which isn't running.

---

## ✅ Solution 1: Use Local Authentication Only (RECOMMENDED)

The app has been configured to automatically use **LOCAL-ONLY mode** when no Supabase credentials are set.

**What this means:**
- ✅ Users created with random UUIDs
- ✅ Passwords hashed with bcrypt (secure)
- ✅ All data stored in JSON files
- ✅ No Supabase connection needed
- ✅ No warning messages

**How to use:**
1. Just restart your app - it will automatically detect no Supabase is configured
2. You'll see: `ℹ Running in LOCAL-ONLY mode (no Supabase)`
3. Everything works normally with local authentication

---

## 🌐 Solution 2: Use Real Supabase (Cloud)

If you want to use Supabase authentication:

### Step 1: Create Supabase Project

1. Go to https://app.supabase.com
2. Click "New Project"
3. Fill in:
   - **Name:** Your project name
   - **Database Password:** Create a strong password
   - **Region:** Choose closest to you
4. Wait for project to be created (~2 minutes)

### Step 2: Get Credentials

1. Go to **Settings** (gear icon) → **API**
2. Copy these values:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon public** key (long string starting with `eyJ...`)

### Step 3: Set Environment Variables

**Windows PowerShell:**
```powershell
$env:SUPABASE_URL="https://your-project.supabase.co"
$env:SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Windows CMD:**
```cmd
set SUPABASE_URL=https://your-project.supabase.co
set SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Linux/Mac:**
```bash
export SUPABASE_URL=https://your-project.supabase.co
export SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Step 4: Restart App

```bash
python app.py
```

You'll see:
```
✓ Supabase connection initialized successfully
  URL: https://your-project.supabase.co
```

---

## 🏠 Solution 3: Use Local Supabase Instance (Advanced)

If you want to run Supabase locally:

### Requirements:
- Docker Desktop installed
- Supabase CLI installed

### Steps:

1. **Install Supabase CLI:**
   ```bash
   npm install -g supabase
   ```

2. **Initialize Supabase in your project:**
   ```bash
   cd d:\iset\3eme\S1\integration\projet\work\server
   supabase init
   ```

3. **Start local Supabase:**
   ```bash
   supabase start
   ```

4. **Get local credentials:**
   After starting, you'll see:
   ```
   API URL: http://localhost:54321
   anon key: eyJhbGc...
   ```

5. **Set environment variables:**
   ```powershell
   $env:SUPABASE_URL="http://localhost:54321"
   $env:SUPABASE_KEY="<anon-key-from-output>"
   ```

6. **Restart your app**

---

## 📊 Comparison

| Mode | Setup Time | Cost | Internet Required | Best For |
|------|-----------|------|-------------------|----------|
| **Local Only** | ✅ 0 min | Free | No | Development, Testing |
| **Supabase Cloud** | ⏱️ 5 min | Free tier available | Yes | Production |
| **Local Supabase** | ⏱️ 15 min | Free | No | Advanced testing |

---

## 🎯 Recommended Approach

**For Development:** Use **Local Only** mode (no setup needed)

**For Production:** Use **Supabase Cloud** (free tier: 50,000 users)

---

## ✅ Current Status

After the fix, your app is now running in **LOCAL-ONLY mode**:

- ✅ No Supabase connection errors
- ✅ Users created with UUIDs
- ✅ Passwords secured with bcrypt
- ✅ All data in JSON files
- ✅ Fully functional

---

## 🆘 Troubleshooting

### Still seeing "404 Not Found" error?

**Restart your Flask app:**
```bash
# Stop the current app (Ctrl+C)
# Then restart:
python app.py
```

You should now see:
```
ℹ Running in LOCAL-ONLY mode (no Supabase)
```

### Want to check if Supabase env vars are set?

**Windows PowerShell:**
```powershell
$env:SUPABASE_URL
$env:SUPABASE_KEY
```

If they return `http://localhost:9999`, unset them:
```powershell
Remove-Item Env:\SUPABASE_URL
Remove-Item Env:\SUPABASE_KEY
```

Then restart your app.

---

## 💡 Quick Test

After restarting, test signup:

```bash
# Should work without any Supabase errors
curl -X POST http://localhost:6021/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","FirstName":"Test","LastName":"User","Password":"password123","DateOfBirth":"2000-01-01","Address":"Test"}'
```

**Expected:** No warning messages, just success response.

---

**The app is now configured to work seamlessly without Supabase! 🎉**
