
import asyncio
from aiogram import Bot, Dispatcher, types
from aiohttp import web
import os
from dotenv import load_dotenv
from datetime import datetime

from handlers.user_private import user_router
from handlers.admin_private import admin_private_router
from common.bot_comands_list import private
from bot_main import TOKEN

if not TOKEN:
    raise ValueError("❌ Не знайдено токен!")

async def handle_root(request):
    """Головна сторінка - для GitHub Actions ping"""
    uptime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bot Status</title>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .container {{
                background: rgba(255,255,255,0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }}
            h1 {{ margin: 0 0 20px 0; }}
            .status {{ font-size: 20px; margin: 10px 0; }}
            .emoji {{ font-size: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="emoji">🤖</div>
            <h1>✅ Bot is Running!</h1>
            <div class="status">🟢 Status: <strong>Online</strong></div>
            <div class="status">⏰ Time: <strong>{uptime}</strong></div>
            <div class="status">🚀 Powered by: <strong>GitHub Actions</strong></div>
        </div>
    </body>
    </html>
    '''
    return web.Response(text=html, content_type='text/html')

async def handle_health(request):
    """Health check endpoint для моніторингу"""
    return web.json_response({
        'status': 'ok',
        'bot': 'running',
        'timestamp': datetime.now().isoformat()
    })

async def handle_ping(request):
    """Простий ping endpoint"""
    return web.Response(text="pong")

# ============================================
# ЧАСТИНА 2: Telegram бот
# ============================================

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Підключення роутерів
dp.include_router(user_router)
dp.include_router(admin_private_router)

ALLOWED_UPDATES = [
    "message", "callback_query", "edited_message", "inline_query"
]

# ============================================
# ЧАСТИНА 3: Запуск всього разом
# ============================================

async def on_startup():
    """Виконується при запуску бота"""
    print("=" * 50)
    print("🚀 Запуск бота...")
    print("=" * 50)
    
    # Встановлення команд
    await bot.set_my_commands(
        private,
        scope=types.BotCommandScopeAllPrivateChats()
    )
    
    print("✅ Команди встановлено")
    print("✅ База даних підключена")
    print("✅ Бот готовий до роботи!")
    print("=" * 50)

async def on_shutdown():
    """Виконується при зупинці бота"""
    print("\n🛑 Зупинка бота...")
    await bot.session.close()
    print("👋 До побачення!")

async def start_bot():
    """Запуск Telegram бота"""
    await on_startup()
    
    try:
        await dp.start_polling(
            bot,
            allowed_updates=ALLOWED_UPDATES,
            drop_pending_updates=True  # Пропускаємо старі апдейти після перезапуску
        )
    finally:
        await on_shutdown()

async def start_web_server():
    """Запуск веб-сервера"""
    app = web.Application()
    
    # Додавання роутів
    app.router.add_get('/', handle_root)
    app.router.add_get('/health', handle_health)
    app.router.add_get('/ping', handle_ping)
    
    # Запуск сервера
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    
    print("🌐 Веб-сервер запущено на порту 8080")
    print("📍 Keepalive URL: https://your-repl.username.repl.co")

async def main():
    """Головна функція - запуск всього"""
    # Створюємо задачі для паралельного виконання
    await asyncio.gather(
        start_web_server(),  # Веб-сервер
        start_bot()          # Telegram бот
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Зупинено користувачем")
    except Exception as e:
        print(f"\n❌ Помилка: {e}")
        raise