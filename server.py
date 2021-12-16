import json
import logging
import os
from urllib.parse import urljoin

from aiogram import Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.webhook import get_new_configured_app
from aiohttp import web
from flask import Flask, request

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


async def shutdown():
    await dp.storage.close()
    await dp.storage.wait_closed()


# if __name__ == '__main__':
#     app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_URL_PATH)
#     app.on_startup.append(on_startup)
#     app.on_shutdown.append(shutdown)
#     print('les go')
#     web.run_app(app, host='0.0.0.0', port=os.getenv('PORT'))

server = Flask(__name__)


@server.route(WEBHOOK_URL_PATH, methods=['POST'])
async def getMessage():
    print(request.stream.read().decode('utf-8'))
    update_id = json.loads(request.stream.read().decode('utf-8'))['update_id']
    print(update_id)
    update = types.update.Update(update_id=update_id)
    print(update)
    await dp.process_update(update)
    print('okey'*5)
    # await dp.process_updates(await bot.get_updates())
    return 'Ну типа Химер запущен', 200
# {"update_id":630215216,
# "message":{"message_id":69,"from":{"id":285942176,"is_bot":false,"first_name":"dam_mek","username":"dam_mek","language_code":"ru"},"chat":{"id":285942176,"first_name":"dam_mek","username":"dam_mek","type":"private"},"date":1639663998,"text":"\u041f\u0440\u043e\u0432\u0435\u0440\u0438\u0442\u044c \u043b\u0438\u043c\u0438\u0442\u044b"}}

@server.route('/')
async def webhook():
    await on_startup(None)
    return 'Ну типа Химер запущен, а я нужен для вебхука', 200


if __name__ == '__main__':
    server.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
