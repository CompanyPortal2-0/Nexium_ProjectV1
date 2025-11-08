"""
Supabase Docker Port Scanner
Helps you find which port your Supabase auth service is running on
"""

import socket
import urllib.request
import json

print("\n" + "="*60)
print("🔍 SCANNING FOR SUPABASE SERVICES")
print("="*60)

# Common Supabase ports
common_ports = {
    8000: "API Gateway (Kong)",
    9999: "Auth Service (GoTrue)",
    54321: "REST API (PostgREST)",
    54323: "Studio UI",
    54324: "Inbucket (Email testing)",
    54325: "Storage API",
    54326: "Edge Functions",
}

print("\n📡 Checking common Supabase ports on localhost...")
print("-"*60)

found_services = []

for port, service_name in common_ports.items():
    try:
        # Try to connect to the port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {port}: {service_name} - OPEN")
            found_services.append((port, service_name))
            
            # Try to get health endpoint for auth service
            if port in [8000, 9999]:
                try:
                    health_url = f"http://localhost:{port}/auth/v1/health"
                    req = urllib.request.Request(health_url)
                    with urllib.request.urlopen(req, timeout=2) as response:
                        if response.status == 200:
                            print(f"   🎯 AUTH SERVICE FOUND! Use this port for SUPABASE_URL")
                            print(f"   → SUPABASE_URL=http://localhost:{port}")
                except:
                    pass
        else:
            print(f"❌ Port {port}: {service_name} - CLOSED")
    except Exception as e:
        print(f"⚠️  Port {port}: Error - {e}")

print("\n" + "="*60)
print("📊 SUMMARY")
print("="*60)

if found_services:
    print(f"\n✅ Found {len(found_services)} Supabase service(s) running:")
    for port, service in found_services:
        print(f"   • Port {port}: {service}")
else:
    print("\n❌ No Supabase services found running!")
    print("\n💡 To start Supabase:")
    print("   supabase start")
    print("   OR")
    print("   docker-compose up -d")

print("\n" + "="*60)
print("🔑 GETTING SUPABASE CREDENTIALS")
print("="*60)

print("\nRun this command to get your Supabase credentials:")
print("   supabase status")
print("\nLook for:")
print("   • API URL (use this as SUPABASE_URL)")
print("   • anon key (use this as SUPABASE_KEY)")

print("\n" + "="*60 + "\n")
