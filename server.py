import json
import logging
import os
from urllib.parse import urljoin

from aiogram import Dispatcher, types, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from flask import Flask, request

from bot.bot import bot
from bot.bot_commands import set_commands
from bot.handlers.handlers import register_handlers
from bot.handlers.utils import process_error
from bot.middlewares import PrintMiddleware
from config import HIMERA_TOKEN_BOT

logging.basicConfig(level=logging.INFO)

server = Flask(__name__)

dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(PrintMiddleware())
register_handlers(dp)

PROJECT_NAME = os.getenv('PROJECT_NAME')

WEBHOOK_HOST = f'https://{PROJECT_NAME}.herokuapp.com/'
WEBHOOK_URL_PATH = f'/webhook/{HIMERA_TOKEN_BOT}'
WEBHOOK_URL = urljoin(WEBHOOK_HOST, WEBHOOK_URL_PATH)


async def on_startup():
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)
    await set_commands(dp)


async def shutdown():
    await dp.storage.close()
    await dp.storage.wait_closed()


@server.route(WEBHOOK_URL_PATH, methods=['POST'])
async def getMessage():
    req = request.stream.read().decode('utf-8')
    update = json.loads(req)
    update = types.Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(dp.bot)
    try:
        await dp.process_update(update)
    except RuntimeError as err:
        await process_error(err, update.message)
    except OSError as err:
        await process_error(err, update.message)
    print('okey'*5)
    return 'Ну типа Химер запущен', 200


@server.route('/')
async def webhook():
    await on_startup()
    return 'Ну типа Химер запущен, а я нужен для вебхука', 200


if __name__ == '__main__':
    server.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
