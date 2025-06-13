"""
Debug script to test JWT token verification
"""
import sys
sys.path.append('.')

from utils.auth import verify_token
from app.config import settings

# 測試token驗證
test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4cCI6MTcxODMxNjU3N30.example"

print("Settings:")
print(f"SECRET_KEY exists: {bool(settings.SECRET_KEY)}")
print(f"ALGORITHM: {settings.ALGORITHM}")

# 先測試真實的登入生成token
from utils.auth import create_access_token
from datetime import timedelta

test_data = {"sub": 1}
token = create_access_token(test_data, timedelta(minutes=30))
print(f"\nGenerated token: {token}")

# 測試驗證
payload = verify_token(token)
print(f"Verified payload: {payload}")

if payload:
    print("✅ Token verification works")
else:
    print("❌ Token verification failed")
