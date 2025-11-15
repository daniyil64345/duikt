from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
ADMINS = [7718368607, 2015615532]
ADMIN_ID = os.getenv("ADMIN_ID") if os.getenv("ADMIN_ID") else 7718368607
DB_PATH = os.getenv("DB_PATH") or "true_detective.db"

print(f"✅ Token: {TOKEN[:10] if TOKEN else 'None'}...")
print(f"✅ DB_PATH from env: {os.getenv('DB_PATH')}")
print(f"✅ DB_PATH final: {DB_PATH}")
print(f"✅ DB_PATH exists: {os.path.exists(DB_PATH)}")
print(f"✅ Current directory: {os.getcwd()}")
print(f"✅ Files in directory: {os.listdir('.')}")
print(f"✅ ADMINS: {ADMINS}")
