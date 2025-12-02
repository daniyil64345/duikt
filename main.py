import asyncio
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiohttp import web
from dotenv import load_dotenv

from handlers.user_private import user_router
from handlers.admin_private import admin_private_router
from common.bot_comands_list import private
from bot_main import TOKEN

# ===============================
# ✅ Завантаження env
# ===============================
load_dotenv()

if not TOKEN:
    raise ValueError("❌ Не знайдено токен!")

# ===============================
# 🌐 Веб-сервер
# ===============================
async def handle_root(request):
    """Головна сторінка"""
    uptime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""
    <html>
    <head><title>Bot Status</title></head>
    <body>
        <h1>✅ Bot is Running!</h1>
        <p>⏰ Time: {uptime}</p>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')

async def handle_health(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "ok",
        "bot": "running",
        "timestamp": datetime.now().isoformat()
    })

async def handle_ping(request):
    """Ping endpoint"""
    return web.Response(text="pong")

async def start_web_server():
    """Запуск веб-сервера"""
    app = web.Application()
    app.router.add_get("/", handle_root)
    app.router.add_get("/health", handle_health)
    app.router.add_get("/ping", handle_ping)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    repl_slug = os.environ.get("REPL_SLUG", "workspace")
    repl_owner = os.environ.get("REPL_OWNER", "owner")
    print(f"🌐 Веб-сервер запущено на порту {port}")
    print(f"📍 Keepalive URL: https://{repl_slug}.{repl_owner}.repl.co")

# ===============================
# 🤖 Telegram бот
# ===============================
bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.include_router(user_router)
dp.include_router(admin_private_router)

ALLOWED_UPDATES = ["message", "callback_query", "edited_message", "inline_query"]

async def on_startup():
    print("="*50)
    print("🚀 Запуск бота...")
    await bot.set_my_commands(private, scope=types.BotCommandScopeAllPrivateChats())
    print("✅ Команди встановлено")
    print("✅ Бот готовий до роботи!")
    print("="*50)

async def on_shutdown():
    print("\n🛑 Зупинка бота...")
    await bot.session.close()
    print("👋 До побачення!")

async def start_bot():
    await on_startup()
    try:
        await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES, drop_pending_updates=True)
    finally:
        await on_shutdown()

# ===============================
# 🔗 Головна функція
# ===============================
async def main():
    """Запуск веб-сервера і бота паралельно"""
    await asyncio.gather(
        start_web_server(),
        start_bot()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Зупинено користувачем")
    except Exception as e:
        print(f"\n❌ Помилка: {e}")
        raise
