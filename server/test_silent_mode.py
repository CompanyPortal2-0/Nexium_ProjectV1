"""
Quick test to verify user creation works without Supabase warnings
"""

import sys
import uuid

# Redirect stderr to capture warnings
from io import StringIO
old_stderr = sys.stderr
sys.stderr = StringIO()

# Import and test
from supaBase.supaBase import SupabaseConnectionSingleton, SupabaseConfig
from Helperes.userHelper import userHelper

# Create userHelper in local-only mode
config = SupabaseConfig(url="https://placeholder.supabase.co", key="placeholder")
supabase_conn = SupabaseConnectionSingleton(config)
user_helper = userHelper(supabase_conn, use_supabase=False)

# Test user creation
test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
new_user = user_helper.CreateUser(
    Email=test_email,
    FirstName="Test",
    LastName="User",
    DateOfBirth="2000-01-01",
    Address="123 Test St",
    password="TestPassword123!"
)

# Check for warnings
warnings = sys.stderr.getvalue()
sys.stderr = old_stderr

print("=" * 70)
print("Testing User Creation in Local-Only Mode")
print("=" * 70)

if new_user:
    print(f"✅ User created successfully!")
    print(f"   Email: {new_user.Email}")
    print(f"   ID: {new_user.ID}")
    
    # Check if any Supabase warnings were printed
    if "Supabase" in warnings:
        print(f"\n⚠️  Warning messages detected:")
        print(warnings)
    else:
        print(f"\n✅ No Supabase warning messages!")
        print("   User creation is completely silent")
    
    # Clean up
    from testStore.userJson import JsonUserStore
    store = JsonUserStore("./userJson.json")
    store.delete_user(new_user.ID)
    print(f"\n✅ Test user cleaned up")
else:
    print("❌ User creation failed")

print("=" * 70)
