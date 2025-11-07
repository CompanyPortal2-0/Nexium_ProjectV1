"""
Quick Test Script - Supabase Verbose Logging
This script helps you test if Supabase logging is working
"""

import os
import sys
import json

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.dirname(__file__))

# Try to load dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed - reading environment variables directly")
    # Load from .env file manually if it exists
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

print("\n" + "="*60)
print("🧪 TESTING SUPABASE CONFIGURATION")
print("="*60)

# Test 1: Check environment variables
print("\n1️⃣ Checking Environment Variables...")
print("-"*60)

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if supabase_url and supabase_key:
    print(f"✅ SUPABASE_URL: {supabase_url}")
    print(f"✅ SUPABASE_KEY: {supabase_key[:20]}...")
    print("\n   → Supabase SHOULD be enabled")
elif supabase_url or supabase_key:
    print("⚠️  Partial configuration:")
    if supabase_url:
        print(f"   ✅ SUPABASE_URL: {supabase_url}")
    else:
        print("   ❌ SUPABASE_URL: NOT SET")
    if supabase_key:
        print(f"   ✅ SUPABASE_KEY: {supabase_key[:20]}...")
    else:
        print("   ❌ SUPABASE_KEY: NOT SET")
    print("\n   → Supabase will be DISABLED (both required)")
else:
    print("❌ No Supabase configuration found")
    print("   → Running in LOCAL-ONLY mode")

# Test 2: Import and check initialization
print("\n2️⃣ Testing Module Import...")
print("-"*60)

try:
    from supaBase.supaBase import SupabaseConnectionSingleton, SupabaseConfig
    from Helperes.userHelper import userHelper
    print("✅ Modules imported successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 3: Initialize userHelper
print("\n3️⃣ Initializing userHelper...")
print("-"*60)

try:
    # Determine if we should use Supabase
    use_supabase = False
    
    if supabase_url and supabase_key and supabase_url != "http://localhost:9999":
        print("🔥 Initializing with SUPABASE ENABLED")
        supabase_config = SupabaseConfig(url=supabase_url, key=supabase_key)
        supabase_connection = SupabaseConnectionSingleton(supabase_config)
        use_supabase = True
    else:
        print("🔵 Initializing with SUPABASE DISABLED")
        supabase_config = SupabaseConfig(url="https://placeholder.supabase.co", key="placeholder")
        supabase_connection = SupabaseConnectionSingleton(supabase_config)
    
    helper = userHelper(supabase_connection, use_supabase=use_supabase)
    print(f"✅ userHelper initialized with use_supabase={use_supabase}")
    
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Check local storage
print("\n4️⃣ Checking Local Storage...")
print("-"*60)

user_json_file = "testStore/userJson.json"
pass_json_file = "testStore/passJson.json"

try:
    if os.path.exists(user_json_file):
        with open(user_json_file, 'r') as f:
            users = json.load(f)
            print(f"✅ userJson.json exists ({len(users)} users)")
    else:
        print("⚠️  userJson.json does not exist")
        
    if os.path.exists(pass_json_file):
        with open(pass_json_file, 'r') as f:
            passwords = json.load(f)
            print(f"✅ passJson.json exists ({len(passwords)} password hashes)")
            if len(passwords) == 0:
                print("   ⚠️  WARNING: No password hashes stored!")
                print("   → Local authentication will FAIL")
                print("   → You MUST use Supabase if no local passwords")
    else:
        print("⚠️  passJson.json does not exist")
        
except Exception as e:
    print(f"❌ Error reading JSON files: {e}")

# Final summary
print("\n" + "="*60)
print("📊 SUMMARY")
print("="*60)

if use_supabase:
    print("\n✅ Configuration Status: SUPABASE ENABLED")
    print("\nWhat happens when you:")
    print("  • Create a user → Supabase signup API is called")
    print("  • Login → Supabase sign-in API is called")
    print("  • Fallback → Local bcrypt if Supabase fails")
    print("\nExpected logs when creating user:")
    print("  🔵 [SUPABASE] Attempting to create user...")
    print("  ✅ [SUPABASE] User created successfully...")
else:
    print("\n🔵 Configuration Status: LOCAL-ONLY MODE")
    print("\nWhat happens when you:")
    print("  • Create a user → Local UUID + bcrypt password")
    print("  • Login → Check passJson.json for password hash")
    print("  • No Supabase → All authentication is local")
    print("\nExpected logs when creating user:")
    print("  🔵 [LOCAL] Creating user with local UUID")
    print("  ✅ [LOCAL] User created with ID...")
    
    # Check if this will work
    if os.path.exists(pass_json_file):
        with open(pass_json_file, 'r') as f:
            passwords = json.load(f)
            if len(passwords) == 0:
                print("\n❌ PROBLEM DETECTED:")
                print("   passJson.json is EMPTY")
                print("   → Login will FAIL (no passwords to check)")
                print("\n💡 SOLUTION:")
                print("   Either:")
                print("   1. Configure Supabase (recommended)")
                print("   2. Create a new user to generate password hash")

print("\n" + "="*60)
print("🎯 NEXT STEPS")
print("="*60)

if not use_supabase:
    print("\n1. To enable Supabase:")
    print("   • Create .env file with SUPABASE_URL and SUPABASE_KEY")
    print("   • Restart the Flask app")
    print("\n2. To use local mode:")
    print("   • Create a user via /signup endpoint")
    print("   • This will generate password hash in passJson.json")
else:
    print("\n1. Start the Flask app:")
    print("   python app.py")
    print("\n2. Watch for the startup banner showing:")
    print("   🔥 USE_SUPABASE FLAG = TRUE")
    print("\n3. Test signup/login and watch the verbose logs!")

print("\n" + "="*60 + "\n")
