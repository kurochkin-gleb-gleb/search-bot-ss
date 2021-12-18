from bot.bot import bot
import asyncio


def test_queue(chat_id, text):
    # await asyncio.sleep(40)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.send_message(chat_id, text))
    loop.close()

