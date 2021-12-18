from time import sleep
from bot.bot import bot


def test_queue(chat_id, text):
    # sleep(40)
    bot.send_message(chat_id, text)
