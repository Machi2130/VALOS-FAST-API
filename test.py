# test_hash.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = "pratham@123"
print(f"Password: {password}")
print(f"Type: {type(password)}")
print(f"Length (chars): {len(password)}")
print(f"Length (bytes): {len(password.encode('utf-8'))}")

try:
    hashed = pwd_context.hash(password)
    print(f"✅ Hash successful: {hashed[:30]}...")
except Exception as e:
    print(f"❌ Error: {e}")
