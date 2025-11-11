import asyncio
import os
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv
from handlers.user_private import user_router
from common.bot_comands_list import private
from aiogram.fsm.strategy import FSMStrategy
from bot_main import TOKEN

from handlers.admin_private import admin_private_router

if not TOKEN:
    raise ValueError("❌ TOKEN не знайдено. Перевір .env файл.")

bot = Bot(TOKEN)
dp = Dispatcher()  # Додамо диспетчер
dp.include_router(user_router)
dp.include_router(admin_private_router)

# ======= Глобальний список адмінів =======



ALLOWED_UPDATES = ["message", "callback_query", "edit_message_text", "edit_message_caption"]

async def main():
    print("✅ Бот запущено")
    await bot.set_my_commands(private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Зупинено вручну")
