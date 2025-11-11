
from dotenv import load_dotenv
import os

# Перевірка 1: Чи файл .env існує?
env_path = os.path.join(os.path.dirname(__file__), '.env')
print(f"🔍 Шукаю .env тут: {env_path}")
print(f"📂 Файл існує? {os.path.exists(env_path)}")

# Перевірка 2: Завантажуємо
result = load_dotenv()
print(f"✅ load_dotenv() результат: {result}")

# Перевірка 3: Всі змінні оточення
print(f"🌍 Всі env змінні: {dict(os.environ)}")

TOKEN = os.getenv("TOKEN")
ADMINS = [7718368607, 2015615532]
DB_PATH = "C:/Users/Asus/OneDrive/Робочий стіл/true_detective.db"

print(f"✅ Token: {TOKEN[:10] if TOKEN else 'None'}...")
print(f"✅ DB_PATH: {DB_PATH}")
print(f"✅ ADMINS: {ADMINS}")