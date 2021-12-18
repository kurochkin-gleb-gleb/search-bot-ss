from bot.bot import bot
import asyncio


def test_queue(chat_id, text):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(asyncio.sleep(40))
    loop.run_until_complete(bot.send_message(chat_id, text))
    loop.close()

