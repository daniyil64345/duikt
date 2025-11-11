from aiogram.filters import Filter
from aiogram import types, Bot

class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types


    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types

class IsAdmin(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        username = message.from_user.username
        if not username:
            return False  

        return username.lower() in [u.lower() for u in bot.my_admins_list]