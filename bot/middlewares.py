from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware


class PrintMiddleware(BaseMiddleware):

    @staticmethod
    async def on_pre_process_message(message: types.Message, data: dict):
        print(message.from_user.username, message.from_user.full_name, message.text)
