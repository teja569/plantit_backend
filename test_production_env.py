"""
Test script to verify production environment setup
Run this locally with production-like environment variables
"""
import os
import sys

print("="*60)
print("Production Environment Test")
print("="*60)

# Required variables
required_vars = {
    "SECRET_KEY": "Must be a secure random string (not 'change-me-in-production')",
    "DATABASE_URL": "Must be PostgreSQL connection string (not SQLite)",
    "GEMINI_API_KEY": "Your Gemini API key",
}

optional_vars = {
    "ALLOWED_ORIGINS": "Comma-separated frontend URLs",
    "FRONTEND_URL": "Main frontend URL",
    "DEBUG": "Should be 'False' for production",
}

print("\n📋 Checking Required Variables:")
print("-" * 60)
all_ok = True
for var, desc in required_vars.items():
    value = os.getenv(var)
    if value:
        if var == "SECRET_KEY" and value == "change-me-in-production":
            print(f"❌ {var}: Using default value (NOT ALLOWED in production)")
            all_ok = False
        elif var == "DATABASE_URL" and value.startswith("sqlite"):
            print(f"❌ {var}: Using SQLite (NOT ALLOWED in production)")
            all_ok = False
        else:
            preview = value[:30] + "..." if len(value) > 30 else value
            print(f"✅ {var}: Set ({len(value)} chars) - {preview}")
    else:
        print(f"❌ {var}: NOT SET - {desc}")
        all_ok = False

print("\n📋 Checking Optional Variables:")
print("-" * 60)
for var, desc in optional_vars.items():
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: Set")
    else:
        print(f"⚠️  {var}: Not set - {desc}")

print("\n" + "="*60)
if all_ok:
    print("✅ All required variables are set correctly!")
    print("\n🧪 Testing imports...")
    try:
        sys.path.insert(0, '.')
        from main import app
        print("✅ App imports successfully!")
        print("✅ Production environment is configured correctly!")
    except Exception as e:
        print(f"❌ Import failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        all_ok = False
else:
    print("❌ Some required variables are missing or invalid!")
    print("\nFix:")
    print("1. Set missing variables in Vercel")
    print("2. Make sure SECRET_KEY is not 'change-me-in-production'")
    print("3. Make sure DATABASE_URL is PostgreSQL (not SQLite)")
    print("4. Redeploy after setting variables")

print("="*60)
sys.exit(0 if all_ok else 1)


