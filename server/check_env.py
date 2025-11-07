"""
Environment Variable Checker
This script helps verify Supabase configuration
"""

import os

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
print("🔍 ENVIRONMENT VARIABLE CHECK")
print("="*60)

# Check for .env file
if os.path.exists('.env'):
    print("✅ .env file found")
    with open('.env', 'r') as f:
        print("\n📄 Contents of .env file:")
        print("-"*60)
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Mask sensitive values
                if '=' in line:
                    key, value = line.split('=', 1)
                    if 'KEY' in key.upper() or 'SECRET' in key.upper():
                        masked_value = value[:10] + '...' if len(value) > 10 else '***'
                        print(f"{key}={masked_value}")
                    else:
                        print(line)
        print("-"*60)
else:
    print("❌ .env file NOT found")
    print("   Create a .env file with your Supabase credentials")

print("\n📋 Environment Variables Status:")
print("-"*60)

# Check SUPABASE_URL
supabase_url = os.getenv("SUPABASE_URL")
is_local_supabase = False
is_cloud_supabase = False

if supabase_url:
    # Detect local vs cloud Supabase
    if "localhost" in supabase_url or "127.0.0.1" in supabase_url:
        is_local_supabase = True
        print(f"✅ SUPABASE_URL: {supabase_url}")
        print(f"   🐳 LOCAL Supabase (Docker) detected!")
    elif supabase_url.startswith("https://") and ".supabase.co" in supabase_url:
        is_cloud_supabase = True
        print(f"✅ SUPABASE_URL: {supabase_url}")
        print(f"   ☁️  CLOUD Supabase detected!")
    else:
        print(f"⚠️  SUPABASE_URL: {supabase_url}")
        print(f"   ⚠️  WARNING: Unusual URL format detected")
        if not supabase_url.startswith("http://") and not supabase_url.startswith("https://"):
            print(f"   → URL should start with http:// or https://")
else:
    print("❌ SUPABASE_URL: NOT SET")

# Check SUPABASE_KEY
supabase_key = os.getenv("SUPABASE_KEY")
if supabase_key:
    print(f"✅ SUPABASE_KEY: {supabase_key[:20]}... (length: {len(supabase_key)})")
    if len(supabase_key) < 50:
        print("   ⚠️  WARNING: Key seems too short for a valid Supabase key")
else:
    print("❌ SUPABASE_KEY: NOT SET")

# Check other variables
print("\n📋 Other Configuration:")
print("-"*60)
secret_key = os.getenv("SECRET_KEY")
jwt_secret_key = os.getenv("JWT_SECRET_KEY")

if secret_key:
    print(f"✅ SECRET_KEY: {secret_key[:10]}...")
else:
    print("⚠️  SECRET_KEY: NOT SET (will use default)")

if jwt_secret_key:
    print(f"✅ JWT_SECRET_KEY: {jwt_secret_key[:10]}...")
else:
    print("⚠️  JWT_SECRET_KEY: NOT SET (will use default)")

print("\n" + "="*60)
print("📝 RECOMMENDATIONS:")
print("="*60)

if not supabase_url or not supabase_key:
    print("\n❌ Supabase is NOT configured properly")
    print("\nTo enable Supabase authentication:")
    print("1. Create a .env file in the server directory")
    print("2. Add these lines:")
    print("\n   For LOCAL Supabase (Docker):")
    print("   SUPABASE_URL=http://localhost:9999")
    print("   SUPABASE_KEY=your-local-anon-key")
    print("\n   For CLOUD Supabase:")
    print("   SUPABASE_URL=https://your-project.supabase.co")
    print("   SUPABASE_KEY=your-anon-public-key")
    print("\n3. Get your credentials:")
    print("   - Local: Run `supabase status` or check Docker logs")
    print("   - Cloud: https://supabase.com/dashboard → Settings → API")
elif is_local_supabase:
    print("\n🐳 Local Supabase (Docker) is configured!")
    print("   The app will use your local Supabase instance")
    print("\n   Make sure:")
    print("   - Supabase Docker container is running")
    print("   - Run: docker ps | grep supabase")
    print("   - Or: supabase status")
    print("\n   Test Supabase health:")
    print("   curl http://localhost:9999/auth/v1/health")
elif is_cloud_supabase:
    print("\n☁️  Cloud Supabase is configured!")
    print("   The app will use your Supabase cloud instance")
    print("\n   Verify in Supabase dashboard:")
    print("   - Project is active")
    print("   - Auth is enabled")
    print("   - Email provider is configured")
else:
    print("\n✅ Supabase appears to be configured!")
    print("   The app should use Supabase for authentication")
    print("\n   If it's not working, check:")
    print("   - Supabase project is active")
    print("   - Auth is enabled in Supabase dashboard")
    print("   - Email provider is configured")

print("="*60 + "\n")
