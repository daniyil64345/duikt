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

load_dotenv()

if not TOKEN:
    raise ValueError("❌ Не знайдено токен!")

# ===============================
# 🌐 Мінімальний health check
# ===============================
async def handle_health(request):
    """Health check для моніторингу"""
    return web.json_response({
        "status": "alive",
        "bot": "running",
        "timestamp": datetime.now().isoformat()
    })

async def start_web_server():
    """Запуск health check сервера"""
    app = web.Application()
    app.router.add_get("/", handle_health)
    app.router.add_get("/health", handle_health)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Health check: http://0.0.0.0:{port}/health")

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
    
    # ⚠️ КРИТИЧНО: Видаляємо webhook перед polling
    await bot.delete_webhook(drop_pending_updates=True)
    
    await bot.set_my_commands(private, scope=types.BotCommandScopeAllPrivateChats())
    print("✅ Webhook видалено")
    print("✅ Команди встановлено")
    print("✅ Бот готовий!")
    print("="*50)

async def on_shutdown():
    print("\n🛑 Зупинка бота...")
    await bot.session.close()

async def start_bot():
    await on_startup()
    try:
        await dp.start_polling(
            bot, 
            allowed_updates=ALLOWED_UPDATES,
            drop_pending_updates=True
        )
    finally:
        await on_shutdown()

async def main():
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
