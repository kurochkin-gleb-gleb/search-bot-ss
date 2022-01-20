import asyncio
import aiohttp
import os

from aiogram import types

from bot import reply_keyboards
from bot.bot import bot
from bot.handlers import utils
from bot.messages import bot_responses
from excel.async_search import search_by_name
from config import HIMERA_TOKEN_BOT


def process_document(bot_message, bot_message_, file_id):
    loop = asyncio.new_event_loop()
    try:
        document = loop.run_until_complete(work_with_excel(bot_message, file_id))
        loop.run_until_complete(end_process(bot_message, bot_message_, file_id, document))
    except Exception as err:
        loop.run_until_complete(bot.send_message(bot_message['chat']['id'], bot_responses['error'].format(error=err),
                                                 reply_markup=reply_keyboards.menu, parse_mode='Markdown'))
    finally:
        loop.close()


async def end_process(bot_message, bot_message_, file_name, document):
    await bot.delete_message(bot_message_['chat']['id'], bot_message_['message_id'])
    await bot.delete_message(bot_message['chat']['id'], bot_message['message_id'])
    new_file_name = document.split('/')[-1]
    doc = types.InputFile(document, filename=new_file_name)
    await bot.send_document(bot_message['chat']['id'], doc, reply_markup=reply_keyboards.menu)
    for file in f'./excel/documents/{file_name}', f'./excel/documents/{new_file_name}':
        if os.path.exists(file):
            os.remove(file)


async def work_with_excel(bot_message, file_id):
    file = await bot.get_file(file_id)
    file_name = f'{file.file_unique_id}.xlsx'
    async with aiohttp.ClientSession() as session:
        url = f'https://api.telegram.org/file/bot{HIMERA_TOKEN_BOT}/{file.file_path}'
        async with session.get(url) as response:
            if not os.path.exists('./excel/documents'):
                os.mkdir('./excel/documents')
            with open(f'./excel/documents/{file_name}', 'wb') as f:
                f.write(await response.read())
    salt = 1
    text = bot_message['text']
    async for statistics in search_by_name(utils.file_name_to_file_path(file_name)):
        if statistics[0] == 'statistics':
            new_text = bot_responses['searching']['statistics'].format(
                number=statistics[1], all_number=statistics[2]
            )
            new_text += '.'*salt
            if text == new_text:
                salt = (salt + 1) % 3
                new_text += '.'
            await bot.edit_message_text(new_text, bot_message['chat']['id'], bot_message['message_id'])
            text = new_text
        else:
            document = statistics[1]
            return document
