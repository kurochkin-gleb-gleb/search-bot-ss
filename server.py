import logging
import os
from urllib.parse import urljoin

from aiogram import Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.webhook import get_new_configured_app
from aiohttp import web

from bot.bot import bot
from bot.bot_commands import set_commands
from bot.handlers.handlers import register_handlers
from bot.middlewares import PrintMiddleware
from config import HIMERA_TOKEN_BOT

logging.basicConfig(level=logging.INFO)

dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(PrintMiddleware())
register_handlers(dp)

PROJECT_NAME = os.getenv('PROJECT_NAME')  # Set it as you've set TOKEN env var

WEBHOOK_HOST = f'https://{PROJECT_NAME}.herokuapp.com/'  # Enter here your link from Heroku project settings
WEBHOOK_URL_PATH = f'/webhook/{HIMERA_TOKEN_BOT}'
WEBHOOK_URL = urljoin(WEBHOOK_HOST, WEBHOOK_URL_PATH)


async def on_startup(app_):
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)
    await set_commands(dp)


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()

if __name__ == '__main__':
    app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_URL_PATH)
    app.on_startup.append(on_startup)
    print('les go')
    web.run_app(app, host='0.0.0.0', port=os.getenv('PORT'))
